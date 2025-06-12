import logging
from typing import Dict, List, Optional, Tuple

import dagger
from index.models import ChunkData, ProcessingConfig
from index.utils.code_parser import parse_code_file
from index.utils.file import get_file_size


class FileProcessor:
    """Handles file processing operations for code indexing."""

    @staticmethod
    def _validate_symbol_lines(symbol_obj, total_lines: int, filepath: str, logger: logging.Logger) -> bool:
        """Validate symbol line numbers."""
        if not (isinstance(symbol_obj.start_line, int) and isinstance(symbol_obj.end_line, int) and
                symbol_obj.start_line > 0 and symbol_obj.end_line >= symbol_obj.start_line):
            logger.warning(
                f"Invalid lines for {getattr(symbol_obj, 'name', 'Unnamed')} in {filepath}")
            return False

        if symbol_obj.start_line > total_lines or symbol_obj.end_line > total_lines:
            logger.warning(
                f"Lines out of bounds for {getattr(symbol_obj, 'name', 'Unnamed')} in {filepath}")
            return False

        return True

    @staticmethod
    def _is_file_processable(file_size: int, filepath: str, config: ProcessingConfig, logger: logging.Logger) -> bool:
        """Check if file should be processed."""
        if file_size == 0:
            logger.info(f"Skipping zero-size file: {filepath}")
            return False
        if file_size > config.max_file_size:
            logger.info(
                f"Skipping large file ({file_size/1000:.0f}KB): {filepath}")
            return False
        return True

    @staticmethod
    def _create_chunk_data(
        content: str,
        filepath: str,
        start_line: int,
        end_line: int,
        language: str,
        symbols: List[Dict],
        context: str
    ) -> ChunkData:
        """Create a standardized chunk data object."""
        return ChunkData(
            content=content,
            filepath=filepath,
            start_line=start_line,
            end_line=end_line,
            language=language,
            symbols=symbols,
            context=context
        )

    @staticmethod
    def _create_semantic_chunks(
        filepath: str,
        lines: List[str],
        all_file_symbols: List,
        file_language: str,
        config: ProcessingConfig,
        logger: logging.Logger
    ) -> List[ChunkData]:
        """Extract semantic chunks from code symbols."""
        chunks = []
        block_symbols = [
            s for s in all_file_symbols
            if hasattr(s, 'start_line') and hasattr(s, 'end_line') and
            hasattr(s, 'type') and s.type in ['function', 'class', 'method']
        ]

        for symbol_obj in block_symbols:
            if not FileProcessor._validate_symbol_lines(symbol_obj, len(lines), filepath, logger):
                continue

            chunk_lines = lines[symbol_obj.start_line - 1:symbol_obj.end_line]
            chunk_text = "\n".join(chunk_lines)

            if not chunk_text.strip():
                continue

            if len(chunk_lines) > config.max_semantic_chunk_lines:
                # Sub-chunk large symbols
                chunks.extend(FileProcessor._sub_chunk_symbol(
                    symbol_obj, chunk_lines, all_file_symbols, file_language, config, logger
                ))
            else:
                symbols_info = [
                    vars(s) for s in all_file_symbols
                    if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                    symbol_obj.start_line <= s.line_number <= symbol_obj.end_line
                ]

                # Ensure main symbol is included
                if not any(s.get('name') == getattr(symbol_obj, 'name', None) for s in symbols_info):
                    if hasattr(symbol_obj, 'line_number') and isinstance(symbol_obj.line_number, int):
                        symbols_info.append(vars(symbol_obj))

                context = getattr(
                    symbol_obj, 'docstring', '') or f"{symbol_obj.type} {getattr(symbol_obj, 'name', 'Unnamed')}"

                chunks.append(FileProcessor._create_chunk_data(
                    chunk_text, filepath, symbol_obj.start_line, symbol_obj.end_line,
                    file_language, symbols_info, context
                ))

        return chunks

    @staticmethod
    def _sub_chunk_symbol(
        symbol_obj,
        chunk_lines: List[str],
        all_file_symbols: List,
        file_language: str,
        config: ProcessingConfig,
        logger: logging.Logger
    ) -> List[ChunkData]:
        """Sub-chunk large symbols into smaller pieces."""
        sub_chunks = []
        logger.info(
            f"Sub-chunking large symbol {getattr(symbol_obj, 'name', 'Unnamed')} ({len(chunk_lines)} lines)")

        for i in range(0, len(chunk_lines), config.fallback_chunk_size):
            sub_chunk_slice = chunk_lines[i:i + config.fallback_chunk_size]
            sub_content_text = "\n".join(sub_chunk_slice)

            if not sub_content_text.strip():
                continue

            actual_start_line = symbol_obj.start_line + i
            actual_end_line = actual_start_line + len(sub_chunk_slice) - 1

            sub_symbols_info = [
                vars(s) for s in all_file_symbols
                if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                actual_start_line <= s.line_number <= actual_end_line
            ]

            context = f"Part of {symbol_obj.type} {getattr(symbol_obj, 'name', 'Unnamed')} (lines {actual_start_line}-{actual_end_line})"

            sub_chunks.append(FileProcessor._create_chunk_data(
                sub_content_text, symbol_obj.filepath if hasattr(
                    symbol_obj, 'filepath') else "unknown",
                actual_start_line, actual_end_line, file_language, sub_symbols_info, context
            ))

        return sub_chunks

    @staticmethod
    def _create_fallback_chunks(
        filepath: str,
        lines: List[str],
        all_file_symbols: List,
        file_language: str,
        config: ProcessingConfig,
        code_file,
        logger: logging.Logger
    ) -> List[ChunkData]:
        """Create fixed-size chunks as fallback."""
        chunks = []
        logger.info(f"Creating fallback chunks for {filepath}")

        for i in range(0, len(lines), config.fallback_chunk_size):
            chunk_end_idx = min(i + config.fallback_chunk_size, len(lines))
            chunk_slice = lines[i:chunk_end_idx]
            chunk_content = "\n".join(chunk_slice)

            if not chunk_content.strip():
                continue

            actual_start_line = i + 1
            actual_end_line = chunk_end_idx

            symbols_info = []
            if all_file_symbols:
                symbols_info = [
                    vars(s) for s in all_file_symbols
                    if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                    actual_start_line <= s.line_number <= actual_end_line
                ]

            context = f"Lines {actual_start_line}-{actual_end_line} from file {filepath}"

            # Try to get richer context if available
            if code_file and hasattr(code_file, 'get_context_around_line'):
                middle_line = actual_start_line + len(chunk_slice) // 2
                try:
                    context = code_file.get_context_around_line(middle_line, 5)
                except Exception as ctx_err:
                    logger.warning(
                        f"Could not get context for {filepath}: {ctx_err}")

            chunks.append(FileProcessor._create_chunk_data(
                chunk_content, filepath, actual_start_line, actual_end_line,
                file_language, symbols_info, context
            ))

        return chunks

    @staticmethod
    async def process_file_core(
        filepath: str,
        content: str,
        config: ProcessingConfig,
        logger: logging.Logger
    ) -> List[ChunkData]:
        """Core file processing logic - returns chunk data without embeddings."""
        lines = content.splitlines()
        logger.info(f"Processing {filepath}: {len(lines)} lines")

        # Parse code file
        code_file = parse_code_file(content, filepath)
        file_language = "unknown"
        all_file_symbols = []

        if code_file:
            file_language = getattr(code_file, 'language', 'unknown')
            all_file_symbols = getattr(code_file, 'symbols', [])
            logger.info(
                f"Parsed {filepath}: language={file_language}, {len(all_file_symbols)} symbols")

        # 1. Try semantic chunking first
        if code_file and all_file_symbols:
            semantic_chunks = FileProcessor._create_semantic_chunks(
                filepath, lines, all_file_symbols, file_language, config, logger
            )
            if semantic_chunks:
                logger.info(
                    f"Created {len(semantic_chunks)} semantic chunks for {filepath}")
                return semantic_chunks

        # 2. Fallback to fixed-size chunking
        if content.strip():
            fallback_chunks = FileProcessor._create_fallback_chunks(
                filepath, lines, all_file_symbols, file_language, config, code_file, logger
            )
            logger.info(
                f"Created {len(fallback_chunks)} fallback chunks for {filepath}")
            return fallback_chunks

        logger.warning(f"No chunks created for {filepath}")
        return []

    @staticmethod
    async def get_filtered_files(container: dagger.Container, extensions: Optional[List[str]] = None) -> List[str]:
        """Get all source files in the container, filtering out build artifacts and binaries."""

        # Comprehensive list of source-related extensions if none provided
        if not extensions:
            extensions = [
                # Code files
                "py", "js", "ts", "tsx", "jsx", "java", "c", "cpp", "h", "hpp", "go", "rs", "rb", "php", "cs", "scala", "kt",
                # Config files
                "yaml", "yml", "json", "toml", "ini", "cfg", "conf", "properties", "xml", "env", "Dockerfile",
                # Documentation
                "md", "rst", "txt",
                # Shell scripts
                "sh", "bash", "zsh", "bat", "ps1",
                # Web files
                "html", "css", "scss", "sass", "less", "svg", "graphql"
            ]

        # Build directory patterns to exclude - just directory names for cleaner matching
        exclude_dirs = [
            "node_modules",
            "build",
            "dist",
            "target",
            ".git",
            "bin",
            "obj",
            "__pycache__",
            ".venv",
            "venv",
            "vendor",
            "out",
            ".idea",
            ".vscode",
            "coverage"
        ]

        # File patterns to exclude
        exclude_files = [
            ".min.js", ".min.css", ".map", ".bundle.",
            # Binary files
            ".so", ".dll", ".exe", ".bin", ".o", ".a", ".lib", ".pyc", ".pyo",
            # Large data files
            ".zip", ".tar", ".gz", ".rar", ".jar", ".war", ".ear"
        ]

        # Get all files
        all_files = await container.with_exec(["find", ".", "-type", "f"]).stdout()
        file_list = all_files.strip().split("\n")

        # Filter files
        filtered_files = []
        excluded_count = 0

        for file_path in file_list:
            # Skip empty paths
            if not file_path or file_path == ".":
                continue

            # Normalize path (remove "./" prefix if exists)
            if file_path.startswith("./"):
                file_path = file_path[2:]

            # Check if path contains any excluded directory
            if any(f"/{exclude_dir}/" in f"/{file_path}/" for exclude_dir in exclude_dirs):
                excluded_count += 1
                continue

            # Check if the file matches any excluded pattern
            if any(exclude_pattern in file_path for exclude_pattern in exclude_files):
                excluded_count += 1
                continue

            # Include if extension matches or if it's a special file
            file_ext = file_path.split(".")[-1] if "." in file_path else ""
            is_special_file = (
                file_path.endswith("Makefile") or
                file_path.endswith("README") or
                file_path.endswith("Jenkinsfile") or
                "requirements" in file_path or
                "setup.py" in file_path or
                "package.json" in file_path
            )

            if file_ext in extensions or is_special_file:
                filtered_files.append(file_path)

        # Log statistics about filtering
        print(
            f"Found {len(file_list)} files, excluded {excluded_count}, kept {len(filtered_files)}")

        return filtered_files

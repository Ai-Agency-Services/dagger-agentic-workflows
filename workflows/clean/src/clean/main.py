import os
import traceback
from typing import Annotated, List, NamedTuple, Optional

import anyio
import dagger
from dagger import dag
import yaml
from clean.core.clean_names_workflow import clean_names_workflow
from clean.models.config import YAMLConfig
from clean.utils.code_parser import parse_code_file
from clean.utils.embeddings import generate_embeddings
from clean.utils.file import get_file_size
from dagger import Doc, function, object_type
from simple_chalk import green, red
from supabase import Client, create_client


class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: str


@object_type
class Clean:
    config: dict
    config_file: dagger.File

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to the YAML config file")]) -> "Clean":
        """ Create a Clean object from a YAML config file """
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, config_file=config_file)

    @function
    async def meaningful_names(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        supabase_url: Annotated[str, Doc("Supabase project URL")],
        supabase_key: Annotated[dagger.Secret, Doc("Supabase API key")],
        repository_url: Annotated[str, Doc("Repository URL to generate tests for")],
        branch: Annotated[str, Doc("Branch to generate tests for")],
        open_router_api_key: Optional[dagger.Secret] = None,
        openai_api_key: Optional[dagger.Secret] = None,
    ) -> str:
        """ Refactor the code to use meaningful names """
        try:
            self.config: YAMLConfig = YAMLConfig(**self.config)
            await clean_names_workflow(
                config=self.config,
                provider=self.config.llm.provider,
                open_router_api_key=open_router_api_key,
                openai_api_key=openai_api_key,
                github_access_token=github_access_token,
                repo_url=repository_url,
                branch=branch,
                supabase_url=supabase_url,
                supabase_key=supabase_key,
                model_name=self.config.llm.model_name,
                max_files=self.config.generation.max_files
            )
        except Exception as e:
            print(red(f"Error during workflow execution: {e}"))
            raise

        return "Workflow completed successfully!"

    @function
    async def index_file(
        self,
        file_path: Annotated[dagger.File, Doc("Path to the file to index")],
        supabase_url: Annotated[str, Doc("Supabase project URL")],
        supabase_key: Annotated[dagger.Secret, Doc("Supabase API key")],
        container: Annotated[dagger.Container, Doc("Dagger container")],
        open_ai_key: Optional[dagger.Secret] = None,
        max_semantic_chunk_lines: Optional[int] = 200,
        fallback_chunk_size: Optional[int] = 50,
    ) -> int:
        """ 
        Process a single code file, chunk it semantically and index it 
        Returns the number of chunks indexed.
        """
        supabase = create_client(supabase_url, await supabase_key.plaintext())  # Added await

        try:
            file_size = await get_file_size(container=container, filepath=file_path)
            if file_size == 0:
                print(f"Skipping zero-size or inaccessible file: {file_path}")
                return 0
            if file_size > 1_000_000:  # 1MB limit
                print(
                    f"Skipping large file (>{file_size/1000:.0f}KB): {file_path}")
                return 0

            content = await container.file(file_path).contents()
            if not content.strip():
                print(f"Skipping empty file content: {file_path}")
                return 0

            # Can return None or CodeFile object
            code_file = parse_code_file(content, file_path)
            lines = content.splitlines()
            processed_chunks_data = []  # To store chunk dictionaries before embedding

            file_language = "unknown"
            all_file_symbols = []  # All symbols found in the file by the parser

            if code_file:
                file_language = getattr(code_file, 'language', 'unknown')
                all_file_symbols = getattr(code_file, 'symbols', [])

            # 1. Attempt Semantic Chunking
            if code_file and all_file_symbols:
                # Identify symbols that define blocks (e.g., functions, classes, methods)
                # Adjust s.type checks based on your parser's output for block-defining symbols
                block_symbols = [
                    s for s in all_file_symbols
                    if hasattr(s, 'start_line') and hasattr(s, 'end_line') and
                    hasattr(s, 'type') and s.type in [
                        'function', 'class', 'method']  # Example types
                ]

                for symbol_obj in block_symbols:
                    # Validate symbol start_line and end_line
                    if not (isinstance(symbol_obj.start_line, int) and isinstance(symbol_obj.end_line, int) and
                            symbol_obj.start_line > 0 and symbol_obj.end_line >= symbol_obj.start_line):
                        print(
                            f"Warning: Symbol {getattr(symbol_obj, 'name', 'Unnamed')} in {file_path} has invalid/missing start/end lines. Skipping.")
                        continue

                    # Ensure line numbers are within file bounds
                    if symbol_obj.start_line > len(lines) or symbol_obj.end_line > len(lines):
                        print(
                            f"Warning: Symbol {getattr(symbol_obj, 'name', 'Unnamed')} in {file_path} line numbers [{symbol_obj.start_line}-{symbol_obj.end_line}] out of bounds for file length {len(lines)}. Skipping.")
                        continue

                    # Extract lines for the current semantic block (1-indexed to 0-indexed)
                    current_chunk_lines_content = lines[symbol_obj.start_line -
                                                        1: symbol_obj.end_line]
                    current_chunk_text = "\n".join(current_chunk_lines_content)

                    if not current_chunk_text.strip():
                        continue

                    # Sub-chunk if the semantic chunk is too large
                    if len(current_chunk_lines_content) > max_semantic_chunk_lines:
                        print(
                            f"Semantic chunk for {getattr(symbol_obj, 'name', 'Unnamed')} in {file_path} ({len(current_chunk_lines_content)} lines) exceeds max {max_semantic_chunk_lines}. Sub-chunking.")
                        for i in range(0, len(current_chunk_lines_content), fallback_chunk_size):
                            sub_chunk_slice = current_chunk_lines_content[i: i +
                                                                          fallback_chunk_size]
                            sub_content_text = "\n".join(sub_chunk_slice)
                            if not sub_content_text.strip():
                                continue

                            actual_start_line = symbol_obj.start_line + i
                            actual_end_line = actual_start_line + \
                                len(sub_chunk_slice) - 1

                            sub_chunk_symbols_info = [
                                vars(s) for s in all_file_symbols
                                if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                                actual_start_line <= s.line_number <= actual_end_line
                            ]

                            processed_chunks_data.append({
                                "content": sub_content_text, "filepath": file_path,
                                "start_line": actual_start_line, "end_line": actual_end_line,
                                "language": file_language, "symbols": sub_chunk_symbols_info,
                                "context": f"Part of {symbol_obj.type} {getattr(symbol_obj, 'name', 'Unnamed')} (lines {actual_start_line}-{actual_end_line})"
                            })
                    else:
                        # Semantic chunk is within size limits
                        chunk_symbols_info = [
                            vars(s) for s in all_file_symbols
                            if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                            symbol_obj.start_line <= s.line_number <= symbol_obj.end_line
                        ]
                        # Ensure the main symbol defining the block is included if its line_number is representative
                        if not any(s_info.get('name') == symbol_obj.name for s_info in chunk_symbols_info if 'name' in s_info) and \
                                hasattr(symbol_obj, 'line_number') and isinstance(symbol_obj.line_number, int) and \
                                symbol_obj.start_line <= symbol_obj.line_number <= symbol_obj.end_line:
                            chunk_symbols_info.append(vars(symbol_obj))

                        processed_chunks_data.append({
                            "content": current_chunk_text, "filepath": file_path,
                            "start_line": symbol_obj.start_line, "end_line": symbol_obj.end_line,
                            "language": file_language, "symbols": chunk_symbols_info,
                            "context": getattr(symbol_obj, 'docstring', '') or f"{symbol_obj.type} {getattr(symbol_obj, 'name', 'Unnamed')}"
                        })

            # 2. Fallback to fixed-size chunking if no semantic chunks were created
            if not processed_chunks_data and content.strip():  # Ensure content is not just whitespace
                print(
                    f"No semantic chunks generated for {file_path}. Applying fixed-size chunking as fallback.")
                for i in range(0, len(lines), fallback_chunk_size):
                    chunk_start_line_0idx = i
                    chunk_end_line_0idx = min(
                        i + fallback_chunk_size, len(lines))

                    chunk_slice = lines[chunk_start_line_0idx: chunk_end_line_0idx]
                    chunk_content_text = "\n".join(chunk_slice)

                    if not chunk_content_text.strip():
                        continue

                    actual_start_line = chunk_start_line_0idx + 1
                    # if slice end is exclusive, this is correct for 1-based end line
                    actual_end_line = chunk_end_line_0idx

                    fixed_chunk_symbols_info = []
                    if all_file_symbols:  # Check if we have symbols from parsing
                        fixed_chunk_symbols_info = [
                            vars(s) for s in all_file_symbols
                            if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                            actual_start_line <= s.line_number <= actual_end_line
                        ]

                    context_str = f"Lines {actual_start_line}-{actual_end_line} from file {file_path}"
                    # Use richer context if available
                    if code_file and hasattr(code_file, 'get_context_around_line'):
                        # Pick a middle line for context
                        middle_line_for_context = actual_start_line + \
                            len(chunk_slice) // 2
                        try:
                            context_str = code_file.get_context_around_line(
                                middle_line_for_context, 5)
                        except Exception as ctx_err:
                            print(
                                f"Warning: Could not get_context_around_line for fallback chunk in {file_path}: {ctx_err}")

                    processed_chunks_data.append({
                        "content": chunk_content_text, "filepath": file_path,
                        "start_line": actual_start_line, "end_line": actual_end_line,
                        "language": file_language, "symbols": fixed_chunk_symbols_info,
                        "context": context_str
                    })

            # 3. Generate embeddings and insert all collected chunks
            chunks_indexed_this_file = 0
            for chunk_data in processed_chunks_data:
                embedding = await generate_embeddings(
                    text=chunk_data["content"],
                    model="text-embedding-3-small",  # Consider making this configurable
                    openai_api_key=open_ai_key
                )
                if not embedding:
                    print(
                        f"Failed to generate embedding for chunk in {file_path} at line {chunk_data['start_line']}. Skipping.")
                    continue

                insert_payload = {
                    "content": chunk_data["content"], "embedding": embedding,
                    "filepath": chunk_data["filepath"], "start_line": chunk_data["start_line"],
                    "end_line": chunk_data["end_line"], "language": chunk_data["language"],
                    # This should be a list of dicts, JSONB in Supabase handles this
                    "symbols": chunk_data["symbols"],
                    "context": chunk_data["context"]
                }
                try:
                    supabase.table("code_embeddings").insert(
                        insert_payload).execute()
                    chunks_indexed_this_file += 1
                except Exception as db_exc:
                    print(
                        f"Error inserting chunk into Supabase for {file_path} (lines {chunk_data['start_line']}-{chunk_data['end_line']}): {db_exc}")
                    # For debugging, you might want to log the payload, but be careful with sensitive data:
                    # print(f"Failed payload (first 500 chars of content): {{'content': '{str(insert_payload.get('content'))[:500]}...', ...}}")

            if chunks_indexed_this_file > 0:
                print(
                    f"Indexed {chunks_indexed_this_file} semantic/fallback chunks from {file_path}")
            return chunks_indexed_this_file

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            traceback.print_exc()  # Print full traceback for debugging
            return 0

    async def _process_single_file(
        self,
        filepath: str,
        supabase: Client,
        container: dagger.Container,
        open_ai_key: dagger.Secret,
        max_semantic_chunk_lines: int,
        fallback_chunk_size: int,
    ) -> int:
        """Internal method to process a single file with direct supabase client."""
        try:
            file_size = await get_file_size(container=container, filepath=filepath)
            if file_size == 0:
                print(f"Skipping zero-size or inaccessible file: {filepath}")
                return 0
            if file_size > 1_000_000:  # 1MB limit
                print(
                    f"Skipping large file (>{file_size/1000:.0f}KB): {filepath}")
                return 0

            content = await container.file(filepath).contents()
            if not content.strip():
                print(f"Skipping empty file content: {filepath}")
                return 0

            # Can return None or CodeFile object
            code_file = parse_code_file(content, filepath)
            lines = content.splitlines()
            processed_chunks_data = []  # To store chunk dictionaries before embedding

            file_language = "unknown"
            all_file_symbols = []  # All symbols found in the file by the parser

            if code_file:
                file_language = getattr(code_file, 'language', 'unknown')
                all_file_symbols = getattr(code_file, 'symbols', [])

            # 1. Attempt Semantic Chunking
            if code_file and all_file_symbols:
                # Identify symbols that define blocks (e.g., functions, classes, methods)
                # Adjust s.type checks based on your parser's output for block-defining symbols
                block_symbols = [
                    s for s in all_file_symbols
                    if hasattr(s, 'start_line') and hasattr(s, 'end_line') and
                    hasattr(s, 'type') and s.type in [
                        'function', 'class', 'method']  # Example types
                ]

                for symbol_obj in block_symbols:
                    # Validate symbol start_line and end_line
                    if not (isinstance(symbol_obj.start_line, int) and isinstance(symbol_obj.end_line, int) and
                            symbol_obj.start_line > 0 and symbol_obj.end_line >= symbol_obj.start_line):
                        print(
                            f"Warning: Symbol {getattr(symbol_obj, 'name', 'Unnamed')} in {filepath} has invalid/missing start/end lines. Skipping.")
                        continue

                    # Ensure line numbers are within file bounds
                    if symbol_obj.start_line > len(lines) or symbol_obj.end_line > len(lines):
                        print(
                            f"Warning: Symbol {getattr(symbol_obj, 'name', 'Unnamed')} in {filepath} line numbers [{symbol_obj.start_line}-{symbol_obj.end_line}] out of bounds for file length {len(lines)}. Skipping.")
                        continue

                    # Extract lines for the current semantic block (1-indexed to 0-indexed)
                    current_chunk_lines_content = lines[symbol_obj.start_line -
                                                        1: symbol_obj.end_line]
                    current_chunk_text = "\n".join(current_chunk_lines_content)

                    if not current_chunk_text.strip():
                        continue

                    # Sub-chunk if the semantic chunk is too large
                    if len(current_chunk_lines_content) > max_semantic_chunk_lines:
                        print(
                            f"Semantic chunk for {getattr(symbol_obj, 'name', 'Unnamed')} in {filepath} ({len(current_chunk_lines_content)} lines) exceeds max {max_semantic_chunk_lines}. Sub-chunking.")
                        for i in range(0, len(current_chunk_lines_content), fallback_chunk_size):
                            sub_chunk_slice = current_chunk_lines_content[i: i +
                                                                          fallback_chunk_size]
                            sub_content_text = "\n".join(sub_chunk_slice)
                            if not sub_content_text.strip():
                                continue

                            actual_start_line = symbol_obj.start_line + i
                            actual_end_line = actual_start_line + \
                                len(sub_chunk_slice) - 1

                            sub_chunk_symbols_info = [
                                vars(s) for s in all_file_symbols
                                if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                                actual_start_line <= s.line_number <= actual_end_line
                            ]

                            processed_chunks_data.append({
                                "content": sub_content_text, "filepath": filepath,
                                "start_line": actual_start_line, "end_line": actual_end_line,
                                "language": file_language, "symbols": sub_chunk_symbols_info,
                                "context": f"Part of {symbol_obj.type} {getattr(symbol_obj, 'name', 'Unnamed')} (lines {actual_start_line}-{actual_end_line})"
                            })
                    else:
                        # Semantic chunk is within size limits
                        chunk_symbols_info = [
                            vars(s) for s in all_file_symbols
                            if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                            symbol_obj.start_line <= s.line_number <= symbol_obj.end_line
                        ]
                        # Ensure the main symbol defining the block is included if its line_number is representative
                        if not any(s_info.get('name') == symbol_obj.name for s_info in chunk_symbols_info if 'name' in s_info) and \
                                hasattr(symbol_obj, 'line_number') and isinstance(symbol_obj.line_number, int) and \
                                symbol_obj.start_line <= symbol_obj.line_number <= symbol_obj.end_line:
                            chunk_symbols_info.append(vars(symbol_obj))

                        processed_chunks_data.append({
                            "content": current_chunk_text, "filepath": filepath,
                            "start_line": symbol_obj.start_line, "end_line": symbol_obj.end_line,
                            "language": file_language, "symbols": chunk_symbols_info,
                            "context": getattr(symbol_obj, 'docstring', '') or f"{symbol_obj.type} {getattr(symbol_obj, 'name', 'Unnamed')}"
                        })

            # 2. Fallback to fixed-size chunking if no semantic chunks were created
            if not processed_chunks_data and content.strip():  # Ensure content is not just whitespace
                print(
                    f"No semantic chunks generated for {filepath}. Applying fixed-size chunking as fallback.")
                for i in range(0, len(lines), fallback_chunk_size):
                    chunk_start_line_0idx = i
                    chunk_end_line_0idx = min(
                        i + fallback_chunk_size, len(lines))

                    chunk_slice = lines[chunk_start_line_0idx: chunk_end_line_0idx]
                    chunk_content_text = "\n".join(chunk_slice)

                    if not chunk_content_text.strip():
                        continue

                    actual_start_line = chunk_start_line_0idx + 1
                    # if slice end is exclusive, this is correct for 1-based end line
                    actual_end_line = chunk_end_line_0idx

                    fixed_chunk_symbols_info = []
                    if all_file_symbols:  # Check if we have symbols from parsing
                        fixed_chunk_symbols_info = [
                            vars(s) for s in all_file_symbols
                            if hasattr(s, 'line_number') and isinstance(s.line_number, int) and
                            actual_start_line <= s.line_number <= actual_end_line
                        ]

                    context_str = f"Lines {actual_start_line}-{actual_end_line} from file {filepath}"
                    # Use richer context if available
                    if code_file and hasattr(code_file, 'get_context_around_line'):
                        # Pick a middle line for context
                        middle_line_for_context = actual_start_line + \
                            len(chunk_slice) // 2
                        try:
                            context_str = code_file.get_context_around_line(
                                middle_line_for_context, 5)
                        except Exception as ctx_err:
                            print(
                                f"Warning: Could not get_context_around_line for fallback chunk in {filepath}: {ctx_err}")

                    processed_chunks_data.append({
                        "content": chunk_content_text, "filepath": filepath,
                        "start_line": actual_start_line, "end_line": actual_end_line,
                        "language": file_language, "symbols": fixed_chunk_symbols_info,
                        "context": context_str
                    })

            # 3. Generate embeddings and insert all collected chunks
            chunks_indexed_this_file = 0
            for chunk_data in processed_chunks_data:
                embedding = await generate_embeddings(
                    text=chunk_data["content"],
                    model="text-embedding-3-small",  # Consider making this configurable
                    openai_api_key=open_ai_key
                )
                if not embedding:
                    print(
                        f"Failed to generate embedding for chunk in {filepath} at line {chunk_data['start_line']}. Skipping.")
                    continue

                insert_payload = {
                    "content": chunk_data["content"], "embedding": embedding,
                    "filepath": chunk_data["filepath"], "start_line": chunk_data["start_line"],
                    "end_line": chunk_data["end_line"], "language": chunk_data["language"],
                    # This should be a list of dicts, JSONB in Supabase handles this
                    "symbols": chunk_data["symbols"],
                    "context": chunk_data["context"]
                }
                try:
                    supabase.table("code_embeddings").insert(
                        insert_payload).execute()
                    chunks_indexed_this_file += 1
                except Exception as db_exc:
                    print(
                        f"Error inserting chunk into Supabase for {filepath} (lines {chunk_data['start_line']}-{chunk_data['end_line']}): {db_exc}")
                    # For debugging, you might want to log the payload, but be careful with sensitive data:
                    # print(f"Failed payload (first 500 chars of content): {{'content': '{str(insert_payload.get('content'))[:500]}...', ...}}")

            if chunks_indexed_this_file > 0:
                print(
                    f"Indexed {chunks_indexed_this_file} semantic/fallback chunks from {filepath}")
            return chunks_indexed_this_file

        except Exception as e:
            print(f"Error processing file {filepath}: {e}")
            traceback.print_exc()  # Print full traceback for debugging
            return 0

    async def index_file_batch(
        self,
        file_batch: List[str],
        supabase: Client,
        openai_api_key: dagger.Secret,
        container: dagger.Container,
        max_semantic_chunk_lines: int,
        fallback_chunk_size: int
    ) -> int:
        """Process a batch of files concurrently and return total chunks indexed."""

        async def process_single_file(filepath: str) -> int:
            """Wrapper for processing a single file."""
            return await self._process_single_file(
                filepath=filepath,
                supabase=supabase,
                container=container,
                open_ai_key=openai_api_key,
                max_semantic_chunk_lines=max_semantic_chunk_lines,
                fallback_chunk_size=fallback_chunk_size
            )

        # Fix: Correct anyio usage with result collection
        results = []

        async def collect_result(filepath: str):
            """Collect result from processing a single file."""
            try:
                result = await process_single_file(filepath)
                results.append(result)
            except Exception as e:
                print(f"Error processing file {filepath}: {e}")
                results.append(0)  # Add 0 for failed files

        async with anyio.create_task_group() as tg:
            for filepath in file_batch:
                tg.start_soon(collect_result, filepath)

        total_chunks = sum(results)
        print(
            f"Batch completed: indexed {total_chunks} chunks from {len(file_batch)} files")
        return total_chunks

    @function
    async def index_codebase(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to index")],
        branch: Annotated[str, Doc("Branch to index")],
        supabase_url: str,
        openai_api_key: dagger.Secret,
        supabase_key: dagger.Secret,
        batch_size: int = 5,
        file_extensions: list[str] = ["py", "js",
                                      "ts", "java", "c", "cpp", "go", "rs"],
    ) -> None:
        """Index all code files in a repository with concurrent processing."""
        try:
            self.config: YAMLConfig = YAMLConfig(**self.config)
            if openai_api_key:
                print(green("Setting OpenAI API key..."))
                os.environ["OPENAI_API_KEY"] = await openai_api_key.plaintext()

            source = (
                await dag.git(url=repository_url, keep_git_dir=True)
                .with_auth_token(github_access_token)  # Correct method name
                .branch(branch)
                .tree()
            )

        except Exception as e:
            print(red(f"Failed to clone repository: {e}"))
            raise

        try:
            container = await dag.builder(self.config_file).build_test_environment(
                source=source, dockerfile_path=self.config.container.docker_file_path
            )
            supabase = create_client(supabase_url, await supabase_key.plaintext())
            print("Supabase client created")
            total_indexed_chunks = 0

            # Define find command to run inside the container (workdir is /src)
            file_list_cmd = ["find", ".", "-type", "f"]
            exclude_dirs = [".git", "node_modules", "venv", ".venv", "build",
                            "dist", "__pycache__", "target", "docs", "examples", "tests", "test"]
            for dir_name in exclude_dirs:
                file_list_cmd.extend(["-not", "-path", f"./{dir_name}/*"])

            # Execute find command in the container's /src directory
            file_list_output = await container.with_exec(file_list_cmd).stdout()
            all_files_relative = [
                f.strip() for f in file_list_output.strip().split("\n") if f.strip()
            ]

            filtered_files = [
                f_rel[2:] if f_rel.startswith("./") else f_rel
                for f_rel in all_files_relative
                if any(f_rel.endswith(ext) for ext in file_extensions) and "/." not in f_rel
            ]
            print(
                f"Found {len(filtered_files)} files to process after filtering.")

            # Get chunking parameters from config
            fallback_chunk_size_val = 50
            max_semantic_chunk_lines_val = 200

            # Convert config dict to YAMLConfig object first
            if isinstance(self.config, dict):
                config_obj = YAMLConfig(**self.config)
            else:
                config_obj = self.config

            if hasattr(config_obj, "indexing"):
                if hasattr(config_obj.indexing, "chunk_size"):
                    fallback_chunk_size_val = config_obj.indexing.chunk_size
                if hasattr(config_obj.indexing, "max_semantic_chunk_lines"):
                    max_semantic_chunk_lines_val = config_obj.indexing.max_semantic_chunk_lines

            print(f"Using Max Semantic Chunk Lines: {max_semantic_chunk_lines_val}, "
                  f"Fallback Chunk Size: {fallback_chunk_size_val}, "
                  f"Batch Size: {batch_size}")

            # Process files in batches concurrently
            for i in range(0, len(filtered_files), batch_size):
                batch = filtered_files[i:i + batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(filtered_files) + batch_size - 1)//batch_size}: "
                      f"{len(batch)} files")

                batch_chunks = await self.index_file_batch(
                    file_batch=batch,
                    supabase=supabase,
                    openai_api_key=openai_api_key,
                    container=container,
                    max_semantic_chunk_lines=max_semantic_chunk_lines_val,
                    fallback_chunk_size=fallback_chunk_size_val
                )

                total_indexed_chunks += batch_chunks
                print(
                    f"Total progress: {total_indexed_chunks} chunks indexed so far")

            print(
                f"Successfully indexed a total of {total_indexed_chunks} code chunks.")
        except Exception as e:
            print(f"Error indexing codebase: {e}")
            import traceback
            traceback.print_exc()
            raise

    @function
    async def index_codebase_with_full_concurrency(
        self,
        supabase_url: str,
        openai_api_key: dagger.Secret,
        supabase_key: dagger.Secret,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to index")],
        branch: Annotated[str, Doc("Branch to index")],
        file_extensions: list[str] = ["py", "js",
                                      "ts", "java", "c", "cpp", "go", "rs"],
        max_concurrent: int = 5,
    ) -> None:
        """Alternative implementation: process all files with semaphore-based concurrency control."""
        try:
            supabase = create_client(supabase_url, await supabase_key.plaintext())
            print("Supabase client created")

            # Get file list (same as before)
            file_list_cmd = ["find", ".", "-type", "f"]
            exclude_dirs = [".git", "node_modules", "venv", ".venv", "build",
                            "dist", "__pycache__", "target", "docs", "examples", "tests", "test"]
            for dir_name in exclude_dirs:
                file_list_cmd.extend(["-not", "-path", f"./{dir_name}/*"])

            try:
                self.config: YAMLConfig = YAMLConfig(**self.config)
                if openai_api_key:
                    print(green("Setting OpenAI API key..."))
                    os.environ["OPENAI_API_KEY"] = await openai_api_key.plaintext()

                source = (
                    await dag.git(url=repository_url, keep_git_dir=True)
                    # Correct method name
                    .with_auth_token(github_access_token)
                    .branch(branch)
                    .tree()
                )

            except Exception as e:
                print(red(f"Failed to clone repository: {e}"))
                raise

            container = await dag.builder(self.config_file).build_test_environment(
                source=source, dockerfile_path=self.config.container.docker_file_path
            )
            file_list_output = await container.with_exec(file_list_cmd).stdout()
            all_files_relative = [
                f.strip() for f in file_list_output.strip().split("\n") if f.strip()
            ]

            filtered_files = [
                f_rel[2:] if f_rel.startswith("./") else f_rel
                for f_rel in all_files_relative
                if any(f_rel.endswith(ext) for ext in file_extensions) and "/." not in f_rel
            ]
            print(
                f"Found {len(filtered_files)} files to process after filtering.")

            # Get chunking parameters
            fallback_chunk_size_val = getattr(
                self.config.indexing, 'chunk_size', 50)
            max_semantic_chunk_lines_val = getattr(
                self.config.indexing, 'max_semantic_chunk_lines', 200)

            print(f"Using Max Semantic Chunk Lines: {max_semantic_chunk_lines_val}, "
                  f"Fallback Chunk Size: {fallback_chunk_size_val}, "
                  f"Max Concurrent: {max_concurrent}")

            # Create semaphore to limit concurrent processing
            semaphore = anyio.Semaphore(max_concurrent)
            results = []

            async def process_with_semaphore(filepath: str):
                """Process a file with semaphore-controlled concurrency."""
                async with semaphore:
                    try:
                        result = await self._process_single_file(
                            filepath=filepath,
                            supabase=supabase,
                            container=container,
                            open_ai_key=openai_api_key,
                            max_semantic_chunk_lines=max_semantic_chunk_lines_val,
                            fallback_chunk_size=fallback_chunk_size_val
                        )
                        results.append(result)
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")
                        results.append(0)

            # Process all files concurrently with controlled concurrency
            async with anyio.create_task_group() as tg:
                for filepath in filtered_files:
                    tg.start_soon(process_with_semaphore, filepath)

            # Sum up results
            total_indexed_chunks = sum(results)
            print(
                f"Successfully indexed a total of {total_indexed_chunks} code chunks.")

        except Exception as e:
            print(f"Error indexing codebase: {e}")
            import traceback
            traceback.print_exc()
            raise

    @function
    async def clear_embeddings_table(
        self,
        supabase_url: Annotated[str, Doc("Supabase project URL")],
        supabase_key: Annotated[dagger.Secret, Doc("Supabase API key")],
    ) -> str:
        """Clear all data from the code_embeddings table."""
        try:
            supabase = create_client(supabase_url, await supabase_key.plaintext())

            # Method 1: Try batch delete approach first
            try:
                print("Attempting to clear code_embeddings table using batch delete...")

                # Get count of existing rows
                count_result = supabase.table("code_embeddings").select(
                    "id", count="exact").execute()
                initial_count = count_result.count if count_result.count else 0
                print(f"Found {initial_count} existing embeddings to clear")

                if initial_count == 0:
                    print("Table is already empty")
                    return "Table was already empty"

                # Delete in batches to avoid timeout
                batch_size = 1000
                deleted_total = 0

                while True:
                    # Get a batch of IDs to delete
                    ids_result = supabase.table("code_embeddings").select(
                        "id").limit(batch_size).execute()

                    if not ids_result.data:
                        break

                    # Extract IDs
                    ids_to_delete = [row["id"] for row in ids_result.data]

                    # Delete this batch
                    delete_result = supabase.table("code_embeddings").delete().in_(
                        "id", ids_to_delete).execute()
                    batch_deleted = len(ids_to_delete)
                    deleted_total += batch_deleted

                    print(
                        f"Deleted batch of {batch_deleted} embeddings (total: {deleted_total}/{initial_count})")

                    # If we deleted fewer than the batch size, we're likely done
                    if len(ids_to_delete) < batch_size:
                        break

            except Exception as batch_error:
                print(f"Batch delete failed: {batch_error}")

                # Method 2: Try RPC function as fallback
                try:
                    print("Batch delete failed, attempting RPC function...")
                    result = supabase.rpc("truncate_code_embeddings").execute()
                    print(
                        f"Table cleared successfully using RPC: {result.data}")
                    return "Table cleared successfully using RPC function"

                except Exception as rpc_error:
                    print(f"RPC function also failed: {rpc_error}")

                    # Method 3: Try simple delete all as last resort
                    try:
                        print("RPC failed, trying simple delete all...")
                        # This might be slower but should work
                        result = supabase.table(
                            "code_embeddings").delete().gte("id", 0).execute()
                        deleted_count = len(result.data) if result.data else 0
                        print(
                            f"Simple delete completed, deleted {deleted_count} rows")
                        return f"Table cleared using simple delete. Deleted {deleted_count} rows."

                    except Exception as simple_delete_error:
                        print(
                            f"All delete methods failed. Last error: {simple_delete_error}")
                        raise Exception(
                            f"Could not clear table. Batch delete: {batch_error}, RPC: {rpc_error}, Simple delete: {simple_delete_error}")

        except Exception as e:
            print(f"Error clearing embeddings table: {e}")
            traceback.print_exc()
            raise

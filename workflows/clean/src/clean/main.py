import traceback
import anyio
from typing import Annotated, NamedTuple, Optional

from clean.utils.code_parser import parse_code_file
from clean.utils.embeddings import generate_embeddings
import dagger
from supabase import create_client
import yaml
from clean.core.clean_names_workflow import clean_names_workflow
from clean.models.config import YAMLConfig
from clean.utils.file import get_file_size
from dagger import Doc, function, object_type
from simple_chalk import red


class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: str


@object_type
class Clean:
    config: dict

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to the YAML config file")]) -> "Clean":
        """ Create a Clean object from a YAML config file """
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict)

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
        max_semantic_chunk_lines: Optional[int] = 20,
        fallback_chunk_size: Optional[int] = 1000,
    ) -> int:
        """ 
        Process a single code file, chunk it semantically and index it 
        Returns the number of chunks indexed.
        """
        supabase = create_client(supabase_url, supabase_key)

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

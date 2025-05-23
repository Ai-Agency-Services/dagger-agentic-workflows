import argparse
import asyncio
import os
from typing import List, Dict, Any, Optional  # Added Optional

import dagger
from clean.models.config import YAMLConfig
# Assuming Symbol has name, type, start_line, end_line, line_number, docstring
from clean.utils.code_parser import parse_code_file
from clean.utils.embeddings import generate_embeddings
from supabase import Client, create_client
import traceback  # For detailed error logging


async def get_file_size(container: dagger.Container, filepath: str) -> int:
    """Get the size of a file inside a container."""
    try:
        # Run stat command inside the container, relative to its workdir
        size_str = await container.with_exec(
            ["stat", "-c", "%s", filepath]
        ).stdout()
        return int(size_str.strip())
    except Exception as e:
        print(f"Error getting size of {filepath}: {e}")
        return 0


async def process_file(
    # Path relative to container's workdir (e.g., "module/file.py")
    filepath: str,
    supabase: Client,
    # Assumed to be at the root of the source code (e.g., /src)
    container: dagger.Container,
    open_ai_key: dagger.Secret,
    max_semantic_chunk_lines: int,
    fallback_chunk_size: int,
) -> int:
    """
    Process a single code file, chunk it semantically, and add its embeddings to Supabase.
    Returns the number of chunks indexed.
    """
    try:
        file_size = await get_file_size(container=container, filepath=filepath)
        if file_size == 0:
            print(f"Skipping zero-size or inaccessible file: {filepath}")
            return 0
        if file_size > 1_000_000:  # 1MB limit
            print(f"Skipping large file (>{file_size/1000:.0f}KB): {filepath}")
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
                chunk_end_line_0idx = min(i + fallback_chunk_size, len(lines))

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


async def index_codebase(
    supabase_url: str,
    open_ai_key: dagger.Secret,
    supabase_key: dagger.Secret,
    file_extensions: List[str],
    # This container should be set to the source code's root directory (e.g., /src)
    container: dagger.Container,
    config: YAMLConfig,
) -> None:
    """
    Index all code files in a repository.
    """
    try:
        supabase = create_client(supabase_url, await supabase_key.plaintext())
        print("Supabase client created")
        total_indexed_chunks = 0

        # Define find command to run inside the container (workdir is /src)
        # Find files in current dir (.)
        file_list_cmd = ["find", ".", "-type", "f"]
        exclude_dirs = [".git", "node_modules", "venv", ".venv", "build",
                        "dist", "__pycache__", "target", "docs", "examples", "tests", "test"]
        for dir_name in exclude_dirs:
            # Paths are relative to find's start dir
            file_list_cmd.extend(["-not", "-path", f"./{dir_name}/*"])

        # Execute find command in the container's /src directory
        file_list_output = await container.with_exec(file_list_cmd).stdout()
        all_files_relative = [
            f.strip() for f in file_list_output.strip().split("\n") if f.strip()]

        filtered_files = [
            # Remove leading "./", path is now like "main.py" or "subdir/file.py"
            f_rel[2:] if f_rel.startswith("./") else f_rel
            for f_rel in all_files_relative
            # Basic hidden file/dir skip
            if any(f_rel.endswith(ext) for ext in file_extensions) and "/." not in f_rel
        ]
        print(f"Found {len(filtered_files)} files to process after filtering.")

        # Get chunking parameters from config
        fallback_chunk_size_val = 50
        max_semantic_chunk_lines_val = 200
        if hasattr(config, "indexing"):
            if hasattr(config.indexing, "chunk_size"):  # chunk_size is now fallback
                fallback_chunk_size_val = config.indexing.chunk_size
            if hasattr(config.indexing, "max_semantic_chunk_lines"):
                max_semantic_chunk_lines_val = config.indexing.max_semantic_chunk_lines

        print(
            f"Using Max Semantic Chunk Lines: {max_semantic_chunk_lines_val}, Fallback Chunk Size: {fallback_chunk_size_val}")

        for filepath_in_container in filtered_files:
            # filepath_in_container is now relative to the container's workdir (e.g., "module/main.py")
            # This is the path used for display and for storing in the database.
            # It's also the path used for container.file() and container.with_exec() for stat.
            total_indexed_chunks += await process_file(
                filepath=filepath_in_container,
                supabase=supabase,
                open_ai_key=open_ai_key,
                container=container,
                max_semantic_chunk_lines=max_semantic_chunk_lines_val,
                fallback_chunk_size=fallback_chunk_size_val
            )

        print(
            f"Successfully indexed a total of {total_indexed_chunks} code chunks.")

    except Exception as e:
        print(f"Error indexing codebase: {e}")
        traceback.print_exc()  # Ensure traceback is printed
        raise

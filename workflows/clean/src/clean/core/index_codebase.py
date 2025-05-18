import argparse
import asyncio
import os
from typing import List, Dict, Any

import dagger
from clean.models.config import YamlConfig
from clean.utils.code_parser import parse_code_file
from clean.utils.embeddings import generate_embeddings
from supabase import Client, create_client


async def get_file_size(container: dagger.Container, filepath: str) -> int:
    """Get the size of a file inside a container."""
    try:
        # Run stat command inside the container
        size_str = await container.with_exec(
            ["stat", "-c", "%s", filepath]
        ).stdout()

        return int(size_str.strip())
    except Exception as e:
        print(f"Error getting size of {filepath}: {e}")
        return 0


async def process_file(
    filepath: str,
    supabase: Client,
    container: dagger.Container,
    chunk_size: int = 50,
) -> int:
    """
    Process a single code file and add its embeddings to Supabase.
    Returns the number of chunks indexed.
    """
    try:
        # Skip binary files, very large files, or non-code files
        # Skip files larger than 1MB
        file_size = await get_file_size(container=container, filepath=filepath)
        if file_size > 1_000_000:
            print(f"Skipping large file: {filepath}")
            return 0

        # Get file content from container
        content = await container.file(filepath).contents()

        # Parse the code file
        code_file = parse_code_file(content, filepath)

        # Split the content into chunks
        lines = content.splitlines()
        chunks = []

        for i in range(0, len(lines), chunk_size):
            end_idx = min(i + chunk_size, len(lines))
            chunk_content = '\n'.join(lines[i:end_idx])

            # Skip empty chunks
            if not chunk_content.strip():
                continue

            # Get symbols in this chunk
            chunk_symbols = [
                s for s in code_file.symbols
                if i < s.line_number <= end_idx
            ]

            chunks.append({
                "content": chunk_content,
                "filepath": filepath,
                "start_line": i + 1,
                "end_line": end_idx,
                "language": code_file.language,
                "symbols": [vars(s) for s in chunk_symbols],
                "context": code_file.get_context_around_line((i + end_idx) // 2, 5)
            })

        # Generate embeddings for each chunk
        for chunk in chunks:
            embedding = await generate_embeddings(chunk["content"])

            # Insert into Supabase
            supabase.table("code_embeddings").insert({
                "content": chunk["content"],
                "embedding": embedding,
                "filepath": chunk["filepath"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "language": chunk["language"],
                "symbols": chunk["symbols"],
                "context": chunk["context"]
            }).execute()

        print(f"Indexed {len(chunks)} chunks from {filepath}")
        return len(chunks)
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        return 0


async def index_codebase(
    supabase_url: str,
    supabase_key: dagger.Secret,
    file_extensions: List[str],
    container: dagger.Container,
    config: YamlConfig,
) -> None:
    """
    Index all code files in a repository.
    """
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, await supabase_key.plaintext())
        indexed_count = 0

        # Get all files with find command
        file_list_cmd = ["find", ".", "-type", "f"]

        # Add exclusion patterns for common directories to skip
        exclude_dirs = [".git", "node_modules", "venv",
                        ".venv", "build", "dist", "__pycache__"]
        for dir_name in exclude_dirs:
            file_list_cmd.extend(["-not", "-path", f"*/{dir_name}/*"])

        # Run the command to get all files
        file_list_output = await container.with_workdir("/src").with_exec(file_list_cmd).stdout()

        # Process the file list
        all_files = file_list_output.strip().split("\n")

        # Filter files by extension
        filtered_files = [
            f for f in all_files
            if any(f.endswith(ext) for ext in file_extensions)
        ]

        print(f"Found {len(filtered_files)} files to process")

        # Process each file
        for filepath in filtered_files:
            # Make sure filepath starts with /src
            if not filepath.startswith("/src"):
                if filepath.startswith("./"):
                    filepath = f"/src{filepath[1:]}"
                else:
                    filepath = f"/src/{filepath}"

            indexed_count += await process_file(
                filepath=filepath,
                supabase=supabase,
                container=container,
                chunk_size=config.indexing.chunk_size if hasattr(
                    config, "indexing") and hasattr(config.indexing, "chunk_size") else 50
            )

        print(f"Successfully indexed {indexed_count} code chunks")

    except Exception as e:
        print(f"Error indexing codebase: {e}")
        raise


# For testing/debugging - only called if this file is run directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index code files for RAG")
    parser.add_argument("--repo-path", required=True,
                        help="Path to the repository")
    parser.add_argument("--supabase-url", required=True, help="Supabase URL")
    parser.add_argument("--supabase-key", required=True,
                        help="Supabase API key")
    parser.add_argument("--extensions", default=".py,.js,.ts,.java,.c,.cpp,.go,.rs,.rb,.php",
                        help="Comma-separated list of file extensions to index")

    args = parser.parse_args()

    # This would be for local testing, not used in Dagger flow
    # file_extensions = args.extensions.split(',')
    # asyncio.run(index_codebase(args.repo_path, args.supabase_url, args.supabase_key, file_extensions))

import logging
from typing import Dict, List, Optional, Tuple

import anyio
import dagger
from index.models import ChunkData, ProcessingConfig
from index.utils.embeddings import generate_embeddings
from supabase import Client


class EmbeddingHandler:
    """Handles embedding generation and storage operations."""

    @staticmethod
    async def generate_embeddings_batch(
        chunks: List[ChunkData],
        openai_key: dagger.Secret,
        model: str,
        logger: logging.Logger
    ) -> List[Tuple[ChunkData, Optional[List[float]]]]:
        """Generate embeddings for a batch of chunks."""
        results = []

        async def generate_single_embedding(chunk: ChunkData):
            """Generate embedding and append to results."""
            try:
                embedding = await generate_embeddings(
                    text=chunk.content,
                    model=model,
                    openai_api_key=openai_key
                )
                results.append((chunk, embedding))
            except Exception as e:
                logger.error(
                    f"Failed to generate embedding for {chunk.filepath}:{chunk.start_line}: {e}")
                results.append((chunk, None))

        async with anyio.create_task_group() as tg:
            for chunk in chunks:
                tg.start_soon(generate_single_embedding, chunk)

        return results

    @staticmethod
    async def insert_chunk_safe(
        chunk: ChunkData,
        embedding: List[float],
        supabase: Client,
        logger: logging.Logger
    ) -> bool:
        """Safely insert a single chunk."""
        try:
            insert_payload = {
                "content": chunk.content,
                "embedding": embedding,
                "filepath": chunk.filepath,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "language": chunk.language,
                "symbols": chunk.symbols,
                "context": chunk.context
            }

            supabase.table("code_embeddings").insert(insert_payload).execute()
            return True

        except Exception as e:
            logger.error(
                f"Failed to insert chunk {chunk.filepath}:{chunk.start_line}-{chunk.end_line}: {e}")
            return False

    @staticmethod
    async def store_chunks_with_embeddings(
        chunks_data: List[ChunkData],
        supabase: Client,
        openai_key: dagger.Secret,
        config: ProcessingConfig,
        logger: logging.Logger
    ) -> int:
        """Store chunks with embeddings in batches."""
        if not chunks_data:
            logger.warning("No chunks to store")
            return 0

        logger.info(f"Processing {len(chunks_data)} chunks for embeddings")
        successful_inserts = 0

        # Process embeddings in batches
        for i in range(0, len(chunks_data), config.embedding_batch_size):
            batch = chunks_data[i:i + config.embedding_batch_size]
            logger.info(
                f"Generating embeddings for batch {i//config.embedding_batch_size + 1}: {len(batch)} chunks")

            # Generate embeddings concurrently for this batch
            embedding_results = await EmbeddingHandler.generate_embeddings_batch(
                batch, openai_key, config.embedding_model, logger
            )

            logger.info(
                f"Generated {len(embedding_results)} embedding results")

            # Insert valid results
            batch_inserts = 0
            for chunk, embedding in embedding_results:
                if embedding and await EmbeddingHandler.insert_chunk_safe(chunk, embedding, supabase, logger):
                    successful_inserts += 1
                    batch_inserts += 1

            logger.info(
                f"Successfully inserted {batch_inserts} chunks from this batch")

        logger.info(f"Total successful inserts: {successful_inserts}")
        return successful_inserts

    @staticmethod
    async def clear_embeddings_safe(supabase: Client, logger: logging.Logger) -> Tuple[bool, str]:
        """Safely clear embeddings table with multiple fallback methods."""
        try:
            # Check if table exists and get count
            count_result = supabase.table("code_embeddings").select(
                "*", count="exact").execute()
            initial_count = count_result.count if hasattr(
                count_result, 'count') and count_result.count else 0

            if initial_count == 0:
                return True, "Table was already empty"

            logger.info(
                f"Attempting to clear {initial_count} rows from code_embeddings table")

            # Method 1: Simple delete with NOT condition (safest)
            try:
                supabase.table("code_embeddings").delete().neq(
                    "id", -999999).execute()

                # Verify deletion
                final_count_result = supabase.table(
                    "code_embeddings").select("*", count="exact").execute()
                final_count = final_count_result.count if hasattr(
                    final_count_result, 'count') and final_count_result.count else 0

                deleted = initial_count - final_count
                if final_count == 0:
                    return True, f"Successfully cleared all {deleted} rows"
                else:
                    return False, f"Partially cleared. {deleted} rows deleted, {final_count} remain"

            except Exception as delete_error:
                logger.error(f"Clear operation failed: {delete_error}")
                return False, f"Clear operation failed: {delete_error}"

        except Exception as e:
            logger.error(f"Error in clear operation: {e}")
            return False, f"Clear operation failed: {e}"

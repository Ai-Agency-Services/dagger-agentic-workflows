import logging
import os
import re
import contextlib
from dataclasses import dataclass
from typing import Annotated, Dict, List, Optional, Tuple

import anyio
import dagger
import yaml
from ais_dagger_agents_config import ConcurrencyConfig, IndexingConfig
from ais_dagger_agents_config.models import YAMLConfig
from dagger import Doc, dag, function, object_type
from index.utils.code_parser import parse_code_file
from index.utils.embeddings import generate_embeddings
from index.utils.file import get_file_size
from index.utils.neo4j_connector import Neo4jConnector
from supabase import Client, create_client


@dataclass
class ProcessingConfig:
    """Configuration for file processing operations."""
    max_semantic_chunk_lines: int = 200
    fallback_chunk_size: int = 50
    max_file_size: int = 1_000_000
    batch_size: int = 5
    max_concurrent: int = 5
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 10


@dataclass
class ChunkData:
    """Data structure for code chunks."""
    content: str
    filepath: str
    start_line: int
    end_line: int
    language: str
    symbols: List[Dict]
    context: str


@object_type
class Index:
    config: dict
    config_file: dagger.File

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to the YAML config file")]) -> "Index":
        """Create a Clean object from a YAML config file."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, config_file=config_file)

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _get_processing_config(self) -> ProcessingConfig:
        """Extract processing configuration from YAML config."""
        config_obj = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config

        # Default to empty configs if not present
        indexing_config = getattr(
            config_obj, 'indexing', None) or IndexingConfig()
        concurrency_config = getattr(
            config_obj, 'concurrency', None) or ConcurrencyConfig()

        return ProcessingConfig(
            max_semantic_chunk_lines=getattr(
                indexing_config, 'max_semantic_chunk_lines', 200),
            fallback_chunk_size=getattr(indexing_config, 'chunk_size', 50),
            max_file_size=getattr(indexing_config, 'max_file_size', 1_000_000),
            # Get concurrency settings from the concurrency config
            batch_size=getattr(concurrency_config, 'batch_size', 5),
            max_concurrent=getattr(concurrency_config, 'max_concurrent', 5),
            embedding_batch_size=getattr(
                concurrency_config, 'embedding_batch_size', 10),
            embedding_model=getattr(
                indexing_config, 'embedding_model', 'text-embedding-3-small'),
        )

    def _validate_symbol_lines(self, symbol_obj, total_lines: int, filepath: str, logger: logging.Logger) -> bool:
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

    def _is_file_processable(self, file_size: int, filepath: str, config: ProcessingConfig, logger: logging.Logger) -> bool:
        """Check if file should be processed."""
        if file_size == 0:
            logger.info(f"Skipping zero-size file: {filepath}")
            return False
        if file_size > config.max_file_size:
            logger.info(
                f"Skipping large file ({file_size/1000:.0f}KB): {filepath}")
            return False
        return True

    def _create_chunk_data(
        self,
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

    def _create_semantic_chunks(
        self,
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
            if not self._validate_symbol_lines(symbol_obj, len(lines), filepath, logger):
                continue

            chunk_lines = lines[symbol_obj.start_line - 1:symbol_obj.end_line]
            chunk_text = "\n".join(chunk_lines)

            if not chunk_text.strip():
                continue

            if len(chunk_lines) > config.max_semantic_chunk_lines:
                # Sub-chunk large symbols
                chunks.extend(self._sub_chunk_symbol(
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

                chunks.append(self._create_chunk_data(
                    chunk_text, filepath, symbol_obj.start_line, symbol_obj.end_line,
                    file_language, symbols_info, context
                ))

        return chunks

    def _sub_chunk_symbol(
        self,
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

            sub_chunks.append(self._create_chunk_data(
                sub_content_text, symbol_obj.filepath if hasattr(
                    symbol_obj, 'filepath') else "unknown",
                actual_start_line, actual_end_line, file_language, sub_symbols_info, context
            ))

        return sub_chunks

    def _create_fallback_chunks(
        self,
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

            chunks.append(self._create_chunk_data(
                chunk_content, filepath, actual_start_line, actual_end_line,
                file_language, symbols_info, context
            ))

        return chunks

    async def _process_file_core(
        self,
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
            semantic_chunks = self._create_semantic_chunks(
                filepath, lines, all_file_symbols, file_language, config, logger
            )
            if semantic_chunks:
                logger.info(
                    f"Created {len(semantic_chunks)} semantic chunks for {filepath}")
                return semantic_chunks

        # 2. Fallback to fixed-size chunking
        if content.strip():
            fallback_chunks = self._create_fallback_chunks(
                filepath, lines, all_file_symbols, file_language, config, code_file, logger
            )
            logger.info(
                f"Created {len(fallback_chunks)} fallback chunks for {filepath}")
            return fallback_chunks

        logger.warning(f"No chunks created for {filepath}")
        return []

    async def _generate_embeddings_batch(
        self,
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

    async def _insert_chunk_safe(
        self,
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

    async def _store_chunks_with_embeddings(
        self,
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
            embedding_results = await self._generate_embeddings_batch(
                batch, openai_key, config.embedding_model, logger
            )

            logger.info(
                f"Generated {len(embedding_results)} embedding results")

            # Insert valid results
            batch_inserts = 0
            for chunk, embedding in embedding_results:
                if embedding and await self._insert_chunk_safe(chunk, embedding, supabase, logger):
                    successful_inserts += 1
                    batch_inserts += 1

            logger.info(
                f"Successfully inserted {batch_inserts} chunks from this batch")

        logger.info(f"Total successful inserts: {successful_inserts}")
        return successful_inserts

    async def _safe_process_file(
        self,
        filepath: str,
        supabase: Client,
        container: dagger.Container,
        openai_key: dagger.Secret,
        config: ProcessingConfig,
        logger: logging.Logger,
        neo4j: Optional[Neo4jConnector] = None  # Add neo4j parameter
    ) -> int:
        """Safely process a single file with comprehensive error handling."""
        try:
            # File size check
            file_size = await get_file_size(container=container, filepath=filepath)
            if not self._is_file_processable(file_size, filepath, config, logger):
                return 0

            # Get content
            content = await container.file(filepath).contents()
            if not content.strip():
                logger.info(f"Skipping empty file: {filepath}")
                return 0

            logger.info(f"Processing file: {filepath} ({len(content)} chars)")

            # Process chunks
            chunks_data = await self._process_file_core(filepath, content, config, logger)

            if not chunks_data:
                logger.warning(f"No chunks generated for {filepath}")
                return 0

            logger.info(f"Generated {len(chunks_data)} chunks for {filepath}")

            # Generate embeddings and store in Supabase
            result = await self._store_chunks_with_embeddings(
                chunks_data, supabase, openai_key, config, logger
            )

            # Add Neo4j integration here
            if neo4j:
                try:
                    # Parse the file to get structured code information
                    code_file = parse_code_file(content, filepath)
                    if code_file:
                        logger.info(f"Adding {filepath} to Neo4j graph")

                        # Add file node
                        neo4j.add_file_node(filepath, getattr(
                            code_file, 'language', 'unknown'))

                        # Add symbol nodes
                        symbols = getattr(code_file, 'symbols', [])
                        for symbol in symbols:
                            if not hasattr(symbol, 'name') or not symbol.name:
                                continue

                            # Extract symbol properties
                            symbol_type = symbol.type.capitalize() if hasattr(symbol, 'type') else 'Symbol'
                            line_number = getattr(symbol, 'line_number', 0)
                            end_line = getattr(symbol, 'end_line', line_number)

                            # Collect additional properties
                            properties = {}
                            for attr in ['signature', 'docstring', 'visibility', 'scope']:
                                if hasattr(symbol, attr) and getattr(symbol, attr):
                                    properties[attr] = getattr(symbol, attr)

                            # Add symbol to Neo4j
                            neo4j.add_symbol(
                                symbol_type=symbol_type,
                                name=symbol.name,
                                filepath=filepath,
                                start_line=line_number,
                                end_line=end_line,
                                properties=properties
                            )

                        # Extract relationships between symbols
                        await self._extract_relationships(filepath, code_file, neo4j)
                        logger.info(
                            f"Successfully added {filepath} to Neo4j with {len(symbols)} symbols")

                except Exception as neo4j_err:
                    logger.error(
                        f"Failed to add {filepath} to Neo4j: {neo4j_err}")
                    # Continue processing - don't let Neo4j errors stop the vector indexing

            logger.info(f"File {filepath} processed: {result} chunks indexed")
            return result

        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}", exc_info=True)
            return 0

    async def _process_files_with_semaphore(
        self,
        files,
        supabase,
        container,
        openai_key,
        config,
        logger,
        neo4j=None
    ) -> int:
        """Process files with semaphore-controlled concurrency using anyio."""
        if not files:
            return 0

        semaphore = anyio.Semaphore(config.max_concurrent)
        results = []

        async def process_with_limit(filepath: str):
            async with semaphore:
                result = await self._safe_process_file(
                    filepath, supabase, container, openai_key, config, logger, neo4j
                )
                results.append(result)

        async with anyio.create_task_group() as tg:
            for filepath in files:
                tg.start_soon(process_with_limit, filepath)

        total_chunks = sum(results)
        logger.info(
            f"Processed {len(files)} files, indexed {total_chunks} total chunks")
        return total_chunks

    async def _setup_repository(
        self,
        github_token: dagger.Secret,
        open_router_api_key: dagger.Secret,
        openai_api_key: dagger.Secret,
        repo_url: str,
        branch: str
    ) -> Tuple[dagger.Container, List[str]]:
        """Setup repository and get filtered file list."""
        try:
            # Clone repository
            source = (
                await dag.git(url=repo_url, keep_git_dir=True)
                .with_auth_token(github_token)
                .branch(branch)
                .tree()
            )

            # Build container
            config_obj = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config

            container = await dag.builder(self.config_file).build_test_environment(
                source=source,
                dockerfile_path=config_obj.container.docker_file_path,
                open_router_api_key=open_router_api_key,
                provider=config_obj.core_api.provider if config_obj.core_api else None,
                openai_api_key=open_router_api_key
            )

            # Get file list
            file_extensions = getattr(config_obj.test_generation, 'file_extensions', [
                                      "py", "js", "ts", "java", "c", "cpp", "go", "rs"])
            files = await self._get_filtered_files(container, file_extensions)

            return container, files

        except Exception as e:
            raise Exception(f"Failed to setup repository {repo_url}: {e}")

    async def _get_filtered_files(self, container: dagger.Container, extensions: List[str]) -> List[str]:
        """Get filtered list of files to process."""
        file_list_cmd = ["find", ".", "-type", "f"]
        exclude_dirs = [".git", "node_modules", "venv", ".venv", "build",
                        "dist", "__pycache__", "target", "docs", "examples", "tests", "test"]

        for dir_name in exclude_dirs:
            file_list_cmd.extend(["-not", "-path", f"./{dir_name}/*"])

        file_list_output = await container.with_exec(file_list_cmd).stdout()
        all_files = [f.strip()
                     for f in file_list_output.strip().split("\n") if f.strip()]

        return [
            f[2:] if f.startswith("./") else f
            for f in all_files
            if any(f.endswith(f".{ext}") for ext in extensions) and "/." not in f
        ]

    async def _clear_embeddings_safe(self, supabase: Client, logger: logging.Logger) -> Tuple[bool, str]:
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

    # Add Neo4j integration to index_codebase method
    @function
    def neo_service(self) -> dagger.Service:
        """Create a Neo4j service as a Dagger service"""
        return (
            dag.container()  # Changed from dag.container()
            .from_("neo4j:2025.05")  # Changed to valid version
            .with_env_variable("NEO4J_AUTH", "neo4j/devpassword")
            .with_env_variable("NEO4J_PLUGINS", '["apoc"]')
            .with_env_variable("NEO4J_apoc_export_file_enabled", "true")
            .with_env_variable("NEO4J_apoc_import_file_enabled", "true")
            .with_env_variable("NEO4J_apoc_import_file_use__neo4j__config", "true")
            .with_env_variable("NEO4J_dbms_memory_pagecache_size", "1G")
            .with_env_variable("NEO4J_dbms_memory_heap_initial__size", "1G")
            .with_env_variable("NEO4J_dbms_memory_heap_max__size", "1G")
            .with_exposed_port(7474)  # HTTP interface
            .with_exposed_port(7687)  # Bolt protocol
            # Persist data
            .with_mounted_cache("/data", dag.cache_volume("neo4j-data"))
            .as_service(use_entrypoint=True)  # Use container's entrypoint
        )

    @function
    async def run_neo_query(self, query: str) -> str:
        """Run a query against the Neo4j service"""
        neo4j_svc = self.neo_service()

        return await (
            dag.container()
            .from_("neo4j:5.13.0")
            .with_service_binding("neo4j_db", neo4j_svc)  # Bind to the service
            .with_env_variable("NEO4J_AUTH", "neo4j/devpassword")
            .with_exec([
                "/bin/bash", "-c",
                f'echo "{query}" | cypher-shell -a "bolt://neo4j_db:7687" -u neo4j -p devpassword'
            ])
            .stdout()
        )

    @function
    async def index_codebase(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to index")],
        branch: Annotated[str, Doc("Branch to index")],
        supabase_url: str,
        openai_api_key: dagger.Secret,
        open_router_api_key: dagger.Secret,
        neo_password: dagger.Secret,
        supabase_key: dagger.Secret,
        neo_uri: str = "bolt://host.docker.internal:7687",
        neo_user: str = "neo4j",
        clear_existing: bool = True,
        use_neo4j: bool = True
    ) -> str:
        """Index all code files in a repository using anyio concurrency."""
        logger = self._setup_logging()
        config = self._get_processing_config()

        try:
            # Setup environment
            if openai_api_key:
                logger.info("Setting OpenAI API key...")
                os.environ["OPENAI_API_KEY"] = await openai_api_key.plaintext()

            # Start Neo4j service if needed
            neo4j_svc = None
            neo4j = None
            if use_neo4j:
                try:
                    logger.info("Starting Neo4j service...")
                    neo4j_svc = self.neo_service()

                    # Test connection with a simple query
                    try:
                        test_result = await self.run_neo_query("RETURN 'Connected' AS result")
                        logger.info(f"Neo4j connection test: {test_result}")

                        # If we need to clear the database
                        if clear_existing:
                            logger.info("Clearing Neo4j database...")
                            await self.run_neo_query("MATCH (n) DETACH DELETE n")

                        # Now create a Neo4j container for batch operations
                        neo4j_client = (
                            dag.container()
                            .from_("neo4j:5.13.0")
                            .with_service_binding("neo4j_db", neo4j_svc)
                        )

                        # Create a custom Neo4j connector for batch operations
                        neo4j = Neo4jConnector(
                            uri="bolt://neo4j_db:7687",  # Use service binding hostname
                            username="neo4j",
                            password="devpassword",
                            database="neo4j",
                            client_container=neo4j_client  # Pass the container for operations
                        )
                    except Exception as test_error:
                        logger.error(
                            f"Neo4j service test failed: {test_error}")
                        neo4j = None

                except Exception as e:
                    logger.error(f"Neo4j service setup failed: {e}")
                    neo4j = None

            # Set up Supabase client
            supabase = create_client(supabase_url, await supabase_key.plaintext())

            # Setup repository and get filtered file list
            container, files = await self._setup_repository(
                github_access_token,
                open_router_api_key,
                openai_api_key,
                repository_url,
                branch
            )
            logger.info(f"Found {len(files)} files to process")

            # Setup database
            supabase = create_client(supabase_url, await supabase_key.plaintext())

            # Clear existing data if requested
            if clear_existing:
                success, message = await self._clear_embeddings_safe(supabase, logger)
                if success:
                    logger.info(f"✓ {message}")
                else:
                    logger.warning(f"⚠ {message}")
                    logger.warning("Continuing with indexing anyway...")

            # Add Neo4j connector
            neo4j = None
            if use_neo4j and neo_password:
                try:
                    neo4j_password_text = await neo_password.plaintext()
                    neo4j = Neo4jConnector(
                        uri=neo_uri,
                        username=neo_user,
                        password=neo4j_password_text,
                        database="neo4j"
                    )
                    connected = neo4j.connect()
                    if connected and clear_existing:
                        neo4j.clear_database()
                    if not connected:
                        logger.warning(
                            "Failed to connect to Neo4j, continuing with Supabase only")
                        neo4j = None
                except Exception as e:
                    logger.error(f"Neo4j initialization failed: {e}")
                    neo4j = None

            # Process files with semaphore-controlled concurrency
            total_chunks = await self._process_files_with_semaphore(
                files,
                supabase,
                container,
                openai_api_key,
                config,
                logger,
                neo4j=neo4j
            )

            logger.info(f"Successfully indexed {total_chunks} code chunks")
            return f"Indexed {total_chunks} chunks from {len(files)} files"

        except Exception as e:
            logger.error(f"Indexing failed: {e}", exc_info=True)
            raise

    @function
    async def clear_embeddings_table(
        self,
        supabase_url: Annotated[str, Doc("Supabase project URL")],
        supabase_key: Annotated[dagger.Secret, Doc("Supabase API key")],
    ) -> str:
        """Clear all data from the code_embeddings table."""
        logger = self._setup_logging()

        try:
            supabase = create_client(supabase_url, await supabase_key.plaintext())
            success, message = await self._clear_embeddings_safe(supabase, logger)

            if success:
                logger.info(f"✓ {message}")
                return message
            else:
                logger.error(f"✗ {message}")
                raise Exception(message)

        except Exception as e:
            logger.error(f"Clear operation failed: {e}")
            raise

    async def _extract_relationships(self, filepath, code_file, neo4j):
        """Extract relationships between code symbols"""
        if not neo4j or not hasattr(code_file, 'symbols') or not code_file.symbols:
            return

        # Map symbols by name for quick lookup
        symbol_map = {}
        for symbol in code_file.symbols:
            if hasattr(symbol, 'name') and symbol.name:
                symbol_map[symbol.name] = symbol

        # Process for import relationships
        if hasattr(code_file, 'language') and code_file.language in ('python', 'javascript', 'typescript'):
            # Find import statements and create relationships
            import_pattern = r'import\s+(\w+)(?:\s*,\s*\{([^}]+)\})?\s+from\s+[\'"]([^\'"]+)[\'"]'
            for i, line in enumerate(code_file.content.split('\n')):
                for match in re.finditer(import_pattern, line):
                    module_name = match.group(3)
                    imported_name = match.group(1)
                    if imported_name in symbol_map:
                        await neo4j.add_relationship(
                            from_type='File',
                            from_name='',
                            from_filepath=filepath,
                            from_line=0,
                            to_type='Module',
                            to_name=module_name,
                            to_filepath=module_name,
                            to_line=0,
                            rel_type='IMPORTS'
                        )

        # Process function calls
        if hasattr(code_file, 'language') and code_file.language in ('python', 'javascript', 'typescript'):
            function_call_pattern = r'(\w+)\s*\('
            for symbol in code_file.symbols:
                if not hasattr(symbol, 'line_number') or not symbol.name:
                    continue

                # Find function calls within this symbol
                if hasattr(symbol, 'body') and symbol.body:
                    for match in re.finditer(function_call_pattern, symbol.body):
                        called_func = match.group(1)
                        if called_func in symbol_map and called_func != symbol.name:
                            called_symbol = symbol_map[called_func]
                            await neo4j.add_relationship(
                                from_type=symbol.type.capitalize(),
                                from_name=symbol.name,
                                from_filepath=filepath,
                                from_line=symbol.line_number,
                                to_type=called_symbol.type.capitalize(),
                                to_name=called_symbol.name,
                                to_filepath=filepath,
                                to_line=called_symbol.line_number,
                                rel_type='CALLS'
                            )

import logging
import os
from typing import Annotated, List, Optional, Tuple

import anyio
import dagger
import yaml
from ais_dagger_agents_config import ConcurrencyConfig, IndexingConfig
from ais_dagger_agents_config.models import YAMLConfig
from dagger import Doc, dag, function, object_type
from index.models import ProcessingConfig
from index.operations.embedding_handler import EmbeddingHandler
from index.operations.file_processor import FileProcessor
from index.operations.relationship_extractor import RelationshipExtractor
from index.services.neo4j_service import Neo4jService
from index.utils.code_parser import parse_code_file
from index.utils.file import get_file_size
from index.utils.neo4j_connector import Neo4jConnector
from supabase import Client, create_client


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

    async def _safe_process_file(
        self,
        filepath: str,
        supabase: Client,
        container: dagger.Container,
        openai_key: dagger.Secret,
        config: ProcessingConfig,
        logger: logging.Logger,
        neo4j: Optional[Neo4jConnector] = None
    ) -> int:
        """Safely process a single file with comprehensive error handling."""
        try:
            # File size check
            file_size = await get_file_size(container=container, filepath=filepath)
            if not FileProcessor._is_file_processable(file_size, filepath, config, logger):
                return 0

            # Get content
            content = await container.file(filepath).contents()
            if not content.strip():
                logger.info(f"Skipping empty file: {filepath}")
                return 0

            logger.info(f"Processing file: {filepath} ({len(content)} chars)")

            # Process chunks
            chunks_data = await FileProcessor.process_file_core(filepath, content, config, logger)

            if not chunks_data:
                logger.warning(f"No chunks generated for {filepath}")
                return 0

            logger.info(f"Generated {len(chunks_data)} chunks for {filepath}")

            # Generate embeddings and store in Supabase
            result = await EmbeddingHandler.store_chunks_with_embeddings(
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
                        await neo4j.add_file_node(filepath, getattr(
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
                            await neo4j.add_symbol(
                                symbol_type=symbol_type,
                                name=symbol.name,
                                filepath=filepath,
                                start_line=line_number,
                                end_line=end_line,
                                properties=properties
                            )

                        # Extract relationships between symbols
                        await RelationshipExtractor.extract_relationships(filepath, code_file, neo4j)
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
            files = await FileProcessor.get_filtered_files(container, file_extensions)

            return container, files

        except Exception as e:
            raise Exception(f"Failed to setup repository {repo_url}: {e}")

    @function
    def neo_service(self) -> dagger.Service:
        """Create a Neo4j service as a Dagger service"""
        return Neo4jService.create_neo4j_service()

    @function
    async def neo4j_client(
        self,
        cypher_shell_repo: str,
        github_access_token: dagger.Secret
    ) -> dagger.Container:
        """Create a Neo4j client container with cypher-shell"""
        return await Neo4jService.create_neo4j_client(
            config_file=self.config_file,
            cypher_shell_repo=cypher_shell_repo,
            github_access_token=github_access_token
        )

    @function
    async def run_neo_query(
        self,
        query: str,
        cypher_shell_repo: str,
        github_access_token: dagger.Secret
    ) -> str:
        """Run a query against the Neo4j service"""
        return await Neo4jService.run_query(
            config_file=self.config_file,
            query=query,
            cypher_shell_repo=cypher_shell_repo,
            github_access_token=github_access_token
        )

    @function
    async def test_neo4j_connection(
        self,
        cypher_shell_repo: str,
        github_access_token: dagger.Secret
    ) -> str:
        """Test connection to Neo4j service"""
        return await Neo4jService.test_connection(
            config_file=self.config_file,
            cypher_shell_repo=cypher_shell_repo,
            github_access_token=github_access_token
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
        cypher_shell_repo: Annotated[str, Doc("Path to the Cypher shell repository")],
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

            neo4j = None
            if use_neo4j:
                try:
                    logger.info("Starting Neo4j service...")

                    # First run a simple query to test that the service is running
                    test_result = await self.run_neo_query(
                        "RETURN 'Connected' AS result",
                        cypher_shell_repo=cypher_shell_repo,
                        github_access_token=github_access_token)
                    logger.info(f"Neo4j connection test: {test_result}")

                    # Now create a Neo4j container for batch operations
                    neo4j_client = await self.neo4j_client(
                        cypher_shell_repo=cypher_shell_repo,
                        github_access_token=github_access_token
                    )

                    # Initialize the Neo4jConnector with the client container
                    neo4j = Neo4jConnector(
                        uri="neo4j://neo:7687",  # Match the service binding name in neo4j_client
                        username="neo4j",
                        password="devpassword",
                        database="neo4j",
                        client_container=neo4j_client  # Pass the container
                    )

                    # Test the Neo4j connector explicitly
                    try:
                        is_connected = neo4j.connect()
                        if is_connected:
                            logger.info(
                                "Neo4j connector successfully initialized")

                            # If we need to clear the database, now we can do it
                            if clear_existing:
                                logger.info("Clearing Neo4j database...")
                                success = await neo4j.clear_database()  # Now this won't be None
                                if success:
                                    logger.info(
                                        "Neo4j database cleared successfully")
                        else:
                            logger.error(
                                "Neo4j connector failed to initialize")
                            neo4j = None
                    except Exception as conn_err:
                        logger.error(
                            f"Neo4j connector initialization error: {conn_err}")
                        neo4j = None
                except Exception as test_error:
                    logger.error(f"Neo4j service test failed: {test_error}")
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
                success, message = await EmbeddingHandler.clear_embeddings_safe(supabase, logger)
                if success:
                    logger.info(f"✓ {message}")
                else:
                    logger.warning(f"⚠ {message}")
                    logger.warning("Continuing with indexing anyway...")

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
            success, message = await EmbeddingHandler.clear_embeddings_safe(supabase, logger)

            if success:
                logger.info(f"✓ {message}")
                return message
            else:
                logger.error(f"✗ {message}")
                raise Exception(message)

        except Exception as e:
            logger.error(f"Clear operation failed: {e}")
            raise

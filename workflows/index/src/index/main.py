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
from index.utils.file import get_file_size
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
        logger: logging.Logger
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
        logger
    ) -> int:
        """Process files with semaphore-controlled concurrency using anyio."""
        if not files:
            return 0

        semaphore = anyio.Semaphore(config.max_concurrent)
        results = []

        async def process_with_limit(filepath: str):
            async with semaphore:
                result = await self._safe_process_file(
                    filepath, supabase, container, openai_key, config, logger
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
            file_extensions = getattr(
                config_obj.indexing, 'file_extensions')
            files = await FileProcessor.get_filtered_files(container, file_extensions)

            return container, files

        except Exception as e:
            raise Exception(f"Failed to setup repository {repo_url}: {e}")

    @function
    async def index_codebase(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to index")],
        branch: Annotated[str, Doc("Branch to index")],
        supabase_url: Annotated[str, Doc("Supabase project URL")],
        openai_api_key: Annotated[dagger.Secret, Doc("OpenAI API key")],
        open_router_api_key: Annotated[dagger.Secret, Doc("OpenRouter API key")],
        supabase_key: Annotated[dagger.Secret, Doc("Supabase API key")],
    ) -> str:
        """Index all code files in a repository using anyio concurrency."""
        logger = self._setup_logging()
        processing_config = self._get_processing_config()
        self.config: YAMLConfig = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config

        try:
            # Setup environment
            if openai_api_key:
                logger.info("Setting OpenAI API key...")
                os.environ["OPENAI_API_KEY"] = await openai_api_key.plaintext()

            # Set up Supabase client
            supabase = create_client(supabase_url, await supabase_key.plaintext())

            # Setup repository and get filtered file list
            container, files = await self._setup_repository(
                github_access_token,
                open_router_api_key,
                repository_url,
                branch
            )
            logger.info(f"Found {len(files)} files to process")

            # Clear existing data if requested
            if self.config.indexing.clear_on_start:
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
                processing_config,
                logger
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

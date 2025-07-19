import logging
import os
from typing import Annotated, Optional, List, Tuple, Dict, Set
import json
import re
import hashlib

import anyio  # Added for concurrency
import dagger
import yaml
from dagger.client.gen import NeoService, NeoServiceSymbolProperties, NeoServiceRelationshipProperties
from ais_dagger_agents_config.models import YAMLConfig
from dagger import Doc, dag, function, object_type
from graph.models.code_file import CodeFile, CodeSymbol
from graph.operations.import_analyzer import ImportAnalyzer
from graph.operations.relationship_extractor import RelationshipExtractor
from graph.utils import dagger_json_file_to_pydantic
from graph.services.neo4j_service import Neo4jService


@object_type
class Graph:
    config: dict
    config_file: dagger.File
    neo_service: Optional[Neo4jService] = None
    neo_data: Optional[dagger.CacheVolume] = None

    @classmethod
    async def create(cls,
                     config_file: Annotated[dagger.File, Doc("Path to the YAML config file")],
                     neo_data: Annotated[dagger.CacheVolume, Doc("Neo4j data cache volume")]) -> "Graph":
        """Create a Graph object from a YAML config file."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, config_file=config_file, neo_data=neo_data)

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("graph.main")

    def _get_processing_config(self) -> dict:
        """Extract processing configuration from YAML config."""
        config_obj = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config

        # Check for concurrency config first, fall back to indexing config
        concurrency_config = getattr(config_obj, 'concurrency', None)
        indexing_config = getattr(config_obj, 'indexing', None)

        return {
            'max_concurrent': (
                getattr(concurrency_config, 'max_concurrent',
                        None) if concurrency_config else None
            ) or (
                getattr(indexing_config, 'batch_size',
                        None) if indexing_config else None
            ) or 3,  # REDUCED from 5 to 3 for better performance
            'batch_size': 1,  # Always use individual queries for best performance
        }

    def _escape_cypher_string(self, value: str) -> str:
        """Escape special characters in Cypher string values."""
        if not value:
            return ""
        # Escape quotes and backslashes
        return value.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

    def _extract_simple_imports(self, content: str, filepath: str) -> List[str]:
        """Extract imports using simple regex patterns."""
        imports = []

        # Get file extension to determine import patterns
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if ext == '.py':
            # Python imports
            patterns = [
                r'from\s+([^\s]+)\s+import',  # from module import
                r'import\s+([^\s,]+)',        # import module
            ]
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript imports
            patterns = [
                r'from\s+[\'"]([^\'"]+)[\'"]',     # from 'module'
                r'import\s+[\'"]([^\'"]+)[\'"]',   # import 'module'
                r'require\([\'"]([^\'"]+)[\'"]\)',  # require('module')
            ]
        else:
            return imports

        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                # Clean up the import path
                import_path = match.strip()
                # Skip relative imports for now
                if import_path and not import_path.startswith('.'):
                    imports.append(import_path)

        return list(set(imports))  # Remove duplicates

    def _build_file_cypher(self, filepath: str, language: str) -> str:
        """Build Cypher query for creating a file node - OPTIMIZED VERSION."""
        escaped_filepath = self._escape_cypher_string(filepath)
        escaped_language = self._escape_cypher_string(language)
        # Single MERGE with ON CREATE/MATCH for optimal performance
        return f'MERGE (f:File {{filepath: "{escaped_filepath}"}}) ON CREATE SET f.language = "{escaped_language}", f.path = "{escaped_filepath}" ON MATCH SET f.language = "{escaped_language}";'

    def _build_symbol_cypher(self, symbol_dict: dict, filepath: str) -> str:
        """Build Cypher query for creating a symbol node - OPTIMIZED VERSION."""
        symbol_name = self._escape_cypher_string(symbol_dict.get("name", ""))
        symbol_type = symbol_dict.get("type", "symbol").capitalize()
        start_line = symbol_dict.get("line_number", 0) or 0
        end_line = symbol_dict.get("end_line_number", -1) or -1
        escaped_filepath = self._escape_cypher_string(filepath)

        # Handle optional properties
        properties = []
        for attr in ['scope', 'docstring', 'parent']:
            if attr in symbol_dict and symbol_dict[attr]:
                escaped_value = self._escape_cypher_string(
                    str(symbol_dict[attr]))
                properties.append(f'{attr}: "{escaped_value}"')

        props_string = ', ' + ', '.join(properties) if properties else ''

        # Use appropriate line property based on symbol type
        if symbol_type == "Variable":
            return f'MERGE (s:{symbol_type} {{name: "{symbol_name}", filepath: "{escaped_filepath}", line_number: {start_line}}}) SET s.end_line = {end_line}{props_string};'
        else:
            return f'MERGE (s:{symbol_type} {{name: "{symbol_name}", filepath: "{escaped_filepath}", start_line: {start_line}}}) SET s.end_line = {end_line}{props_string};'

    def _build_import_cypher(self, from_file: str, to_file: str) -> str:
        """Build Cypher query for creating import relationships - OPTIMIZED VERSION."""
        escaped_from = self._escape_cypher_string(from_file)
        escaped_to = self._escape_cypher_string(to_file)
        # Single efficient query
        return f'MERGE (from:File {{filepath: "{escaped_from}"}}) MERGE (to:File {{filepath: "{escaped_to}"}}) MERGE (from)-[:IMPORTS]->(to);'

    def _build_relationship_cypher(self, filepath: str, symbol_type: str) -> str:
        """Build DEFINED_IN relationship query."""
        escaped_filepath = self._escape_cypher_string(filepath)
        return f'MATCH (s:{symbol_type} {{filepath: "{escaped_filepath}"}}) MATCH (f:File {{filepath: "{escaped_filepath}"}}) MERGE (s)-[:DEFINED_IN]->(f);'

    async def _execute_queries_concurrently(
        self,
        queries: List[str],
        query_type: str,
        logger: logging.Logger,
        max_concurrent: int = 15
    ) -> Tuple[int, int]:
        """Execute queries concurrently with controlled concurrency."""
        if not queries:
            return 0, 0

        semaphore = anyio.Semaphore(max_concurrent)
        successful = 0
        failed = 0

        async def execute_with_limit(query: str, index: int):
            nonlocal successful, failed
            async with semaphore:
                try:
                    await self.neo_service.run_query(query)
                    successful += 1
                    # Log progress every 50 queries
                    if index % 50 == 0:
                        logger.info(
                            f"Executed {index + 1}/{len(queries)} {query_type} queries")
                    return True
                except Exception as e:
                    failed += 1
                    logger.error(
                        f"Failed to execute {query_type} query {index + 1}: {e}")
                    return False

        # Use anyio task group for concurrent execution
        async with anyio.create_task_group() as tg:
            for i, query in enumerate(queries):
                tg.start_soon(execute_with_limit, query, i)

        logger.info(
            f"Completed {query_type} queries: {successful} successful, {failed} failed")
        return successful, failed

    async def _execute_queries_in_concurrent_batches(
        self,
        queries: List[str],
        query_type: str,
        logger: logging.Logger,
        batch_size: int = 5,
        max_concurrent_batches: int = 5
    ) -> Tuple[int, int]:
        """Execute queries in small concurrent batches for optimal performance."""
        if not queries:
            return 0, 0

        # Split queries into small batches
        batches = [queries[i:i + batch_size]
                   for i in range(0, len(queries), batch_size)]
        semaphore = anyio.Semaphore(max_concurrent_batches)
        total_successful = 0
        total_failed = 0

        async def execute_batch_with_limit(batch: List[str], batch_index: int):
            nonlocal total_successful, total_failed
            async with semaphore:
                batch_query = "\n".join(batch)
                try:
                    await self.neo_service.run_query(batch_query)
                    total_successful += len(batch)
                    logger.info(
                        f"Executed {query_type} batch {batch_index + 1}/{len(batches)} ({len(batch)} queries)")
                    return len(batch), 0  # successful, failed
                except Exception as e:
                    total_failed += len(batch)
                    logger.error(
                        f"Failed to execute {query_type} batch {batch_index + 1}: {e}")
                    return 0, len(batch)  # successful, failed

        # Execute batches concurrently
        async with anyio.create_task_group() as tg:
            for i, batch in enumerate(batches):
                tg.start_soon(execute_batch_with_limit, batch, i)

        logger.info(
            f"Completed {query_type} batches: {total_successful} successful, {total_failed} failed")
        return total_successful, total_failed

    async def _safe_build_graph_data_for_file(
        self,
        filepath: str,
        container: dagger.Container,
        logger: logging.Logger
    ) -> Dict[str, any]:
        """Safely process a single file and return graph data instead of executing queries."""
        try:
            # Get file content
            content = await container.file(filepath).contents()
            if not content.strip():
                logger.debug(f"Skipping empty file: {filepath}")
                return {"success": True, "queries": [], "imports": [], "symbols": []}

            logger.debug(f"Processing file: {filepath} ({len(content)} chars)")

            # Parse and build graph data for file
            result = await self._build_graph_data_for_file(filepath, content, container, logger)

            if result["success"]:
                logger.debug(f"Successfully processed {filepath}")
            else:
                logger.warning(f"Failed to process {filepath}")

            return result

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            return {"success": False, "queries": [], "imports": [], "symbols": []}

    async def _build_graph_data_for_file(
        self,
        filepath: str,
        content: str,
        container: dagger.Container,
        logger: logging.Logger
    ) -> Dict[str, any]:
        """Process a file and return Cypher queries instead of executing them."""
        try:
            # Additional file types to explicitly exclude
            excluded_extensions = ['xml', 'json', 'md',
                                   'txt', 'csv', 'yml', 'yaml', 'html']

            # Extract extension and check if it's explicitly excluded
            _, ext = os.path.splitext(filepath)
            ext = ext.lstrip('.').lower()

            if ext in excluded_extensions:
                logger.debug(
                    f"Skipping excluded file type: {filepath} (extension: {ext})")
                return {"success": True, "queries": [], "imports": [], "symbols": []}

            # Check against allowed extensions if configured
            config_obj = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config
            if hasattr(config_obj, 'indexing') and hasattr(config_obj.indexing, 'file_extensions'):
                valid_extensions = config_obj.indexing.file_extensions
                if ext not in valid_extensions:
                    logger.debug(
                        f"Skipping non-code file: {filepath} (extension: {ext})")
                    return {"success": True, "queries": [], "imports": [], "symbols": []}

            queries = []
            imports = []
            symbols = []

            # Parse code file using the agent_utils parser
            try:
                agent_utils = dag.agent_utils()
                code_file_json = await agent_utils.parse_code_file_to_json(content, filepath)
                json_content = await code_file_json.contents()
                code_file_dict = json.loads(json_content)

                if not code_file_dict:
                    logger.warning(f"Could not parse {filepath}")
                    return {"success": False, "queries": [], "imports": [], "symbols": []}

                language = code_file_dict["language"]
                parsed_symbols = code_file_dict["symbols"]

                # Build file creation query
                queries.append(self._build_file_cypher(filepath, language))

                # Build symbol creation queries and collect symbol info
                if parsed_symbols:
                    for symbol_dict in parsed_symbols:
                        symbol_name = symbol_dict.get("name", "")
                        if symbol_name:
                            symbol_type = symbol_dict.get(
                                "type", "symbol").capitalize()
                            queries.append(self._build_symbol_cypher(
                                symbol_dict, filepath))
                            symbols.append((filepath, symbol_type))

                # Extract imports using simple regex patterns
                try:
                    file_imports = self._extract_simple_imports(
                        content, filepath)
                    for import_path in file_imports:
                        imports.append((filepath, import_path))
                except Exception as import_err:
                    logger.warning(
                        f"Error extracting imports for {filepath}: {import_err}")

                # Simple config file handling
                if filepath.endswith(('config.js', 'config.ts', 'setup.js', 'setup.ts')):
                    if "module.exports" in content or "export default" in content:
                        config_query = f'MERGE (f:File {{filepath: "{self._escape_cypher_string(filepath)}"}}) MERGE (f)-[:EXPORTS]->(:ConfigExport {{type: "configuration"}});'
                        queries.append(config_query)

                return {
                    "success": True,
                    "queries": queries,
                    "imports": imports,
                    "symbols": symbols
                }

            except Exception as parse_err:
                logger.error(f"Failed to parse {filepath}: {parse_err}")
                return {"success": False, "queries": [], "imports": [], "symbols": []}

        except Exception as e:
            logger.error(f"Failed to build graph data for {filepath}: {e}")
            return {"success": False, "queries": [], "imports": [], "symbols": []}

    async def _process_files_with_semaphore(
        self,
        files: List[str],
        container: dagger.Container,
        logger: logging.Logger,
        max_concurrent: int = 3
    ) -> Tuple[int, int, List[str], List[Tuple[str, str]], List[Tuple[str, str]]]:
        """Process files with semaphore-controlled concurrency and collect all queries."""
        if not files:
            return 0, 0, [], [], []

        semaphore = anyio.Semaphore(max_concurrent)
        results = []
        all_queries = []
        all_imports = []
        all_symbols = []

        async def process_with_limit(filepath: str):
            async with semaphore:
                result = await self._safe_build_graph_data_for_file(filepath, container, logger)
                results.append(result["success"])
                if result["success"]:
                    all_queries.extend(result["queries"])
                    all_imports.extend(result["imports"])
                    all_symbols.extend(result["symbols"])
                return result

        # Use anyio task group for concurrent processing
        async with anyio.create_task_group() as tg:
            for filepath in files:
                tg.start_soon(process_with_limit, filepath)

        # Count results
        processed = sum(1 for result in results if result is True)
        failed = sum(1 for result in results if result is False)

        logger.info(
            f"Processed {processed} files successfully, {failed} failed")
        logger.info(
            f"Generated {len(all_queries)} node/symbol queries, {len(all_imports)} import relationships, {len(all_symbols)} symbol relationships")

        return processed, failed, all_queries, all_imports, all_symbols

    @function
    async def setup_neo(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
    ) -> str:
        """Set up Neo4j service and return connection status."""
        logger = self._setup_logging()

        try:
            self.config = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config

            # Create Neo4j service
            self.neo_service = dag.neo_service(
                self.config_file,
                password=neo_password,
                github_access_token=github_access_token,
                neo_auth=neo_auth,
                neo_data=self.neo_data
            )
            # Test connection
            test_result = await self.neo_service.test_connection()
            logger.info(f"Neo4j connection established")
            clear = await self.neo_service.clear_database()
            if clear:
                logger.info("Neo4j database cleared successfully")

            return f"Neo4j connection successful: {test_result}"
        except Exception as e:
            logger.error(f"Failed to setup Neo4j: {e}")
            raise

    @function
    async def build_graph_for_repository(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to analyze")],
        branch: Annotated[str, Doc("Branch to analyze")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
        open_router_api_key: Annotated[dagger.Secret, Doc(
            "OpenRouter API key")]
    ) -> str:
        """Build a graph representation of an entire repository using concurrent query execution."""
        # Setup logging
        logger = self._setup_logging()
        processing_config = self._get_processing_config()

        try:
            # Setup Neo4j first
            await self.setup_neo(
                github_access_token=github_access_token,
                neo_password=neo_password,
                neo_auth=neo_auth
            )

            # Clone repository
            source = (
                await dag.git(url=repository_url, keep_git_dir=True)
                .with_auth_token(github_access_token)
                .branch(branch)
                .tree()
            )

            # Build container
            self.config: YAMLConfig = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config
            container = await dag.builder(
                self.config_file
            ).build_test_environment(
                source=source,
                dockerfile_path=self.config.container.docker_file_path,
                open_router_api_key=open_router_api_key,
                provider=self.config.core_api.provider if self.config.core_api else None,
                openai_api_key=open_router_api_key
            )

            # Get working directory from config
            work_dir = getattr(self.config.container, 'work_dir', '/app')
            logger.info(f"Using work directory: {work_dir}")

            # Get file extensions to process
            file_extensions = getattr(
                self.config.indexing, 'file_extensions', ['py', 'js', 'ts'])

            # Build find command for multiple extensions with exclusions
            find_cmd = ["find", work_dir, "-type", "f", "("]

            # Add extension patterns
            for i, ext in enumerate(file_extensions):
                ext = ext.strip('.')
                if i > 0:
                    find_cmd.append("-o")
                find_cmd.extend(["-name", f"*.{ext}"])

            find_cmd.append(")")

            # Exclude specific patterns including test directories
            find_cmd.extend([
                "!", "-path", "*/node_modules/*",
                "!", "-path", r"*/\.*",
                "!", "-path", "*/dist/*",
                "!", "-path", "*/build/*",
                "!", "-path", "*/tests/*",
                "!", "-path", "*/test/*",
                "!", "-path", "*/__tests__/*",
                "!", "-path", "*/spec/*",
                "!", "-path", "*/.pytest_cache/*",
                "!", "-path", "*/.coverage/*",
                "!", "-name", "*.test.*",
                "!", "-name", "*.spec.*",
                "!", "-name", "*_test.*",
                "!", "-name", "test_*",
                "!", "-name", "*.min.*",
                "!", "-name", "*.xml",
                "!", "-name", "*.json",
                "!", "-name", "*.md",
                "!", "-name", "*.yaml",
                "!", "-name", "*.yml"
            ])

            logger.info(f"Running find command: {' '.join(find_cmd)}")
            file_list = await container.with_exec(find_cmd).stdout()

            # Parse file list
            files = file_list.strip().split("\n")
            files = [f for f in files if f.strip()]

            if not files:
                logger.warning(
                    f"No files found in {work_dir} with extensions: {file_extensions}")
                return f"No files found in {work_dir} with specified extensions"

            logger.info(f"Found {len(files)} files to process")

            # Process files concurrently and collect all queries
            processed, failed, all_queries, all_imports, all_symbols = await self._process_files_with_semaphore(
                files=files,
                container=container,
                logger=logger,
                max_concurrent=processing_config['max_concurrent']
            )

            # Clear database first
            logger.info("Clearing existing database")
            await self.neo_service.clear_database()

            # Create constraints and indexes to match neo4j_schema
            logger.info("Creating constraints and indexes")
            constraints_and_indexes = [
                "CREATE CONSTRAINT file_path_constraint IF NOT EXISTS FOR (file:File) REQUIRE file.path IS UNIQUE",
                "CREATE CONSTRAINT file_filepath_unique IF NOT EXISTS FOR (f:File) REQUIRE f.filepath IS UNIQUE",
                "CREATE CONSTRAINT function_name_path_line IF NOT EXISTS FOR (function:Function) REQUIRE (function.name, function.filepath, function.start_line) IS UNIQUE",
                "CREATE CONSTRAINT class_name_path_line IF NOT EXISTS FOR (class:Class) REQUIRE (class.name, class.filepath, class.start_line) IS UNIQUE",
                "CREATE CONSTRAINT variable_name_path_line IF NOT EXISTS FOR (variable:Variable) REQUIRE (variable.name, variable.filepath, variable.line_number) IS UNIQUE",
                "CREATE INDEX function_name_idx IF NOT EXISTS FOR (f:Function) ON (f.name)",
                "CREATE INDEX file_language_idx IF NOT EXISTS FOR (f:File) ON (f.language)",
                "CREATE INDEX file_filepath_idx IF NOT EXISTS FOR (f:File) ON (f.filepath)"
            ]

            for query in constraints_and_indexes:
                try:
                    await self.neo_service.run_query(query)
                    constraint_name = query.split()[2]
                    logger.info(f"Created constraint/index: {constraint_name}")
                except Exception as e:
                    logger.warning(f"Could not create constraint/index: {e}")

            # Execute queries using concurrent batches for maximum performance
            logger.info(
                f"Executing {len(all_queries)} node/symbol queries using concurrent batches")
            node_successful, node_failed = await self._execute_queries_in_concurrent_batches(
                all_queries, "node/symbol", logger, batch_size=5, max_concurrent_batches=8
            )

            # Create DEFINED_IN relationships using concurrent batches
            logger.info(
                f"Creating {len(all_symbols)} DEFINED_IN relationships using concurrent batches")
            relationship_queries = []
            for filepath, symbol_type in set(all_symbols):  # Remove duplicates
                rel_query = self._build_relationship_cypher(
                    filepath, symbol_type)
                relationship_queries.append(rel_query)

            rel_successful, rel_failed = await self._execute_queries_in_concurrent_batches(
                relationship_queries, "relationship", logger, batch_size=5, max_concurrent_batches=8
            )

            # Execute import queries using concurrent batches
            logger.info(
                f"Creating {len(all_imports)} import relationships using concurrent batches")
            import_queries = []
            unique_imports = set(all_imports)  # Remove duplicates

            for from_file, to_file in unique_imports:
                import_query = self._build_import_cypher(from_file, to_file)
                import_queries.append(import_query)

            import_successful, import_failed = await self._execute_queries_in_concurrent_batches(
                import_queries, "import", logger, batch_size=5, max_concurrent_batches=8
            )

            logger.info(
                "Successfully executed all concurrent batch Cypher queries")

            # Verify the results
            test_result = await self.neo_service.test_connection()

            return f"Graph built successfully: {processed} files processed, {failed} file failures, {node_successful} nodes created, {rel_successful} relationships created, {import_successful} imports created. Database status: {test_result}"

        except Exception as e:
            logger.error(f"Graph building failed: {e}")
            raise

import logging
import os
from typing import Annotated, Optional
import json

import dagger
import yaml
from dagger.client.gen import NeoService, NeoServiceSymbolProperties, NeoServiceRelationshipProperties
from ais_dagger_agents_config.models import YAMLConfig
from dagger import Doc, dag, function, object_type
from graph.models.code_file import CodeFile, CodeSymbol
from graph.operations.import_analyzer import ImportAnalyzer
from graph.operations.relationship_extractor import RelationshipExtractor
from graph.utils import dagger_json_file_to_pydantic


@object_type
class Graph:
    config: dict
    config_file: dagger.File
    neo_service: Optional[NeoService] = None

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to the YAML config file")]) -> "Graph":
        """Create a Graph object from a YAML config file."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, config_file=config_file)

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("graph.main")

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
                neo_auth=neo_auth
            )

            # Test connection
            test_result = await self.neo_service.test_connection()
            logger.info(f"Neo4j connection established")

            return f"Neo4j connection successful: {test_result}"
        except Exception as e:
            logger.error(f"Failed to setup Neo4j: {e}")
            raise

    @function
    async def build_graph_for_file(
        self,
        filepath: str,
        content: str,
        container: dagger.Container,
    ) -> bool:
        """Process a file to build its graph representation in Neo4j."""
        logger = self._setup_logging()

        try:
            if not self.neo_service:
                logger.error(
                    "Neo4j service not initialized. Call setup_neo first.")
                return False

            # Additional file types to explicitly exclude
            excluded_extensions = ['xml', 'json', 'md',
                                   'txt', 'csv', 'yml', 'yaml', 'html']

            # Extract extension and check if it's explicitly excluded
            _, ext = os.path.splitext(filepath)
            ext = ext.lstrip('.').lower()  # Remove leading dot and normalize

            if ext in excluded_extensions:
                logger.info(
                    f"Skipping excluded file type: {filepath} (extension: {ext})")
                return True  # Return true to avoid counting as failure

            # Check against allowed extensions if configured
            if hasattr(self.config.indexing, 'file_extensions'):
                valid_extensions = self.config.indexing.file_extensions
                if ext not in valid_extensions:
                    logger.info(
                        f"Skipping non-code file: {filepath} (extension: {ext})")
                    return True

            # Parse code file using the agent_utils parser - JSON approach
            try:
                # Create an AgentUtils instance
                agent_utils = dag.agent_utils()

                # Parse the file and get a JSON file
                code_file_json = await agent_utils.parse_code_file_to_json(content, filepath)

                # Read the JSON content directly
                json_content = await code_file_json.contents()
                # Work with dict directly
                code_file_dict = json.loads(json_content)

                if not code_file_dict:
                    logger.warning(f"Could not parse {filepath}")
                    return False

                # Access as dictionary keys, not attributes
                language = code_file_dict["language"]
                # This is a list of dictionaries
                symbols = code_file_dict["symbols"]

                # Add file to Neo4j
                logger.info(
                    f"Adding {filepath} to Neo4j graph with language: {language}")
                await self.neo_service.add_file_node(filepath, language)

                # Process symbols if we have any
                if symbols:  # Check if we have symbols
                    for symbol_dict in symbols:
                        # Access dictionary values
                        symbol_name = symbol_dict.get("name", "")
                        if not symbol_name:
                            continue

                        # Extract symbol properties
                        symbol_type = symbol_dict.get(
                            "type", "symbol").capitalize()

                        # Get line numbers
                        start_line = symbol_dict.get("line_number", 0) or 0
                        end_line = symbol_dict.get("end_line_number", -1) or -1

                        # Collect additional properties
                        properties = {}
                        for attr in ['signature', 'visibility', 'scope', 'docstring', 'parent']:
                            if attr in symbol_dict and symbol_dict[attr]:
                                properties[attr] = symbol_dict[attr]

                        # Create symbol properties using the from_dict factory method
                        if properties:
                            symbol_props = NeoServiceSymbolProperties(
                                **properties)

                            # Pass it to the Neo4j service
                            await self.neo_service.add_symbol(
                                symbol_type=symbol_type,
                                name=symbol_name,
                                filepath=filepath,
                                start_line=start_line,
                                end_line=end_line,
                                properties=symbol_props
                            )
                        else:
                            # No properties case
                            await self.neo_service.add_symbol(
                                symbol_type=symbol_type,
                                name=symbol_name,
                                filepath=filepath,
                                start_line=start_line,
                                end_line=end_line,
                                properties=None
                            )

                    # Collect queries for all symbols
                    symbol_queries = []
                    for symbol_dict in symbols:
                        # Access dictionary values
                        symbol_name = symbol_dict.get("name", "")
                        if not symbol_name:
                            continue

                        # Extract symbol properties
                        symbol_type = symbol_dict.get(
                            "type", "symbol").capitalize()

                        # Get line numbers
                        start_line = symbol_dict.get("line_number", 0) or 0
                        end_line = symbol_dict.get("end_line_number", -1) or -1

                        # Escape values for Cypher
                        escaped_name = symbol_name.replace('"', '\\"')
                        escaped_filepath = filepath.replace('"', '\\"')
                        start_line_str = str(start_line)
                        end_line_str = "null" if end_line < 0 else str(
                            end_line)

                        # Build the Cypher query for this symbol
                        query = f'''
                        MERGE (s:{symbol_type} {{name: "{escaped_name}", filepath: "{escaped_filepath}"}})
                        SET s.start_line = {start_line_str}, s.end_line = {end_line_str}
                        WITH s
                        MATCH (f:File {{filepath: "{escaped_filepath}"}})
                        MERGE (s)-[:DEFINED_IN]->(f)
                        '''

                        symbol_queries.append(query)

                    # Run all symbol queries at once
                    if symbol_queries:
                        await self.neo_service.run_batch_queries(symbol_queries)

                    # Process relationships if we have valid symbols
                    if symbols:  # symbols is already a list of dictionaries
                        try:
                            await RelationshipExtractor.extract_relationships(
                                filepath=filepath,
                                code_file_dict=code_file_dict,  # Pass the dictionary, not an object
                                neo4j=self.neo_service
                            )
                        except Exception as rel_err:
                            logger.warning(
                                f"Error extracting relationships for {filepath}: {rel_err}")
                else:
                    logger.warning(f"No iterable symbols found for {filepath}")

                # Analyze imports regardless of symbols
                try:
                    await ImportAnalyzer.analyze_file_imports(
                        filepath=filepath,
                        content=content,
                        neo4j=self.neo_service
                    )
                except Exception as import_err:
                    logger.warning(
                        f"Error analyzing imports for {filepath}: {import_err}")

                # Special handling for config files
                if filepath.endswith(('config.js', 'config.ts', 'setup.js', 'setup.ts')):
                    logger.info(f"Processing configuration file: {filepath}")

                    try:
                        # Add EXPORTS relationship for config files
                        if "module.exports" in content or "export default" in content:
                            from dagger.client.gen import \
                                NeoServiceRelationshipProperties

                            # Try different approaches to create the relationship
                            try:
                                # Try to create with type parameter
                                export_props = NeoServiceRelationshipProperties(
                                    type="configuration")
                            except Exception:
                                # Fall back to no properties
                                export_props = None

                            await self.neo_service.add_relationship(
                                start_filepath=filepath,
                                relationship_type="EXPORTS",
                                end_filepath=os.path.dirname(filepath),
                                properties=export_props
                            )
                            logger.info(
                                f"Added EXPORTS relationship for config file {filepath}")
                    except Exception as config_err:
                        logger.warning(
                            f"Error adding config exports relationship: {config_err}")

                symbols_count = len(symbols) if hasattr(
                    symbols, '__iter__') else 0
                logger.info(
                    f"Successfully added {filepath} to Neo4j with {symbols_count} symbols")
                return True

            except Exception as parse_err:
                logger.error(f"Failed to parse {filepath}: {parse_err}")
                return False

        except Exception as e:
            logger.error(f"Failed to build graph for {filepath}: {e}")
            return False

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
        """Build a graph representation of an entire repository."""
        # Setup logging
        logger = self._setup_logging()

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
            find_cmd = ["find", work_dir, "-type", "f", "("]  # Start grouping

            # Add extension patterns
            for i, ext in enumerate(file_extensions):
                # Clean extension format (remove dots if present)
                ext = ext.strip('.')

                # Add OR operator between multiple conditions
                if i > 0:
                    find_cmd.append("-o")

                find_cmd.extend(["-name", f"*.{ext}"])

            find_cmd.append(")")  # Close grouping

            # Exclude specific patterns
            find_cmd.extend([
                "!", "-path", "*/node_modules/*",
                "!", "-path", r"*/\.*",
                "!", "-path", "*/dist/*",
                "!", "-name", "*.min.*",
                "!", "-name", "*.xml",
                "!", "-name", "*.json",
                "!", "-name", "*.md",
                "!", "-name", "*.yaml",
                "!", "-name", "*.yml"
            ])

            logger.info(f"Running find command: {' '.join(find_cmd)}")
            file_list = await container.with_exec(find_cmd).stdout()

            # Rest of function remains the same...
            files = file_list.strip().split("\n")
            if not files or files[0] == '':
                logger.warning(
                    f"No files found in {work_dir} with extensions: {file_extensions}")
                return f"No files found in {work_dir} with specified extensions"

            # Process each file
            processed = 0
            failed = 0

            for filepath in files:
                # Get file content
                print(f"Processing file: {filepath}")
                content = await container.file(filepath).contents()
                if not content.strip():
                    logger.info(f"Skipping empty file: {filepath}")
                    continue

                # Build graph for file
                if await self.build_graph_for_file(filepath, content, container):
                    processed += 1
                else:
                    failed += 1

            return f"Graph built with {processed} files processed, {failed} failed from {work_dir}"

        except Exception as e:
            logger.error(f"Graph building failed: {e}")
            raise

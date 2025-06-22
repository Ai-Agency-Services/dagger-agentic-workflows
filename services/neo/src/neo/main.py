import json
import logging
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

import dagger
from dagger import Doc, dag, field, function, object_type
from simple_chalk import green
import yaml
from ais_dagger_agents_config import YAMLConfig


@object_type
class SymbolProperties:
    """Properties for a code symbol"""
    # Common properties you might need
    docstring: Optional[str] = field(default=None)
    signature: Optional[str] = field(default=None)
    scope: Optional[str] = field(default=None)
    parent: Optional[str] = field(default=None)

    # You can add more fields as needed
    # Or use JSON for arbitrary properties
    json_data: Optional[str] = field(default=None)

    @classmethod
    def from_dict(cls, data: dict) -> "SymbolProperties":
        """Create a SymbolProperties from a dictionary"""
        # Extract known fields
        props = {}
        if data:
            for field_name in ["docstring", "signature", "scope", "parent"]:
                if field_name in data:
                    props[field_name] = data.pop(field_name)

            # Store remaining properties as JSON
            if data:
                props["json_data"] = json.dumps(data)

        return cls(**props)


@object_type
class NeoService:
    """Neo4j service management and operations."""
    config: dict
    config_file: dagger.File
    password: dagger.Secret
    github_access_token: dagger.Secret
    neo_auth: dagger.Secret
    client_container: dagger.Container

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("Path to YAML config file")],
        password: Annotated[dagger.Secret, Doc("Neo4j password")],
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token for cypher-shell repository")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j authentication string in the format 'username/password'")],
    ):
        """ Create """
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(
            config=config_dict, password=password,
            github_access_token=github_access_token,
            neo_auth=neo_auth,
            client_container=dag.container(),
            config_file=config_file
        )

    @function
    async def create_neo_service(self) -> dagger.Service:
        """Create a Neo4j service as a Dagger service"""
        self.config: YAMLConfig = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config
        plugin_string = json.dumps(
            self.config.neo4j.plugins) if self.config.neo4j.plugins else '[]'

        # Generate unique cache name to avoid lock conflicts
        unique_cache_name = f"{self.config.neo4j.cache_volume_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        print(green(f"Using Neo4j plugins: {plugin_string}"))
        return (
            dag.container()
            .from_(self.config.neo4j.image)
            .with_secret_variable("NEO4J_AUTH", self.neo_auth)
            .with_env_variable("NEO4J_PLUGINS",  plugin_string)
            .with_env_variable("NEO4J_apoc_export_file_enabled", self.config.neo4j.apoc_export_file_enabled)
            .with_env_variable("NEO4J_apoc_import_file_enabled", self.config.neo4j.apoc_import_file_enabled)
            .with_env_variable("NEO4J_apoc_import_file_use__neo4j__config", self.config.neo4j.apoc_import_use_neo4j_config)
            .with_env_variable("NEO4J_server_memory_pagecache_size",  self.config.neo4j.memory_pagecache_size)
            .with_env_variable("NEO4J_server_memory_heap_initial__size", self.config.neo4j.memory_heap_initial_size)
            .with_env_variable("NEO4J_server_memory_heap_max__size",  self.config.neo4j.memory_heap_max_size)
            .with_env_variable("NEO4J_dbms_allow__upgrade", "true")  # Allow upgrade of database
            .with_env_variable("NEO4J_dbms_tx_log_fail__on__corrupted__log__files", "false")  # Be more forgiving with corrupted files
            .with_exposed_port(self.config.neo4j.http_port)  # HTTP interface
            .with_exposed_port(self.config.neo4j.bolt_port)  # Bolt protocol
            .with_mounted_cache(self.config.neo4j.data_volume_path, dag.cache_volume(unique_cache_name))
            .as_service()
            .with_hostname("neo")
        )

    @function
    async def create_neo_client(self) -> dagger.Container:
        """Create a Neo4j client container with cypher-shell"""
        self.config: YAMLConfig = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config
        source = (
            await dag.git(url=self.config.neo4j.cypher_shell_repository, keep_git_dir=True)
            .with_auth_token(self.github_access_token)
            .branch("main")
            .tree()
        )
        self.client_container = dag.builder(self.config_file).build_cypher_shell(
            source=source,
        )

        self.client_container = (
            self.client_container
            .with_service_binding("neo", await self.create_neo_service())
            .with_secret_variable("NEO4J_PASSWORD", self.password)
            .with_env_variable("NEO4J_USERNAME", self.config.neo4j.username)
        )

        return self.client_container

    @function
    async def run_query(self, query: str) -> str:
        """Run a query against the Neo4j service"""
        # Create client with service binding if not already created
        if not self.client_container:
            self.client_container = await self.create_neo_client()

        # Write query to file
        client = (
            self.client_container.with_new_file(
                "/tmp/query.cypher", query)
        )

        return await client.with_exec([
            "cypher-shell",
            "-a", self.config.neo4j.uri,
            "--non-interactive",
            "-f", "/tmp/query.cypher"
        ]).stdout()

    @function
    async def test_connection(self) -> str:
        """Test connection to Neo4j service"""
        self.config: YAMLConfig = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config
        await self.create_neo_client()
        return await self.run_query("RETURN 'Connected' AS result")

    @function
    def connect(self) -> bool:
        """Verify connection to Neo4j"""
        # If we have a client container, connection is already verified
        if self.client_container:
            return True

        # Otherwise return False as we need a container for operations
        logger = self._get_logger()
        logger.error("Neo4j service requires a client container")
        return False

    @function
    async def clear_database(self) -> bool:
        """Clear all nodes and relationships from the database"""
        try:
            # Create query for clearing database
            query = "MATCH (n) DETACH DELETE n"
            await self.run_query(query)
            return True
        except Exception as e:
            logger = self._get_logger()
            logger.error(f"Failed to clear Neo4j database: {e}")
            return False

    @function
    async def add_file_node(self, filepath: str, language: str) -> bool:
        """Add a file node to the graph"""
        try:
            # Escape quotes in strings
            filepath = filepath.replace('"', '\\"')
            language = language.replace('"', '\\"')

            # Create a Cypher query to add the file node
            query = f'MERGE (f:File {{filepath: "{filepath}"}}) SET f.language = "{language}"'
            await self.run_query(query)
            return True
        except Exception as e:
            logger = self._get_logger()
            logger.error(f"Failed to add file node {filepath}: {e}")
            return False

    @function
    async def add_symbol(
        self,
        symbol_type: str,
        name: str,
        filepath: str,
        start_line: int,
        end_line: int,
        properties: Optional[SymbolProperties] = None
    ) -> bool:
        """Add a symbol node to the graph with connection to its file"""
        try:
            # Get logger when needed
            logger = self._get_logger()

            # Escape quotes in strings
            name = name.replace('"', '\\"')
            filepath = filepath.replace('"', '\\"')

            # Format end_line properly (None → null)
            end_line_str = "null" if end_line is None else str(end_line)
            start_line_str = "null" if start_line is None else str(start_line)

            # Create properties string for Cypher
            props = []

            # Handle known properties
            if properties:
                if properties.docstring:
                    escaped_docstring = properties.docstring.replace(
                        '"', '\\"')
                    props.append(f's.docstring = "{escaped_docstring}"')

                if properties.signature:
                    escaped_signature = properties.signature.replace(
                        '"', '\\"')
                    props.append(f's.signature = "{escaped_signature}"')

                if properties.scope:
                    props.append(f's.scope = "{properties.scope}"')

                if properties.parent:
                    props.append(f's.parent = "{properties.parent}"')

                # Handle JSON data if present
                if properties.json_data:
                    # Parse the JSON to add individual properties
                    try:
                        extra_props = json.loads(properties.json_data)
                        for k, v in extra_props.items():
                            if v is None:
                                props.append(f's.{k} = null')
                            elif isinstance(v, (int, float, bool)):
                                props.append(f's.{k} = {v}')
                            else:
                                # Properly escape quotes
                                escaped_v = str(v).replace('"', '\\"')
                                props.append(f's.{k} = "{escaped_v}"')
                    except:
                        # If JSON parsing fails, add as raw text
                        escaped_json = properties.json_data.replace('"', '\\"')
                        props.append(f's.extra_data = "{escaped_json}"')

            properties_str = ", ".join(props) if props else ""

            # Build the query
            query = f'''
            MERGE (s:{symbol_type} {{name: "{name}", filepath: "{filepath}"}})
            SET s.start_line = {start_line_str}, s.end_line = {end_line_str}
            '''

            if properties_str:
                query += f", {properties_str}"

            # Connect to file
            query += f'''
            WITH s
            MATCH (f:File {{filepath: "{filepath}"}})
            MERGE (s)-[:DEFINED_IN]->(f)
            '''

            await self.run_query(query)
            return True
        except Exception as e:
            # Get logger again for error
            logger = self._get_logger()
            logger.error(f"Failed to add symbol {name} in {filepath}: {e}")
            return False

    def _get_logger(self):
        """Get a logger for this service"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger("neo4j.service")

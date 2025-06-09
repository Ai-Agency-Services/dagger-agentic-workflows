import logging
from typing import Dict, Optional

import dagger
from dagger import dag


class Neo4jService:
    """Neo4j service management and operations."""

    def __init__(
        self,
        cypher_shell_repo: str,
        password: dagger.Secret,
        github_access_token: dagger.Secret,
        user: str = "neo4j",
        config_file: dagger.File = None,
        database: str = "neo4j",
        uri: str = "neo4j://neo:7687",
    ):
        """Initialize Neo4jService with user and password."""
        self.user = user
        self.password = password or dag.secret
        self.cypher_shell_repo = cypher_shell_repo
        self.github_access_token = github_access_token
        self.config_file = config_file
        self.database = database
        self.uri = uri
        self.client_container = None
        self.logger = logging.getLogger(__name__)

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logging.debug(f"Initialized Neo4jService with user: {self.user}")

    def create_neo4j_service(self) -> dagger.Service:
        """Create a Neo4j service as a Dagger service"""
        return (
            dag.container()
            .from_("neo4j:2025.05")
            .with_env_variable("NEO4J_AUTH", f"{self.user}/{self.password}")
            .with_env_variable("NEO4J_PLUGINS", '["apoc"]')
            .with_env_variable("NEO4J_apoc_export_file_enabled", "true")
            .with_env_variable("NEO4J_apoc_import_file_enabled", "true")
            .with_env_variable("NEO4J_apoc_import_file_use__neo4j__config", "true")
            .with_env_variable("NEO4J_server_memory_pagecache_size", "1G")
            .with_env_variable("NEO4J_server_memory_heap_initial__size", "1G")
            .with_env_variable("NEO4J_server_memory_heap_max__size", "1G")
            .with_exposed_port(7474)  # HTTP interface
            .with_exposed_port(7687)  # Bolt protocol
            .with_mounted_cache("/data", dag.cache_volume("neo4j-data"))
            .as_service()
            .with_hostname("neo")
        )

    async def create_neo4j_client(self) -> dagger.Container:
        """Create a Neo4j client container with cypher-shell"""
        source = (
            await dag.git(url=self.cypher_shell_repo, keep_git_dir=True)
            .with_auth_token(self.github_access_token)
            .branch("main")
            .tree()
        )
        cypher_cli = dag.builder(self.config_file).build_cypher_shell(
            source=source,
        )

        self.client_container = (
            cypher_cli
            .with_service_binding("neo", Neo4jService.create_neo4j_service())
        )

        return self.client_container

    async def run_query(self, query: str) -> str:
        """Run a query against the Neo4j service"""
        # Create client with service binding if not already created
        if not self.client_container:
            self.client_container = await self.create_neo4j_client()

        # Write query to file
        client = self.client_container.with_new_file(
            "/tmp/query.cypher", query)

        # Run query using cypher-shell
        return await client.with_exec([
            "cypher-shell",
            "-a", self.uri,
            "-u", self.user,
            "-p", await self.password.plaintext(),
            "--non-interactive",
            "-f", "/tmp/query.cypher"
        ]).stdout()

    async def test_connection(self) -> str:
        """Test connection to Neo4j service"""
        return await self.run_query("RETURN 'Connected' AS result")

    def connect(self) -> bool:
        """Verify connection to Neo4j"""
        # If we have a client container, connection is already verified
        if self.client_container:
            return True

        # Otherwise return False as we need a container for operations
        self.logger.error("Neo4j service requires a client container")
        return False

    async def clear_database(self) -> bool:
        """Clear all nodes and relationships from the database"""
        try:
            # Create query for clearing database
            query = "MATCH (n) DETACH DELETE n"
            await self.run_query(query)
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear Neo4j database: {e}")
            return False

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
            self.logger.error(f"Failed to add file node {filepath}: {e}")
            return False

    async def add_symbol(self, symbol_type: str, name: str, filepath: str,
                         start_line: int, end_line: int, properties: Dict = None) -> bool:
        """Add a symbol node to the graph with connection to its file"""
        if properties is None:
            properties = {}

        try:
            # Escape quotes in strings
            name = name.replace('"', '\\"')
            filepath = filepath.replace('"', '\\"')

            # Format end_line properly (None → null)
            end_line_str = "null" if end_line is None else str(end_line)
            start_line_str = "null" if start_line is None else str(start_line)

            # Create properties string for Cypher
            props = []
            for k, v in properties.items():
                if v is None:
                    props.append(f's.{k} = null')
                elif isinstance(v, (int, float, bool)):
                    props.append(f's.{k} = {v}')
                else:
                    # Properly escape quotes
                    escaped_v = str(v).replace('"', '\\"')
                    props.append(f's.{k} = "{escaped_v}"')

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
            self.logger.error(
                f"Failed to add symbol {name} in {filepath}: {e}")
            return False

    async def add_relationship(self, from_type: str, from_name: str, from_filepath: str,
                               from_line: int, to_type: str, to_name: str, to_filepath: str,
                               to_line: int, rel_type: str) -> bool:
        """Add a relationship between two code elements"""
        try:
            # Escape quotes in strings
            from_name = from_name.replace('"', '\\"')
            from_filepath = from_filepath.replace('"', '\\"')
            to_name = to_name.replace('"', '\\"')
            to_filepath = to_filepath.replace('"', '\\"')

            # Build the query with relationship
            query = f'''
            MATCH (from:{from_type} {{name: "{from_name}", filepath: "{from_filepath}"}}),
                  (to:{to_type} {{name: "{to_name}", filepath: "{to_filepath}"}})
            MERGE (from)-[:{rel_type}]->(to)
            '''

            await self.run_query(query)
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to add relationship {from_name}-[{rel_type}]->{to_name}: {e}")
            return False

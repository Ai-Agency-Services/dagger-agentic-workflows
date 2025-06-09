import logging
from typing import Dict, List, Optional, Any
import dagger


class Neo4jConnector:
    """Connector for Neo4j graph database for indexing code structure using Dagger services"""

    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j", client_container: Optional[dagger.Container] = None):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.logger = logging.getLogger(__name__)
        self.client_container = client_container

    def connect(self) -> bool:
        """Verify connection to Neo4j"""
        # If we have a client container, connection is already verified
        if self.client_container:
            return True

        # Otherwise return False as we need a container for operations
        self.logger.error("Neo4j connector requires a client container")
        return False

    async def clear_database(self) -> bool:
        """Clear all nodes and relationships from the database"""
        if not self.client_container:
            self.logger.error("Cannot clear database: No client container")
            return False

        try:
            # Create query for clearing database
            query = "MATCH (n) DETACH DELETE n"

            # Write query to file
            client = self.client_container.with_new_file(
                "/tmp/query.cypher", query)

            # Execute the query using cypher-shell
            await client.with_exec([
                "cypher-shell",
                "-a", self.uri,
                "-u", "neo4j",
                "-p", "devpassword",
                "--non-interactive",
                "-f", "/tmp/query.cypher"
            ]).stdout()

            return True
        except Exception as e:
            self.logger.error(f"Failed to clear Neo4j database: {e}")
            return False

    async def add_file_node(self, filepath: str, language: str):
        """Add a file node to the graph"""
        if not self.client_container:
            self.logger.error("Cannot add file node: No client container")
            return

        try:
            # Create a Cypher query to add the file node
            query = f'MERGE (f:File {{filepath: "{filepath}"}}) SET f.language = "{language}"'

            # Write query to file instead of using echo
            client = self.client_container.with_new_file(
                "/tmp/query.cypher", query)

            # Execute the query using cypher-shell
            await client.with_exec([
                "cypher-shell",
                "-a", self.uri,  # Match the service binding
                "-u", "neo4j",
                "-p", "devpassword",
                "--non-interactive",
                "-f", "/tmp/query.cypher"
            ]).stdout()

        except Exception as e:
            self.logger.error(f"Failed to add file node {filepath}: {e}")

    async def add_symbol(self, symbol_type: str, name: str, filepath: str,
                         start_line: int, end_line: int, properties: Dict = None):
        """Add a symbol node to the graph with connection to its file"""
        if not self.client_container:
            self.logger.error(f"Cannot add symbol {name}: No client container")
            return

        if properties is None:
            properties = {}

        try:
            # Escape quotes in strings
            name = name.replace('"', '\\"')
            filepath = filepath.replace('"', '\\"')

            # Create properties string for Cypher
            props = [
                f's.{k} = "{str(v).replace("""", "\\""")}"' for k, v in properties.items()]
            properties_str = ", ".join(props) if props else ""

            # Build the query
            query = f'''
            MERGE (s:{symbol_type} {{name: "{name}", filepath: "{filepath}"}})
            SET s.start_line = {start_line}, s.end_line = {end_line}
            '''

            if properties_str:
                query += f", {properties_str}"

            # Connect to file
            query += f'''
            WITH s
            MATCH (f:File {{filepath: "{filepath}"}})
            MERGE (s)-[:DEFINED_IN]->(f)
            '''

            # Execute the query
            await self.client_container.with_exec([
                "/bin/bash", "-c",
                f'echo "{query}" | cypher-shell -a "{self.uri}" -u {self.username} -p {self.password}'
            ]).stdout()

        except Exception as e:
            self.logger.error(
                f"Failed to add symbol {name} in {filepath}: {e}")

    async def add_relationship(self, from_type: str, from_name: str, from_filepath: str,
                               from_line: int, to_type: str, to_name: str, to_filepath: str,
                               to_line: int, rel_type: str):
        """Add a relationship between two code elements"""
        if not self.client_container:
            self.logger.error(f"Cannot add relationship: No client container")
            return

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

            # Execute the query
            await self.client_container.with_exec([
                "/bin/bash", "-c",
                f'echo "{query}" | cypher-shell -a "{self.uri}" -u {self.username} -p {self.password}'
            ]).stdout()

        except Exception as e:
            self.logger.error(
                f"Failed to add relationship {from_name}-[{rel_type}]->{to_name}: {e}")

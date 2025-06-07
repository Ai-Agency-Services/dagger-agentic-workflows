import logging
from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase, Driver
import dagger


class Neo4jConnector:
    """Connector for Neo4j graph database"""

    def __init__(self, uri: str, username: str, password: dagger.Secret, database: str = "neo4j"):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.driver: Optional[Driver] = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.username, self.password)
            )
            # Verify connection
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]
                if test_value != 1:
                    raise ValueError("Connection test failed")
            self.logger.info(f"Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            return False

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self.driver = None

    def clear_database(self) -> bool:
        """Clear all nodes and relationships in the database"""
        if not self.driver:
            return False

        try:
            with self.driver.session(database=self.database) as session:
                session.run("MATCH (n) DETACH DELETE n")
            self.logger.info("Neo4j database cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear Neo4j database: {e}")
            return False

    def add_file_node(self, filepath: str, language: str) -> bool:
        """Add a file node to the graph"""
        if not self.driver:
            return False

        try:
            with self.driver.session(database=self.database) as session:
                session.run(
                    """
                    MERGE (f:File {path: $filepath})
                    SET f.language = $language
                    RETURN f
                    """,
                    filepath=filepath, language=language
                )
            return True
        except Exception as e:
            self.logger.error(f"Failed to add file node: {e}")
            return False

    def add_symbol(self,
                   symbol_type: str,
                   name: str,
                   filepath: str,
                   start_line: int,
                   end_line: Optional[int] = None,
                   properties: Optional[Dict[str, Any]] = None) -> bool:
        """Add a code symbol node to the graph"""
        if not self.driver:
            return False

        if properties is None:
            properties = {}

        try:
            with self.driver.session(database=self.database) as session:
                session.run(
                    f"""
                    MATCH (f:File {{path: $filepath}})
                    MERGE (s:{symbol_type} {{
                        name: $name,
                        filepath: $filepath,
                        start_line: $start_line,
                        end_line: $end_line
                    }})
                    SET s += $properties
                    MERGE (s)-[:DEFINED_IN]->(f)
                    RETURN s
                    """,
                    name=name,
                    filepath=filepath,
                    start_line=start_line,
                    end_line=end_line if end_line is not None else start_line,
                    properties=properties
                )
            return True
        except Exception as e:
            self.logger.error(f"Failed to add {symbol_type} node: {e}")
            return False

    def add_relationship(self,
                         from_type: str,
                         from_name: str,
                         from_filepath: str,
                         from_line: int,
                         to_type: str,
                         to_name: str,
                         to_filepath: str,
                         to_line: int,
                         rel_type: str) -> bool:
        """Add a relationship between two code symbols"""
        if not self.driver:
            return False

        try:
            with self.driver.session(database=self.database) as session:
                session.run(
                    f"""
                    MATCH (from:{from_type} {{
                        name: $from_name,
                        filepath: $from_filepath,
                        start_line: $from_line
                    }})
                    MATCH (to:{to_type} {{
                        name: $to_name,
                        filepath: $to_filepath,
                        start_line: $to_line
                    }})
                    MERGE (from)-[:{rel_type}]->(to)
                    """,
                    from_name=from_name,
                    from_filepath=from_filepath,
                    from_line=from_line,
                    to_name=to_name,
                    to_filepath=to_filepath,
                    to_line=to_line
                )
            return True
        except Exception as e:
            self.logger.error(f"Failed to add relationship: {e}")
            return False

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a custom Cypher query"""
        if not self.driver:
            return []

        if params is None:
            params = {}

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, params)
                return [record.data() for record in result]
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []

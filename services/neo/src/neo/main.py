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
class RelationshipProperties:
    """Properties for a relationship between nodes in the graph"""
    type: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    value: Optional[str] = field(default=None)
    weight: Optional[int] = field(default=None)

    @classmethod
    def from_dict(cls, data: dict) -> "RelationshipProperties":
        """Create a RelationshipProperties from a dictionary"""
        props = {}
        if data:
            for field_name in ["type", "name", "value", "weight"]:
                if field_name in data:
                    props[field_name] = data.pop(field_name)
        return cls(**props)


@object_type
class NeoService:
    """Neo4j service management and operations."""
    config: dict
    config_file: dagger.File
    password: dagger.Secret
    github_access_token: dagger.Secret
    neo_auth: dagger.Secret
    neo_service: Optional[dagger.Service] = None  # Store the service instance
    cypher_shell_client: Optional[dagger.Container] = None
    neo_data: dagger.CacheVolume

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("Path to YAML config file")],
        password: Annotated[dagger.Secret, Doc("Neo4j password")],
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token for cypher-shell repository")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j authentication string in the format 'username/password'")],
        neo_data: Annotated[dagger.CacheVolume, Doc("Neo4j data cache volume")],
    ):
        """ Create """
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(
            config=config_dict, password=password,
            github_access_token=github_access_token,
            neo_auth=neo_auth,
            config_file=config_file,
            neo_data=neo_data
        )

    @function
    async def create_neo_service(self) -> dagger.Service:
        """Create a Neo4j service as a Dagger service"""
        # Return existing service if we have one
        if self.neo_service:
            return self.neo_service

        self.config = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config
        plugin_string = json.dumps(
            self.config.neo4j.plugins) if self.config.neo4j.plugins else '[]'

        # Generate unique cache name - but only once per instance
        # unique_cache_name = f"{self.config.neo4j.cache_volume_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        print(
            green(f"Creating new Neo4j service with plugins: {plugin_string}"))
        self.neo_service = (
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
            .with_exposed_port(self.config.neo4j.http_port)  # HTTP interface
            .with_exposed_port(self.config.neo4j.bolt_port)  # Bolt protocol
            .with_mounted_cache(self.config.neo4j.data_volume_path, self.neo_data)
            .as_service()
            .with_hostname("neo")
        )

        return self.neo_service

    @function
    async def create_neo_client(self) -> dagger.Container:
        """Create a Neo4j client container with cypher-shell"""
        # Return existing client if we have one
        if self.cypher_shell_client:
            return self.cypher_shell_client

        self.config = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config

        # Get service first (reusing if available)
        neo_service = await self.create_neo_service()

        # Clone repository only once
        source = (
            await dag.git(url=self.config.neo4j.cypher_shell_repository, keep_git_dir=True)
            .with_auth_token(self.github_access_token)
            .branch("main")
            .tree()
        )

        # Build and configure client
        self.cypher_shell_client = dag.builder(self.config_file).build_cypher_shell(
            source=source,
        )

        self.cypher_shell_client = (
            self.cypher_shell_client
            .with_service_binding("neo", neo_service)
            .with_secret_variable("NEO4J_PASSWORD", self.password)
            .with_env_variable("NEO4J_USERNAME", self.config.neo4j.username)
        )

        return self.cypher_shell_client

    @function
    async def ensure_client(self) -> dagger.Container:
        """Ensure we have a client container, creating it if needed"""
        if not self.cypher_shell_client:
            self.cypher_shell_client = await self.create_neo_client()
        return self.cypher_shell_client

    @function
    async def run_query(self, query: str) -> str:
        """Run a query against the Neo4j service"""
        # Convert config dict to YAMLConfig object
        self.config: YAMLConfig = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config

        # Ensure client exists
        await self.ensure_client()

        # Write query to file
        client = (
            self.cypher_shell_client.with_new_file(
                "/tmp/query.cypher", query)
        )

        return await client.with_exec([
            "cypher-shell",
            "-a", self.config.neo4j.uri,
            "--non-interactive",
            "-f", "/tmp/query.cypher"
        ]).stdout()

    @function
    async def run_batch_queries(self, queries: List[str]) -> str:
        """Run multiple queries in a single transaction for better performance"""
        if not queries:
            return ""

        # Join queries with semicolons
        combined = ";\n".join(queries) + ";"

        # Run as a single operation
        return await self.run_query(combined)

    @function
    async def test_connection(self) -> str:
        """Test connection to Neo4j service using simple working queries"""
        logger = self._get_logger()

        self.config: YAMLConfig = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config

        await self.ensure_client()

        try:
            # Use the same simple queries that work in simple_test
            connection_result = await self.run_query("RETURN 'Connected' as status")
            total_nodes_raw = await self.run_query("MATCH (n) RETURN count(n)")
            total_rels_raw = await self.run_query("MATCH ()-[r]->() RETURN count(r)")

            # Get node type counts using simpler approach
            node_stats_raw = await self.run_query("CALL db.labels()")
            rel_stats_raw = await self.run_query("CALL db.relationshipTypes()")

            # Get sample relationships using a simpler query
            sample_rels_raw = await self.run_query("""
            MATCH (a)-[r]->(b) 
            RETURN type(r), labels(a)[0], labels(b)[0]
            LIMIT 15
            """)

            # Simple parsing functions that we know work
            def simple_parse(raw_output: str) -> str:
                lines = [line.strip()
                         for line in raw_output.strip().split('\n') if line.strip()]
                return lines[1] if len(lines) >= 2 else "0"

            def parse_list(raw_output: str) -> str:
                lines = [line.strip()
                         for line in raw_output.strip().split('\n') if line.strip()]
                if len(lines) > 1:
                    # Remove quotes and format nicely
                    items = [line.strip('"') for line in lines[1:]]
                    return '\n'.join(items)
                return "None found"

            def parse_sample_rels(raw_output: str) -> str:
                lines = [line.strip()
                         for line in raw_output.strip().split('\n') if line.strip()]
                if len(lines) > 1:
                    # Skip header, format relationship data
                    formatted = []
                    for line in lines[1:]:
                        # Simple space-split for the three columns
                        parts = line.split()
                        if len(parts) >= 3:
                            rel_type = parts[0].strip('"')
                            from_type = parts[1].strip('"')
                            to_type = parts[2].strip('"')
                            formatted.append(
                                f"{from_type} -[{rel_type}]-> {to_type}")
                        else:
                            formatted.append(line.strip('"'))
                    # Limit to 10 for readability
                    return '\n'.join(formatted[:10])
                return "No relationships found"

            # Get individual node type counts
            node_type_counts = {}
            node_types = parse_list(node_stats_raw).split('\n')
            for node_type in node_types:
                if node_type and node_type != "None found":
                    try:
                        count_raw = await self.run_query(f"MATCH (n:{node_type}) RETURN count(n)")
                        count = simple_parse(count_raw)
                        node_type_counts[node_type] = count
                    except:
                        node_type_counts[node_type] = "?"

            # Get individual relationship type counts
            rel_type_counts = {}
            rel_types = parse_list(rel_stats_raw).split('\n')
            for rel_type in rel_types:
                if rel_type and rel_type != "None found":
                    try:
                        count_raw = await self.run_query(f"MATCH ()-[r:{rel_type}]->() RETURN count(r)")
                        count = simple_parse(count_raw)
                        rel_type_counts[rel_type] = count
                    except:
                        rel_type_counts[rel_type] = "?"

            # Parse the basic results
            total_nodes = simple_parse(total_nodes_raw)
            total_rels = simple_parse(total_rels_raw)
            connection_status = simple_parse(connection_result).strip('"')
            sample_rels = parse_sample_rels(sample_rels_raw)

            # Format node type counts
            node_stats_formatted = []
            for node_type, count in node_type_counts.items():
                node_stats_formatted.append(f"{node_type}: {count}")
            node_stats = '\n'.join(
                node_stats_formatted) if node_stats_formatted else "No nodes found"

            # Format relationship type counts
            rel_stats_formatted = []
            for rel_type, count in rel_type_counts.items():
                rel_stats_formatted.append(f"{rel_type}: {count}")
            rel_stats = '\n'.join(
                rel_stats_formatted) if rel_stats_formatted else "No relationships found"

            # Format final report
            report = [
                "=== Neo4j Connection Test ===",
                f"Status: {connection_status}",
                "",
                "=== Total Counts ===",
                f"Nodes: {total_nodes}",
                f"Relationships: {total_rels}",
                "",
                "=== Node Types ===",
                node_stats,
                "",
                "=== Relationship Types ===",
                rel_stats,
                "",
                "=== Sample Relationships (max 15) ===",
                sample_rels
            ]

            return "\n".join(report)

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return f"Connection failed: {str(e)}"

    @function
    def connect(self) -> bool:
        """Verify connection to Neo4j"""
        # If we have a client container, connection is already verified
        if self.cypher_shell_client:
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
            # Convert config dict to YAMLConfig object
            self.config: YAMLConfig = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config

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

    @function
    async def add_relationship(
        self,
        start_filepath: str,
        relationship_type: str,
        end_filepath: str,
        properties: Optional[RelationshipProperties] = None
    ) -> bool:
        """Add a relationship between two files in the graph"""
        try:
            self.config = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config

            # Escape strings
            start_filepath = start_filepath.replace('"', '\\"')
            end_filepath = end_filepath.replace('"', '\\"')
            relationship_type = relationship_type.upper()

            # Build properties string if provided
            props_str = ""
            if properties:
                props_parts = []

                # Handle each property directly
                if properties.type:
                    props_parts.append(
                        f'type: "{properties.type.replace('"', '\\"')}"')
                if properties.name:
                    props_parts.append(
                        f'name: "{properties.name.replace('"', '\\"')}"')
                if properties.value:
                    props_parts.append(
                        f'value: "{properties.value.replace('"', '\\"')}"')
                if properties.weight:
                    props_parts.append(f'weight: {properties.weight}')

                if props_parts:
                    props_str = f" {{{', '.join(props_parts)}}}"

            # Build and execute query
            query = f'''
            MATCH (a:File {{filepath: "{start_filepath}"}}), (b:File {{filepath: "{end_filepath}"}})
            MERGE (a)-[r:{relationship_type}{props_str}]->(b)
            RETURN type(r) as relationship
            '''

            await self.run_query(query)
            return True
        except Exception as e:
            logger = self._get_logger()
            logger.error(
                f"Failed to add relationship from {start_filepath} to {end_filepath}: {e}")
            return False

    @function
    async def debug_database(self) -> str:
        """Debug function to see raw query outputs"""
        logger = self._get_logger()
        await self.ensure_client()

        try:
            # Run simple queries and return raw output
            count_query = "MATCH (n) RETURN count(n)"
            raw_count = await self.run_query(count_query)

            labels_query = "CALL db.labels()"
            raw_labels = await self.run_query(labels_query)

            rel_types_query = "CALL db.relationshipTypes()"
            raw_rel_types = await self.run_query(rel_types_query)

            # Return everything for debugging
            return f"""
=== DEBUG DATABASE ===

Count Query: {count_query}
Raw Count Output:
{raw_count}

Labels Query: {labels_query}
Raw Labels Output:
{raw_labels}

Relationship Types Query: {rel_types_query}
Raw Relationship Types Output:
{raw_rel_types}
"""

        except Exception as e:
            return f"Debug failed: {str(e)}"

    @function
    async def simple_test(self) -> str:
        """Simple test using the same queries as debug_database"""
        try:
            await self.ensure_client()

            # Use the exact same queries that work in debug_database
            count_result = await self.run_query("MATCH (n) RETURN count(n)")
            labels_result = await self.run_query("CALL db.labels()")
            rel_types_result = await self.run_query("CALL db.relationshipTypes()")

            # Simple parsing - just take the second line
            def simple_parse(raw_output: str) -> str:
                lines = [line.strip()
                         for line in raw_output.strip().split('\n') if line.strip()]
                return lines[1] if len(lines) >= 2 else "0"

            def parse_list(raw_output: str) -> str:
                lines = [line.strip()
                         for line in raw_output.strip().split('\n') if line.strip()]
                # Skip header, return the rest
                if len(lines) > 1:
                    return '\n'.join(lines[1:])
                return "None found"

            node_count = simple_parse(count_result)
            node_types = parse_list(labels_result)
            rel_types = parse_list(rel_types_result)

            return f"""
=== Simple Neo4j Test ===
Node Count: {node_count}

Node Types:
{node_types}

Relationship Types:
{rel_types}
"""

        except Exception as e:
            return f"Simple test failed: {str(e)}"

    def _get_logger(self):
        """Get a logger for this service"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger("neo4j.service")

import logging

import dagger
from dagger import dag


class Neo4jService:
    """Neo4j service management and operations."""

    @staticmethod
    def create_neo4j_service() -> dagger.Service:
        """Create a Neo4j service as a Dagger service"""
        return (
            dag.container()
            .from_("neo4j:2025.05")
            .with_env_variable("NEO4J_AUTH", "neo4j/devpassword")
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

    @staticmethod
    async def create_neo4j_client(
        config_file: dagger.File,
        cypher_shell_repo: str,
        github_access_token: dagger.Secret
    ) -> dagger.Container:
        """Create a Neo4j client container with cypher-shell"""
        source = (
            await dag.git(url=cypher_shell_repo, keep_git_dir=True)
            .with_auth_token(github_access_token)
            .branch("main")
            .tree()
        )
        cypher_cli = dag.builder(config_file).build_cypher_shell(
            source=source,
        )

        return (
            cypher_cli
            .with_service_binding("neo", Neo4jService.create_neo4j_service())
        )

    @staticmethod
    async def run_query(
        config_file: dagger.File,
        query: str,
        cypher_shell_repo: str,
        github_access_token: dagger.Secret
    ) -> str:
        """Run a query against the Neo4j service"""
        # Create client with service binding
        client = await Neo4jService.create_neo4j_client(
            config_file=config_file,
            cypher_shell_repo=cypher_shell_repo,
            github_access_token=github_access_token
        )

        # Write query to file
        client = client.with_new_file("/tmp/query.cypher", query)

        # Run query using cypher-shell
        return await client.with_exec([
            "cypher-shell",
            "-a", "neo4j://neo:7687",
            "-u", "neo4j",
            "-p", "devpassword",
            "--non-interactive",
            "-f", "/tmp/query.cypher"
        ]).stdout()

    @staticmethod
    async def test_connection(
        config_file: dagger.File,
        cypher_shell_repo: str,
        github_access_token: dagger.Secret
    ) -> str:
        """Test connection to Neo4j service"""
        return await Neo4jService.run_query(
            config_file=config_file,
            query="RETURN 'Connected' AS result",
            cypher_shell_repo=cypher_shell_repo,
            github_access_token=github_access_token
        )

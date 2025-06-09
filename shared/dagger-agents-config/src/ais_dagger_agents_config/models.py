from typing import List, NamedTuple, Optional

import dagger
from dagger import object_type
from pydantic import BaseModel, EmailStr, Field


@object_type
class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: dagger.Secret


class ContainerConfig(BaseModel):
    """Container configuration."""
    work_dir: str = Field(
        default="/src", description="Working directory in container")
    docker_file_path: Optional[str] = Field(
        default=None, description="Path to Dockerfile")


class GitConfig(BaseModel):
    """Git configuration."""
    user_name: str = Field(description="Git user name")
    user_email: EmailStr = Field(description="Git user email")


class ConcurrencyConfig(BaseModel):
    """Configuration for controlling concurrency across operations."""
    batch_size: int = Field(default=5, description="Files per batch")
    max_concurrent: int = Field(
        default=5, description="Max concurrent operations")
    embedding_batch_size: int = Field(
        default=10, description="Embeddings per batch")


class IndexingConfig(BaseModel):
    """Code indexing configuration."""
    max_semantic_chunk_lines: int = Field(
        default=200, description="Max lines per semantic chunk")
    chunk_size: int = Field(default=50, description="Fallback chunk size")
    max_file_size: int = Field(
        default=1_000_000, description="Max file size to process")
    embedding_model: str = Field(
        default="text-embedding-3-small", description="Embedding model")
    file_extensions: List[str] = Field(
        default=["py", "js", "ts", "java", "c", "cpp", "go", "rs"],
        description="File extensions to process"
    )
    max_files: int = Field(default=50, description="Maximum files to process")
    skip_indexing: bool = Field(
        default=False, description="Skip indexing if true"
    )
    concurrency: ConcurrencyConfig = Field(
        default_factory=ConcurrencyConfig,
        description="Concurrency settings"
    )

    # For backward compatibility - these properties delegate to concurrency config
    @property
    def batch_size(self) -> int:
        """Returns batch size from concurrency config."""
        return self.concurrency.batch_size

    @property
    def max_concurrent(self) -> int:
        """Returns max concurrent from concurrency config."""
        return self.concurrency.max_concurrent

    @property
    def embedding_batch_size(self) -> int:
        """Returns embedding batch size from concurrency config."""
        return self.concurrency.embedding_batch_size


class TestGenerationConfig(BaseModel):
    """Test generation configuration with optional fields."""
    limit: Optional[int] = Field(
        default=None, description="Optional limit for test generation")
    test_directory: Optional[str] = Field(
        default=None, description="Directory where tests will be generated"
    )
    test_suffix: Optional[str] = Field(
        default=None, description="Suffix for generated test files")
    save_next_to_code_under_test: Optional[bool] = Field(
        default=None, description="Save next to code under test"
    )


class ReporterConfig(BaseModel):
    """Reporter configuration with all optional fields."""
    name: Optional[str] = Field(
        default=None, description="The name of the reporter, e.g., 'jest'")
    command: Optional[str] = Field(
        default=None, description="The command to run tests with coverage")
    report_directory: Optional[str] = Field(
        default=None, description="The directory where coverage reports are saved"
    )
    output_file_path: Optional[str] = Field(
        default=None, description="The path to the JSON output file for test results"
    )
    # Add new fields to support file-specific test commands
    file_test_command_template: Optional[str] = Field(
        default=None, description="Template for running tests on a specific file (use {file} as placeholder)"
    )
    test_timeout_seconds: int = Field(
        default=60, description="Maximum time to wait for tests to complete"
    )


class CoreAPIConfig(BaseModel):
    """Core API configuration with optional fields."""
    model: Optional[str] = Field(
        default=None, description="Model to use for core operations")
    provider: Optional[str] = Field(
        default=None, description="Provider for the core API, e.g., 'openai'")
    fallback_models: List[str] = Field(
        default_factory=list,
        description="List of fallback models for the core API"
    )


class Neo4jConfig(BaseModel):
    """Neo4j connection configuration"""
    # Connection details
    uri: str = Field(default="neo4j://neo:7687",
                     description="Neo4j connection URI")
    username: str = Field(default="neo4j", description="Neo4j username")
    password: dagger.Secret = Field(description="Neo4j password")
    database: str = Field(default="code", description="Neo4j database name")
    enabled: bool = Field(
        default=True, description="Whether Neo4j integration is enabled")

    # Repository settings
    cypher_shell_repository: str = Field(
        default="https://github.com/Ai-Agency-Services/cypher-shell.git",
        description="Repository URL for Cypher shell"
    )

    # Service configuration
    http_port: int = Field(default=7474, description="Neo4j HTTP port")
    bolt_port: int = Field(
        default=7687, description="Neo4j Bolt protocol port")
    data_volume_path: str = Field(
        default="/data", description="Path for Neo4j data volume")
    cache_volume_name: str = Field(
        default="neo4j-data", description="Name of cache volume for Neo4j data")

    # Plugins and capabilities
    plugins: List[str] = Field(
        default=["apoc"], description="Neo4j plugins to enable")

    # APOC settings
    apoc_export_file_enabled: bool = Field(
        default=True, description="Enable APOC file export")
    apoc_import_file_enabled: bool = Field(
        default=True, description="Enable APOC file import")
    apoc_import_use_neo4j_config: bool = Field(
        default=True, description="Use Neo4j config for APOC import")

    # Memory settings
    memory_pagecache_size: str = Field(
        default="1G", description="Neo4j page cache size")
    memory_heap_initial_size: str = Field(
        default="1G", description="Neo4j initial heap size")
    memory_heap_max_size: str = Field(
        default="1G", description="Neo4j maximum heap size")


class YAMLConfig(BaseModel):
    """Main configuration model."""
    container: ContainerConfig
    git: GitConfig
    concurrency: Optional[ConcurrencyConfig] = Field(
        default_factory=ConcurrencyConfig)
    indexing: Optional[IndexingConfig] = Field(default_factory=IndexingConfig)
    test_generation: Optional[TestGenerationConfig] = Field(default=None)
    reporter: Optional[ReporterConfig] = Field(default=None)
    core_api: Optional[CoreAPIConfig] = Field(default=None)
    neo4j: Optional['Neo4jConfig'] = None

    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for flexibility

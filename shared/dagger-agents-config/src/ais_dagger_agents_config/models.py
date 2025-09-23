import json
from typing import List, NamedTuple, Optional

import dagger
from dagger import field, object_type
from pydantic import BaseModel, EmailStr, Field


@object_type
class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: dagger.Secret


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
    base_pull_request_branch: str = Field(
        description="Base branch for pull requests")


class ConcurrencyConfig(BaseModel):
    """Configuration for controlling concurrency across operations."""
    batch_size: int = Field(default=5, description="Files per batch")
    max_concurrent: int = Field(
        default=5, description="Max concurrent operations")
    embedding_batch_size: int = Field(
        default=10, description="Embeddings per batch")


class IndexingConfig(BaseModel):
    """Code indexing configuration."""
    clear_on_start: bool = Field(
        default=True, description="Clear existing index on start")
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
    ignore_directories: List[str] = Field(
        default_factory=lambda: [
            "node_modules", "build", "dist", "target", ".git", "bin", "obj",
            "__pycache__", ".venv", "venv", "vendor", "out", ".idea",
            ".vscode", "coverage", "sdk"
        ],
        description="Directory names to ignore during scanning and parsing"
    )
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


# --- Add Smell configuration models ---
class SmellThresholdsConfig(BaseModel):
    """Global thresholds for smell detectors."""
    long_function_lines: int = Field(default=120, description="Minimum span (lines) for Long Functions")
    long_param_count: int = Field(default=6, description="Minimum param count for Long Parameter List")
    large_class_loc: int = Field(default=200, description="Minimum LOC for Large Class by LOC")
    god_class_methods: int = Field(default=20, description="Minimum methods for God Class by methods")
    high_fan_out: int = Field(default=20, description="Minimum imports for High Fan-Out")
    high_fan_in: int = Field(default=10, description="Minimum inbound imports for High Fan-In")


class SmellDetectorsConfig(BaseModel):
    """Include/exclude configuration for smell detectors."""
    include: List[str] = Field(default_factory=list, description="Only run these detectors (empty = all)")
    exclude: List[str] = Field(default_factory=list, description="Always exclude these detectors")


class SmellConfig(BaseModel):
    """Top-level smell configuration."""
    thresholds: SmellThresholdsConfig = Field(default_factory=SmellThresholdsConfig)
    detectors: SmellDetectorsConfig = Field(default_factory=SmellDetectorsConfig)


class CoreAPIConfig(BaseModel):
    """Core API configuration with optional fields."""
    model: Optional[str] = Field(
        default=None, description="Model to use for core operations")
    fqdn: Optional[str] = Field(
        default=None, description="Fully qualified domain name for the core API")
    provider: Optional[str] = Field(
        default=None, description="Provider for the core API, e.g., 'openai'")
    fallback_models: List[str] = Field(
        default_factory=list,
        description="List of fallback models for the core API"
    )


class Neo4jConfig(BaseModel):
    """Neo4j connection configuration"""
    # Connection details
    image: str = Field(
        default="neo4j:2025.05", description="Docker image for Neo4j")
    uri: str = Field(default="neo4j://neo:7687",
                     description="Neo4j connection URI")
    username: str = Field(default="neo4j", description="Neo4j username")
    database: str = Field(default="code", description="Neo4j database name")
    clear_on_start: bool = Field(
        default=True, description="Clear existing database on start")
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

    # APOC settings environment variables must be strings
    apoc_export_file_enabled: str = Field(
        default="true", description="Enable APOC file export")
    apoc_import_file_enabled: str = Field(
        default="true", description="Enable APOC file import")
    apoc_import_use_neo4j_config: str = Field(
        default="true", description="Use Neo4j config for APOC import")

    # Memory settings
    memory_pagecache_size: str = Field(
        default="1G", description="Neo4j page cache size")
    memory_heap_initial_size: str = Field(
        default="1G", description="Neo4j initial heap size")
    memory_heap_max_size: str = Field(
        default="1G", description="Neo4j maximum heap size")
    # Transaction timeout (ISO-8601 duration, e.g., PT120S)
    transaction_timeout: str = Field(
        default="PT120S", description="Default transaction timeout (e.g., PT120S)")


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
    neo4j: Optional[Neo4jConfig] = Field(default=None)
    # Add smell configuration (optional)
    smell: Optional[SmellConfig] = Field(default=None, description="Smell detection thresholds and detector filters")

    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for flexibility


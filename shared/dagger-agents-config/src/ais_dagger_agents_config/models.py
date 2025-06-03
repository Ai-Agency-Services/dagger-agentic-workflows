from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr


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


class YAMLConfig(BaseModel):
    """Main configuration model."""
    container: ContainerConfig
    git: GitConfig
    concurrency: Optional[ConcurrencyConfig] = Field(default_factory=ConcurrencyConfig)
    indexing: Optional[IndexingConfig] = Field(default_factory=IndexingConfig)
    test_generation: Optional[TestGenerationConfig] = Field(default=None)
    reporter: Optional[ReporterConfig] = Field(default=None)
    core_api: Optional[CoreAPIConfig] = Field(default=None)

    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for flexibility

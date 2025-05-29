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


class IndexingConfig(BaseModel):
    """Code indexing configuration."""
    max_semantic_chunk_lines: int = Field(
        default=200, description="Max lines per semantic chunk")
    chunk_size: int = Field(default=50, description="Fallback chunk size")
    max_file_size: int = Field(
        default=1_000_000, description="Max file size to process")
    batch_size: int = Field(default=5, description="Files per batch")
    max_concurrent: int = Field(
        default=5, description="Max concurrent operations")
    embedding_model: str = Field(
        default="text-embedding-3-small", description="Embedding model")
    embedding_batch_size: int = Field(
        default=10, description="Embeddings per batch")
    file_extensions: List[str] = Field(
        default=["py", "js", "ts", "java", "c", "cpp", "go", "rs"],
        description="File extensions to process"
    )
    max_files: int = Field(default=50, description="Maximum files to process")
    skip_indexing: bool = Field(
        default=False, description="Skip indexing if true"
    )


class TestGenerationConfig(BaseModel):
    limit: Optional[int] = Field(
        default=None, description="Optional limit for test generation")  # Make limit optional
    test_directory: str = Field(
        ..., description="Directory where tests will be generated"
    )
    test_suffix: str = Field(...,
                             description="Suffix for generated test files")
    save_next_to_code_under_test: bool = Field(
        ..., description="Save next to code under test"
    )


class ReporterConfig(BaseModel):
    """Reporter configuration."""
    name: str = Field(...,
                      description="The name of the reporter, e.g., 'jest'")
    command: str = Field(...,
                         description="The command to run tests with coverage")
    report_directory: str = Field(
        ..., description="The directory where coverage reports are saved"
    )
    output_file_path: str = Field(
        ..., description="The path to the JSON output file for test results"
    )


class CoreAPIConfig(BaseModel):
    """Core API configuration."""
    model: str = Field(description="Model to use for core operations")
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
    indexing: IndexingConfig = Field(default_factory=IndexingConfig)
    test_generation: TestGenerationConfig
    reporter: ReporterConfig
    core_api: CoreAPIConfig

    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for flexibility

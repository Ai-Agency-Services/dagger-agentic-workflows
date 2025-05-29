"""Shared configuration models using Pydantic."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ContainerConfig(BaseModel):
    """Container configuration."""
    work_dir: str = Field(default="/src", description="Working directory in container")
    docker_file_path: Optional[str] = Field(default=None, description="Path to Dockerfile")


class GitConfig(BaseModel):
    """Git configuration."""
    user_name: str = Field(description="Git user name")
    user_email: str = Field(description="Git user email")


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = Field(description="LLM provider (openai, openrouter, etc.)")
    model_name: str = Field(description="Model name to use")


class IndexingConfig(BaseModel):
    """Code indexing configuration."""
    max_semantic_chunk_lines: int = Field(default=200, description="Max lines per semantic chunk")
    chunk_size: int = Field(default=50, description="Fallback chunk size")
    max_file_size: int = Field(default=1_000_000, description="Max file size to process")
    batch_size: int = Field(default=5, description="Files per batch")
    max_concurrent: int = Field(default=5, description="Max concurrent operations")
    embedding_model: str = Field(default="text-embedding-3-small", description="Embedding model")
    embedding_batch_size: int = Field(default=10, description="Embeddings per batch")


class GenerationConfig(BaseModel):
    """Test generation configuration."""
    file_extensions: List[str] = Field(
        default=["py", "js", "ts", "java", "c", "cpp", "go", "rs"],
        description="File extensions to process"
    )
    max_files: int = Field(default=50, description="Maximum files to process")


class ReporterConfig(BaseModel):
    """Reporter configuration."""
    command: str = Field(description="Command to run for reporting")


class CoreAPIConfig(BaseModel):
    """Core API configuration."""
    model: str = Field(description="Model to use for core operations")


class YAMLConfig(BaseModel):
    """Main configuration model."""
    container: ContainerConfig
    git: GitConfig
    llm: LLMConfig
    indexing: IndexingConfig = Field(default_factory=IndexingConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    test_generation: GenerationConfig = Field(default_factory=GenerationConfig)  # Alias for backward compatibility
    reporter: ReporterConfig
    core_api: CoreAPIConfig

    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for flexibility
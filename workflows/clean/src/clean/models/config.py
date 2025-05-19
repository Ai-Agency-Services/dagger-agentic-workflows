from typing import Optional, Dict
from pydantic import BaseModel, Field, EmailStr


class IndexingConfig(BaseModel):
    skip_indexing: bool = False
    chunk_size: int = 50  # This will be used as fallback_chunk_size
    max_semantic_chunk_lines: int = 200  # Max lines for a semantic chunk


class GenerationConfig(BaseModel):
    max_files: int = Field(
        5, description="Maximum number of files to refactor"
    )


class ContainerConfig(BaseModel):
    work_dir: str = Field(...,
                          description="Working directory for test generation")
    docker_file_path: str = Field(
        ..., description="Path to the Dockerfile for the container"
    )


class GitConfig(BaseModel):
    user_name: str = Field(..., description="Username for commit author")
    user_email: EmailStr = Field(..., description="Email for commit author")


class LLMConfig(BaseModel):
    provider: str = Field(...,
                          description="LLM provider ('openrouter' or 'openai')")
    model_name: str = Field(
        ..., description="LLM model name (e.g., 'openai/gpt-4o', 'anthropic/claude-3.5-sonnet')"
    )


class YAMLConfig(BaseModel):
    git: GitConfig
    container: ContainerConfig
    llm: LLMConfig
    generation: GenerationConfig
    indexing: IndexingConfig = IndexingConfig()

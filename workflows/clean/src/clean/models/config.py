from pydantic import BaseModel, Field, EmailStr


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
    open_router_api_key: str = Field(
        ..., description="OpenRouter API key (required if provider is 'openrouter')"
    )
    model_name: str = Field(
        ..., description="LLM model name (e.g., 'openai/gpt-4o', 'anthropic/claude-3.5-sonnet')"
    )
    openai_api_key: str = Field(
        ..., description="OpenAI API key (required if provider is 'openai')"
    )


class YAMLConfig(BaseModel):
    git: GitConfig
    container: ContainerConfig
    llm: LLMConfig
    generation: GenerationConfig

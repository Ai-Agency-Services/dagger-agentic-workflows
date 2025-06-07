from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional  # Import Optional


class ReporterConfig(BaseModel):
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
    model: str = Field(
        ..., description="The model identifier for core API, e.g., 'gpt-4o-2024-08-06'"
    )
    fallback_models: list[str] = Field(
        default_factory=list,
        description="List of fallback models for the core API"
    )


class TestGenerationConfig(BaseModel):
    iterations: int = Field(...,
                            description="Number of iterations for test generation")
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


class ContainerConfig(BaseModel):
    work_dir: str = Field(...,
                          description="Working directory for test generation")
    docker_file_path: str = Field(
        ..., description="Path to the Dockerfile for the container"
    )


class GitConfig(BaseModel):
    user_name: str = Field(..., description="Username for commit author")
    user_email: EmailStr = Field(..., description="Email for commit author")


class YAMLConfig(BaseModel):
    reporter: ReporterConfig
    core_api: CoreAPIConfig
    test_generation: TestGenerationConfig
    git: GitConfig
    container: ContainerConfig

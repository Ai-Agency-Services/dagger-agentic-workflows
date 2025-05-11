import json
import os
from typing import List, NamedTuple, Optional, Tuple

import dagger
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from simple_chalk import green, red

from .models.coverage_report import CoverageReport


def base_file_name(file_path: str, test_suffix: str):
    base_name = os.path.basename(file_path)
    file_name, file_extension = os.path.splitext(base_name)
    path = f"{file_name}.{test_suffix}{file_extension}"
    return path


def dagger_json_file_to_pydantic(json_file: dagger.File, pydantic_model: type) -> List:
    """
    Convert a Dagger JSON file to a list of Pydantic models.

    Args:
    json_file (dagger.File): The Dagger JSON file to convert.
    pydantic_model (type): The Pydantic model class to use for conversion.

    Returns:
    List: A list of Pydantic models.
    """

    async def convert():
        # Read the contents of the JSON file
        json_content = await json_file.contents()

        # Deserialize JSON content into a list of dictionaries
        data_list = json.loads(json_content)

        # Convert dictionaries back into Pydantic models
        return [pydantic_model.model_validate(item) for item in data_list]

    return convert()


def generate_code(code_module):
    """
    Combine the imports and code from a code module into a single string.

    Args:
        code_module: An object with `imports` and `code` attributes.

    Returns:
        str: The combined code as a string.
    """
    return f"{code_module.imports}\n{code_module.code}"


async def get_code_under_test_directory(
    test_container: dagger.Container, report: CoverageReport
) -> str:
    """
    Get the directory where the code under test is located, excluding common
    dependency, build, config, and temporary directories.

    Args:
    test_container (dagger.Container): The test container.
    report (CoverageReport): The coverage report containing the target file name.

    Returns:
    str: The directory where the code under test is located. Returns '.' if not found
         or if multiple locations are found outside excluded paths.
    """

    # Comprehensive list of paths/patterns to exclude
    exclude_paths = [
        # Version Control
        "./.git",
        "./.hg",
        "./.svn",
        # Node.js
        "./node_modules",
        # Python
        "./venv",
        "./.venv",
        "./env",
        "./.env",
        "./__pycache__",
        "./*.pyc",
        "./*.pyo",
        "./.pytest_cache",
        "./.mypy_cache",
        "./build",
        "./dist",
        "./*.egg-info",
        # Go
        "./vendor",
        # Java / JVM
        "./target",  # Maven, sbt
        "./build",  # Gradle
        "./out",  # IntelliJ
        "./bin",  # Often compiled output
        "./.gradle",
        # Ruby
        "./vendor/bundle",
        "./tmp",
        "./log",
        # PHP
        "./vendor",
        # .NET
        "./bin",
        "./obj",
        # General Build/Dist Artifacts
        "./dist",
        "./build",
        "./out",
        "./bin",
        "./release",
        "./coverage",
        "./*.log",
        "./logs",
        # IDE/Editor specific
        "./.idea",
        "./.vscode",
        "./*.swp",
        "./*.swo",
        # OS specific
        "./.DS_Store",
        "./Thumbs.db",
        # Config / Secrets (less likely to contain source, but good to exclude)
        "./config",
        "./secrets",
        "./*.pem",
        "./*.key",
    ]

    find_command = ["find", "."]

    # Add exclusion rules: -path <exclude_path> -prune -o
    # Note: -path matches the whole path string, not just directory names
    # So './build' excludes anything starting with './build/'
    for exclude_path in exclude_paths:
        # Handle simple wildcards like *.pyc - use -name instead of -path
        if "*" in os.path.basename(exclude_path) and "/" not in exclude_path.strip('./'):
            find_command.extend(
                ["-name", exclude_path.strip('./'), "-prune", "-o"])
        else:
            find_command.extend(["-path", exclude_path, "-prune", "-o"])

    # Add the main search criteria: -type f -name <filename> -exec dirname {} \;
    find_command.extend([
        "-type", "f",
        "-name", f"{report.file}",
        "-exec", "dirname", "{}", ";",
    ])

    try:
        # print(f"Executing find command: {' '.join(find_command)}") # Uncomment for debugging
        result_container = test_container.with_exec(find_command)
        stdout = await result_container.stdout()
        stderr = await result_container.stderr()  # Capture stderr for debugging

        if stderr:
            print(red(f"Find command stderr: {stderr.strip()}"))

        # Process stdout: Split lines, remove duplicates and empty lines
        potential_dirs = list(set(filter(None, stdout.strip().split('\n'))))

        if not potential_dirs:
            print(red(
                f"Could not find directory for file: {report.file} (excluding specified paths)"))
            return "."  # Default to current directory if not found
        elif len(potential_dirs) > 1:
            # If multiple found, try to prefer paths containing 'src' or 'lib'
            preferred_dirs = [
                d for d in potential_dirs if '/src' in d or '/lib' in d]
            if preferred_dirs:
                code_under_test_dir = preferred_dirs[0]
                if len(preferred_dirs) > 1:
                    print(red(
                        f"Found multiple preferred directories for {report.file}: {preferred_dirs}. Returning first: {code_under_test_dir}"))
                else:
                    print(
                        f"Found multiple directories for {report.file}, choosing preferred: {code_under_test_dir}")

            else:
                # Fallback to first match
                code_under_test_dir = potential_dirs[0]
                print(red(
                    f"Found multiple possible directories for {report.file}: {potential_dirs}. No preferred ('src', 'lib'). Returning first match: {code_under_test_dir}"))
        else:
            code_under_test_dir = potential_dirs[0]

        return code_under_test_dir

    except Exception as e:
        print(red(f"Error executing find command: {e}"))
        return "."  # Default to current directory on error


def rank_reports_by_coverage(coverage_reports: List[CoverageReport]) -> List[CoverageReport]:
    """
    Rank the modules based on the lack of coverage calculated by analyzing the statement, branches, and function percentages.
    """
    # Debug before filtering
    print(f"Total reports before filtering: {len(coverage_reports)}")

    # Files with coverage >= this threshold will be considered "fully covered"
    COVERAGE_THRESHOLD = 99.9

    # Filter out modules with coverage at or above threshold
    filtered_modules = [
        module for module in coverage_reports if module.coverage_percentage < COVERAGE_THRESHOLD
    ]

    # Debug after filtering
    print(
        f"Reports after filtering files with ≥{COVERAGE_THRESHOLD}% coverage: {len(filtered_modules)}")

    # Sort the files based on coverage_percentage in ascending order (lowest coverage first)
    sorted_modules = sorted(
        filtered_modules, key=lambda x: x.coverage_percentage)

    # Print top 5 files to be processed
    if sorted_modules:
        print("Top 5 files to process:")
        for i, module in enumerate(sorted_modules[:5]):
            print(f"  {i+1}. {module.file}: {module.coverage_percentage}%")

    return sorted_modules


class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: str


async def get_llm_credentials(
    provider: str,
    open_router_key: Optional[dagger.Secret],
    openai_key: Optional[dagger.Secret],
) -> LLMCredentials:
    """
    Determines the LLM base URL and retrieves the plaintext API key based on the provider.

    Args:
        provider: The name of the LLM provider ('openrouter' or 'openai').
        open_router_key: The Dagger secret for the OpenRouter API key.
        openai_key: The Dagger secret for the OpenAI API key.

    Returns:
        A tuple containing (base_url, api_key_plain).
        base_url is None for OpenAI default.

    Raises:
        ValueError: If the provider is unsupported or the required key is missing.
    """
    base_url: Optional[str] = None
    api_key_secret: Optional[dagger.Secret] = None

    if provider == "openrouter":
        if not open_router_key:
            raise ValueError(
                "open_router_api_key is required for provider 'openrouter'")
        base_url = "https://openrouter.ai/api/v1"
        api_key_secret = open_router_key
        print("Using OpenRouter provider.")
    elif provider == "openai":
        if not openai_key:
            raise ValueError(
                "openai_api_key is required for provider 'openai'")
        base_url = None  # OpenAIProvider uses default if None
        api_key_secret = openai_key
        print("Using OpenAI provider.")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    # Retrieve plaintext key - this will implicitly check if the secret was assigned
    if not api_key_secret:
        # Should be caught by provider checks, but defensive programming
        raise ValueError(
            f"API key secret not found for provider '{provider}'.")

    api_key_plain = await api_key_secret.plaintext()
    if not api_key_plain:  # Extra check in case plaintext() returns empty
        raise ValueError(
            f"Failed to retrieve plaintext API key for provider '{provider}'.")

    return LLMCredentials(base_url=base_url, api_key=api_key_plain)


def create_llm_model(
    api_key: str,
    base_url: Optional[str],
    model_name: str
) -> OpenAIModel:
    """
    Creates the Pydantic AI model instance (currently OpenAIModel).

    Args:
        api_key: The plaintext API key.
        base_url: The base URL for the API (None for OpenAI default).
        model_name: The specific model name to use.

    Returns:
        An instance of OpenAIModel.

    Raises:
        Exception: If initialization of the provider or model fails.
    """
    try:
        llm_provider = OpenAIProvider(api_key=api_key, base_url=base_url)
        # Determine effective base URL for logging
        # Assuming default
        effective_base_url = base_url if base_url else "https://api.openai.com/v1"
        pydantic_ai_model = OpenAIModel(
            model_name=model_name, provider=llm_provider)
        print(
            f"Pydantic AI Model created for '{model_name}' using effective base URL: {effective_base_url}")
        return pydantic_ai_model
    except Exception as e:
        print(red(f"Failed to initialize Pydantic AI Provider/Model: {e}"))
        raise  # Re-raise the exception to be handled by the caller

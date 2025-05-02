import os
from typing import Annotated, Optional, List  # Added List

import dagger
from dagger import Doc, dag, function, object_type

from coverage_agent.core.llm_service import BaseLLMService, OpenAIService, OpenRouterService


@object_type
class CoverageAgent:
    """Coverage agent to generate unit tests for a given repository."""

    @function
    async def generate_unit_tests(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to generate tests for")],
        branch: Annotated[str, Doc("Branch to generate tests for")],
        config: Annotated[dagger.File, Doc("Path to the configuration file")],
        dockerfile_path: Annotated[str, Doc("Dockerfile path for test container")],
        model: Annotated[str, Doc("Primary LLM model to use (e.g., 'openai/gpt-4o')")],
        provider: Annotated[str, Doc(
            "LLM provider ('openrouter' or 'openai')")] = "openrouter",
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key (required if provider is 'openrouter')")] = None,
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key (required if provider is 'openai')")] = None,
        fallback_models: Annotated[Optional[List[str]], Doc(
            "Optional: List of fallback model names for OpenRouter (e.g., ['anthropic/claude-3.5-sonnet'])"
        )] = None,


    ) -> Optional[dagger.Container]:  # Consider returning generated files or status
        """Generate unit tests for a given repository using the specified LLM provider."""

        service: BaseLLMService
        api_key_secret: Optional[dagger.Secret] = None

        if provider == "openrouter":
            if not open_router_api_key:
                raise ValueError(
                    "open_router_api_key is required for provider 'openrouter'")
            api_key_secret = open_router_api_key
            os.environ["OPEN_ROUTER_API_KEY"] = await api_key_secret.plaintext()
            service = OpenRouterService()
        elif provider == "openai":
            if not openai_api_key:
                raise ValueError(
                    "openai_api_key is required for provider 'openai'")
            api_key_secret = openai_api_key
            os.environ["OPENAI_API_KEY"] = await api_key_secret.plaintext()
            service = OpenAIService()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        source_tree = (
            await dag.git(url=repository_url, keep_git_dir=True)
            .with_auth_token(github_access_token)
            .branch(branch)
            .tree()
        )

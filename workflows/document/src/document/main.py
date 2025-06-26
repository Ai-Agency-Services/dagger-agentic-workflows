import logging
import traceback
from typing import Annotated, Optional

import dagger
import yaml
from ais_dagger_agents_config import YAMLConfig
from dagger import DaggerError, Doc, dag, function, object_type
from document.core.documenter_agent import (
    DocumenterAgentDependencies, 
    create_documenter_agent
)
from document.utils import create_llm_model, get_llm_credentials
from pydantic_ai import UnexpectedModelBehavior
from simple_chalk import green, red, yellow


@object_type
class Document:
    """Documentation generator agent for Python codebases."""
    config: dict
    config_file: dagger.File
    container: Optional[dagger.Container] = None

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to config file")]):
        """Create a new Document workflow instance."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, config_file=config_file)
    
    @function
    async def setup_environment(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to generate tests for")],
        branch: Annotated[str, Doc("Branch to generate tests for")],
        model_name: Annotated[str, Doc(
            "LLM model name (e.g., 'openai/gpt-4o', 'anthropic/claude-3.5-sonnet')")] = "openai/gpt-4.1-nano",
        provider: Annotated[str, Doc(
            "LLM provider ('openrouter' or 'openai')")] = "openrouter",
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key (required if provider is 'openrouter')")] = None,
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key (required if provider is 'openai')")] = None
    ) -> dagger.Container:
        """Set up the test environment and return a ready-to-use container."""
        try:
            self.github_token = github_access_token
            self.open_router_api_key = open_router_api_key
            self.openai_api_key = openai_api_key
            self.config: YAMLConfig = YAMLConfig(**self.config)
            self.model = model_name
            # We no longer store github_token as a member variable

            # Setup repository
            source = (
                await dag.git(url=repository_url, keep_git_dir=True)
                .with_auth_token(github_access_token)
                .branch(branch)
                .tree()
            )

            # Build test container
            self.container = await dag.builder(self.config_file).build_test_environment(
                source=source,
                dockerfile_path=self.config.container.docker_file_path,
                open_router_api_key=open_router_api_key,
                openai_api_key=openai_api_key,
                provider=provider,
            )
            print(green("Test environment container built successfully."))

            return self.container
        except DaggerError as e:
            print(red(f"Error setting up environment: {e}"))
            return "Test pipeline failure: " + e.stderr


    @function
    async def generate_documentation(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to document")],
        branch: Annotated[str, Doc("Branch to document")],
        model_name: Annotated[str, Doc("LLM model name")] = "openai/gpt-4.1-nano",
        provider: Annotated[str, Doc("LLM provider ('openrouter' or 'openai')")] = "openrouter",
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc("OpenRouter API key")] = None,
        openai_api_key: Annotated[Optional[dagger.Secret], Doc("OpenAI API key")] = None
    ) -> dagger.Container:
        """Generate documentation for agents in the repo."""
       # Set up environment first
        current_container = await self.setup_environment(
            github_access_token=github_access_token,
            repository_url=repository_url,
            branch=branch,
            model_name=model_name,
            provider=provider,
            open_router_api_key=open_router_api_key,
            openai_api_key=openai_api_key
        )


        error_message = f"Unknown error processing documentation for {repository_url} on branch {branch}. Please check the logs for more details."

        """Generate documentation for a repository."""
        try:
            # Set up credentials
            llm_credentials = await get_llm_credentials(
                provider=provider,
                open_router_key=open_router_api_key,
                openai_key=openai_api_key
            )

            # Create model
            documenter_ai_model = await create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name=model_name
            )

            # Create documenter agent
            documenter_agent = create_documenter_agent(pydantic_ai_model=documenter_ai_model)
            documenter_agent.instrument_all()
            
            # Create agent dependencies
            deps = DocumenterAgentDependencies(
                config=self.config,
                container=self.container
            )

            # Run documentation generation
            result = await documenter_agent.run(
                "Generate documentation for all agents in this repository",
                deps=deps
            )

            self.container = await deps.container.sync()

            print(green("Documentation generation complete"))
            print(result)
            print(yellow(f"THE CONTAINER IS: {self.container}"))

            if result is None or (hasattr(result, 'error') and result.error):
                # Test generation failed
                error_message = ""
                if result is None:
                    error_message = f"Agent returned None for {branch}."
                else:
                    error_message = f"Agent encountered an error: {result.error}"

                print(red(error_message))

                # Create PR with insights
                documenter_pull_request_container = dag.builder(self.config_file).setup_documenter_pull_request_container(
                    base_container=self.container,
                    token=github_access_token
                )

                documenter_pull_request_result = dag.documenter_pull_request_agent(self.config_file).run(
                    provider=self.config.core_api.provider,
                    open_router_api_key=self.open_router_api_key,
                    error_context=result.error if hasattr(
                        result, 'error') else error_message,
                    container=documenter_pull_request_container,
                    insight_context=result.strategy if hasattr(
                        result, 'strategy') else None,
                )

                if documenter_pull_request_result:
                    print(
                        green(f"PR created successfully for {branch}"))
                else:
                    print(
                        yellow(f"PR creation may have failed for {branch}"))

                return await documenter_pull_request_result.sync()
            else:
    # Documentation generated successfully
                print(green(f"Successfully generated documentation for {branch}"))

    # 📄 1. Ensure docs/agents/ exists
                self.container = await self.container.with_exec(["mkdir", "-p", "docs/agents"])

    # 📝 2. Write the markdown file into the container
                markdown_path = "docs/agents/documenter_agent.md"
                markdown_contents = result.output  # This assumes it's a string

                self.container = await self.container.with_new_file(markdown_path, contents=markdown_contents)

    # ✅ Optional: Confirm it's written
                self.container = await self.container.with_exec(["cat", markdown_path])

    # 🤝 3. Set up the PR container
                documenter_pull_request_container = dag.builder(self.config_file).setup_documenter_pull_request_container(
                    base_container=self.container,
                    token=github_access_token
         )

    # 🚀 4. Run PR agent
                documenter_pull_request_result = dag.documenter_pull_request_agent(self.config_file).run(
                    provider=provider,
                    open_router_api_key=self.open_router_api_key,
                    error_context=result.error if hasattr(result, 'error') else error_message,
                    container=documenter_pull_request_container,
                    insight_context=result.strategy if hasattr(result, 'strategy') else None,
                )

            return await documenter_pull_request_result.sync()

        except UnexpectedModelBehavior as agent_err:
            print(red(f"Model error processing {branch}: {agent_err}"))
            traceback.print_exc()
            return self.container
        except DaggerError as e:
            print(red(f"Unexpected error processing {branch}: {e.stderr}"))
            traceback.print_exc()
            return self.container
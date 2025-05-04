import traceback
from typing import Annotated, Optional

import dagger
from coverage_agent.core.configuration_loader import ConfigurationLoader
from coverage_agent.core.container_builder import ContainerBuilder
from coverage_agent.core.coverai_agent import (Dependencies,
                                               create_coverai_agent)
from coverage_agent.models.code_module import CodeModule
from coverage_agent.models.config import YAMLConfig
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.utils import (dagger_json_file_to_pydantic,
                                  rank_reports_by_coverage)
from dagger import Doc, dag, function, object_type
from dagger.client.gen import Reporter
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from simple_chalk import green, red, yellow


@object_type
class CoverageAgent:
    """Coverage agent to generate unit tests for a given repository."""
    config: dict
    reporter: Reporter  # Use specific type

    @classmethod
    async def create(
        cls, config_file: Annotated[dagger.File, "Path to the configuration file"]
    ):
        """Creates an instance of the CoverageAgent class."""
        config_dict, reporter_instance = await ConfigurationLoader.load(config=config_file)
        return cls(config=config_dict, reporter=reporter_instance)

    @function
    async def generate_unit_tests(
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
            "OpenAI API key (required if provider is 'openai')")] = None,
        docker_file_path: Annotated[Optional[str], Doc(  # Make optional
            "Optional: Path to the Dockerfile for the container environment"
        )] = None,

    ) -> Optional[dagger.Container]:
        """Generate unit tests for a given repository using the CoverAI agent."""

        self.config = YAMLConfig(**self.config)  # Instantiate YAMLConfig
        llm_base_url: Optional[str] = None  # Use specific variable name
        llm_api_key_plain: Optional[str] = None  # Store plaintext key

        print(f"Configuring LLM provider: {provider}")  # Add logging

        if provider == "openrouter":
            if not open_router_api_key:
                raise ValueError(
                    "open_router_api_key is required for provider 'openrouter'")
            llm_base_url = "https://openrouter.ai/api/v1"
            llm_api_key_plain = await open_router_api_key.plaintext()
            print("Using OpenRouter provider.")
        elif provider == "openai":
            if not openai_api_key:
                raise ValueError(
                    "openai_api_key is required for provider 'openai'")
            llm_base_url = None  # OpenAIProvider uses default if None
            llm_api_key_plain = await openai_api_key.plaintext()
            print("Using OpenAI provider.")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        if not llm_api_key_plain:
            # This check might be redundant given the checks above, but good practice
            raise ValueError(
                f"API key for provider '{provider}' could not be determined.")

        try:
            llm_provider = OpenAIProvider(
                api_key=llm_api_key_plain, base_url=llm_base_url)
            pydantic_ai_model = OpenAIModel(
                model_name=model_name, provider=llm_provider)
            print(
                f"Pydantic AI Model created for '{model_name}' using base URL: {llm_provider.base_url}")
        except Exception as e:
            print(red(f"Failed to initialize Pydantic AI Provider/Model: {e}"))
            raise

        unit_test_agent = create_coverai_agent(
            pydantic_ai_model=pydantic_ai_model)

        builder = ContainerBuilder(config=self.config)
        source = (
            await dag.git(url=repository_url, keep_git_dir=True)
            .with_auth_token(github_access_token)
            .branch(branch)
            .tree()
        )
        container = builder.build_test_environment(
            source=source,
            dockerfile_path=docker_file_path,
            config=self.config
        )
        print(green("Test environment container built successfully."))

        # --- Process Coverage Reports ---
        async def process_coverage_reports_inner(
            start_container: dagger.Container,
            limit: Optional[int],
            agent: Agent,
            config: YAMLConfig,
            reporter: Reporter
        ) -> dagger.Container:
            """Iterate through ranked coverage reports and execute tests."""
            current_container = start_container  # Keep track of the container state
            try:
                coverage_reports_file: dagger.File = await reporter.get_coverage_reports(
                    current_container, config.reporter.report_directory
                )
                print(green(f"****** Got coverage reports file ******** "))
                coverage_data_list = await dagger_json_file_to_pydantic(
                    coverage_reports_file, CoverageReport
                )
                if not coverage_data_list:
                    print(yellow("No coverage reports found or parsed from file."))
                    return current_container  # Return current container if no reports

                # Rank reports
                ranked_reports = rank_reports_by_coverage(coverage_data_list)
                print(
                    green(f"***** Ranked {len(ranked_reports)} coverage reports **********"))

                # Determine the actual limit
                process_limit = limit if limit is not None else len(
                    ranked_reports)
                print(f"Processing up to {process_limit} reports.")

                for i, report in enumerate(ranked_reports[:process_limit]):
                    print(green(
                        f"--- Processing report {i+1}/{process_limit}: {report.file} ({report.coverage_percentage}%) ---"))
                    # Create Dependencies for this iteration
                    # IMPORTANT: Pass the *current* state of the container
                    deps = Dependencies(
                        config=config,  # Use passed config
                        container=current_container,  # Use the latest container state
                        report=report,
                        reporter=reporter  # Use passed reporter instance
                    )
                    # Run the agent
                    print(f"Running agent for report {i+1}...")
                    try:
                        code_module_result: CodeModule = await agent.run(
                            'Generate unit tests to increase the code coverage based on the provided context.',
                            deps=deps
                        )
                        # Update the container state for the next iteration
                        current_container = deps.container  # Agent tools modify deps.container
                        print(green(
                            f"Agent finished iteration {i+1}. Result: {code_module_result if code_module_result else 'No CodeModule'}"))
                    except Exception as agent_err:
                        print(
                            red(f"Error during agent run for report {i+1} ({report.file}): {agent_err}"))
                        # Optionally print more details
                        traceback.print_exc()
                        # Decide whether to continue to the next report or stop
                        # continue # Option: Skip to next report
                        raise  # Option: Stop processing entirely

            except Exception as e:
                print(
                    red(f"Error during coverage report processing loop: {str(e)}"))
                traceback.print_exc()  # Print full traceback
                # Decide whether to raise or return the container state before the error
                # raise # Option 1: Stop execution
                return current_container  # Option 2: Return container state before error

            return current_container  # Return the final state of the container

        # Process coverage reports using the configured limit
        # Pass necessary instances to the inner function
        final_container = await process_coverage_reports_inner(
            start_container=container,  # Start with the initially built container
            limit=self.config.test_generation.limit,  # Use limit from config
            agent=unit_test_agent,
            config=self.config,
            reporter=self.reporter
        )

        print(green("--- Test generation process complete ---"))
        return final_container

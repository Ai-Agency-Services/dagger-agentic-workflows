import traceback
from typing import Annotated, Optional

import dagger
import logfire
from coverage_agent.core.code_review_agent import (ReviewAgentDependencies,
                                                   create_code_review_agent)
from coverage_agent.core.configuration_loader import ConfigurationLoader
from coverage_agent.core.container_builder import ContainerBuilder
from coverage_agent.core.coverai_agent import (CoverAgentDependencies,
                                               create_coverai_agent)
from coverage_agent.models.code_module import CodeModule
from coverage_agent.models.config import YAMLConfig
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.utils import (create_llm_model,
                                  dagger_json_file_to_pydantic,
                                  get_llm_credentials,
                                  rank_reports_by_coverage)
from dagger import Doc, dag, function, object_type
from dagger.client.gen import Reporter
from pydantic_ai import Agent, UnexpectedModelBehavior
from simple_chalk import green, red, yellow


@object_type
class CoverageAgent:
    """Coverage agent to generate unit tests for a given repository."""
    config: dict
    reporter: Reporter

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
        logfire_access_token: Annotated[Optional[dagger.Secret], Doc("Logfire access token")],
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

    ) -> Optional[dagger.Container]:
        """Generate unit tests for a given repository using the CoverAI agent."""
        if logfire_access_token:
            logfire.configure(token=await logfire_access_token.plaintext(),
                              send_to_logfire=True,
                              service_name="coverage-agent",
                              )
        self.config = YAMLConfig(**self.config)
        print(f"Configuring LLM provider: {provider}")  # Add logging
        try:
            llm_credentials = await get_llm_credentials(
                provider=provider,
                open_router_key=open_router_api_key,
                openai_key=openai_api_key,
            )
        except ValueError as e:
            print(red(f"LLM Configuration Error: {e}"))
            raise
        try:
            cover_ai_model = create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name=model_name
            )
            review_ai_model = create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name='deepseek/deepseek-r1'
            )
        except Exception as e:
            # The helper function already prints the error, just re-raise
            raise

        unit_test_agent = create_coverai_agent(
            pydantic_ai_model=cover_ai_model
        )
        unit_test_agent.instrument_all()
        review_agent = create_code_review_agent(
            pydantic_ai_model=review_ai_model
        )
        review_agent.instrument_all()

        builder = ContainerBuilder(config=self.config)
        source = (
            await dag.git(url=repository_url, keep_git_dir=True)
            .with_auth_token(github_access_token)
            .branch(branch)
            .tree()
        )
        container = builder.build_test_environment(
            source=source,
            dockerfile_path=self.config.container.docker_file_path,
            config=self.config
        )
        print(green("Test environment container built successfully."))

        # --- Process Coverage Reports ---
        async def process_coverage_reports_inner(
            start_container: dagger.Container,
            limit: Optional[int],
            cover_agent: Agent,
            review_agent: Agent,
            config: YAMLConfig,
            reporter: Reporter
        ) -> dagger.Container:
            """Iterate through ranked coverage reports and execute tests."""
            current_container = start_container
            try:
                coverage_reports_file: dagger.File = await reporter.get_coverage_reports(
                    current_container, config.reporter.report_directory
                )
                coverage_data_list = await dagger_json_file_to_pydantic(
                    coverage_reports_file, CoverageReport
                )
                if not coverage_data_list:
                    print(yellow("No coverage reports found or parsed from file."))
                    return current_container

                # Rank reports
                ranked_reports = rank_reports_by_coverage(coverage_data_list)

                # Determine the actual limit
                process_limit = limit if limit is not None else len(
                    ranked_reports)
                print(f"Processing up to {process_limit} reports.")

                for i, report in enumerate(ranked_reports[:process_limit]):
                    print(green(
                        f"--- Processing report {i+1}/{process_limit}: {report.file} ({report.coverage_percentage}%) ---"))
                    # Create Dependencies for this iteration
                    # IMPORTANT: Pass the *current* state of the container
                    deps = CoverAgentDependencies(
                        config=config,  # Use passed config
                        container=current_container,  # Use the latest container state
                        report=report,
                        reporter=reporter  # Use passed reporter instance
                    )
                    # Run the agent
                    print(f"Running agent for report {i+1}...")
                    try:
                        code_module_result: CodeModule = await cover_agent.run(
                            '''Generate unit tests to increase the code coverage based on the provided context. 
                               Always run the tests in the container. If the tests fail, 
                               please provide the error message and the code that caused the failure.''',
                            deps=deps
                        )
                        current_container = deps.container  # Agent tools modify deps.container
                        print(green(
                            f"Agent finished iteration {i+1}. Result: {code_module_result if code_module_result else 'No CodeModule'}"))

                        review_deps = ReviewAgentDependencies(
                            config=config,
                            container=current_container,
                            report=report,
                            reporter=reporter,
                            code_module=code_module_result,
                        )
                        review_agent_result = await review_agent.run(
                            '''Review the code and try to resolve any issues. if the code is correct,
                               please provide a message indicating that the code is correct.
                               If the code is incorrect, please provide a message indicating that the code is incorrect and provide the correct code.''',
                            deps=review_deps)
                        print(green(
                            f"Review agent finished iteration {i+1}. Result: {review_agent_result if review_agent_result else 'No ReviewAgentResult'}"))
                        # Check if the review agent result is None
                        if review_agent_result is None:
                            print(
                                red(f"Review agent returned None for report {i+1} ({report.file})."))
                            # Skip to the next report
                            continue
                        elif review_agent_result.error:
                            print(red(
                                f"Review agent encountered an error for report {i+1} ({report.file}): {review_agent_result.error}"))
                            # Skip to the next report
                            continue
                    except UnexpectedModelBehavior as agent_err:
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

        # Pass necessary instances to the inner function
        final_container = await process_coverage_reports_inner(
            start_container=container,  # Start with the initially built container
            limit=self.config.test_generation.limit,  # Use limit from config
            cover_agent=unit_test_agent,
            review_agent=review_agent,
            config=self.config,
            reporter=self.reporter
        )

        print(green("--- Test generation process complete ---"))
        return final_container

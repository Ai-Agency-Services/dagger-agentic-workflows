import os
import traceback
from typing import Annotated, Optional

import dagger
from coverage_agent.core.configuration_loader import ConfigurationLoader
from coverage_agent.core.container_builder import ContainerBuilder
from coverage_agent.core.coverage_review_agent import (
    ReviewAgentDependencies, create_coverage_review_agent)
from coverage_agent.core.coverai_agent import (CoverAgentDependencies,
                                               create_coverai_agent)
from coverage_agent.core.pull_request_agent import (
    PullRequestAgentDependencies, create_pull_request_agent)
from coverage_agent.models.code_module import CodeModule
from coverage_agent.models.config import YAMLConfig
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.models.test_review import TestReview
from coverage_agent.utils import (create_llm_model,
                                  dagger_json_file_to_pydantic,
                                  get_llm_credentials,
                                  rank_reports_by_coverage)
from dagger import Doc, dag, function, object_type
from dagger.client.gen import Reporter
from pydantic_ai import Agent, UnexpectedModelBehavior
from simple_chalk import green, red, yellow
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


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
            "OpenAI API key (required if provider is 'openai')")] = None

    ) -> Optional[dagger.Container]:
        """Generate unit tests for a given repository using the CoverAI agent."""
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://logfire-api.pydantic.dev"
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization={await logfire_access_token.plaintext() if logfire_access_token else ""}"
        os.environ["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] = 'https://logfire-api.pydantic.dev/v1/metrics'
        os.environ["OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"] = 'https://logfire-api.pydantic.dev/v1/logs'

        if logfire_access_token:
            tracer_provider = TracerProvider()  # Renamed from provider to tracer_provider
            processor = BatchSpanProcessor(OTLPSpanExporter(
                endpoint="https://logfire-api.pydantic.dev/v1/traces",
                headers={"Authorization": await logfire_access_token.plaintext()},
            ))
            tracer_provider.add_span_processor(processor)
            trace.set_tracer_provider(tracer_provider)

        self.config = YAMLConfig(**self.config)
        # This now correctly prints the provider string
        print(f"Configuring LLM provider: {provider}")
        try:
            llm_credentials = await get_llm_credentials(
                provider=provider,  # This is now correctly the string parameter
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
                model_name='openai/gpt-4o-mini'
            )
            pull_request_ai_model = create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name='x-ai/grok-3-mini-beta'
            )
        except Exception as e:
            # The helper function already prints the error, just re-raise
            raise

        unit_test_agent: Agent = create_coverai_agent(
            pydantic_ai_model=cover_ai_model
        )
        unit_test_agent.instrument_all()
        review_agent: Agent = create_coverage_review_agent(
            pydantic_ai_model=review_ai_model
        )
        review_agent.instrument_all()
        pull_request_agent: Agent = create_pull_request_agent(
            pydantic_ai_model=pull_request_ai_model
        )
        pull_request_agent.instrument_all()

        builder = ContainerBuilder(config=self.config)

        source = (
            await dag.git(url=repository_url, keep_git_dir=True)
            .with_auth_token(github_access_token)
            .branch(branch)
            .tree()
        )

        container = await builder.build_test_environment(
            source=source,
            dockerfile_path=self.config.container.docker_file_path,
            config=self.config,
            logfire_access_token=logfire_access_token
        )
        print(green("Test environment container built successfully."))

        # --- Process Coverage Reports ---
        async def process_coverage_reports_inner(
            start_container: dagger.Container,
            limit: Optional[int],
            cover_agent: Agent,
            review_agent: Agent,
            pull_request_agent: Agent,
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
                        # Agent tools modify deps.container
                        current_container = await deps.container.sync()

                        print(green(
                            f"Agent finished iteration {i+1}. Result: {code_module_result if code_module_result else 'No CodeModule'}"))

                        # Check if the code_module_result is None or has an error
                        if code_module_result is None or (hasattr(code_module_result, 'error') and code_module_result.error):
                            # Test generation failed, create PR with insights
                            error_message = ""
                            if code_module_result is None:
                                error_message = f"Agent returned None for report {i+1} ({report.file})."
                            else:
                                error_message = f"Agent encountered an error: {code_module_result.error}"

                            print(red(error_message))

                            # Create a PR with insights about the issues
                            print(
                                yellow(f"Creating PR with insights for report {i+1} ({report.file})..."))
                            pull_request_container = builder.setup_pull_request_container(
                                base_container=current_container,
                                token=github_access_token
                            )
                            pull_deps = PullRequestAgentDependencies(
                                config=config,
                                container=pull_request_container,
                                reporter=reporter,
                                report=report,
                                insight_context=error_message  # Add the error context
                            )
                            pull_request_result = await pull_request_agent.run(
                                '''Create a pull request with insights about the issues encountered.
                                Include details about why the tests couldn't be generated or what problems were found.''',
                                deps=pull_deps
                            )
                            if pull_request_result:
                                print(
                                    green(f"PR created successfully for report {i+1}"))
                            else:
                                print(
                                    yellow(f"PR creation may have failed for report {i+1}"))

                            # Add after PR operations:
                            current_container = await pull_deps.container.sync()

                            # Skip to the next report
                            continue

                        # Tests were generated successfully, create PR with new code
                        print(green(
                            f"Successfully generated tests for report {i+1} ({report.file}). Creating pull request..."))

                        # Create a regular pull request with the generated code
                        pull_request_container = builder.setup_pull_request_container(
                            base_container=current_container,
                            token=github_access_token
                        )
                        pull_deps = PullRequestAgentDependencies(
                            config=config,
                            container=pull_request_container,
                            reporter=reporter,
                            report=report,
                        )
                        pull_request_result = await pull_request_agent.run(
                            '''Create a pull request with the newly generated tests.
                            Include details about what tests were added and how they improve the codebase.''',
                            deps=pull_deps
                        )
                        if pull_request_result:
                            print(
                                green(f"PR created successfully for report {i+1}"))
                        else:
                            print(
                                yellow(f"PR creation may have failed for report {i+1}"))

                        # Add after PR operations:
                        current_container = await pull_deps.container.sync()

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
            pull_request_agent=pull_request_agent,
            config=self.config,
            reporter=self.reporter
        )

        print(green("--- Test generation process complete ---"))
        return final_container

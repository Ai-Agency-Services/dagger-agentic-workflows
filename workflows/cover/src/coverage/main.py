import logging
import traceback
from typing import Annotated, Optional

import anyio
import dagger
import yaml
from ais_dagger_agents_config import YAMLConfig, ConcurrencyConfig
from coverage.core.coverai_agent import (CoverAgentDependencies,
                                         create_coverai_agent)
from coverage.core.pull_request_agent import (PullRequestAgentDependencies,
                                              create_pull_request_agent)
from coverage.models.code_module import CodeModule
from coverage.models.coverage_report import CoverageReport
from coverage.utils import (create_llm_model, dagger_json_file_to_pydantic,
                            get_llm_credentials, rank_reports_by_coverage)
from dagger import Doc, dag, function, object_type
from dagger.client.gen import Reporter
from pydantic_ai import Agent, UnexpectedModelBehavior
from simple_chalk import green, red, yellow


@object_type
class Cover:
    """Coverage agent to generate unit tests for a given repository."""
    config: dict
    config_file: dagger.File
    reporter: Reporter

    @classmethod
    async def create(
        cls, config_file: Annotated[dagger.File, "Path to the configuration file"]
    ):
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)

        reporter_name = config_dict["reporter"]["name"]
        reporter = dag.reporter(name=reporter_name)

        return cls(config=config_dict, reporter=reporter, config_file=config_file)

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "Cover agent initialized with configuration: %s", self.config)

    def _get_concurrency_config(self) -> ConcurrencyConfig:
        """Extract processing configuration from the YAML config."""
        try:
            config_obj = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config
            if not hasattr(config_obj, "concurrency"):
                raise ValueError("Concurrency configuration is missing.")
            return ConcurrencyConfig(**self.config["concurrency"])
        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")

    async def _process_report_with_semaphore(
        self,
        report: CoverageReport,
        cover_agent: Agent,
        pull_request_agent: Agent,
        config: YAMLConfig,
        reporter: Reporter,
        github_access_token: dagger.Secret,
        container: dagger.Container,
        semaphore: anyio.Semaphore,
        batch_index: int,
        report_index: int,
    ) -> dagger.Container:
        """Process a single coverage report with semaphore-based concurrency control."""
        async with semaphore:
            try:
                print(green(
                    f"--- Processing report: {report.file} ({report.coverage_percentage}%) ---"))

                # Create a unique branch name for this report based on batch and report indices
                unique_branch_name = f"test-gen-batch-{batch_index}-report-{report_index}-{report.file.replace('/', '-')}"

                # Configure git before starting work
                try:
                    # Configure git to handle conflicts
                    await container.with_exec(["git", "config", "pull.rebase", "false"]).sync()

                    # Create and checkout a new branch specific to this report
                    current_container = await container.with_exec(["git", "checkout", "-b", unique_branch_name]).sync()
                    print(
                        green(f"Created new branch {unique_branch_name} for {report.file}"))
                except Exception as git_err:
                    print(
                        yellow(f"Git setup error for {report.file}: {git_err}"))
                    # Continue with existing container if branch creation fails
                    current_container = container

                # Create Dependencies for this iteration, using the container with unique branch
                deps = CoverAgentDependencies(
                    config=config,
                    container=current_container,
                    report=report,
                    reporter=reporter
                )

                # Run the agent
                print(f"Running agent for {report.file}...")
                code_module_result: CodeModule = await cover_agent.run(
                    '''Generate unit tests to increase the code coverage based on the provided context. 
                       Always run the tests in the container. If the tests fail, 
                       please provide the error message and the code that caused the failure.''',
                    deps=deps
                )

                # Get updated container
                current_container = await deps.container.sync()

                # Handle success or failure
                if code_module_result is None or (hasattr(code_module_result, 'error') and code_module_result.error):
                    # Test generation failed, create PR with insights
                    error_message = ""
                    if code_module_result is None:
                        error_message = f"Agent returned None for report {report.file}."
                    else:
                        error_message = f"Agent encountered an error: {code_module_result.error}"

                    print(red(error_message))

                    # Create a PR with insights about the issues
                    print(
                        yellow(f"Creating PR with insights for {report.file}..."))
                    pull_request_container = dag.builder(self.config_file).setup_pull_request_container(
                        base_container=current_container,
                        token=github_access_token
                    )
                    pull_deps = PullRequestAgentDependencies(
                        config=config,
                        container=pull_request_container,
                        reporter=reporter,
                        report=report,
                        insight_context=error_message
                    )
                    pull_request_result = await pull_request_agent.run(
                        '''Create a pull request with insights about the issues encountered.
                        Include details about why the tests couldn't be generated or what problems were found.''',
                        deps=pull_deps
                    )

                    if pull_request_result:
                        print(
                            green(f"PR created successfully for {report.file}"))
                    else:
                        print(
                            yellow(f"PR creation may have failed for {report.file}"))

                    return await pull_deps.container.sync()
                else:
                    # Tests were generated successfully, create PR with new code
                    print(green(
                        f"Successfully generated tests for {report.file}. Creating pull request..."))

                    # Create a regular pull request with the generated code
                    pull_request_container = dag.builder(self.config_file).setup_pull_request_container(
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
                            green(f"PR created successfully for {report.file}"))
                    else:
                        print(
                            yellow(f"PR creation may have failed for {report.file}"))

                    return await pull_deps.container.sync()

            except UnexpectedModelBehavior as agent_err:
                print(
                    red(f"Error during agent run for {report.file}: {agent_err}"))
                traceback.print_exc()
                # Return the original container if there's an error
                return container
            except Exception as e:
                print(red(f"Unexpected error processing {report.file}: {e}"))
                traceback.print_exc()
                # Return the original container if there's an error
                return container

    async def _process_reports_concurrently(
        self,
        ranked_reports: list[CoverageReport],
        limit: Optional[int],
        cover_agent: Agent,
        pull_request_agent: Agent,
        config: YAMLConfig,
        reporter: Reporter,
        github_access_token: dagger.Secret,
        container: dagger.Container,
    ) -> dagger.Container:
        """Process coverage reports with controlled concurrency."""

        # Get concurrency configuration
        concurrency_config = config.concurrency
        batch_size = concurrency_config.batch_size
        max_concurrent = concurrency_config.max_concurrent

        # Apply limit if specified
        process_limit = limit if limit is not None else len(ranked_reports)
        reports_to_process = ranked_reports[:process_limit]

        print(
            f"Processing {len(reports_to_process)} reports with concurrency {max_concurrent}, batch size {batch_size}")

        # Create a semaphore to limit concurrent operations
        semaphore = anyio.Semaphore(max_concurrent)

        # Process in batches
        current_container = container
        for batch_start in range(0, len(reports_to_process), batch_size):
            batch = reports_to_process[batch_start:batch_start + batch_size]
            batch_index = batch_start // batch_size + 1  # Calculate batch number
            print(
                green(f"Processing batch {batch_index}, size {len(batch)}"))

            # Create a task group to process the batch concurrently
            async with anyio.create_task_group() as tg:
                # Create a list to store the results
                results: list[dagger.Container] = []

                # Track which reports are being processed
                processing: dict[int, CoverageReport] = {}

                # Define a callback to handle results
                async def process_report_callback(i: int, report: CoverageReport) -> None:
                    processing[i] = report
                    result_container = await self._process_report_with_semaphore(
                        report=report,
                        cover_agent=cover_agent,
                        pull_request_agent=pull_request_agent,
                        config=config,
                        reporter=reporter,
                        github_access_token=github_access_token,
                        container=current_container,
                        semaphore=semaphore,
                        batch_index=batch_index,  # Add the batch index parameter
                        report_index=i,           # Add the report index parameter
                    )
                    results.append(result_container)
                    del processing[i]

                # Start tasks for each report in the batch
                for i, report in enumerate(batch, batch_start):
                    tg.start_soon(process_report_callback, i, report)

            # After all tasks in this batch are done, merge containers
            # Note: This is a simplified approach - actual container merging would be complex
            # For now, we'll just use the last container as the result
            if results:
                current_container = results[-1]

            print(green(f"Completed batch {batch_index}"))

            import gc
            gc.collect()  # Force garbage collection between batches

            # Consider adding a small delay to allow memory to stabilize
            await anyio.sleep(1.0)

        return current_container

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
            "OpenAI API key (required if provider is 'openai')")] = None

    ) -> Optional[dagger.Container]:
        """Generate unit tests for a given repository using the CoverAI agent with concurrency."""

        self.config = YAMLConfig(**self.config)
        print(f"Configuring LLM provider: {provider}")

        # Setup LLM credentials and models
        try:
            llm_credentials = await get_llm_credentials(
                provider=provider,
                open_router_key=open_router_api_key,
                openai_key=openai_api_key,
            )

            cover_ai_model = create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name=model_name
            )

            grok = create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name='x-ai/grok-3-mini-beta'
            )
        except Exception as e:
            print(red(f"Error setting up LLM: {e}"))
            raise

        # Create agents
        unit_test_agent: Agent = create_coverai_agent(
            pydantic_ai_model=cover_ai_model)
        pull_request_agent: Agent = create_pull_request_agent(
            pydantic_ai_model=grok)
        unit_test_agent.instrument_all()
        pull_request_agent.instrument_all()

        # Setup repository
        source = (
            await dag.git(url=repository_url, keep_git_dir=True)
            .with_auth_token(github_access_token)
            .branch(branch)
            .tree()
        )

        # Build test container
        container = await dag.builder(self.config_file).build_test_environment(
            source=source,
            dockerfile_path=self.config.container.docker_file_path,
            open_router_api_key=open_router_api_key,
            openai_api_key=openai_api_key,
            provider=provider,
        )
        print(green("Test environment container built successfully."))

        # Get coverage reports
        try:
            # Get coverage reports from reporter
            coverage_reports_file: dagger.File = await self.reporter.get_coverage_reports(
                container, self.config.reporter.report_directory
            )

            coverage_data_list = await dagger_json_file_to_pydantic(
                coverage_reports_file, CoverageReport
            )

            if not coverage_data_list:
                print(yellow("No coverage reports found or parsed from file."))
                return container

            # Rank reports
            ranked_reports = rank_reports_by_coverage(coverage_data_list)

            # Process reports concurrently
            final_container = await self._process_reports_concurrently(
                ranked_reports=ranked_reports,
                limit=self.config.test_generation.limit,
                cover_agent=unit_test_agent,
                pull_request_agent=pull_request_agent,
                config=self.config,
                reporter=self.reporter,
                github_access_token=github_access_token,
                container=container,
            )

            print(green("--- Test generation process complete ---"))
            return final_container

        except Exception as e:
            print(red(f"Error during coverage report processing: {e}"))
            traceback.print_exc()
            return container

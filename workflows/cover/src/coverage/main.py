import logging
import traceback
from typing import Annotated, List, Optional

import anyio
import dagger
import yaml
from ais_dagger_agents_config import YAMLConfig
from coverage.core.coverai_agent import (CoverAgentDependencies,
                                         create_coverai_agent)
from coverage.models.code_module import CodeModule
from coverage.models.coverage_report import CoverageReport
from coverage.utils import (create_llm_model, dagger_json_file_to_pydantic,
                            get_llm_credentials, rank_reports_by_coverage)
from dagger import DaggerError, Doc, dag, field, function, object_type
from dagger.client.gen import Reporter
from pydantic_ai import UnexpectedModelBehavior
from simple_chalk import green, red, yellow


@object_type
class Cover:
    """Coverage agent to generate unit tests for a given repository."""
    config: dict
    config_file: dagger.File
    container: Optional[dagger.Container] = field(default=None)
    reporter: Reporter
    github_token: Optional[dagger.Secret] = None
    open_router_api_key: Optional[dagger.Secret] = None
    openai_api_key: Optional[dagger.Secret] = None
    model: str = "x-ai/grok-3-mini-beta"

    @classmethod
    async def create(
        cls, config_file: Annotated[dagger.File, "Path to the configuration file"]
    ):
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)

        reporter_name = config_dict["reporter"]["name"]
        reporter = dag.reporter(name=reporter_name)

        return cls(
            config=config_dict,
            reporter=reporter,
            config_file=config_file,
            github_token=None,
            open_router_api_key=None,
            openai_api_key=None,
        )

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "Cover agent initialized with configuration: %s", self.config)

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
    async def process_report(
        self,
        report: Annotated[dagger.File, Doc("Coverage report file")],
        branch_suffix: Annotated[str, Doc("Unique suffix for branch name")],
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        model_name: Annotated[str, Doc(
            "LLM model name")] = "openai/gpt-4.1-nano",
        provider: Annotated[str, Doc("LLM provider")] = "openrouter",
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None,
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None
    ) -> dagger.Container:
        """Process a single coverage report and generate tests."""
        if not self.container:
            raise ValueError(
                "Environment not set up. Call setup_environment first.")

        error_message = f"Unknown error processing report {report.file}"

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

            # Create agents as local variables
            test_agent = create_coverai_agent(pydantic_ai_model=cover_ai_model)
            test_agent.instrument_all()

            # Create a unique branch name
            unique_branch_name = f"test-gen-{branch_suffix}-{report.file.replace('/', '-')}"

            # Create branch for this report
            try:
                # Configure git
                await self.container.with_exec(["git", "config", "pull.rebase", "false"]).sync()

                # Create and checkout new branch
                current_container = await self.container.with_exec(
                    ["git", "checkout", "-b", unique_branch_name]
                ).sync()

                print(
                    green(f"Created branch {unique_branch_name} for {report.file}"))
            except Exception as git_err:
                print(yellow(f"Git branch creation failed: {git_err}"))
                current_container = self.container

            # Create dependencies for the agent
            deps = CoverAgentDependencies(
                config=self.config,
                container=current_container,
                report=report,
                reporter=self.reporter
            )

            # Run test generation
            print(f"Generating tests for {report.file}...")

            # Force garbage collection to reduce memory pressure
            import gc
            gc.collect()

            code_module_result: CodeModule = await test_agent.run(
                '''Generate unit tests to increase the code coverage based on the provided context.
                   Always run the tests in the container. If the tests fail,
                   please provide the error message and the code that caused the failure.''',
                deps=deps
            )

            # Get updated container
            current_container = await deps.container.sync()

            # Handle result
            if code_module_result is None or (hasattr(code_module_result, 'error') and code_module_result.error):
                # Test generation failed
                error_message = ""
                if code_module_result is None:
                    error_message = f"Agent returned None for report {report.file}."
                else:
                    error_message = f"Agent encountered an error: {code_module_result.error}"

                print(red(error_message))

                # Create PR with insights
                pull_request_container = dag.builder(self.config_file).setup_pull_request_container(
                    base_container=current_container,
                    token=github_access_token
                )

                pull_request_result = dag.pull_request_agent(self.config_file).run(
                    provider=self.config.core_api.provider,
                    open_router_api_key=self.open_router_api_key,
                    error_context=code_module_result.error if hasattr(
                        code_module_result, 'error') else error_message,
                    container=pull_request_container,
                    insight_context=code_module_result.strategy if hasattr(
                        code_module_result, 'strategy') else None,
                )

                if pull_request_result:
                    print(
                        green(f"PR created successfully for {report.file}"))
                else:
                    print(
                        yellow(f"PR creation may have failed for {report.file}"))

                return await pull_request_result.sync()
            else:
                # Tests generated successfully
                print(
                    green(f"Successfully generated tests for {report.file}"))

                # Create PR with the new tests
                pull_request_container = dag.builder(self.config_file).setup_pull_request_container(
                    base_container=current_container,
                    token=github_access_token
                )

                pull_request_result = dag.pull_request_agent(self.config_file).run(
                    provider=self.config.core_api.provider,
                    open_router_api_key=self.open_router_api_key,
                    error_context=code_module_result.error if hasattr(
                        code_module_result, 'error') else error_message,
                    container=pull_request_container,
                    insight_context=code_module_result.strategy if hasattr(
                        code_module_result, 'strategy') else None,
                )

                if pull_request_result:
                    print(
                        green(f"PR created successfully for {report.file}"))
                else:
                    print(
                        yellow(f"PR creation may have failed for {report.file}"))

                return await pull_request_result.sync()

        except UnexpectedModelBehavior as agent_err:
            print(red(f"Model error processing {report}: {agent_err}"))
            traceback.print_exc()
            return self.container
        except DaggerError as e:
            print(red(f"Unexpected error processing {report}: {e.stderr}"))
            traceback.print_exc()
            return self.container

    @function
    async def process_reports_batch(
        self,
        reports: Annotated[List[dagger.File], Doc("List of coverage report files")],
        batch_id: Annotated[str, Doc("Unique identifier for this batch")]
    ) -> dagger.Container:
        """Process a batch of reports concurrently."""
        try:
            if not reports:
                return self.container

            print(
                green(f"Processing batch {batch_id} with {len(reports)} reports"))

            # Use lower concurrency to avoid memory issues
            max_concurrent = min(2, getattr(
                self.config.concurrency, 'max_concurrent', 2))
            semaphore = anyio.Semaphore(max_concurrent)
            results = {}

            async with anyio.create_task_group() as tg:
                async def process_with_semaphore(i: int, report: dagger.File) -> None:
                    # Add a try-except block to catch ALL errors
                    try:
                        async with semaphore:
                            result = await self.process_report(
                                report=report,
                                branch_suffix=f"{batch_id}-{i}",
                                github_access_token=self.github_token,
                                model_name=self.config.core_api.model,
                                provider=self.config.core_api.provider,
                                open_router_api_key=self.open_router_api_key,
                                openai_api_key=self.openai_api_key
                            )
                            results[i] = result
                    except Exception as e:
                        print(
                            red(f"Error in task for report {report.file}: {str(e)}"))
                        traceback.print_exc()
                        # Still add the container to results to maintain ordering
                        results[i] = self.container

                # Start tasks for each report
                for i, report in enumerate(reports):
                    tg.start_soon(process_with_semaphore, i, report)

            # After task group completion:
            ordered_results = [results[i] for i in sorted(results.keys())]
            if ordered_results:
                self.container = ordered_results[-1]

            # Force garbage collection
            import gc
            gc.collect()

            # Allow time for resources to stabilize
            await anyio.sleep(1.0)

            return self.container

        except DaggerError as e:
            print(red(f"Error processing batch {batch_id}: {e.stderr}"))
            traceback.print_exc()
            return self.container

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
    ) -> dagger.Container:
        """Generate unit tests for a given repository using the CoverAI agent."""
        # Set up environment first
        await self.setup_environment(
            github_access_token=github_access_token,
            repository_url=repository_url,
            branch=branch,
            model_name=model_name,
            provider=provider,
            open_router_api_key=open_router_api_key,
            openai_api_key=openai_api_key
        )

        try:
            # Get coverage reports from reporter
            coverage_reports_file = await self.reporter.get_coverage_reports(
                self.container, self.config.reporter.report_directory
            )

            # Parse coverage reports
            coverage_data_list = await dagger_json_file_to_pydantic(
                coverage_reports_file, CoverageReport
            )

            if not coverage_data_list:
                print(yellow("No coverage reports found or parsed from file."))
                return self.container
            ranked_reports = rank_reports_by_coverage(coverage_data_list)

            # Apply limit if specified
            limit = getattr(self.config.test_generation, 'limit', None)
            if limit:
                ranked_reports = ranked_reports[:limit]

            # Process in batches
            batch_size = getattr(self.config.concurrency, 'batch_size', 2)
            for batch_start in range(0, len(ranked_reports), batch_size):
                batch = ranked_reports[batch_start:batch_start + batch_size]
                batch_id = f"{batch_start // batch_size + 1}"

                # Process this batch
                self.container = await self.process_reports_batch(
                    reports=batch,
                    batch_id=batch_id
                )

            print(green("--- Test generation process complete ---"))
            return self.container

        except DaggerError as e:
            print(red(f"Error during coverage report processing: {e.stderr}"))
            traceback.print_exc()
            return self.container

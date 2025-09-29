"""Main Dagger module orchestrating all Codebuff-equivalent agents."""

import uuid
from datetime import UTC, datetime
from typing import Annotated, Optional

import dagger
import yaml
from ais_dagger_agents_config import YAMLConfig
from codebuff.orchestrator.agent import create_orchestrator_agent
from codebuff.orchestrator.models import (
    OrchestrationState,
    OrchestratorDependencies, Phase,
    Status,
    TaskSpec
)
from codebuff.test_env.agent import TestEnvDependencies, create_test_env_agent
from dagger import Doc, dag, function, object_type
from dagger._exceptions import DaggerError
from dagger.mod import field

from simple_chalk import green, red

from codebuff.utils import create_llm_model, get_llm_credentials


@object_type
class Codebuff:
    """Orchestrator for Codebuff-equivalent agents."""

    config: dict
    config_file: dagger.File
    container: Optional[dagger.Container] = field(default=None)
    github_token: Optional[dagger.Secret] = field(default=None)
    open_router_api_key: Optional[dagger.Secret] = field(default=None)
    openai_api_key: Optional[dagger.Secret] = field(default=None)
    model: Optional[str] = field(default=None)

    def _get_model_for_agent(self, agent_name: str) -> str:
        """Get model name for specific agent from config, with fallbacks."""
        # Check agent-specific config first
        if "agents" in self.config and agent_name in self.config["agents"]:
            if "model" in self.config["agents"][agent_name]:
                return self.config["agents"][agent_name]["model"]

        # Fallback to core_api model
        if "core_api" in self.config and "model" in self.config["core_api"]:
            return self.config["core_api"]["model"]

        # Ultimate fallback by agent type
        fallbacks = {
            "file_explorer": "openai/gpt-4o-mini",
            "file_picker": "openai/gpt-4o-mini",
            "thinker": "openai/gpt-4o",
            "implementation": "openai/gpt-4o",
            "reviewer": "openai/gpt-4o",
            "context_pruner": "openai/gpt-4o-mini",
            "orchestrator": "openai/gpt-4o"
        }
        return fallbacks.get(agent_name, "openai/gpt-4o")

    async def _get_llm_for_agent(
        self,
        agent_name: str,
        open_router_api_key: Optional[dagger.Secret],
        openai_api_key: Optional[dagger.Secret],
    ) -> object:
        """Determines the correct provider and creates the LLM for a given agent."""
        model_name = self._get_model_for_agent(agent_name)

        # Determine provider based on available keys
        # Prefer OpenRouter if available since it supports more models
        if open_router_api_key:
            provider = "openrouter"
        elif openai_api_key:
            provider = "openai"
        else:
            provider = "openai"  # fallback

        creds = await get_llm_credentials(provider, open_router_api_key, openai_api_key)
        return await create_llm_model(creds.api_key, creds.base_url, model_name)

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("YAML configuration file")]
    ) -> "Codebuff":
        """Create orchestrator from configuration."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(
            config=config_dict,
            config_file=config_file,
            container=None,
            github_token=None,
            open_router_api_key=None,
            openai_api_key=None,
            model=None
        )

    @function
    async def orchestrate_feature_development(
        self,
        github_token: Annotated[dagger.Secret, Doc("GitHub token for repo access")],
        feature_task_description: Annotated[str, Doc("Description of the feature to develop")],
        repository_url: Annotated[str, Doc("GitHub repository URL")],
        branch: Annotated[str, Doc("Branch to work on")] = "main",
        provider: Annotated[str, Doc(
            "LLM provider ('openrouter' or 'openai')")] = "openrouter",
        focus_area: Annotated[str, Doc(
            "Area to focus exploration on")] = "entire project",
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None,
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None
    ) -> str:
        """Orchestrate complete feature development workflow using all Codebuff agents."""
        print(green("🔧 DEBUG: Starting orchestrate_feature_development"))
        try:
            # Store github token for later use in PR creation
            self.github_token = github_token
            print(green("🔧 DEBUG: Checking API keys"))
            api_key = openai_api_key or open_router_api_key
            if not api_key:
                return "Error: No API key provided"

            print(green("🔧 DEBUG: Getting LLM credentials"))
            model = await self._get_llm_for_agent(
                "orchestrator", open_router_api_key, openai_api_key
            )
            print(green("🔧 DEBUG: Created LLM model"))

            print(green("🔧 DEBUG: About to call setup_environment"))
            await self.setup_environment(
                github_access_token=github_token,
                repository_url=repository_url,
                branch=branch,
                model_name="gpt-4o",
                provider=provider,
                open_router_api_key=open_router_api_key,
                openai_api_key=openai_api_key
            )
            print(green("🔧 DEBUG: setup_environment completed successfully"))
            try:
                container = self.container.with_new_file(
                    ".codebuff-state/log.txt", "")
            except Exception:
                pass

            print(green("🔧 DEBUG: Creating OrchestratorDependencies"))
            try:
                # Build a tolerant config for tests: fallback to minimal valid config if required fields are missing
                try:
                    cfg_obj = YAMLConfig(**self.config)
                except Exception:
                    cfg_obj = YAMLConfig(**{
                        "container": {"work_dir": "/src", "docker_file_path": None},
                        "git": {"user_name": "Test User", "user_email": "test@example.com", "base_pull_request_branch": "main"}
                    })
                deps = OrchestratorDependencies(
                    config=cfg_obj,
                    config_file=self.config_file,
                    container=container,
                    api_key=api_key,
                    state=OrchestrationState(
                        task_id=str(uuid.uuid4()),
                        current_phase=Phase.EXPLORATION,
                        status=Status.IN_PROGRESS,
                        start_time=datetime.now(UTC),
                        last_update=datetime.now(UTC),
                        task_spec=TaskSpec(
                            id=str(uuid.uuid4()),
                            goal=feature_task_description,
                            focus_area=focus_area
                        )
                    )
                )
            except Exception as deps_error:
                print(
                    red(f"🔧 ERROR: Failed to create OrchestratorDependencies: {deps_error}"))
                return f"Error creating dependencies: {deps_error}"

            print(green("🔧 DEBUG: Creating orchestrator agent"))
            agent = create_orchestrator_agent(model)
            print(green("🔧 DEBUG: Orchestrator agent created successfully"))

            # Execute complete workflow
            workflow_prompt = f"""
Execute the complete feature development workflow for: {feature_task_description}

Workflow steps:
1. Start the task with focus area: {focus_area}
2. Explore the codebase
3. Select relevant files
4. Create implementation plan
5. Execute implementation
6. Review changes
7. Create pull request
8. Provide final status

Execute all steps in sequence and provide a comprehensive summary.
"""
            print(green("🔧 DEBUG: About to run agent with workflow"))
            result = await agent.run(workflow_prompt, deps=deps)
            print(green("🔧 DEBUG: Agent workflow completed successfully"))

            # Get final status
            final_status = await agent.run(
                "Provide the final orchestration status and summary",
                deps=deps
            )

            out1 = result.output if isinstance(
                result.output, str) else str(result.output)
            out2 = final_status.output if isinstance(
                final_status.output, str) else str(final_status.output)
            return f"Workflow Result: {out1}\n\nFinal Status:\n{out2}"
        except Exception as e:
            return f"Error in orchestrated workflow: {e}"

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
            "OpenAI API key (required if provider is 'openai')")] = None,
    ) -> dagger.Container:
        """Set up the test environment and return a ready-to-use container."""
        print(green("🔧 DEBUG: Entering setup_environment"))
        try:
            print(green("🔧 DEBUG: Processing config"))
            # Store API keys and model info (note: these are for reference only in this context)
            # In practice, you'd use them directly in agent calls

            try:
                config_obj = YAMLConfig(**self.config)
            except Exception:
                config_obj = YAMLConfig(**{
                    "container": {"work_dir": "/src", "docker_file_path": None},
                    "git": {"user_name": "Test User", "user_email": "test@example.com", "base_pull_request_branch": "main"}
                })
            print(green("🔧 DEBUG: YAMLConfig created successfully"))

            print(green("🔧 DEBUG: Setting up repository"))
            # Setup repository
            source = (
                await dag.git(url=repository_url, keep_git_dir=True)
                .with_auth_token(github_access_token)
                .branch(branch)
                .tree()
            )
            print(green("🔧 DEBUG: Repository source created"))

            print(green("🔧 DEBUG: About to build test container"))
            # Build test container using builder module
            container = await dag.builder(self.config_file).build_test_environment(
                source=source,
                dockerfile_path=config_obj.container.docker_file_path,
                open_router_api_key=open_router_api_key,
                openai_api_key=openai_api_key,
                provider=provider,
            )
            print(green("Test environment container built successfully."))

            print(green("🔧 DEBUG: About to store container"))
            # Store container for use in orchestration
            try:
                self.container = container
                print(green("🔧 DEBUG: Container stored successfully"))
            except Exception as container_error:
                print(
                    red(f"🔧 DEBUG: Error storing container: {container_error}"))
                print(red(f"🔧 DEBUG: Container type: {type(container)}"))
                print(red(f"🔧 DEBUG: Self type: {type(self)}"))
                raise
            return container
        except DaggerError as e:
            print(red(f"Error setting up environment: {e}"))
            return "Test pipeline failure: " + e.stderr

    @function
    async def export_state(
        self,
        container: Annotated[dagger.Container, Doc(
            "Container holding .codebuff-state")]
    ) -> dagger.Directory:
        """Return the .codebuff-state directory from the provided container for export."""
        try:
            return container.directory(".codebuff-state")
        except Exception:
            # Return empty directory if state dir is missing
            return dag.directory()

    @function
    async def export_state_from_self(self) -> dagger.Directory:
        """Return the .codebuff-state directory from this object's stored container (if available)."""
        try:
            if self.container is None:
                return dag.directory()
            return self.container.directory(".codebuff-state")
        except Exception:
            return dag.directory()

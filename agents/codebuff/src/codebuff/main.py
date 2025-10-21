"""
Main Dagger module orchestrating all Codebuff-equivalent agents.
"""

import uuid
import json
from datetime import datetime, timezone
from typing import Annotated, Optional

import dagger
import yaml
from ais_dagger_agents_config import YAMLConfig
from codebuff.orchestrator.agent import create_orchestrator_agent
from codebuff.orchestrator.state_loader import load_orchestration_state
from codebuff.orchestrator.pr_feedback import parse_orchestrator_commands, save_user_feedback, load_user_feedback, load_feedback_sentinel
from codebuff.utils.git_metadata import extract_state_metadata
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
        """DEPRECATED: Use run_speckit_workflow instead. Orchestrate complete feature development workflow."""
        try:
            import logging
            # Configure logging to suppress OpenTelemetry warnings
            logging.getLogger(
                "opentelemetry.exporter.otlp.proto.http.metric_exporter").setLevel(logging.ERROR)
            # Store github token for later use in PR creation
            self.github_token = github_token

            model = await self._get_llm_for_agent(
                "orchestrator", open_router_api_key, openai_api_key
            )

            # Also create implementation model for sub-agent use
            impl_model = await self._get_llm_for_agent(
                "implementation", open_router_api_key, openai_api_key
            )
            file_picker_model = await self._get_llm_for_agent(
                "file_picker", open_router_api_key, openai_api_key
            )
            file_explorer_model = await self._get_llm_for_agent(
                "file_explorer", open_router_api_key, openai_api_key
            )
            review_model = await self._get_llm_for_agent(
                "reviewer", open_router_api_key, openai_api_key
            )

            await self.setup_environment(
                github_access_token=github_token,
                repository_url=repository_url,
                branch=branch,
                model_name="gpt-4o",
                provider=provider,
                open_router_api_key=open_router_api_key,
                openai_api_key=openai_api_key
            )

            container = self.container.with_new_file(
                ".codebuff-state/log.txt", "")

            # Build tolerant config for tests
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
                github_token=github_token,
                api_key=openai_api_key or open_router_api_key,
                model=model,  # NEW: pass implementation model for sub-agent
                implementation=impl_model,
                file_picker=file_picker_model,
                file_explorer=file_explorer_model,
                reviewer=review_model,
                state=OrchestrationState(
                    task_id=str(uuid.uuid4()),
                    current_phase=Phase.EXPLORATION,
                    status=Status.IN_PROGRESS,
                    start_time=datetime.now(timezone.utc),
                    last_update=datetime.now(timezone.utc),
                    task_spec=TaskSpec(
                        id=str(uuid.uuid4()),
                        goal=feature_task_description,
                        focus_area=focus_area
                    )
                )
            )

            agent = create_orchestrator_agent(model)

            # Execute spec-kit workflow
            workflow_prompt = f"""
You are orchestrating a feature development workflow using the Spec-Kit methodology.

**Primary Workflow (Recommended)**:
Call `run_speckit_workflow` with:
- task_description: "{feature_task_description}"
- focus_area: "{focus_area}"

This will execute the complete Constitution → Spec → Tasks workflow with:
- Automated exploration and constitution generation
- Requirement analysis and specification
- Task breakdown with dependency management
- Implementation-review loops per task
- Automated testing and PR creation

**Alternative (Legacy)**:
If resuming an old workflow or debugging, use individual tools:
1. start_task, 2. explore_codebase, 3. create_implementation_plan, 
4. execute_implementation, 5. review_changes, 6. create_pull_request

Start the spec-kit workflow now.
"""

            result = await agent.run(workflow_prompt, deps=deps)

            # Check for feedback gate (simplified with initialized file)
            try:
                fb_cfg = self.config.get("orchestrator", {}).get(
                    "feedback", {}) if isinstance(self.config, dict) else {}
                if fb_cfg.get("enabled"):
                    # Ensure sentinel is populated so feedback is requested
                    try:
                        phase_to_stop = fb_cfg.get(
                            "stop_after_phase", "PLANNING")
                        self.container = self.container.with_new_file(
                            ".codebuff-state/feedback_sentinel.json",
                            json.dumps({"phase": phase_to_stop,
                                       "requested": True}, indent=2)
                        )
                    except Exception:
                        pass

                    # Read sentinel file (guaranteed to exist now)
                    sentinel_contents = await self.container.file(".codebuff-state/feedback_sentinel.json").contents()

                    # Check if it contains actual feedback request data (not just empty {})
                    if sentinel_contents and sentinel_contents.strip() != "{}":
                        try:
                            sentinel_data = json.loads(sentinel_contents)
                            focus_phase = sentinel_data.get("phase") or fb_cfg.get(
                                "stop_after_phase", "PLANNING")
                        except json.JSONDecodeError:
                            focus_phase = fb_cfg.get(
                                "stop_after_phase", "PLANNING")

                        pr_msg = await self.request_feedback_from_self(
                            github_token=github_token,
                            feature_task_description=feature_task_description,
                            branch_prefix=fb_cfg.get(
                                "branch_prefix", "feature/orchestrator-"),
                            focus_phase=focus_phase,
                            open_router_api_key=open_router_api_key,
                            openai_api_key=openai_api_key,
                        )
                        return pr_msg
            except Exception:
                # Continue normal workflow if any issues
                pass

            # Get final status
            final_status = await agent.run("Provide the final orchestration status summary", deps=deps)

            out1 = result.output if hasattr(result, 'output') else str(result)
            out2 = final_status.output if hasattr(
                final_status, 'output') else str(final_status)

            return f"Workflow Result: {out1}\n\nFinal Status: {out2}"

        except Exception as e:
            return f"Error in orchestrated workflow: {e}"

    @function
    async def setup_environment(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to generate tests for")],
        branch: Annotated[str, Doc("Branch to generate tests for")] = "main",
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

            try:
                config_obj = YAMLConfig(**self.config)
            except Exception:
                config_obj = YAMLConfig(**{
                    "container": {"work_dir": "/src", "docker_file_path": None},
                    "git": {"user_name": "Test User", "user_email": "test@example.com", "base_pull_request_branch": "main"}
                })
            print(green("🔧 DEBUG: YAMLConfig created successfully"))

            print(green("🔧 DEBUG: Setting up repository"))
            source = (
                await dag.git(url=repository_url, keep_git_dir=True, http_auth_token=github_access_token)
                .branch(branch)
                .tree()
            )
            print(green("🔧 DEBUG: Repository source created"))

            print(green("🔧 DEBUG: About to build test container"))
            container = await dag.builder(self.config_file).build_test_environment(
                source=source,
                dockerfile_path=config_obj.container.docker_file_path,
                open_router_api_key=open_router_api_key,
                openai_api_key=openai_api_key,
                provider=provider,
            )
            print(green("Test environment container built successfully."))

            # Initialize .codebuff-state directory with required files
            container = container.with_new_file(".codebuff-state/log.txt", "")
            container = container.with_new_file(
                ".codebuff-state/feedback_sentinel.json", "{}")

            print(green("🔧 DEBUG: About to store container"))
            self.container = container
            print(green("🔧 DEBUG: Container stored successfully"))
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

    @function
    async def request_feedback(
        self,
        container: Annotated[dagger.Container, Doc("Container with repo context (post-setup_environment)")],
        github_token: Annotated[dagger.Secret, Doc("GitHub token for repo access")],
        feature_task_description: Annotated[str, Doc("Feature description to seed branch/PR")],
        branch_prefix: Annotated[str, Doc(
            "Prefix for working branches")] = "feature/orchestrator-",
        focus_phase: Annotated[str, Doc(
            "Current phase to reflect in commit/PR body")] = "PLANNING",
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter key")] = None,
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI key")] = None,
    ) -> str:
        """Persist current state, create/update working branch, and open/refresh a draft PR to collect user feedback.

        Notes:
        - This does not run heavy git commands here; builder + PR agent handle container auth and PR creation.
        - Writes .codebuff-state/feedback_request.json and commits it via the PR agent workflow.
        """
        try:
            # Persist request prompt to .codebuff-state for review in PR
            slug_base = "-".join(feature_task_description.lower().split()
                                 )[:48] or "feature"
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            branch_name = f"{branch_prefix}{slug_base}-{ts}"

            # Build a basic feedback request payload
            feedback_payload = {
                "phase": focus_phase,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "feature": feature_task_description,
                "proposed_branch": branch_name,
                "instructions": [
                    "Review the plan and selected files",
                    "Reply with @orchestrator approve | modify <instructions> | cancel",
                    "Optionally: @orchestrator add-files <paths> or revise-plan <changes>"
                ],
            }

            # Save .codebuff-state payloads into the container
            try:
                container = container.with_new_file(
                    ".codebuff-state/feedback_request.json",
                    json.dumps(feedback_payload, indent=2)
                )
                # Also set the sentinel to a non-empty value to trigger gates
                container = container.with_new_file(
                    ".codebuff-state/feedback_sentinel.json",
                    json.dumps({"phase": focus_phase, "requested": True,
                               "timestamp": feedback_payload["timestamp"]}, indent=2)
                )
            except Exception:
                pass

            # Prepare an authenticated container for PR ops using the builder module
            # Delegate to PR agent which handles branch create/push + PR creation per its template
            try:
                pull_request_container = await dag.builder(self.config_file).setup_pull_request_container(
                    base_container=container,
                    github_token=github_token
                )
                pr_agent = await dag.pull_request_agent(self.config_file).run(
                    provider="openrouter",
                    open_router_api_key=open_router_api_key,
                    container=pull_request_container
                )
                if pr_agent:
                    print(
                        green(f"Pull request agent executed: successfully created/updated PR."))
                else:
                    print(
                        red(f"Pull request agent execution failed or returned no result."))
            except Exception as e:
                # If PR tooling is not available, return a helpful message; branch can be created manually
                return (
                    f"Feedback request saved. Suggested branch: {branch_name}. "
                    f"PR agent unavailable: {e}"
                )

            return (
                f"Feedback requested via PR. Working branch: {branch_name}. "
                f"Check PR for instructions and reply with @orchestrator commands."
            )
        except Exception as e:
            return f"request_feedback failed: {e}"

    @function
    async def request_feedback_from_self(
        self,
        github_token: Annotated[dagger.Secret, Doc("GitHub token for repo access")],
        feature_task_description: Annotated[str, Doc("Feature description to seed branch/PR")],
        branch_prefix: Annotated[str, Doc(
            "Prefix for working branches")] = "feature/orchestrator-",
        focus_phase: Annotated[str, Doc(
            "Current phase to reflect in commit/PR body")] = "",
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter key")] = None,
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI key")] = None,
    ) -> str:
        """Same as request_feedback, but uses the stored self.container."""
        if self.container is None:
            return "request_feedback_from_self failed: container not initialized, run setup_environment first"

        # Get configured phase if focus_phase is empty
        if not focus_phase:
            fb_cfg = ((self.config.get("orchestrator", {}) or {}).get(
                "feedback", {}) or {}) if isinstance(self.config, dict) else {}
            focus_phase = fb_cfg.get("stop_after_phase", "PLANNING")

        return await self.request_feedback(
            container=self.container,
            github_token=github_token,
            feature_task_description=feature_task_description,
            branch_prefix=branch_prefix,
            focus_phase=focus_phase,
            open_router_api_key=open_router_api_key,
            openai_api_key=openai_api_key,
        )

    @function
    async def resume_workflow(
        self,
        github_token: Annotated[dagger.Secret, Doc("GitHub token for repo access")],
        repository_url: Annotated[str, Doc("GitHub repository URL")],
        branch_name: Annotated[str, Doc("Working branch to resume from")],
        provider: Annotated[str, Doc("LLM provider")] = "openrouter",
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter key")] = None,
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI key")] = None,
    ) -> str:
        """Recreate container from given branch, read .codebuff-state, and return a concise resume summary.

        This does not automatically continue the workflow; it prepares the state so orchestrator can proceed.
        """
        try:
            # Recreate repo source from the working branch
            src = (
                dag.git(url=repository_url, keep_git_dir=True,
                        http_auth_token=github_token)
                .branch(branch_name)
                .tree()
            )

            # Rebuild test environment using builder (mirrors setup_environment)
            try:
                cfg_obj = YAMLConfig(**self.config)
            except Exception:
                cfg_obj = YAMLConfig(**{
                    "container": {"work_dir": "/src", "docker_file_path": None},
                    "git": {"user_name": "Resumer", "user_email": "resume@example.com", "base_pull_request_branch": "main"}
                })

            container = await dag.builder(self.config_file).build_test_environment(
                source=src,
                dockerfile_path=cfg_obj.container.docker_file_path,
                open_router_api_key=open_router_api_key,
                openai_api_key=openai_api_key,
                provider=provider,
            )
            self.container = container

            # Load orchestration state from .codebuff-state with fallbacks
            state, report = await load_orchestration_state(container)
            self.container = container

            if state is None:
                # Fallback: try to read last commit message for metadata footer
                try:
                    last_commit = await self.container.with_exec(["bash", "-lc", "git log -1 --pretty=%B"]).stdout()
                except Exception:
                    last_commit = ""
                meta = extract_state_metadata(last_commit or "")
                meta_phase = (meta or {}).get(
                    "phase") if isinstance(meta, dict) else None
                meta_status = (meta or {}).get(
                    "status") if isinstance(meta, dict) else None
                return (
                    "Resumed from branch {b}. Missing critical state (task_spec). Loaded: {l}, Missing: {m}. Meta phase={p}, status={s}".format(
                        b=branch_name,
                        l=report.get("loaded", []),
                        m=report.get("missing", []),
                        p=meta_phase or "unknown",
                        s=meta_status or "unknown",
                    )
                )

            phase_val = getattr(state.current_phase, "value",
                                str(state.current_phase))
            return (
                "Resumed from branch {b}. Phase: {p}. Loaded: {l}, Missing: {m}".format(
                    b=branch_name, p=phase_val, l=report.get("loaded", []), m=report.get("missing", [])
                )
            )
        except Exception as e:
            return f"resume_workflow failed: {e}"

    @function
    async def continue_workflow(
        self,
        github_token: Annotated[dagger.Secret, Doc("GitHub token for repo access")],
        repository_url: Annotated[str, Doc("GitHub repository URL")],
        branch_name: Annotated[str, Doc("Working branch to continue from")],
        provider: Annotated[str, Doc("LLM provider")] = "openrouter",
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter key")] = None,
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI key")] = None,
    ) -> str:
        """Load state from .codebuff-state and continue the orchestration to the next phase.

        If container is not initialized, reconstruct it from the branch.
        """
        try:
            # Ensure container exists; if not, rebuild from branch (mirrors resume_workflow setup)
            if self.container is None:
                src = (
                    dag.git(url=repository_url, keep_git_dir=True,
                            http_auth_token=github_token)
                    .branch(branch_name)
                    .tree()
                )
                try:
                    cfg_obj = YAMLConfig(**self.config)
                except Exception:
                    cfg_obj = YAMLConfig(**{
                        "container": {"work_dir": "/src", "docker_file_path": None},
                        "git": {"user_name": "Resumer", "user_email": "resume@example.com", "base_pull_request_branch": "main"}
                    })
                self.container = await dag.builder(self.config_file).build_test_environment(
                    source=src,
                    dockerfile_path=cfg_obj.container.docker_file_path,
                    open_router_api_key=open_router_api_key,
                    openai_api_key=openai_api_key,
                    provider=provider,
                )

            # Load orchestration state
            state, report = await load_orchestration_state(self.container)
            if state is None:
                return (
                    "Continue failed: missing critical state (task_spec). Loaded: {l}, Missing: {m}".format(
                        l=report.get("loaded", []), m=report.get("missing", [])
                    )
                )

            # Prepare models for orchestrator + subagents
            orch_model = await self._get_llm_for_agent("orchestrator", open_router_api_key, openai_api_key)
            impl_model = await self._get_llm_for_agent("implementation", open_router_api_key, openai_api_key)
            picker_model = await self._get_llm_for_agent("file_picker", open_router_api_key, openai_api_key)
            explorer_model = await self._get_llm_for_agent("file_explorer", open_router_api_key, openai_api_key)
            reviewer_model = await self._get_llm_for_agent("reviewer", open_router_api_key, openai_api_key)

            # Build config (tolerant)
            try:
                cfg_obj = YAMLConfig(**self.config)
            except Exception:
                cfg_obj = YAMLConfig(**{
                    "container": {"work_dir": "/src", "docker_file_path": None},
                    "git": {"user_name": "Test User", "user_email": "test@example.com", "base_pull_request_branch": "main"}
                })

            # Check feedback gate before continuing
            sentinel = await load_feedback_sentinel(self.container)
            feedback = await load_user_feedback(self.container)
            if (sentinel.get("requested") is True) and not feedback:
                return "Feedback gate active for phase={p}. Waiting for PR feedback (@orchestrator approve/modify/cancel).".format(p=state.current_phase.value)
            if feedback:
                action = feedback.get("action")
                if action == "cancel":
                    return "Workflow canceled via PR feedback."
                if action in ("modify", "add-files", "revise-plan"):
                    return f"Received '{action}' request. Please run a plan/selection update step manually or implement automated handlers."
                # approve -> proceed

            # Assemble orchestrator deps with reconstructed state
            deps = OrchestratorDependencies(
                config=cfg_obj,
                config_file=self.config_file,
                container=self.container,
                github_token=github_token,
                api_key=openai_api_key or open_router_api_key,
                model=orch_model,
                implementation=impl_model,
                reviewer=reviewer_model,
                file_picker=picker_model,
                file_explorer=explorer_model,
                state=state,
            )

            agent = create_orchestrator_agent(orch_model)

            # Decide next tool based on current phase + status
            phase = state.current_phase
            status = state.status

            def decide_next(phase, status) -> tuple[str, str]:
                # returns (tool_name, prompt)
                if phase == Phase.EXPLORATION:
                    return ("create_implementation_plan", "Call create_implementation_plan now.") if status == Status.SUCCESS else ("explore_codebase", "Call explore_codebase now.")
                if phase == Phase.PLANNING:
                    return ("execute_implementation", "Call execute_implementation now.") if status == Status.SUCCESS else ("create_implementation_plan", "Call create_implementation_plan now.")
                if phase == Phase.IMPLEMENTATION:
                    return ("review_changes", "Call review_changes now.") if status == Status.SUCCESS else ("execute_implementation", "Call execute_implementation now.")
                if phase == Phase.REVIEW:
                    return ("create_pull_request", "Call create_pull_request now.") if status == Status.SUCCESS else ("review_changes", "Call review_changes now.")
                if phase == Phase.PULL_REQUEST:
                    return ("get_orchestration_status", "Call get_orchestration_status now.")
                # Default fallback
                return ("get_orchestration_status", "Call get_orchestration_status now.")

            tool, prompt = decide_next(phase, status)
            run_prompt = f"{prompt}"

            result = await agent.run(run_prompt, deps=deps)
            out = result.output if hasattr(result, "output") else str(result)

            phase_val = getattr(state.current_phase, "value",
                                str(state.current_phase))
            status_val = getattr(state.status, "value", str(state.status))
            return f"Continued from phase={phase_val} status={status_val}. Requested tool={tool}. Result: {out}"
        except Exception as e:
            return f"continue_workflow failed: {e}"

    @function
    async def process_pr_feedback(
        self,
        comments_json: Annotated[str, Doc("JSON array of PR comments {body, user{login}, created_at}")],
    ) -> str:
        """Parse PR comments for @orchestrator commands and persist to .codebuff-state/user_feedback.json."""
        try:
            comments = json.loads(comments_json or "[]")
            if not isinstance(comments, list):
                return "Error: comments_json must be a JSON array"
            cmd = parse_orchestrator_commands(comments)
            if not cmd:
                return "No @orchestrator commands found"
            if self.container is None:
                return "process_pr_feedback failed: container not initialized"
            self.container = await save_user_feedback(self.container, cmd)
            return f"Saved user_feedback.json: action={cmd.get('action')}"
        except Exception as e:
            return f"process_pr_feedback failed: {e}"

    @function
    async def process_orchestrator_command(

        self,
        github_token: Annotated[dagger.Secret, Doc("GitHub token for repo access")],
        repository_url: Annotated[str, Doc("GitHub repository URL")],
        branch: Annotated[str, Doc("Branch to work on")] = "main",
        command_text: Annotated[str, Doc("PR comment or command text")] = "",
        feature_task_description: Annotated[Optional[str], Doc(
            "Feature description override (optional)")] = None,
        provider: Annotated[str, Doc(
            "LLM provider ('openrouter' or 'openai')")] = "openrouter",
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None,
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None,
    ) -> str:
        """Process an '@orchestrator ...' command from a PR comment and perform the requested action.

        Currently supported:
        - "@orchestrator feature - kickoff feature-development-workflow"
          Kicks off the feature development workflow. The feature description is taken from the
          'feature_task_description' param if provided, otherwise defaults to 'Feature from PR'.
        """
        try:
            if not isinstance(command_text, str) or not command_text.strip():
                return "Error: Empty command text"

            text = command_text.strip().lower()
            if "@orchestrator" not in text:
                return "Ignored: not an orchestrator command"

            # General @orchestrator command parsing (approve|modify|cancel|add-files|revise-plan)
            try:
                from codebuff.orchestrator.pr_feedback import parse_orchestrator_commands, save_user_feedback
                parsed = parse_orchestrator_commands([{"body": command_text}])
            except Exception:
                parsed = None

            if parsed and isinstance(parsed, dict) and parsed.get("action"):
                if self.container is None:
                    return "process_orchestrator_command failed: container not initialized"
                self.container = await save_user_feedback(self.container, parsed)
                return f"Saved user_feedback.json: action={parsed.get('action')}"

            # Recognize: @orchestrator feature - kickoff feature-development-workflow
            if "feature" in text and "kickoff" in text and "feature-development-workflow" in text:
                desc = feature_task_description or "Feature from PR"
                # Use whichever provider key was provided
                provider = "openrouter" if open_router_api_key else (
                    "openai" if openai_api_key else provider)
                return await self.orchestrate_feature_development(
                    github_token=github_token,
                    feature_task_description=desc,
                    repository_url=repository_url,
                    branch=branch,
                    provider=provider,
                    focus_area="entire project",
                    openai_api_key=openai_api_key,
                    open_router_api_key=open_router_api_key
                )

            return "Unknown orchestrator command"
        except Exception as e:
            return f"process_orchestrator_command failed: {e}"


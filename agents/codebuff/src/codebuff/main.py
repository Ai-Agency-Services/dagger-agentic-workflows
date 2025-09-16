"""Main Dagger module orchestrating all Codebuff-equivalent agents."""

from typing import Annotated, Optional

import dagger
import yaml
from dagger import Doc, dag, function, object_type
from ais_dagger_agents_config import YAMLConfig

from codebuff.file_explorer.agent import create_file_explorer_agent, FileExplorerDependencies
from codebuff.file_picker.agent import create_file_picker_agent, FilePickerDependencies
from codebuff.thinker.agent import create_thinker_agent, ThinkerDependencies
from codebuff.implementation.agent import create_implementation_agent, ImplementationDependencies
from codebuff.reviewer.agent import create_reviewer_agent, ReviewerDependencies
from codebuff.context_pruner.agent import create_context_pruner_agent, ContextPrunerDependencies
from codebuff.utils import get_llm_credentials, create_llm_model


@object_type
class Codebuff:
    """Orchestrator for Codebuff-equivalent agents."""

    config: dict
    config_file: dagger.File

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("YAML configuration file")]
    ) -> "Codebuff":
        """Create orchestrator from configuration."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, config_file=config_file)

    @function
    async def explore_files(
        self,
        container: Annotated[dagger.Container, Doc("Container with source code")],
        focus_area: Annotated[str, Doc(
            "Area to focus exploration on")] = "entire project",
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None,
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None
    ) -> str:
        """Explore and map the codebase structure like Codebuff's File Explorer."""
        try:
            api_key = openai_api_key or open_router_api_key
            if not api_key:
                return "Error: No API key provided"

            creds = await get_llm_credentials(self.config, api_key, open_router_api_key is not None)
            model = create_llm_model(creds, "gpt-4o-mini")

            deps = FileExplorerDependencies(
                config=YAMLConfig(**self.config),
                container=container,
                focus_area=focus_area
            )

            agent = create_file_explorer_agent(model)
            result = await agent.run(
                f"Explore and map the codebase focusing on: {focus_area}",
                deps=deps
            )
            return result.data
        except Exception as e:
            return f"Error exploring files: {e}"

    @function
    async def pick_files(
        self,
        container: Annotated[dagger.Container, Doc("Container with source code")],
        task_description: Annotated[str, Doc("Description of the coding task")],
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None,
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None
    ) -> str:
        """Pick relevant files for a task like Codebuff's File Picker."""
        try:
            api_key = openai_api_key or open_router_api_key
            if not api_key:
                return "Error: No API key provided"

            creds = await get_llm_credentials(self.config, api_key, open_router_api_key is not None)
            model = create_llm_model(creds, "gpt-4o-mini")

            deps = FilePickerDependencies(
                config=YAMLConfig(**self.config),
                container=container,
                task_description=task_description
            )

            agent = create_file_picker_agent(model)
            result = await agent.run(
                f"Pick the most relevant files for: {task_description}",
                deps=deps
            )
            return result.data
        except Exception as e:
            return f"Error picking files: {e}"

    @function
    async def create_plan(
        self,
        container: Annotated[dagger.Container, Doc("Container with source code")],
        task_description: Annotated[str, Doc("High-level task to plan")],
        relevant_files: Annotated[str, Doc(
            "Comma-separated list of relevant files")] = "",
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None,
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None
    ) -> str:
        """Create an execution plan like Codebuff's Thinker/Planner agent."""
        try:
            api_key = openai_api_key or open_router_api_key
            if not api_key:
                return "Error: No API key provided"

            creds = await get_llm_credentials(self.config, api_key, open_router_api_key is not None)
            model = create_llm_model(creds, "gpt-4o")

            file_list = [f.strip() for f in relevant_files.split(
                ",") if f.strip()] if relevant_files else []

            deps = ThinkerDependencies(
                config=YAMLConfig(**self.config),
                container=container,
                task_description=task_description,
                relevant_files=file_list
            )

            agent = create_thinker_agent(model)
            result = await agent.run(
                f"Create a detailed plan for: {task_description}",
                deps=deps
            )
            return result.data
        except Exception as e:
            return f"Error creating plan: {e}"

    @function
    async def implement_plan(
        self,
        container: Annotated[dagger.Container, Doc("Container with source code")],
        plan: Annotated[str, Doc("Execution plan to implement")],
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None,
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None
    ) -> str:
        """Implement the plan like Codebuff's Implementation agent."""
        try:
            api_key = openai_api_key or open_router_api_key
            if not api_key:
                return "Error: No API key provided"

            creds = await get_llm_credentials(self.config, api_key, open_router_api_key is not None)
            model = create_llm_model(creds, "gpt-4o")

            deps = ImplementationDependencies(
                config=YAMLConfig(**self.config),
                container=container,
                plan=plan
            )

            agent = create_implementation_agent(model)
            result = await agent.run(
                f"Implement this plan: {plan[:200]}...",
                deps=deps
            )
            return result.data
        except Exception as e:
            return f"Error implementing plan: {e}"

    @function
    async def review_changes(
        self,
        container: Annotated[dagger.Container, Doc("Container with changes to review")],
        changes_description: Annotated[str, Doc("Description of what was changed")],
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None,
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None
    ) -> str:
        """Review code changes like Codebuff's Reviewer agent."""
        try:
            api_key = openai_api_key or open_router_api_key
            if not api_key:
                return "Error: No API key provided"

            creds = await get_llm_credentials(self.config, api_key, open_router_api_key is not None)
            model = create_llm_model(creds, "gpt-4o")

            deps = ReviewerDependencies(
                config=YAMLConfig(**self.config),
                container=container,
                changes_description=changes_description
            )

            agent = create_reviewer_agent(model)
            result = await agent.run(
                f"Review these changes: {changes_description}",
                deps=deps
            )
            return result.data
        except Exception as e:
            return f"Error reviewing changes: {e}"

    @function
    async def prune_context(
        self,
        container: Annotated[dagger.Container, Doc("Container for context")],
        context_data: Annotated[str, Doc("Context data to prune")],
        max_tokens: Annotated[int, Doc("Maximum tokens to keep")] = 4000,
        strategy: Annotated[str, Doc(
            "Pruning strategy: smart, truncate, summarize, sections")] = "smart",
        openai_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenAI API key")] = None,
        open_router_api_key: Annotated[Optional[dagger.Secret], Doc(
            "OpenRouter API key")] = None
    ) -> str:
        """Prune context like Codebuff's Context Pruner agent."""
        try:
            api_key = openai_api_key or open_router_api_key
            if not api_key:
                return "Error: No API key provided"

            creds = await get_llm_credentials(self.config, api_key, open_router_api_key is not None)
            model = create_llm_model(creds, "gpt-4o-mini")

            deps = ContextPrunerDependencies(
                config=YAMLConfig(**self.config),
                container=container,
                context_data=context_data,
                max_tokens=max_tokens
            )

            agent = create_context_pruner_agent(model)
            result = await agent.run(
                f"Prune context using {strategy} strategy to fit {max_tokens} tokens",
                deps=deps
            )
            return result.data
        except Exception as e:
            return f"Error pruning context: {e}"

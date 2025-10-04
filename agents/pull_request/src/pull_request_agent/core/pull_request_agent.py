from dataclasses import dataclass
from typing import Optional

import dagger
from ais_dagger_agents_config import YAMLConfig
from pull_request_agent.template import get_pull_request_agent_template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from datetime import datetime
from simple_chalk import yellow


@dataclass
class PullRequestAgentDependencies:
    config: YAMLConfig
    container: dagger.Container
    error_context: Optional[str] = None
    insight_context: Optional[str] = None


async def run_command(ctx: RunContext[PullRequestAgentDependencies], command: list[str]) -> str:
    """
    Run a command in the container and return the output.
    """
    try:
        # Branch safety guard: never commit/push on protected base branches
        base_branch = None
        try:
            git_cfg = getattr(ctx.deps.config, 'git', None)
            if git_cfg:
                base_branch = getattr(git_cfg, 'base_pull_request_branch', None) or getattr(git_cfg, 'default_branch', None)
        except Exception:
            base_branch = None
        if not base_branch:
            base_branch = 'develop'
        # Read cloned source branch; treat as protected too
        source_branch = None
        try:
            sb_raw = await ctx.deps.container.file(".codebuff-state/source_branch.json").contents()
            if sb_raw:
                import json as _json
                source_branch = (_json.loads(sb_raw) or {}).get("source_branch")
        except Exception:
            source_branch = None

        protected = {base_branch, 'main', 'master', 'develop'}
        if source_branch:
            protected.add(source_branch)

        # Check current branch
        try:
            current_branch = await ctx.deps.container.with_exec(["bash", "-c", "git rev-parse --abbrev-ref HEAD"]).stdout()
            current_branch = (current_branch or '').strip()
        except Exception:
            current_branch = ''

        # If this command will commit or push and we're on a protected branch, switch first
        cmd_str = " ".join(command) if isinstance(command, list) else str(command)
        needs_branch = ("git commit" in cmd_str) or ("git push" in cmd_str)
        if needs_branch:
            if not current_branch or current_branch in protected:
                # Determine branch prefix
                branch_prefix = 'feature/codebuff-'
                try:
                    orch = getattr(ctx.deps.config, 'orchestrator', None)
                    if orch:
                        branch_prefix = getattr(orch, 'branch_prefix', branch_prefix) or branch_prefix
                except Exception:
                    pass
                safe_branch = f"{branch_prefix}{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                ctx.deps.container = ctx.deps.container.with_exec(["bash", "-c", f"git checkout -b {safe_branch}"])

        # Add debug for push commands
        if len(command) >= 3 and "git push" in command[2]:
            print(yellow("Detected push command, adding debug info..."))

            # Get branch info
            branch_info = await ctx.deps.container.with_exec(["bash", "-c", "git branch -vv"]).stdout()
            print(yellow(f"Branch info before push:\n{branch_info}"))

            # Get git status
            status = await ctx.deps.container.with_exec(["bash", "-c", "git status"]).stdout()
            print(yellow(f"Git status before push:\n{status}"))

            # Use more robust push command instead
            branch_name = await ctx.deps.container.with_exec(["bash", "-c", "git rev-parse --abbrev-ref HEAD"]).stdout()
            branch_name = branch_name.strip()
            print(yellow(f"Current branch: {branch_name}"))

            # Replace with better push command
            command = ["bash", "-c",
                       f"git push --set-upstream origin {branch_name} --force"]
            print(yellow(f"Using modified push command: {command}"))

        # Make sure we're getting a properly formatted command
        if len(command) < 3 or command[0] != "bash" or command[1] != "-c":
            # If not formatted correctly, log and fix it
            print(
                yellow(f"Warning: Command not properly formatted: {command}"))
            # Try to convert it to the correct format
            if len(command) == 1:
                # Single string command
                command = ["bash", "-c", command[0]]
            else:
                # Join multiple arguments into a single command
                command = ["bash", "-c", " ".join(command)]
            print(yellow(f"Reformatted command: {command}"))

        # Execute the command and get the container
        container_with_exec = ctx.deps.container.with_exec(command)
        # Extract stdout as a string
        stdout = await container_with_exec.stdout()
        # Update the container in deps
        ctx.deps.container = container_with_exec
        # Return the command output
        return stdout
    except Exception as e:
        return f"Error running command '{command}': {e}"


def create_pull_request_agent(pydantic_ai_model: OpenAIModel) -> Agent:
    """
    Create and configure a pydantic_ai.Agent instance for code review and test generation.

    Args:
        pydantic_ai_model: An instance of pydantic_ai.models.OpenAIModel
                           configured with the desired provider and API key.

    Returns:
        A configured pydantic_ai.Agent instance.
    """

    base_system_prompt = get_pull_request_agent_template()

    agent = Agent(
        model=pydantic_ai_model,
        system_prompt=base_system_prompt,
        deps_type=PullRequestAgentDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=15,
        output_type=str,
        result_retries=100
    )

    agent.tool(run_command)

    print(
        f"CoverAI pull request Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Export necessary components
__all__ = ["create_pull_request_agent", "PullRequestAgentDependencies"]

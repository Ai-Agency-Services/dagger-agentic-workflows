from dataclasses import dataclass
from typing import Optional

import dagger
from ais_dagger_agents_config import YAMLConfig
from pull_request_agent.template import get_pull_request_agent_template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
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

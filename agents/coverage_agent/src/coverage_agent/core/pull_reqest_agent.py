from dataclasses import dataclass
from typing import TYPE_CHECKING

import dagger
from coverage_agent.models.config import YAMLConfig
from coverage_agent.template import get_pull_request_agent_template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, red, yellow


@dataclass
class PullRequestAgentDependencies:
    config: YAMLConfig
    container: dagger.Container


async def run_command(ctx: RunContext[PullRequestAgentDependencies], command: str) -> str:
    """
    Run a command in the container and return the output.
    Args:  
        ctx: The run context containing the container and config.
        command: The command to run in the container.
    Returns:
        The output of the command.

    """

    try:
        return await ctx.deps.container.with_exec([command])
    except Exception as e:
        return f"Error running command'{command}': {e}"


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
        retries=5
    )

    agent.tool(run_command)

    print(
        f"CoverAI pull request Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Export necessary components
__all__ = ["create_pull_request_agent", "PullRequestAgentDependencies"]

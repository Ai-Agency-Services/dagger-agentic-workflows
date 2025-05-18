from dataclasses import dataclass
from typing import List

import dagger
from clean.core.rag_naming_agent import RenameCandidate
from clean.template import get_meaningful_names_agent_template
from pydantic_ai import Agent, RunContext


@dataclass
class MeaningfulNamesAgentDependencies:
    container: dagger.Container
    rename_candidates: List[RenameCandidate]
    file_path: str


def create_meaningful_names_agent(
    pydantic_ai_model: Agent,
) -> Agent:
    """
    Create an agent for refactoring code to use meaningful names.
    """
    base_system_prompt = get_meaningful_names_agent_template()

    agent = Agent(
        model=pydantic_ai_model,
        system_prompt=base_system_prompt,
        deps_type=MeaningfulNamesAgentDependencies,
        instrument=True,
        end_strategy="exhaustive",
        output_type=str  # Returns refactored code content
    )

    # Add tools for the agent
    agent.tool(read_file)
    agent.tool(write_file)

    return agent


async def read_file(
    ctx: RunContext[MeaningfulNamesAgentDependencies],
    file_path: str = None
) -> str:
    """
    Read the content of a file from the container.
    """
    path = file_path or ctx.deps.file_path
    try:
        content = await ctx.deps.container.with_exec(
            ["cat", path]
        ).stdout()
        return content
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return ""


async def write_file(
    ctx: MeaningfulNamesAgentDependencies,
    file_path: str,
    content: str
) -> bool:
    """
    Write content to a file in the container.
    """
    try:
        result = await ctx.container.with_new_file(file_path, content).with_exec(
            ["test", "-f", file_path]
        ).exit_code()
        return result == 0
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

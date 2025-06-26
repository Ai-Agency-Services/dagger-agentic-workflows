from dataclasses import dataclass
from typing import Optional

import dagger
from ais_dagger_agents_config import YAMLConfig
from documenter.template import get_documenter_agent_template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import yellow


@dataclass
class DocumenterAgentDependencies:
    container: dagger.Container
    config: YAMLConfig
    error_context: Optional[str] = None
    insight_context: Optional[str] = None
    
async def scan_agents_directory(ctx: RunContext[DocumenterAgentDependencies], directory: str = "agents") -> str:
    """
    Scan the specified directory for Python files containing agent definitions.

    Args:
        ctx: The run context containing the container and agent dependencies.
        directory: The path to the agents directory inside the container (default: "agents").

    Returns:
        A string containing the source code of all found Python agent files.
    """

    print(f"Scanning directory inside container: {directory}")
    print(f"Found files:\n{files}")
    
    # Use 'find' to locate all Python files under the directory
    find_command = ["bash", "-c", f"find {directory} -type f -name '*.py'"]
    files = await run_command(ctx, find_command)

    if not files.strip():
        return f"No Python files found in {directory}"

    results = []

    # Loop through each file path returned and read its contents using 'cat'
    for file_path in files.strip().split('\n'):
        cat_command = ["bash", "-c", f"cat {file_path}"]
        content = await run_command(ctx, cat_command)
        results.append(f"File: {file_path}\n{content}\n")

    return "\n".join(results)

# Add the new functions to the agent's tools
def create_documenter_agent(pydantic_ai_model: OpenAIModel) -> Agent:
    """
    Create and configure a pydantic_ai.Agent instance for documentation generation and update.
    
    Args:
        pydantic_ai_model: An instance of pydantic_ai.models.OpenAIModel
                           configured with the desired provider and API key.
    
    Returns:
        A configured pydantic_ai.Agent instance.
    """
    
    base_system_prompt = get_documenter_agent_template()
    
    agent = Agent(
        model=pydantic_ai_model,
        system_prompt=base_system_prompt,
        deps_type=DocumenterAgentDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=15,
        output_type=str,
        result_retries=100
    )
    
    # Register all tools
    agent.tool(run_command)
    agent.tool(scan_agents_directory)
    
    print(f"DocumenterAI Agent created with model: {pydantic_ai_model.model_name}")
    return agent

# Update exports
__all__ = ["create_documenter_agent", "DocumenterAgentDependencies", 
           "scan_agents_directory", "document_agent"]


async def run_command(ctx: RunContext[DocumenterAgentDependencies], command: list[str]) -> str:
    """
    Run a command in the container and return the output.
    Args:  
        ctx: The run context containing the container and config.
        command: The command to run in the container.
    Returns:
        The output of the command.
    """
    try:
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
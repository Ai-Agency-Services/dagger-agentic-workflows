from dataclasses import dataclass

import dagger
from builder.template import get_container_builder_template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import yellow


@dataclass
class BuilderAgentDependencies:
    container: dagger.Container


dependencies: list[str] = [
    "git",
    "bash",
    "gh",
    "tree",
]


async def add_required_dependencies_prompt() -> str:
    """ System Prompt: Get the required dependencies content. """
    try:
        required_dependencies = "\n".join(dependencies)
        return f"Please install the following dependencies: {required_dependencies}"
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        raise


async def run_command(ctx: RunContext[BuilderAgentDependencies], command: list[str]) -> str:
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


def create_builder_agent(pydantic_ai_model: OpenAIModel) -> Agent:

    base_system_prompt = get_container_builder_template()

    agent = Agent(
        model=pydantic_ai_model,
        system_prompt=base_system_prompt,
        deps_type=BuilderAgentDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=15,
        output_type=str,
        result_retries=100,
    )

    agent.system_prompt(add_required_dependencies_prompt)
    agent.tool(run_command)
    print(f"Builder agent created with model: {pydantic_ai_model.model_name}")

    # Add this line to fix the missing return
    return agent


__all__ = ["create_builder_agent", "BuilderAgentDependencies"]

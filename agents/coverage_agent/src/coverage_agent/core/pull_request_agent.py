from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import dagger
from coverage_agent.models.config import YAMLConfig
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.template import get_pull_request_agent_template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, red, yellow

if TYPE_CHECKING:
    from dagger.client.gen import \
        Reporter


@dataclass
class PullRequestAgentDependencies:
    config: YAMLConfig
    container: dagger.Container
    reporter: 'Reporter'  # Assuming Reporter is defined elsewhere
    report: CoverageReport
    error_context: Optional[str] = None  # For failed test generation
    insight_context: Optional[str] = None  # For no coverage increase


async def get_code_under_test_prompt(ctx: RunContext[PullRequestAgentDependencies]) -> str:
    """ System Prompt: Get the code under test from the coverage report """
    try:
        coverage_report_html = await ctx.deps.reporter.get_coverage_html(
            html_report_path=ctx.deps.report.coverage_report_path,
            test_container=ctx.deps.container)
        code_under_test = await ctx.deps.reporter.get_code_under_test(coverage_report_html)
        return f"""
                    \n ------- \n
                    <code_under_test> \n
                    {code_under_test}
                    </code_under_test> \n
                    \n ------- \n
                """
    except Exception as e:
        print(f"Error in get_code_under_test_prompt: {e}")
        return "\n ------- \n <code_under_test>Error retrieving code under test.</code_under_test> \n ------- \n"


async def add_coverage_report_prompt(ctx: RunContext[PullRequestAgentDependencies]) -> str:
    """ System Prompt: Get the coverage report content. """
    try:
        coverage_report_html = await ctx.deps.reporter.get_coverage_html(
            html_report_path=ctx.deps.report.coverage_report_path,
            test_container=ctx.deps.container)
        return f"""
                    \n ------- \n
                    <coverage_report_html> \n
                    {coverage_report_html}
                    </coverage_report_html> \n
                    \n ------- \n
                """
    except Exception as e:
        print(f"Error in add_coverage_report_prompt: {e}")
        return "\n ------- \n <coverage_report_html>Error retrieving coverage report.</coverage_report_html> \n ------- \n"


async def run_command(ctx: RunContext[PullRequestAgentDependencies], command: list[str]) -> str:
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

    agent.system_prompt(get_code_under_test_prompt)
    agent.system_prompt(add_coverage_report_prompt)
    agent.tool(run_command)

    print(
        f"CoverAI pull request Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Export necessary components
__all__ = ["create_pull_request_agent", "PullRequestAgentDependencies"]

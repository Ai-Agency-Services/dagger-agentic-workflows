import os
from dataclasses import dataclass
from typing import TYPE_CHECKING  # Use for type hinting Reporter if needed

import dagger
from coverage_agent.core.test_file_handler import TestFileHandler
from coverage_agent.models.code_module import CodeModule
from coverage_agent.models.config import YAMLConfig
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.template import get_system_template
from coverage_agent.utils import get_code_under_test_directory
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel  # Use the specific model type

# Conditional import for Reporter type hint if it's complex
if TYPE_CHECKING:
    from dagger.client.gen import \
        Reporter  # Or your custom Reporter class path


@dataclass
class Dependencies:
    config: YAMLConfig
    container: dagger.Container
    report: CoverageReport
    reporter: 'Reporter'


async def get_code_under_test_prompt(ctx: RunContext[Dependencies]) -> str:
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


async def add_coverage_report_prompt(ctx: RunContext[Dependencies]) -> str:
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


async def add_directories_prompt(ctx: RunContext[Dependencies]) -> str:
    """ System Prompt: Get the directory structure associated with the code under test."""
    try:
        code_file_path = ctx.deps.report.file
        directories_output = await ctx.deps.container.with_exec(
            ["find", ".", "-path", f"*/{os.path.basename(code_file_path)}"]
        ).stdout()
        found_path = directories_output.strip().split(
            '\n')[0] if directories_output.strip() else "Not Found"

        code_under_test_directory = await get_code_under_test_directory(
            ctx.deps.container, report=ctx.deps.report
        )

        current_directory = (
            code_under_test_directory
            if ctx.deps.config.test_generation.save_next_to_code_under_test
            else ctx.deps.config.test_generation.test_directory
        )

        return f"""
                    \n ------- \n
                    <directories> \n
                    Your current target directory for writing tests is: {current_directory} \n
                    The code_under_test file path is approximately: {found_path}
                    </directories> \n
                    \n ------- \n
                """
    except Exception as e:
        print(f"Error in add_directories_prompt: {e}")
        return "\n ------- \n <directories>Error retrieving directory information.</directories> \n ------- \n"

# --- Define Agent Tools (Standalone) ---
async def read_file_tool(ctx: RunContext[Dependencies], path: str) -> str:
    """Tool: Read the contents of a file in the workspace.
    Args:
        path: The path to the file to read.
    """
    try:
        return await ctx.deps.container.file(path).contents()
    except Exception as e:
        return f"Error reading file '{path}': {e}"


async def write_test_file_tool(ctx: RunContext[Dependencies], contents: str) -> str:
    """Tool: Write a new test file to the container using TestFileHandler.
    Args:
        contents: The code content to write to the file.
    """
    try:
        test_file_handler = TestFileHandler(ctx.deps.config)
        updated_container = await test_file_handler.handle_test_file(
            container=ctx.deps.container,
            code=contents,
            report=ctx.deps.report,
        )
        ctx.deps.container = updated_container
        file_written = test_file_handler.file_name
        save_dir = test_file_handler.get_save_path(
            await get_code_under_test_directory(ctx.deps.container, ctx.deps.report)
        )
        return f"Successfully wrote content to {save_dir}/{file_written}."
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error writing test file: {e}"


async def run_tests_tool(ctx: RunContext[Dependencies]) -> str:
    """Tool: Attempt to run all of the unit tests in the container using the configured command."""
    try:
        test_command = ctx.deps.config.reporter.command
        result_container = await ctx.deps.container.with_exec(["bash", "-c", f"{test_command}; echo -n $? > /exit_code"])
        stdout = await result_container.stdout()
        stderr = await result_container.stderr()
        return f"Test Run STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    except Exception as e:
        return f"Error running tests: {e}"

# --- Factory Function ---


def create_coverai_agent(pydantic_ai_model: OpenAIModel) -> Agent:
    """
    Creates and configures the CoverAI agent instance.

    Args:
        pydantic_ai_model: An instance of pydantic_ai.models.OpenAIModel
                           configured with the desired provider and API key.

    Returns:
        A configured pydantic_ai.Agent instance.
    """

    base_system_prompt = get_system_template()

    agent = Agent(
        model=pydantic_ai_model,
        output_type=CodeModule,
        system_prompt=base_system_prompt,
        deps_type=Dependencies
    )

    agent.system_prompt(get_code_under_test_prompt)
    agent.system_prompt(add_coverage_report_prompt)
    agent.system_prompt(add_directories_prompt)

    agent.tool(read_file_tool)
    agent.tool(write_test_file_tool)
    agent.tool(run_tests_tool)

    print(f"CoverAI Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Export necessary components
__all__ = ["create_coverai_agent", "Dependencies"]

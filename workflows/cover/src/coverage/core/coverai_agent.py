import json
import os
import traceback
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Annotated, Optional

import dagger
from coverage.core.test_file_handler import TestFileHandler
from coverage.models.code_module import CodeModule
from ais_dagger_agents_config import YAMLConfig
from coverage.models.coverage_report import CoverageReport
from coverage.template import get_system_template
from coverage.utils import get_code_under_test_directory
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import \
    OpenAIModel  # Use the specific model type
from simple_chalk import red, yellow, blue

# Conditional import for Reporter type hint if it's complex
if TYPE_CHECKING:
    from dagger.client.gen import \
        Reporter  # Or your custom Reporter class path


@dataclass
class CoverAgentDependencies:
    config: YAMLConfig
    container: dagger.Container
    report: CoverageReport
    reporter: 'Reporter'
    current_code_module: Optional[CodeModule] = field(default=None)


async def get_code_under_test_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
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


async def add_coverage_report_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
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


async def add_directories_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """
    System Prompt: Get the directory structure context, target test directory,
    and approximate path for the code under test.
    """
    dir_context = "<directories>\n"
    try:
        code_file_path = ctx.deps.report.file
        code_under_test_dir = await get_code_under_test_directory(
            ctx.deps.container, report=ctx.deps.report
        )

        # Construct the approximate full path
        found_path = os.path.join(code_under_test_dir, os.path.basename(
            code_file_path)) if code_under_test_dir != "." else f"./{os.path.basename(code_file_path)} (approx)"

        # Determine target directory for writing tests
        target_test_directory = (
            code_under_test_dir  # Use the found directory if saving next to code
            if ctx.deps.config.test_generation.save_next_to_code_under_test
            else ctx.deps.config.test_generation.test_directory
        )

        dir_context += f"  Target directory for writing tests: {target_test_directory}\n"
        dir_context += f"  Code under test file path (approximate): {found_path}\n"

        # Add directory tree structure around the code under test
        try:
            # Limit depth to avoid excessive output (e.g., depth 3)
            # Use tree if available, otherwise fallback to find
            tree_cmd = ["tree", "-L", "3", code_under_test_dir]
            find_cmd = ["find", code_under_test_dir,
                        "-maxdepth", "3", "-print"]

            # Try tree first
            tree_exec = ctx.deps.container.with_exec(
                tree_cmd)
            tree_stdout = await tree_exec.stdout()
            dir_context += f"\n  Directory structure near code under test ({code_under_test_dir}):\n"
            dir_context += f"```\n{tree_stdout.strip()}\n```\n"
        except dagger.ExecError:
            # Fallback to find if tree fails (e.g., not installed)
            print(yellow(
                "`tree` command failed or not found, falling back to `find` for directory structure."))
            try:
                find_exec = ctx.deps.container.with_exec(
                    find_cmd)
                find_stdout = await find_exec.stdout()
                dir_context += f"\n  Directory structure near code under test ({code_under_test_dir}):\n"
                dir_context += f"```\n{find_stdout.strip()}\n```\n"
            except Exception as find_err:
                print(red(f"Fallback `find` command also failed: {find_err}"))
                dir_context += "\n  (Could not retrieve directory structure)\n"
        except Exception as tree_err:
            print(
                red(f"Error getting directory structure with tree: {tree_err}"))
            dir_context += "\n  (Could not retrieve directory structure)\n"

        dir_context += "</directories>"
        return f"\n ------- \n{dir_context}\n ------- \n"

    except Exception as e:
        print(red(f"Error in add_directories_prompt: {e}"))
        traceback.print_exc()  # Add traceback for debugging
        dir_context += "\n  Error retrieving directory information.\n</directories>"
        return f"\n ------- \n{dir_context}\n ------- \n"


async def add_dependency_files_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """
    System Prompt: Provide content of the first common dependency management file found.
    """
    dep_context = "<project_dependencies>\n"
    found_file = None  # Track if a file was found
    common_dep_files = [
        "package.json",   # Node.js
        "requirements.txt",
        "pyproject.toml",  # Common in Python
        "go.mod",         # Go
        "pom.xml",        # Maven (Java)
        "build.gradle",   # Gradle (Java/Kotlin)
        "Gemfile",        # Ruby
        "composer.json",  # PHP
        # Add others if relevant (*.csproj for .NET, etc.)
    ]

    work_dir = ctx.deps.config.container.work_dir

    for filename in common_dep_files:
        file_path = os.path.join(work_dir, filename)
        try:
            # Attempt ls, catch ExecError if file not found
            check_cmd = ["ls", "-d", file_path]
            # Removed skip_entrypoint=True
            check_exec = ctx.deps.container.with_exec(check_cmd)
            await check_exec.stdout()  # Raises ExecError if ls fails

            # If stdout() succeeded, the file exists. Proceed to read.
            try:
                print(
                    blue(f"Found dependency file: {filename}. Reading content..."))
                content = await ctx.deps.container.file(file_path).contents()
                dep_context += f"\n--- {filename} ---\n"
                # Limit content length for prompt context
                # Limit to 1000 chars
                dep_context += f"```\n{content.strip()[:1000]}\n```\n"
                found_file = filename  # Mark that we found a file
                break  # *** Exit the loop after finding the first file ***
            except Exception as read_err:
                print(red(
                    f"Error reading dependency file '{filename}' after existence check: {read_err}"))
                dep_context += f"\n--- {filename} ---\nError reading file after check.\n"
                # Optionally break here too if reading fails, or continue searching
                # break

        except dagger.ExecError as ls_err:
            # ls failed, likely because the file doesn't exist
            if "No such file or directory" in str(ls_err) or ls_err.exit_code == 2:
                pass  # Expected, continue to the next filename
            else:
                print(
                    red(f"Unexpected error checking for dependency file '{filename}': {ls_err}"))
                dep_context += f"\n--- {filename} ---\nError checking file existence.\n"
        except Exception as e:
            print(
                red(f"Unexpected error processing dependency file '{filename}': {e}"))
            dep_context += f"\n--- {filename} ---\nUnexpected error.\n"

    if not found_file:  # Check if any file was found
        dep_context += "No common dependency files found.\n"

    dep_context += "</project_dependencies>"
    return f"\n ------- \n{dep_context}\n ------- \n"


async def add_current_code_module_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """ System Prompt: Get the current code module and any previous errors, if they exist. """
    try:
        if ctx.deps.current_code_module:
            # Start with the code module part
            prompt_string = f"""
                        \n ------- \n
                        <current_code_module> \n
                        {ctx.deps.current_code_module.code}
                        </current_code_module> \n
                        \n ------- \n
                    """
            # Conditionally add the error block if an error exists
            if ctx.deps.current_code_module.error:
                prompt_string += f"""
                        \n ------- \n
                        <resulting_errors>
                        \n --- --- --- \n You previously tried to increase code coverage using the current_code_module.
                        \n --- --- --- \n Here is the resulting error from your solution: {ctx.deps.current_code_module.error}
                        \n --- --- --- \n Your task is to correct the errors with a new solution for the code_under_test to increase code coverage.
                        </resulting_errors>
                        \n -------- \n
                    """
            return prompt_string
        else:
            # No previous code module, return a simple message
            return "\n ------- \n <current_code_module>No current code module available. Generate the first set of tests.</current_code_module> \n ------- \n"
    except Exception as e:
        print(f"Error in add_current_code_module_prompt: {e}")
        return "\n ------- \n <current_code_module>Error retrieving current code module.</current_code_module> \n ------- \n"


# Keep this as a system prompt function
async def find_symbol_references_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """
    System Prompt: Provide context about potential references to the file under test.
    Uses ripgrep (rg) for searching. Ensure 'ripgrep' is installed in the container.

    Returns:
        A string containing a summary of potential references found, formatted for the system prompt,
        or an error message.
    """
    try:
        # Get the filename from the report
        code_file_path = ctx.deps.report.file
        # Use the filename (without path) as the search term.
        # This is a simple text search, not a true symbol search.
        search_term = os.path.basename(code_file_path)
        # Define the search directory (e.g., the configured workdir)
        search_dir = ctx.deps.config.container.work_dir

        # Use --json for structured output, -- for safety with terms starting with '-'
        # Add --case-sensitive if needed
        rg_command = ["rg", "--json", "--", search_term, search_dir]

        # Ensure all items in rg_command are strings before joining for the print statement
        rg_command_str_list = [str(item) for item in rg_command]
        print(yellow(
            f"Running reference search for prompt context: {' '.join(rg_command_str_list)}"))

        # Execute the command
        result_container = await ctx.deps.container.with_exec(rg_command)

        # Get stdout (JSON lines) and stderr
        stdout = await result_container.stdout()
        stderr = await result_container.stderr()

        if stderr:
            # rg often prints 'no matches found' to stderr, which isn't a true error
            if "No files were searched" not in stderr and "No matches found" not in stderr:
                print(
                    red(f"ripgrep stderr (for prompt context): {stderr.strip()}"))
                # Decide if stderr indicates a real error or just no matches/files searched

        # Process the JSON Lines output
        matches = []
        if stdout:
            for line in stdout.strip().split('\n'):
                try:
                    match_data = json.loads(line)
                    if match_data.get("type") == "match":
                        file_path = match_data.get(
                            "data", {}).get("path", {}).get("text")
                        line_num = match_data.get(
                            "data", {}).get("line_number")
                        line_text = match_data.get("data", {}).get(
                            "lines", {}).get("text", "").strip()
                        if file_path and line_num:
                            # Format for readability in the prompt
                            matches.append(
                                f"  - {file_path} (Line {line_num}): {line_text}")
                except json.JSONDecodeError:
                    print(
                        red(f"Failed to parse rg JSON line (for prompt context): {line}"))

        # Format the results for the system prompt
        if not matches:
            references_context = f"No potential references found for the filename '{search_term}' in '{search_dir}' (excluding the file itself)."
        else:
            references_context = f"Potential references to the filename '{search_term}' found in other files:\n" + "\n".join(
                matches)
            # Limit output length if necessary for the prompt context
            # Limit response size
            references_context = references_context[:2000]

        # Wrap in tags for clarity in the overall system prompt
        return f"""
                    \n ------- \n
                    <symbol_references_context> \n
                    {references_context}
                    </symbol_references_context> \n
                    \n ------- \n
                """

    except Exception as e:
        traceback.print_exc()
        error_message = f"Error running ripgrep to find references for prompt context ('{search_term}'): {e}"
        print(red(error_message))
        # Return an error message within the tags for the prompt
        return f"""
                    \n ------- \n
                    <symbol_references_context> \n
                    {error_message}
                    </symbol_references_context> \n
                    \n ------- \n
                """


# --- Define Agent Tools (Standalone) ---
async def read_file_tool(ctx: RunContext[CoverAgentDependencies], path: str) -> str:
    """Tool: Read the contents of a file in the workspace. Useful for reading reference files or test files.
    Args:
        path: The path to the file to read.
    """
    try:
        return await ctx.deps.container.file(path).contents()
    except Exception as e:
        return f"Error reading file '{path}': {e}"


async def write_test_file_tool(ctx: RunContext[CoverAgentDependencies], contents: str) -> str:
    """Tool: Write a new test file to the container using TestFileHandler.
    Args:
        contents: The code content to write to the file.
    """
    try:
        test_file_handler = TestFileHandler(ctx.deps.config)
        ctx.deps.current_code_module = CodeModule(
            code=contents
        )
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
        traceback.print_exc()
        return f"Error writing test file: {e}"


async def run_tests_tool(ctx: RunContext[CoverAgentDependencies]) -> str:
    """Tool: Attempt to run all of the unit tests in the container using the configured command.

    This tool is part of the agent's self-correction loop.
    It executes the tests generated in the previous step.
    If errors occur, they are captured and stored in `ctx.deps.current_code_module.error`.
    The `add_current_code_module_prompt` will then feed this error back to the LLM
    in the next iteration, asking it to correct the generated code.
    """
    try:
        test_command = ctx.deps.config.reporter.command
        result_container = await ctx.deps.container.with_exec(["bash", "-c", f"{test_command}; echo -n $? > /exit_code"])
        test_results = await result_container.file(
            f"{ctx.deps.config.reporter.output_file_path}"
        ).contents()

        error = await ctx.deps.reporter.parse_test_results(test_results)
        if error:
            # Store the error for the next iteration's system prompt (self-correction)
            if ctx.deps.current_code_module:
                ctx.deps.current_code_module.error = error
            else:
                # Should ideally not happen if write_test_file_tool was called first,
                # but handle defensively.
                print(yellow(
                    "Warning: run_tests_tool executed without a current_code_module being set."))
            # Return the error message to the agent/user
            return f"Test Run Failed: {error}"
        else:
            # Tests passed, clear any previous error
            if ctx.deps.current_code_module:
                ctx.deps.current_code_module.error = None
            return "Test Run Succeeded."

    except Exception as e:
        # Handle unexpected errors during test execution itself (not test failures)
        error_msg = f"Error running tests: {e}"
        # Store the error for the next iteration's system prompt
        if ctx.deps.current_code_module:
            ctx.deps.current_code_module.error = error_msg
        traceback.print_exc()
        return error_msg


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
        deps_type=CoverAgentDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=5,
        result_retries=3
    )

    agent.system_prompt(get_code_under_test_prompt)
    agent.system_prompt(add_coverage_report_prompt)
    agent.system_prompt(add_directories_prompt)
    agent.system_prompt(add_current_code_module_prompt)
    agent.system_prompt(add_dependency_files_prompt)

    agent.tool(read_file_tool)
    agent.tool(write_test_file_tool)
    agent.tool(run_tests_tool)

    print(f"CoverAI Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Export necessary components
__all__ = ["create_coverai_agent", "CoverAgentDependencies"]

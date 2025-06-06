import os
import time
import traceback
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import dagger
from ais_dagger_agents_config import YAMLConfig
from coverage.core.test_file_handler import TestFileHandler
from coverage.models.code_module import CodeModule
from coverage.models.coverage_report import CoverageReport
from coverage.template import get_system_template
from coverage.utils import get_code_under_test_directory
from opentelemetry import trace
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, red, yellow

# Initialize tracer for OpenTelemetry
tracer = trace.get_tracer(__name__)

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
            strategy="Generate unit tests to improve coverage",
            imports="",  # These will be part of the contents
            code=contents,
            test_path=""  # Will be updated below
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

        # Store the test file path in the CodeModule
        test_path = f"{save_dir}/{file_written}"
        ctx.deps.current_code_module.test_path = test_path

        return f"Successfully wrote content to {test_path}."
    except Exception as e:
        traceback.print_exc()
        return f"Error writing test file: {e}"


async def run_all_tests_tool(ctx: RunContext[CoverAgentDependencies]) -> str:
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


async def run_test_tool(ctx: RunContext[CoverAgentDependencies]) -> str:
    """Tool: Run tests only for the generated code module."""
    with tracer.start_as_current_span("run_test_tool") as span:
        try:
            span.set_attribute("tool.name", "run_test_tool")
            print(yellow("=== START: run_test_tool ==="))

            # Check if we have a current code module
            if not ctx.deps.current_code_module:
                span.set_attribute("error", "No test file generated")
                return "No test file has been generated yet. Use write_test_file_tool first."

            # Safely access test_path with getattr to avoid AttributeError
            test_file_path = None
            try:
                test_file_path = getattr(
                    ctx.deps.current_code_module, 'test_path', None)
                span.set_attribute("test_file_path", test_file_path)
                print(
                    f"Got test path from current_code_module: {test_file_path}")
            except (AttributeError, ValueError) as e:
                span.set_attribute("error.type", "AttributeError")
                span.set_attribute("error.message", str(e))
                print(f"Error getting test_path from current_code_module: {e}")
                pass

            if not test_file_path:
                span.set_attribute("error", "Unknown test file path")
                return "Test file path is unknown. Please use write_test_file_tool first."

            print(
                f"Preparing to run tests for specific file: {test_file_path}")
            base_command = ctx.deps.config.reporter.command
            span.set_attribute("base_command", base_command)

            # Generate the test command with proper span tracking
            with tracer.start_as_current_span("generate_test_command") as cmd_span:
                file_test_command = None
                try:
                    if hasattr(ctx.deps.config.reporter, 'file_test_command_template'):
                        # Use the reporter's file test command template if available
                        file_test_command = ctx.deps.config.reporter.file_test_command_template.replace(
                            "{file}", test_file_path)
                        cmd_span.set_attribute("command_source", "template")
                        print(
                            f"Using reporter-provided command: {file_test_command}")
                except AttributeError as e:
                    cmd_span.set_attribute("error.type", "AttributeError")
                    cmd_span.set_attribute("error.message", str(e))
                    print(
                        f"Error checking for file_test_command_template: {e}")
                    pass

                # Add fallback if still None
                if not file_test_command:
                    reporter_name = getattr(
                        ctx.deps.config.reporter, 'name', '').lower()
                    cmd_span.set_attribute("reporter_name", reporter_name)

                    if "jest" in reporter_name:
                        file_test_command = f"{base_command} -- {test_file_path} --verbose"
                        cmd_span.set_attribute(
                            "command_source", "jest_fallback")
                    elif "pytest" in reporter_name:
                        file_test_command = f"python -m pytest {test_file_path} -v"
                        cmd_span.set_attribute(
                            "command_source", "pytest_fallback")
                    else:
                        # Generic fallback
                        file_test_command = f"{base_command} {test_file_path}"
                        cmd_span.set_attribute(
                            "command_source", "generic_fallback")
                    print(f"Using fallback test command: {file_test_command}")

                cmd_span.set_attribute("final_command", file_test_command)

            print(f"Running test command: {file_test_command}")
            span.set_attribute("test_command", file_test_command)

            # Execute the test command with span tracking
            with tracer.start_as_current_span("execute_test_command") as exec_span:
                start_time = time.time()
                try:
                    # Create a script that captures more info
                    script = f"""
                    echo "Starting test execution at $(date)"
                    {file_test_command} > /tmp/test_stdout 2> /tmp/test_stderr
                    TEST_EXIT_CODE=$?
                    echo "Test execution completed at $(date) with exit code: $TEST_EXIT_CODE"
                    echo -n $TEST_EXIT_CODE > /exit_code
                    """

                    result_container = await ctx.deps.container.with_exec(
                        ["bash", "-c", script]
                    )
                    exec_span.set_attribute("execution.success", True)
                    print("Command execution completed")

                    # Get stdout and stderr
                    stdout = await result_container.file("/tmp/test_stdout").contents()
                    stderr = await result_container.file("/tmp/test_stderr").contents()
                    exit_code = await result_container.file("/exit_code").contents()

                    exec_span.set_attribute("exit_code", exit_code.strip())
                    exec_span.set_attribute("stdout.length", len(stdout))
                    exec_span.set_attribute("stderr.length", len(stderr))

                    # Log first 200 chars of output for debugging
                    print(f"Exit code: {exit_code.strip()}")
                    print(f"Stdout (first 200 chars): {stdout[:200]}")
                    if stderr:
                        print(f"Stderr (first 200 chars): {stderr[:200]}")

                except Exception as exec_err:
                    exec_span.set_attribute("execution.success", False)
                    exec_span.set_attribute(
                        "error.type", type(exec_err).__name__)
                    exec_span.set_attribute("error.message", str(exec_err))
                    print(red(f"Error executing test command: {exec_err}"))
                    if ctx.deps.current_code_module:
                        ctx.deps.current_code_module.error = f"Test execution failed: {exec_err}"
                    return f"Test Run Failed for {test_file_path}: Test execution error: {exec_err}"
                finally:
                    exec_span.set_attribute(
                        "duration_ms", (time.time() - start_time) * 1000)

            # Parse the results with span tracking
            with tracer.start_as_current_span("parse_test_results") as parse_span:
                parse_start_time = time.time()
                try:
                    if hasattr(ctx.deps.reporter, 'parse_test_results'):
                        parse_span.set_attribute(
                            "parser", "reporter.parse_test_results")
                        print("Reporter has parse_test_results method")

                        try:
                            output_file_path = getattr(
                                ctx.deps.config.reporter, 'output_file_path', None)
                            parse_span.set_attribute(
                                "output_file_path", str(output_file_path))
                            print(
                                f"Output file path from config: '{output_file_path}'")

                            if output_file_path:
                                try:
                                    # Use os.path.join for proper path construction
                                    work_dir = ctx.deps.config.container.work_dir
                                    report_dir = ctx.deps.config.reporter.report_directory

                                    # Construct the path properly
                                    path = os.path.join(
                                        work_dir, report_dir, output_file_path)
                                    parse_span.set_attribute("full_path", path)
                                    print(f"Full output file path: '{path}'")

                                    # First check if file exists with ls
                                    ls_result = await ctx.deps.container.with_exec(["ls", "-la", path]).stdout()
                                    parse_span.set_attribute(
                                        "file_exists", "yes")
                                    parse_span.set_attribute(
                                        "file_details", ls_result.strip())
                                    print(f"File exists: {ls_result.strip()}")

                                    # Now read the results file
                                    test_results = await result_container.file(path).contents()
                                    parse_span.set_attribute(
                                        "results.length", len(test_results))
                                    print(
                                        f"Test results file content length: {len(test_results)}")
                                    print(
                                        f"Test results (first 200 chars): {test_results[:200]}")

                                    # Parse the test results
                                    print("Parsing test results with reporter...")
                                    error = await ctx.deps.reporter.parse_test_results(test_results)
                                    parse_span.set_attribute(
                                        "parse.success", True)
                                    parse_span.set_attribute(
                                        "parse.error", str(error))
                                    print(f"Result of parsing: error={error}")

                                except Exception as e:
                                    parse_span.set_attribute(
                                        "error.type", type(e).__name__)
                                    parse_span.set_attribute(
                                        "error.message", str(e))
                                    print(
                                        red(f"Error reading or parsing test results file: {e}"))
                                    error = f"Error accessing test results: {e}"
                            else:
                                parse_span.set_attribute(
                                    "output_file_missing", True)
                                print(
                                    "No output file path configured, skipping file parsing")
                                error = None
                        except Exception as e:
                            parse_span.set_attribute(
                                "error.type", type(e).__name__)
                            parse_span.set_attribute("error.message", str(e))
                            print(
                                red(f"Error in test results handling logic: {e}"))
                            error = None
                    else:
                        parse_span.set_attribute("parser", "none")
                        print("Reporter doesn't have parse_test_results method")
                        # Fall back to exit code checking
                        error = None
                        if exit_code.strip() != "0":
                            error = f"Test failed with exit code {exit_code.strip()}"
                            if stderr:
                                error += f"\n\nStderr output:\n{stderr[:500]}"

                    # Update the code module with the error or success
                    if error:
                        parse_span.set_attribute("test.success", False)
                        parse_span.set_attribute("test.error", error[:200])
                        print(f"Test failed with error: {error}")
                        ctx.deps.current_code_module.error = error
                        return f"Test Run Failed for {test_file_path}: {error}"
                    else:
                        parse_span.set_attribute("test.success", True)
                        print("No errors found, tests passed")
                        ctx.deps.current_code_module.error = None
                        return f"Test Run Succeeded for {test_file_path}."

                except Exception as parse_err:
                    parse_span.set_attribute(
                        "error.type", type(parse_err).__name__)
                    parse_span.set_attribute("error.message", str(parse_err))
                    print(red(f"Error in test results parsing: {parse_err}"))

                    # Fall back to exit code check as last resort
                    if exit_code.strip() == "0":
                        return f"Test Run Succeeded for {test_file_path} (fallback to exit code check)."
                    else:
                        error_msg = f"Test failed with exit code {exit_code.strip()}"
                        if stderr:
                            error_msg += f"\nError output:\n{stderr[:500]}"
                        ctx.deps.current_code_module.error = error_msg
                        return f"Test Run Failed for {test_file_path}: {error_msg}"
                finally:
                    parse_span.set_attribute(
                        "duration_ms", (time.time() - parse_start_time) * 1000)

        except Exception as e:
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            error_msg = f"Error running test for specific file: {e}"
            print(red(f"EXCEPTION in run_test_tool: {e}"))
            traceback.print_exc()
            if ctx.deps.current_code_module:
                ctx.deps.current_code_module.error = error_msg
            return error_msg
        finally:
            span.set_attribute("function.completed", True)
            print(yellow("=== END: run_test_tool ==="))
            print("")  # Extra newline for better separation in logs


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
    agent.tool(run_test_tool)
    agent.tool(write_test_file_tool)

    print(f"CoverAI Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Export necessary components
__all__ = ["create_coverai_agent", "CoverAgentDependencies"]

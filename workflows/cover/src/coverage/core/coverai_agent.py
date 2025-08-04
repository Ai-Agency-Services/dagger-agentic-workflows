import os
import time
import traceback
import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import dagger
from ais_dagger_agents_config import YAMLConfig
from coverage.core.test_file_handler import TestFileHandler
from coverage.models.code_module import CodeModule
from coverage.models.coverage_report import CoverageReport
from coverage.template import get_system_template
from coverage.utils import get_code_under_test_directory
from dagger import dag
from opentelemetry import trace
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, red, yellow, green

from dagger.client.gen import NeoService

# Initialize tracer for OpenTelemetry
tracer = trace.get_tracer(__name__)

# Conditional import for Reporter type hint if it's complex
if TYPE_CHECKING:
    from dagger.client.gen import Reporter


@dataclass
class CoverAgentDependencies:
    config: YAMLConfig
    container: dagger.Container
    report: CoverageReport
    reporter: 'Reporter'
    current_code_module: Optional[CodeModule] = field(default=None)
    neo_service: Optional[NeoService] = field(default=None)


# === UTILITY FUNCTIONS ===

def normalize_filepath(path: str, work_dir: str) -> str:
    """Convert relative paths to absolute container paths using work_dir"""
    if path.startswith(work_dir + '/'):
        return path  # Already absolute with work_dir
    elif path.startswith('./'):
        return f"{work_dir}/{path[2:]}"  # Remove ./ and add work_dir/
    elif path.startswith('/'):
        # If it's absolute but not in work_dir, assume it's meant to be
        if not path.startswith(work_dir):
            return f"{work_dir}{path}"
        return path
    else:
        return f"{work_dir}/{path}"  # Add work_dir/ prefix


def validate_cypher_query(query: str) -> tuple[bool, str]:
    """Basic Cypher query validation"""
    if not query.strip():
        return False, "Query cannot be empty"

    # Check for common syntax issues
    if "type((s1)-[r]->" in query or "type((a)-[r]->" in query:
        return False, "Cannot introduce new variables in type() function. Define relationship variable in MATCH clause first."

    return True, ""


def calculate_relative_path(test_dir: str, source_file: str, work_dir: str) -> str:
    """Calculate the correct relative import path from test directory to source file."""
    try:
        # Normalize paths by removing work_dir prefix
        rel_test_dir = test_dir.replace(
            work_dir + '/', '') if test_dir.startswith(work_dir) else test_dir
        rel_source = source_file.replace(
            work_dir + '/', '') if source_file.startswith(work_dir) else source_file

        # Remove leading './' if present
        rel_test_dir = rel_test_dir.lstrip('./')
        rel_source = rel_source.lstrip('./')

        # Split into parts
        test_parts = [p for p in rel_test_dir.split('/') if p]
        source_parts = [p for p in rel_source.split('/') if p]

        # Remove filename from source path
        source_dir_parts = source_parts[:-1]
        source_filename = source_parts[-1]

        # Calculate how many levels up we need to go from test directory
        up_levels = len(test_parts)

        # Build the relative path
        up_path = '../' * up_levels
        down_path = '/'.join(source_dir_parts)

        if down_path:
            full_path = up_path + down_path + '/' + source_filename
        else:
            full_path = up_path + source_filename

        # Remove file extension for import
        if '.' in source_filename:
            full_path = full_path.rsplit('.', 1)[0]

        return full_path
    except Exception as e:
        return f"Error calculating path: {e}"


# === SYSTEM PROMPT FUNCTIONS ===

async def add_mandatory_analysis_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """System Prompt: FORCE the agent to analyze before generating tests."""
    current_file = ctx.deps.report.file if ctx.deps.report else "unknown"
    has_error = ctx.deps.current_code_module and ctx.deps.current_code_module.error

    # Get working directory from config
    config = ctx.deps.config
    work_dir = getattr(config.container, 'work_dir', '/app')
    normalized_current_file = normalize_filepath(current_file, work_dir)

    if has_error:
        # Extract specific import errors for targeted fixing
        error_text = ctx.deps.current_code_module.error
        import_errors = []

        # Parse common import error patterns
        lines = error_text.split('\n')
        for line in lines:
            if 'Cannot find module' in line and ('error TS2307' in line or 'MODULE_NOT_FOUND' in line):
                # Extract the problematic import
                if "'" in line:
                    bad_import = line.split("'")[1]
                    import_errors.append(bad_import)
                elif '"' in line:
                    bad_import = line.split('"')[1]
                    import_errors.append(bad_import)

        error_details = ""
        for bad_import in import_errors:
            error_details += f"❌ FAILED IMPORT: \"{bad_import}\"\n"

        return f"""
\n ------- \n
<MANDATORY_ANALYSIS_FIRST>
🚨🚨🚨 CRITICAL ERROR RECOVERY MODE 🚨🚨🚨

Your previous test generation FAILED due to errors:

{error_details}

You MUST follow this EXACT sequence (no exceptions):

STEP 1: Get the EXACT file path first:
find_file_path_tool("use-toast")
find_file_path_tool("chart")

STEP 2: Run analysis using the FULL paths found above:
analyze_imports_tool("/app/src/hooks/use-toast.ts")  // Use EXACT path from step 1

STEP 3: Check what's exported from the file (use FULL path):
run_cypher_query_tool("MATCH (symbol:Function|Class|Interface|Variable)-[:DEFINED_IN]->(f:File {{filepath: '/app/src/hooks/use-toast.ts'}}) WHERE symbol.scope = 'public' OR symbol.scope IS NULL RETURN symbol.name, labels(symbol)[0] as type LIMIT 20")

STEP 4: Read the actual source file:
read_file_tool("/app/src/hooks/use-toast.ts")  // Use EXACT path from step 1

⚠️ CRITICAL PATH RULES:
- NEVER use partial paths like "/app/use-toast.ts" ❌
- ALWAYS use complete paths from find_file_path_tool results
- For npm packages like '@testing-library/react-hooks', verify they exist in package.json

ONLY AFTER completing ALL steps should you generate tests with correct imports.
</MANDATORY_ANALYSIS_FIRST>
\n ------- \n
"""
    else:
        return f"""
\n ------- \n
<MANDATORY_ANALYSIS_FIRST>
🎯 REQUIRED ANALYSIS WORKFLOW

Before generating ANY test code, you MUST run these commands in order:

1. Get the EXACT file path:
   find_file_path_tool("{os.path.basename(current_file)}")

2. Run analysis with the FULL path found above:
   analyze_imports_tool("FULL_PATH_FROM_STEP_1")

3. Check what's exported (use FULL path):
   run_cypher_query_tool("MATCH (symbol:Function|Class|Interface|Variable)-[:DEFINED_IN]->(f:File {{filepath: 'FULL_PATH_FROM_STEP_1'}}) RETURN symbol.name, labels(symbol)[0] as type LIMIT 20")

This will show you the EXACT import paths and available exports to use in your tests.
</MANDATORY_ANALYSIS_FIRST>
\n ------- \n
"""


async def add_import_path_guidance_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """System Prompt: Specific guidance on how to construct correct import paths."""
    config = ctx.deps.config
    work_dir = getattr(config.container, 'work_dir', '/app')

    # Get test directory info
    code_under_test_dir = await get_code_under_test_directory(ctx.deps.container, ctx.deps.report)
    target_test_directory = (
        code_under_test_dir
        if ctx.deps.config.test_generation.save_next_to_code_under_test
        else ctx.deps.config.test_generation.test_directory
    )

    current_file = ctx.deps.report.file if ctx.deps.report else "unknown"

    # Calculate suggested import path
    suggested_import = calculate_relative_path(
        target_test_directory, current_file, work_dir)

    return f"""
\n ------- \n
<IMPORT_PATH_CONSTRUCTION>
🎯 HOW TO BUILD CORRECT IMPORT PATHS

Current file being tested: {current_file}
Test files will be written to: {target_test_directory}
Container work directory: {work_dir}

💡 CALCULATED IMPORT PATH: "{suggested_import}"

CRITICAL IMPORT RULES:

1. **From test directory to source file**: 
   - Test directory: {target_test_directory}
   - Source file: {current_file}
   - Correct import: `import {{ something }} from "{suggested_import}"`

2. **Common Patterns**:
   - Tests in "tests/" → Source in "src/": use "../src/path/to/file"
   - Tests next to source → Source in same dir: use "./filename"
   - Never use absolute paths in imports ❌

3. **Use Neo4j to verify**:
   - Find exact filenames and extensions (.ts, .tsx, .js, etc.)
   - Check what's actually exported before importing
   - Verify file exists in the database

4. **Import Examples**:
   ✅ `import {{ reducer }} from "../src/hooks/use-toast"`
   ✅ `import {{ ChartContainer }} from "../src/components/ui/chart"`
   ❌ `import {{ reducer }} from "./src/hooks/use-toast"`
   ❌ `import {{ ChartContainer }} from "./chart"`

WORKFLOW:
1. Use analyze_imports_tool() to understand structure
2. Use Neo4j to find exact file paths
3. Calculate relative path from test dir to source
4. Verify exports exist before importing
</IMPORT_PATH_CONSTRUCTION>
\n ------- \n
"""


async def add_enhanced_directories_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """Enhanced directory prompt with import path context."""
    dir_context = "<PROJECT_STRUCTURE>\n"
    try:
        code_file_path = ctx.deps.report.file
        code_under_test_dir = await get_code_under_test_directory(
            ctx.deps.container, report=ctx.deps.report
        )

        # Determine target directory for writing tests
        target_test_directory = (
            code_under_test_dir
            if ctx.deps.config.test_generation.save_next_to_code_under_test
            else ctx.deps.config.test_generation.test_directory
        )

        work_dir = ctx.deps.config.container.work_dir

        dir_context += f"🎯 CRITICAL PATH INFORMATION:\n"
        dir_context += f"  - File being tested: {code_file_path}\n"
        dir_context += f"  - Tests will be written to: {target_test_directory}\n"
        dir_context += f"  - Container work directory: {work_dir}\n\n"

        # Calculate and show suggested import path
        suggested_import = calculate_relative_path(
            target_test_directory, code_file_path, work_dir)
        dir_context += f"💡 SUGGESTED IMPORT PATH:\n"
        dir_context += f"  import {{ something }} from \"{suggested_import}\"\n\n"

        # Add directory tree structure
        try:
            # Show a focused tree around the work directory
            tree_cmd = ["tree", "-L", "4", work_dir,
                        "-I", "node_modules|.git|dist|build"]
            tree_exec = ctx.deps.container.with_exec(tree_cmd)
            tree_stdout = await tree_exec.stdout()
            dir_context += f"📁 PROJECT STRUCTURE (up to 4 levels):\n"
            dir_context += f"```\n{tree_stdout.strip()}\n```\n"
        except dagger.ExecError:
            try:
                # Fallback with find, focusing on source files
                find_cmd = ["find", work_dir, "-maxdepth", "4", "-type", "f",
                            "\\(", "-name", "*.ts", "-o", "-name", "*.tsx", "-o",
                            "-name", "*.js", "-o", "-name", "*.jsx", "\\)",
                            "!", "-path", "*/node_modules/*", "!", "-path", "*/.git/*"]
                find_exec = ctx.deps.container.with_exec(find_cmd)
                find_stdout = await find_exec.stdout()
                dir_context += f"📁 SOURCE FILES IN PROJECT:\n"
                dir_context += f"```\n{find_stdout.strip()}\n```\n"
            except Exception as find_err:
                dir_context += f"📁 Could not retrieve directory structure: {find_err}\n"

        dir_context += "</PROJECT_STRUCTURE>"
        return f"\n ------- \n{dir_context}\n ------- \n"

    except Exception as e:
        print(red(f"Error in add_enhanced_directories_prompt: {e}"))
        traceback.print_exc()
        dir_context += f"\nError retrieving directory information: {e}\n</PROJECT_STRUCTURE>"
        return f"\n ------- \n{dir_context}\n ------- \n"


async def add_current_code_module_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """System Prompt: Get the current code module and any previous errors, if they exist."""
    try:
        if ctx.deps.current_code_module:
            prompt_string = ""

            if ctx.deps.current_code_module.error:
                # Extract and highlight specific import errors
                error_text = ctx.deps.current_code_module.error
                import_errors = []
                type_errors = []

                lines = error_text.split('\n')
                for line in lines:
                    if 'Cannot find module' in line:
                        if "'" in line:
                            bad_import = line.split("'")[1]
                            import_errors.append(bad_import)
                        elif '"' in line:
                            bad_import = line.split('"')[1]
                            import_errors.append(bad_import)
                    elif 'is not assignable to parameter of type' in line:
                        type_errors.append(line.strip())

                prompt_string += f"""
\n ------- \n
<PREVIOUS_TEST_ERRORS>
🚨 CRITICAL: Your previous test generation FAILED with these errors:

{ctx.deps.current_code_module.error}

SPECIFIC ISSUES DETECTED:
"""

                if import_errors:
                    prompt_string += f"\n📦 IMPORT ERRORS:\n"
                    for bad_import in import_errors:
                        prompt_string += f"❌ BAD IMPORT: \"{bad_import}\"\n"
                    prompt_string += f"\n🔧 IMPORT FIXES REQUIRED:\n"
                    prompt_string += f"1. Run analyze_imports_tool() to find correct file paths\n"
                    prompt_string += f"2. Use Neo4j queries to verify file locations\n"
                    prompt_string += f"3. Calculate correct relative paths from test directory to source\n"
                    prompt_string += f"4. Use '../' to go up from test directory, NOT './'\n"

                if type_errors:
                    prompt_string += f"\n🔧 TYPE ERRORS:\n"
                    for type_error in type_errors:
                        prompt_string += f"❌ {type_error}\n"
                    prompt_string += f"\n🔧 TYPE FIXES REQUIRED:\n"
                    prompt_string += f"1. Use Neo4j to find correct type definitions\n"
                    prompt_string += f"2. Check actual exported types from source files\n"
                    prompt_string += f"3. Ensure imported types match actual definitions\n"

                prompt_string += f"\n🚨 MANDATORY: You MUST run analysis tools before generating new tests!\n"
                prompt_string += f"</PREVIOUS_TEST_ERRORS>\n\n ------- \n"

            # Add the failed code for reference
            prompt_string += f"""
\n ------- \n
<current_code_module>
Previous test code that FAILED (analyze these mistakes):
{ctx.deps.current_code_module.code}

DO NOT repeat the same import and type errors shown above!
</current_code_module>
\n ------- \n
"""

            return prompt_string
        else:
            return "\n ------- \n <current_code_module>No current code module available. Generate the first set of tests.</current_code_module> \n ------- \n"
    except Exception as e:
        print(f"Error in add_current_code_module_prompt: {e}")
        return "\n ------- \n <current_code_module>Error retrieving current code module.</current_code_module> \n ------- \n"


async def add_neo4j_usage_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """System Prompt: Enhanced Neo4j usage guidance with specific error solutions"""
    config = ctx.deps.config
    work_dir = getattr(config.container, 'work_dir', '/app')
    current_file = ctx.deps.report.file if ctx.deps.report else "unknown"
    normalized_current_file = normalize_filepath(current_file, work_dir)

    return f"""
\n ------- \n
<neo4j_codebase_analysis>
🎯 CURRENT FILE: {current_file}
🎯 NORMALIZED PATH: {normalized_current_file}

CRITICAL: Use these Neo4j queries to avoid import errors!

🔍 ESSENTIAL QUERIES FOR IMPORT RESOLUTION:

1. **Find files by partial name (e.g., chart, toast)**:
```
MATCH (f:File) WHERE f.filepath CONTAINS 'chart' OR f.filepath CONTAINS 'toast' RETURN f.filepath, f.language LIMIT 10
```
    
2. **Check what the current file imports**:
```
MATCH (f:File {{filepath: "{normalized_current_file}"}})-[:IMPORTS]->(imported:File) RETURN imported.filepath, imported.language
```
    
3. **Find exports from specific file**:
```
MATCH (symbol:Function|Class|Interface|Variable)-[:DEFINED_IN]->(f:File {{filepath: "{normalized_current_file}"}}) WHERE symbol.scope = "public" OR symbol.scope IS NULL RETURN symbol.name, labels(symbol)[0] as type, symbol.scope LIMIT 20
```

4. **Find symbols by name across all files**:
```
MATCH (symbol:Function|Class|Interface|Variable) 
WHERE symbol.name CONTAINS "ChartContainer" OR 
symbol.name CONTAINS "reducer" 
RETURN symbol.name, symbol.filepath, labels(symbol)[0] as type LIMIT 10
```
    
IMPORTANT:
- Always normalize paths using work_dir
- Use absolute container paths in queries
</neo4j_codebase_analysis>
\n ------- \n
"""


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

        # Enhanced script with better error capture
        script = f"""
        echo "=== Starting all tests at $(date) ==="
        echo "Command: {test_command}"
        
        {test_command} > /tmp/test_stdout 2> /tmp/test_stderr
        TEST_EXIT_CODE=$?
        
        echo "=== All tests completed at $(date) with exit code: $TEST_EXIT_CODE ==="
        echo -n $TEST_EXIT_CODE > /exit_code
        """

        result_container = await ctx.deps.container.with_exec(["bash", "-c", script])

        # Get all outputs
        stdout = await result_container.file("/tmp/test_stdout").contents()
        stderr = await result_container.file("/tmp/test_stderr").contents()
        exit_code = await result_container.file("/exit_code").contents()

        print(f"All tests exit code: {exit_code.strip()}")
        print(f"Stdout (first 200 chars): {stdout[:200]}")
        if stderr:
            print(f"Stderr (first 200 chars): {stderr[:200]}")

        # Try to use reporter's parser if available
        error = None
        if hasattr(ctx.deps.reporter, 'parse_test_results'):
            try:
                output_file_path = getattr(
                    ctx.deps.config.reporter, 'output_file_path', None)
                if output_file_path:
                    work_dir = ctx.deps.config.container.work_dir
                    report_dir = ctx.deps.config.reporter.report_directory
                    full_path = os.path.join(
                        work_dir, report_dir, output_file_path)

                    test_results = await result_container.file(full_path).contents()
                    error = await ctx.deps.reporter.parse_test_results(test_results)
            except Exception as parse_err:
                print(yellow(f"Could not use reporter parser: {parse_err}"))

        # Fallback to exit code and stderr
        if not error and exit_code.strip() != "0":
            error_parts = []
            if stderr:
                error_parts.append("STDERR:")
                error_parts.append(stderr[:1000])
            if stdout:
                error_parts.append("STDOUT:")
                error_parts.append(stdout[:500])
            error_parts.append(f"Exit Code: {exit_code.strip()}")
            error = "\n".join(error_parts)

        if error:
            if ctx.deps.current_code_module:
                ctx.deps.current_code_module.error = error
            return f"All Tests Run Failed: {error}"
        else:
            if ctx.deps.current_code_module:
                ctx.deps.current_code_module.error = None
            return "All Tests Run Succeeded."

    except Exception as e:
        error_msg = f"Error running all tests: {e}"
        if ctx.deps.current_code_module:
            ctx.deps.current_code_module.error = error_msg
        traceback.print_exc()
        return error_msg


# Add these missing functions after your existing utility functions:

async def add_validation_prompt(ctx: RunContext[CoverAgentDependencies]) -> str:
    """System Prompt: Encourage analysis before test generation."""
    has_error = ctx.deps.current_code_module and ctx.deps.current_code_module.error
    current_file = ctx.deps.report.file if ctx.deps.report else "unknown"

    if has_error:
        return f"""
\n ------- \n
<validation_strategy>
🚨 MANDATORY ANALYSIS REQUIRED 🚨

Your previous attempt failed. Before generating ANY new tests:

1. FIRST run: analyze_imports_tool("{current_file}")
2. THEN check for missing modules using Neo4j queries  
3. VERIFY all import paths and exports exist
4. ONLY THEN generate corrected tests

DO NOT skip the analysis step - it will cause the same errors again!
</validation_strategy>
\n ------- \n
"""
    else:
        return f"""
\n ------- \n
<validation_strategy>
📋 RECOMMENDED WORKFLOW:

1. Start by running: analyze_imports_tool("{current_file}")
2. Understand the codebase structure before writing tests
3. Use Neo4j queries to verify import paths and exports
4. Generate tests with correct imports and types
</validation_strategy>
\n ------- \n
"""


# Replace your existing create_coverai_agent function with this enhanced version:
def create_coverai_agent(pydantic_ai_model: OpenAIModel) -> Agent:
    """Creates and configures the enhanced CoverAI agent instance."""

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

    # CRITICAL: Analysis prompts FIRST to force analysis before generation
    # 🚨 FIRST - Forces analysis
    agent.system_prompt(add_mandatory_analysis_prompt)
    # Shows specific errors prominently
    agent.system_prompt(add_current_code_module_prompt)
    # 🎯 Import path education
    agent.system_prompt(add_import_path_guidance_prompt)
    # Enhanced with calculated paths
    agent.system_prompt(add_enhanced_directories_prompt)
    agent.system_prompt(get_code_under_test_prompt)         # Code content
    agent.system_prompt(add_coverage_report_prompt)        # Coverage context
    agent.system_prompt(add_dependency_files_prompt)       # Dependencies
    # Neo4j guidance (moved later)
    agent.system_prompt(add_neo4j_usage_prompt)
    agent.system_prompt(add_validation_prompt)            # Validation strategy

    # Register enhanced tools
    agent.tool(read_file_tool)
    agent.tool(run_test_tool)           # Your existing enhanced version
    agent.tool(write_test_file_tool)
    agent.tool(run_cypher_query_tool)   # Add validation to your existing one
    agent.tool(analyze_imports_tool)    # Your existing enhanced version
    agent.tool(find_file_path_tool)     # NEW - Add file path finder tool

    print(
        f"Enhanced CoverAI Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Add validation to your existing run_cypher_query_tool:
async def run_cypher_query_tool(ctx: RunContext[CoverAgentDependencies], query: str, retries: int = 3) -> str:
    """Tool: Run a Cypher query against the Neo4j database with validation and retry logic."""

    # Validate query first
    is_valid, validation_error = validate_cypher_query(query)
    if not is_valid:
        error_msg = f"Invalid Cypher query: {validation_error}\nQuery: {query}"
        print(red(f"❌ {error_msg}"))
        return error_msg

    # Add full query logging (not truncated)
    print(yellow(f"=== FULL QUERY ===\n{query}\n=== END QUERY ==="))
    print(
        blue(f"🔍 Running Neo4j query: {query[:100]}{'...' if len(query) > 100 else ''}"))

    if not ctx.deps.neo_service:
        error_msg = "Neo4j client is not available. Cannot run Cypher query."
        print(red(f"❌ {error_msg}"))
        return error_msg

    # Retry logic
    for attempt in range(retries):
        try:
            print(
                blue(f"⚙️ Executing query (attempt {attempt + 1}/{retries})..."))
            result = await ctx.deps.neo_service.run_query(query=query)

            print(
                green(f"✅ Query executed successfully! Result length: {len(result)}"))
            print(blue(f"📊 First 200 chars of result: {result[:200]}"))
            return result

        except Exception as e:
            if attempt == retries - 1:
                error_msg = f"Error executing Neo4j query after {retries} attempts: {e}"
                print(red(f"❌ {error_msg}"))
                return error_msg
            else:
                print(
                    yellow(f"⚠️ Attempt {attempt + 1} failed: {e}, retrying..."))
                await asyncio.sleep(2 ** attempt)


# Enhanced analyze_imports_tool with export detection:
async def analyze_imports_tool(ctx: RunContext[CoverAgentDependencies], filepath: str) -> str:
    """Tool: Analyze the imports for a specific file with enhanced information."""
    print(yellow(f"=== START: analyze_imports_tool for {filepath} ==="))

    if not ctx.deps.neo_service:
        error_msg = "Neo4j client is not available. Cannot analyze imports."
        print(red(f"❌ {error_msg}"))
        return error_msg

    try:
        print(blue(f"📊 Analyzing imports for file: {filepath}"))

        # Get working directory from config
        config = ctx.deps.config
        work_dir = getattr(config.container, 'work_dir', '/app')
        print(blue(f"🔧 Using work directory from config: {work_dir}"))

        normalized_filepath = normalize_filepath(filepath, work_dir)
        print(blue(f"🔧 Normalized filepath: {normalized_filepath}"))

        # Query 1: Check if file exists
        print(blue(f"🔍 Verifying file exists in database..."))
        exists_query = f"""
        MATCH (f:File {{filepath: "{normalized_filepath}"}})
        RETURN f.filepath, f.language
        """
        exists_result = await run_cypher_query_tool(ctx, exists_query)

        # Query 2: Direct imports
        print(blue(f"🔍 Finding files imported by {normalized_filepath}..."))
        imports_query = f"""
        MATCH (f:File {{filepath: "{normalized_filepath}"}})-[:IMPORTS]->(imported:File)
        RETURN imported.filepath as imported_file, imported.language as language
        """
        imports_result = await run_cypher_query_tool(ctx, imports_query)

        # Query 3: Files that import this file
        print(blue(f"🔍 Finding files that import {normalized_filepath}..."))
        dependents_query = f"""
        MATCH (f:File)-[:IMPORTS]->(target:File {{filepath: "{normalized_filepath}"}})
        RETURN f.filepath as dependent_file, f.language as language
        """
        dependents_result = await run_cypher_query_tool(ctx, dependents_query)

        # Query 4: Get exported symbols
        print(
            blue(f"🔍 Finding exported symbols from {normalized_filepath}..."))
        exports_query = f"""
        MATCH (symbol:Function|Class|Interface|Variable)-[:DEFINED_IN]->(f:File {{filepath: "{normalized_filepath}"}})
        WHERE symbol.scope = "public" OR symbol.scope IS NULL
        RETURN symbol.name, labels(symbol)[0] as symbol_type, symbol.scope
        LIMIT 20
        """
        exports_result = await run_cypher_query_tool(ctx, exports_query)

        # Calculate import path suggestion
        code_under_test_dir = await get_code_under_test_directory(ctx.deps.container, ctx.deps.report)
        target_test_directory = (
            code_under_test_dir
            if ctx.deps.config.test_generation.save_next_to_code_under_test
            else ctx.deps.config.test_generation.test_directory
        )

        suggested_import = calculate_relative_path(
            target_test_directory, normalized_filepath, work_dir)

        result = f"""
═══ Enhanced Imports Analysis for {filepath} ═══
Work directory: {work_dir}
Normalized path: {normalized_filepath}
Test directory: {target_test_directory}

💡 SUGGESTED IMPORT PATH: "{suggested_import}"

🔍 FILE EXISTS IN DATABASE:
{exists_result}

📥 FILES IMPORTED BY {filepath}:
{imports_result}

📤 FILES THAT IMPORT {filepath}:
{dependents_result}

🎯 EXPORTED SYMBOLS FROM {filepath}:
{exports_result}

💡 USAGE EXAMPLE:
import {{ symbolName }} from "{suggested_import}";

🔧 DEBUGGING TIPS:
- If file doesn't exist, check the exact path in Neo4j database
- If no imports shown, file might not have been indexed properly
- Use exported symbols list to verify what's available for import
- Always use the suggested import path for correct relative imports
"""

        print(green(f"✅ Enhanced analysis complete for {filepath}"))
        return result

    except Exception as e:
        error_msg = f"Error analyzing imports: {e}"
        print(red(f"❌ {error_msg}"))
        traceback.print_exc()
        return error_msg
    finally:
        print(yellow(f"=== END: analyze_imports_tool for {filepath} ==="))
        print()


async def find_file_path_tool(ctx: RunContext[CoverAgentDependencies], partial_name: str) -> str:
    """Tool: Find the full path of a file by its partial name using Neo4j."""
    print(yellow(f"=== START: find_file_path_tool for {partial_name} ==="))

    if not ctx.deps.neo_service:
        return "Neo4j client is not available. Cannot find file path."

    try:
        # Get working directory from config
        config = ctx.deps.config
        work_dir = getattr(config.container, 'work_dir', '/app')
        print(blue(f"🔍 Searching for files containing: {partial_name}"))

        # Clean partial name for query
        cleaned_name = partial_name.strip()
        if cleaned_name.startswith('./'):
            cleaned_name = cleaned_name[2:]
        if cleaned_name.startswith('/'):
            cleaned_name = cleaned_name[1:]
        if '.' in cleaned_name and not cleaned_name.endswith('.ts') and not cleaned_name.endswith('.tsx'):
            # If there's a dot but no extension, it might be a path
            base_name = cleaned_name.split('.')[-1]
            cleaned_name = base_name

        # Search for file in Neo4j
        search_query = f"""
        MATCH (f:File) 
        WHERE f.filepath CONTAINS '{cleaned_name}'
        RETURN f.filepath, f.language
        ORDER BY f.filepath
        LIMIT 15
        """

        search_results = await run_cypher_query_tool(ctx, search_query)

        # Generate suggestion for next steps
        result = f"""
═══ File Path Search Results for '{partial_name}' ═══

FOUND FILES:
{search_results}

SUGGESTED NEXT STEPS:
1. Check the list above for the correct complete filepath
2. Copy the EXACT full path for your query
3. Use this path in your next Neo4j query:
   
   MATCH (symbol:Function|Class|Interface|Variable)-[:DEFINED_IN]->(f:File {{filepath: "FULL_PATH_FROM_ABOVE"}})
   WHERE symbol.scope = "public" OR symbol.scope IS NULL
   RETURN symbol.name, labels(symbol)[0] as type, symbol.scope
   LIMIT 20

📋 PROPER PATH USAGE:
✅ Use complete paths like: "/app/src/hooks/use-toast.ts"
❌ Don't use partial paths like: "/app/use-toast.ts"
"""

        print(
            green(f"✅ Found {search_results.count(chr(10))} potential file matches"))
        return result

    except Exception as e:
        error_msg = f"Error finding file path: {e}"
        print(red(f"❌ {error_msg}"))
        traceback.print_exc()
        return error_msg
    finally:
        print(yellow(f"=== END: find_file_path_tool ==="))

# Add this function after your other tool functions:


async def run_test_tool(ctx: RunContext[CoverAgentDependencies]) -> str:
    """Tool: Run tests only for the generated code module with enhanced error handling."""
    with tracer.start_as_current_span("run_test_tool") as span:
        try:
            span.set_attribute("tool.name", "run_test_tool")
            print(yellow("=== START: Enhanced run_test_tool ==="))

            # Validation
            if not ctx.deps.current_code_module:
                span.set_attribute("error", "No test file generated")
                return "No test file has been generated yet. Use write_test_file_tool first."

            test_file_path = getattr(
                ctx.deps.current_code_module, 'test_path', None)
            if not test_file_path:
                span.set_attribute("error", "Unknown test file path")
                return "Test file path is unknown. Please use write_test_file_tool first."

            span.set_attribute("test_file_path", test_file_path)
            print(f"Running tests for: {test_file_path}")

            # Generate test command
            base_command = ctx.deps.config.reporter.command

            # Try to use reporter's template first
            file_test_command = None
            if hasattr(ctx.deps.config.reporter, 'file_test_command_template'):
                file_test_command = ctx.deps.config.reporter.file_test_command_template.replace(
                    "{file}", test_file_path)
                print(f"Using reporter template: {file_test_command}")
            else:
                # Smart fallback based on reporter type
                reporter_name = getattr(
                    ctx.deps.config.reporter, 'name', '').lower()
                if "jest" in reporter_name:
                    file_test_command = f"{base_command} -- {test_file_path} --verbose"
                elif "pytest" in reporter_name:
                    file_test_command = f"python -m pytest {test_file_path} -v"
                else:
                    file_test_command = f"{base_command} {test_file_path}"
                print(f"Using fallback command: {file_test_command}")

            span.set_attribute("test_command", file_test_command)

            # Execute tests with enhanced error capture
            script = f"""
            echo "=== Starting test execution at $(date) ==="
            echo "Command: {file_test_command}"
            
            {file_test_command} > /tmp/test_stdout 2> /tmp/test_stderr
            TEST_EXIT_CODE=$?
            
            echo "=== Test execution completed at $(date) with exit code: $TEST_EXIT_CODE ==="
            echo -n $TEST_EXIT_CODE > /exit_code
            
            # Capture additional context on failure
            if [ $TEST_EXIT_CODE -ne 0 ]; then
                echo "=== Additional error context ===" >> /tmp/test_stderr
                echo "PWD: $(pwd)" >> /tmp/test_stderr
                echo "Test file exists:" >> /tmp/test_stderr
                ls -la "{test_file_path}" >> /tmp/test_stderr 2>&1 || echo "Test file not found: {test_file_path}" >> /tmp/test_stderr
                echo "Directory contents:" >> /tmp/test_stderr
                ls -la $(dirname "{test_file_path}") >> /tmp/test_stderr 2>&1 || true
            fi
            """

            result_container = await ctx.deps.container.with_exec(["bash", "-c", script])

            # Get all outputs
            stdout = await result_container.file("/tmp/test_stdout").contents()
            stderr = await result_container.file("/tmp/test_stderr").contents()
            exit_code = await result_container.file("/exit_code").contents()

            span.set_attribute("exit_code", exit_code.strip())
            span.set_attribute("stdout.length", len(stdout))
            span.set_attribute("stderr.length", len(stderr))

            print(f"Exit code: {exit_code.strip()}")
            print(f"Stdout (first 200 chars): {stdout[:200]}")
            if stderr:
                print(f"Stderr (first 200 chars): {stderr[:200]}")

            # Enhanced result parsing
            if exit_code.strip() == "0":
                print(green("✅ Tests passed successfully"))
                ctx.deps.current_code_module.error = None
                return f"Test Run Succeeded for {test_file_path}."
            else:
                # Try to use reporter's parser if available
                combined_error = ""

                if hasattr(ctx.deps.reporter, 'parse_test_results'):
                    try:
                        print("Reporter has parse_test_results method")
                        output_file_path = getattr(
                            ctx.deps.config.reporter, 'output_file_path', None)
                        if output_file_path:
                            work_dir = ctx.deps.config.container.work_dir
                            report_dir = ctx.deps.config.reporter.report_directory
                            full_path = os.path.join(
                                work_dir, report_dir, output_file_path)

                            print(
                                f"Output file path from config: '{output_file_path}'")
                            print(f"Full output file path: '{full_path}'")

                            # Check if file exists
                            try:
                                ls_result = await result_container.with_exec(["ls", "-la", full_path]).stdout()
                                print(f"File exists: {ls_result.strip()}")
                            except:
                                print(f"File does not exist: {full_path}")

                            try:
                                test_results = await result_container.file(full_path).contents()
                                print(
                                    f"Test results file content length: {len(test_results)}")
                                print(
                                    f"Test results (first 200 chars): {test_results[:200]}")

                                print("Parsing test results with reporter...")
                                parsed_error = await ctx.deps.reporter.parse_test_results(test_results)
                                print(
                                    f"Result of parsing: error={parsed_error}")

                                if parsed_error:
                                    combined_error = parsed_error
                            except Exception as file_err:
                                print(
                                    yellow(f"Could not read test results file: {file_err}"))
                    except Exception as parse_err:
                        print(
                            yellow(f"Could not use reporter parser: {parse_err}"))

                # Fallback to raw output if reporter parsing failed
                if not combined_error:
                    error_parts = []
                    if stderr:
                        error_parts.append("STDERR:")
                        error_parts.append(stderr[:1000])  # Limit length
                    if stdout:
                        error_parts.append("STDOUT:")
                        error_parts.append(stdout[:500])
                    error_parts.append(f"Exit Code: {exit_code.strip()}")
                    combined_error = "\n".join(error_parts)

                print(red(f"❌ Tests failed: {combined_error[:300]}..."))
                ctx.deps.current_code_module.error = combined_error
                return f"Test Run Failed for {test_file_path}: {combined_error}"

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
            print(yellow("=== END: Enhanced run_test_tool ==="))
            print()

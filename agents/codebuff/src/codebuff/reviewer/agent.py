from dataclasses import dataclass
from typing import List,  Callable, Any
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from simple_chalk import blue, green, yellow, red
import re


@dataclass
class ReviewerDependencies:
    """Dependencies for the reviewer agent."""
    container: Any  # dagger.Container
    config: YAMLConfig
    read_file: Callable[[str], str]
    write_file: Callable[[str, str], Any]
    # Returns container with command executed
    run_command: Callable[[List[str]], Any]


async def check_syntax(
    ctx: RunContext[ReviewerDependencies],
    file_patterns: str = "*.py *.js *.ts"
) -> str:
    """Check syntax of modified files using language-appropriate tools."""
    print(blue(f"🔍 Checking syntax for: {file_patterns}"))

    # Check if review is disabled in config
    if hasattr(ctx.deps.config, 'review') and hasattr(ctx.deps.config.review, 'enabled') and not ctx.deps.config.review.enabled:
        return "Syntax check disabled in configuration"

    results = []
    container = ctx.deps.container

    try:
        # Check Python files with ruff/pylint/py_compile
        if "*.py" in file_patterns:
            # Use raw string (r"""...""") to avoid escape sequence issues
            py_check = await container.with_exec([
                "bash", "-c", r"""
                if command -v ruff >/dev/null 2>&1; then
                    echo "Using ruff for Python validation"
                    find . -name "*.py" -not -path "*/\.*" -not -path "*/node_modules/*" | 
                    xargs ruff check --select E9,F63,F7,F82 --format=text 2>&1 || 
                    echo "Python syntax issues found"
                elif command -v pylint >/dev/null 2>&1; then
                    echo "Using pylint for Python validation"
                    find . -name "*.py" -not -path "*/\.*" -not -path "*/node_modules/*" | 
                    xargs pylint --disable=all --enable=syntax-error,undefined-variable 2>&1 ||
                    echo "Python syntax issues found"
                else
                    echo "Using basic Python syntax check"
                    find . -name "*.py" -not -path "*/\.*" -not -path "*/node_modules/*" -exec python -m py_compile {} \; 2>&1 ||
                    echo "Python syntax check completed with issues"
                fi
                """
            ]).stdout()
            results.append(
                f"Python syntax check:\n{py_check.strip() if py_check.strip() else 'PASSED'}")

        # Check JavaScript/TypeScript files
        if "*.js" in file_patterns or "*.ts" in file_patterns:
            # Use raw string here too
            js_check = await container.with_exec([
                "bash", "-c", r"""
                if [ -f package.json ]; then
                    # Try eslint if available
                    if [ -d "node_modules/.bin" ] && [ -f "node_modules/.bin/eslint" ]; then
                        echo "Using ESLint for JS/TS validation"
                        ./node_modules/.bin/eslint --no-eslintrc --no-ignore --parser-options=ecmaVersion:latest \
                        --rule 'semi:0,no-undef:2,no-unused-vars:0' --ext .js,.ts,.jsx,.tsx . 2>&1 || 
                        echo "JS/TS syntax issues found"
                        exit 0
                    fi
                        
                    # TypeScript compiler check
                    if [ -d "node_modules/.bin" ] && [ -f "node_modules/.bin/tsc" ]; then
                        echo "Using TypeScript compiler for TS validation"
                        find . -name "*.ts" -o -name "*.tsx" -not -path "*/\.*" -not -path "*/node_modules/*" -not -path "*/dist/*" | 
                        xargs ./node_modules/.bin/tsc --noEmit --allowJs --checkJs false --noImplicitAny false \
                        --target ES2015 --moduleResolution node 2>&1 || echo "TypeScript syntax issues found"
                    elif command -v tsc >/dev/null 2>&1; then
                        echo "Using system TypeScript compiler"
                        find . -name "*.ts" -o -name "*.tsx" -not -path "*/\.*" -not -path "*/node_modules/*" -not -path "*/dist/*" | 
                        xargs tsc --noEmit --allowJs --checkJs false --noImplicitAny false \
                        --target ES2015 --moduleResolution node 2>&1 || echo "TypeScript syntax issues found"
                    fi
                        
                    # Node.js syntax check for JS files
                    if command -v node >/dev/null 2>&1; then
                        echo "Using Node.js for JS syntax validation"
                        find . -name "*.js" -o -name "*.jsx" -not -path "*/\.*" -not -path "*/node_modules/*" -not -path "*/dist/*" |
                        while read file; do
                            node --check "$file" 2>&1 || echo "Syntax error in $file"
                        done
                    fi
                else
                    echo "No package.json found, skipping JS/TS validation"
                fi
                """
            ]).stdout()
            results.append(
                f"JavaScript/TypeScript syntax check:\n{js_check.strip()}")

        # Summarize results
        summary = "\n\n".join(results)
        if "issues found" in summary or "Syntax error" in summary:
            print(yellow("⚠️ Syntax check found potential issues"))
        else:
            print(green("✅ Syntax check completed successfully"))

        return summary

    except Exception as e:
        error_msg = f"Error checking syntax: {e}"
        print(red(f"❌ {error_msg}"))
        return error_msg


async def run_tests(
    ctx: RunContext[ReviewerDependencies],
    test_command: str = "auto-detect"
) -> str:
    """Run tests to validate changes made by the implementation agent."""
    print(blue(f"🧪 Running implementation tests"))

    # Check if review is disabled in config
    if hasattr(ctx.deps.config, 'review') and hasattr(ctx.deps.config.review, 'enabled') and not ctx.deps.config.review.enabled:
        return "Test execution disabled in configuration"

    try:
        # Get modified/created test files from git
        modified_tests = await ctx.deps.container.with_exec([
            "bash", "-c", "git status --porcelain | grep -E '(^\\?\\?|^A|^M).*\\.(test|spec)\\.|test_|_test\\.|(/__tests__/)' | awk '{print $2}'"
        ]).stdout()

        test_files = [file.strip()
                      for file in modified_tests.splitlines() if file.strip()]

        if not test_files:
            print(yellow("⚠️ No implementation-created test files found"))
            return "No new or modified test files found from implementation agent"

        print(green(f"Found {len(test_files)} test files to validate"))

        # Get test command template from config
        reporter_config = getattr(ctx.deps.config, 'reporter', None)
        file_test_template = None
        if reporter_config:
            if hasattr(reporter_config, 'file_test_command_template'):
                file_test_template = reporter_config.file_test_command_template
            elif isinstance(reporter_config, dict):
                file_test_template = reporter_config.get(
                    'file_test_command_template')

        results = []
        for test_file in test_files[:10]:  # Limit to 10 tests for safety
            # Use template if available, otherwise auto-detect
            if file_test_template:
                cmd = file_test_template.replace("{file}", test_file)
            else:
                if test_file.endswith('.py'):
                    cmd = f"pytest -xvs {test_file}"
                elif any(test_file.endswith(ext) for ext in ['.ts', '.tsx', '.js', '.jsx']):
                    cmd = f"npm test -- --testPathPattern='{test_file}'"
                elif test_file.endswith('.go'):
                    cmd = f"go test -v $(dirname {test_file})"
                else:
                    cmd = f"echo 'No test runner configured for {test_file}'"

            # Run the test and capture output
            try:
                test_output = await ctx.deps.container.with_exec([
                    "bash", "-c", f"{cmd}; echo $? > /tmp/exit_code"
                ]).stdout()

                # Get exit code to determine if test passed
                exit_code_str = await ctx.deps.container.file("/tmp/exit_code").contents()
                exit_code = int(exit_code_str.strip()
                                ) if exit_code_str.strip().isdigit() else 1

                status = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
                results.append(
                    f"{status} - {test_file}\nCommand: {cmd}\n{'-' * 40}\n{test_output[:300]}...\n")
            except Exception as e:
                results.append(
                    f"❌ ERROR - {test_file}\nCommand: {cmd}\nError: {str(e)}\n")

        result_summary = f"""Test Execution Results:
Found {len(test_files)} implementation test files:{chr(10).join(f'- {file}' for file in test_files)}
Detailed Results:{chr(10).join(results)}"""

        print(green("✅ Implementation test execution completed"))
        return result_summary

    except Exception as e:
        error_msg = f"Error running implementation tests: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


async def analyze_changes(
    ctx: RunContext[ReviewerDependencies],
    files_pattern: str = "*"
) -> str:
    """Analyze code quality and suggest improvements."""
    print(blue(f"📊 Analyzing code quality"))

    # Check if review is disabled in config
    if hasattr(ctx.deps.config, 'review') and hasattr(ctx.deps.config.review, 'enabled') and not ctx.deps.config.review.enabled:
        return "Code quality analysis disabled in configuration"

    try:
        # Get modified files from git
        modified_files = await ctx.deps.container.with_exec([
            "bash", "-c", "git status --porcelain | grep -E '^(M|A|\\?\\?)' | awk '{print $2}'"
        ]).stdout()

        files = [file.strip()
                 for file in modified_files.splitlines() if file.strip()]

        if not files:
            print(yellow("⚠️ No modified files found to analyze"))
            return "No modified files found for quality analysis"

        print(green(f"Found {len(files)} files to analyze"))

        # For each file, perform basic quality checks
        results = []
        for file_path in files[:20]:  # Limit to 20 files for safety
            try:
                # Skip non-code files
                if not any(file_path.endswith(ext) for ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.go']):
                    continue

                # Read file contents
                content = await ctx.deps.read_file(file_path)

                # Check line length
                lines = content.splitlines()
                long_lines = [(i+1, len(line))
                              for i, line in enumerate(lines) if len(line) > 100]
                if long_lines:
                    results.append(
                        f"📏 {file_path}: Found {len(long_lines)} lines exceeding 100 characters")

                # Check function length
                if file_path.endswith('.py'):
                    # Simple heuristic for Python function length
                    func_def_pattern = r'def\s+([a-zA-Z0-9_]+)\s*\('
                    func_defs = [(m.start(), m.group(1))
                                 for m in re.finditer(func_def_pattern, content)]

                    for i, (start_pos, func_name) in enumerate(func_defs):
                        # Find start line
                        start_line = content[:start_pos].count('\n') + 1

                        # Find end (next function or end of file)
                        end_pos = len(content)
                        if i < len(func_defs) - 1:
                            end_pos = func_defs[i+1][0]

                        func_content = content[start_pos:end_pos]
                        func_lines = func_content.count('\n')

                        if func_lines > 30:
                            results.append(
                                f"📚 {file_path}:{start_line}: Function '{func_name}' is {func_lines} lines long")

                # Check for TODOs
                todos = [(i+1, line) for i, line in enumerate(lines)
                         if 'TODO' in line or 'FIXME' in line]
                if todos:
                    results.append(
                        f"📝 {file_path}: Found {len(todos)} TODOs/FIXMEs")

            except Exception as e:
                results.append(f"❌ Error analyzing {file_path}: {str(e)}")

        if not results:
            result_summary = "✅ No significant code quality issues found"
        else:
            result_summary = "Code Quality Analysis Results:\n\n" + \
                "\n".join(results)

        print(green("✅ Code quality analysis completed"))
        return result_summary

    except Exception as e:
        error_msg = f"Error analyzing code quality: {e}"
        print(red(f"❌ {error_msg}"))
        return error_msg


async def review_code(
    ctx: RunContext[ReviewerDependencies],
    change_summary: str,
    iteration: int = 0
) -> str:
    """
    Perform a comprehensive code review by running all review tools
    and providing a consolidated summary with findings and recommendations.

    Args:
        change_summary: Summary of the changes to review
        iteration: Current review iteration number
    """
    print(blue(f"🔎 Starting code review (iteration {iteration})"))

    # Check if review is disabled in config
    if hasattr(ctx.deps.config, 'review') and hasattr(ctx.deps.config.review, 'enabled') and not ctx.deps.config.review.enabled:
        return "Code review disabled in configuration"

    # Run all review tools directly (not via run_tool which doesn't exist)
    print(blue("Running syntax checks..."))
    syntax_results = await check_syntax(ctx)

    print(blue("Running tests..."))
    test_results = await run_tests(ctx)

    print(blue("Analyzing code quality..."))
    quality_results = await analyze_changes(ctx)

    # Determine overall status - using lowercase values to match enum expectations
    status = "approved"
    if "❌" in test_results or "Syntax error" in syntax_results or "issues found" in syntax_results:
        status = "critical_issues"
    elif "⚠️" in test_results or "TODO" in quality_results or "exceeding" in quality_results:
        status = "needs_changes"

    # Build summary report
    summary = f"""## Code Review Report (Iteration {iteration})
### Review Status: {status}
### Syntax Check{syntax_results.strip()}
### Test Execution{test_results.strip()}
### Code Quality Analysis{quality_results.strip()}
### Recommendations{"Critical issues must be fixed before proceeding." if status == "critical_issues" else
                    "Address warnings before proceeding." if status == "needs_changes" else
                    "All checks passed, implementation looks good!"}"""

    print(blue(f"Review completed with status: {status}"))
    return summary


def create_reviewer_agent(model: OpenAIChatModel = None) -> Agent:
    """Create a reviewer agent with the given model."""
    agent = Agent(
        name="Code Reviewer",
        system_prompt="Reviews code changes for correctness, test coverage, and quality.",
        model=model
    )

    agent.tool(check_syntax)
    agent.tool(run_tests)
    agent.tool(analyze_changes)
    agent.tool(review_code)

    return agent

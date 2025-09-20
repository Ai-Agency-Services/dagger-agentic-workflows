from dataclasses import dataclass

import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, green, yellow, red


@dataclass
class ReviewerDependencies:
    config: YAMLConfig
    container: dagger.Container
    changes_description: str


async def check_syntax(
    ctx: RunContext[ReviewerDependencies],
    file_patterns: str = "*.py *.js *.ts"
) -> str:
    """Check syntax of modified files."""
    print(blue(f"🔍 Checking syntax for: {file_patterns}"))
    
    try:
        results = []
        
        # Check Python files
        if "*.py" in file_patterns:
            py_check = await ctx.deps.container.with_exec([
                "bash", "-c", r"find . -name '*.py' -exec python -m py_compile {} \; 2>&1 || echo 'Python syntax check completed with issues'"
            ]).stdout()
            results.append(f"Python syntax check: {py_check.strip() if py_check.strip() else 'PASSED'}")
        
        # Check for Node.js and validate JS/TS if available
        if "*.js" in file_patterns or "*.ts" in file_patterns:
            js_env_check = await ctx.deps.container.with_exec([
                "bash", "-c", "which node > /dev/null 2>&1 && echo 'Node.js available for JS validation' || echo 'Node.js not available'"
            ]).stdout()
            results.append(f"JavaScript environment: {js_env_check.strip()}")
        
        result = "\n".join(results)
        print(green("✅ Syntax check completed"))
        return result
        
    except Exception as e:
        error_msg = f"Error checking syntax: {e}"
        print(red(f"❌ {error_msg}"))
        return error_msg


async def run_tests(
    ctx: RunContext[ReviewerDependencies],
    test_command: str = "auto-detect"
) -> str:
    """Run tests to validate changes."""
    print(blue(f"🧪 Running tests"))
    
    try:
        # Find test files
        test_check = await ctx.deps.container.with_exec([
            "bash", "-c", "find . -name '*test*.py' -o -name 'test_*' -o -name '*_test.py' -o -name '*.test.js' -o -name '*.spec.js' | head -10"
        ]).stdout()
        
        if not test_check.strip():
            return "No test files found - skipping test execution"
        
        # Auto-detect test runner if not specified
        if test_command == "auto-detect":
            # Check for pytest
            pytest_check = await ctx.deps.container.with_exec([
                "bash", "-c", "which pytest > /dev/null 2>&1 && echo 'pytest' || echo 'python -m pytest'"
            ]).stdout()
            test_command = pytest_check.strip()
        
        # Run tests
        test_result = await ctx.deps.container.with_exec([
            "bash", "-c", f"{test_command} --tb=short -v 2>&1 || echo 'Tests completed with issues'"
        ]).stdout()
        
        result = f"""Test Execution Results:

Test files found:
{test_check}

Test command used: {test_command}

Test output:
{test_result[:1000]}{'...' if len(test_result) > 1000 else ''}"""
        
        print(green("✅ Test execution completed"))
        return result
        
    except Exception as e:
        error_msg = f"Error running tests: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


async def analyze_changes(
    ctx: RunContext[ReviewerDependencies]
) -> str:
    """Analyze the changes made to the codebase."""
    print(blue("📊 Analyzing changes"))
    
    try:
        # Check git status if available
        git_status = await ctx.deps.container.with_exec([
            "bash", "-c", "if [ -d .git ]; then echo 'Git status:' && git status --porcelain && echo '---' && echo 'Git diff summary:' && git diff --stat 2>/dev/null; else echo 'Not a git repository'; fi"
        ]).stdout()
        
        # Get file modification times
        recent_changes = await ctx.deps.container.with_exec([
            "bash", "-c", "find . -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.java' -o -name '*.go' | xargs ls -lt 2>/dev/null | head -15"
        ]).stdout()
        
        # Check for potential issues
        potential_issues = await ctx.deps.container.with_exec([
            "bash", "-c", "grep -r 'TODO\\|FIXME\\|XXX\\|HACK' --include='*.py' --include='*.js' --include='*.ts' . 2>/dev/null | head -5 || echo 'No TODO/FIXME comments found'"
        ]).stdout()
        
        result = f"""Change Analysis:

Changes description: {ctx.deps.changes_description}

Git analysis:
{git_status}

Recent file modifications:
{recent_changes}

Potential issues/TODOs:
{potential_issues}"""
        
        print(green("✅ Change analysis completed"))
        return result
        
    except Exception as e:
        error_msg = f"Error analyzing changes: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


def create_reviewer_agent(model: OpenAIModel) -> Agent:
    """Create the Reviewer agent."""
    system_prompt = """
You are a Reviewer Agent, equivalent to Codebuff's code review capabilities.

Your role:
- Review code changes for correctness and quality
- Run syntax checks and tests
- Validate that changes meet requirements
- Provide feedback and recommendations
- Ensure code quality standards are maintained

Your tools:
1. check_syntax - Validate syntax of modified files
2. run_tests - Execute tests to validate functionality
3. analyze_changes - Analyze the scope and impact of changes

Review criteria:
- Syntax correctness
- Test coverage and passing tests
- Code quality and best practices
- Adherence to project standards
- Potential side effects or regressions
- Security considerations
- Performance implications

Provide clear, actionable feedback with specific recommendations for improvements.
"""
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=ReviewerDependencies,
        instrument=False,
        end_strategy="exhaustive",
        retries=3
    )
    
    agent.tool(check_syntax)
    agent.tool(run_tests)
    agent.tool(analyze_changes)
    
    print(f"Reviewer Agent created with model: {model.model_name}")
    return agent
from dataclasses import dataclass
from typing import List

import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, green, yellow


@dataclass
class ThinkerDependencies:
    config: YAMLConfig
    container: dagger.Container
    task_description: str
    relevant_files: List[str]


async def analyze_task_complexity(
    ctx: RunContext[ThinkerDependencies]
) -> str:
    """Analyze the complexity and requirements of the task."""
    print(blue(f"🧠 Analyzing task complexity: {ctx.deps.task_description[:50]}..."))
    
    try:
        # Check if files exist and get their info
        file_analysis = []
        for file_path in ctx.deps.relevant_files[:5]:  # Limit to first 5 files
            try:
                file_info = await ctx.deps.container.with_exec([
                    "bash", "-c", f"if [ -f '{file_path}' ]; then echo 'File exists:' && wc -l '{file_path}' && file '{file_path}'; else echo 'File not found: {file_path}'; fi"
                ]).stdout()
                file_analysis.append(f"{file_path}: {file_info.strip()}")
            except:
                file_analysis.append(f"{file_path}: Could not analyze")
        
        # Check for dependencies
        deps_check = await ctx.deps.container.with_exec([
            "bash", "-c", "find . -maxdepth 2 -name 'requirements.txt' -o -name 'package.json' -o -name 'pyproject.toml' -o -name 'go.mod' -o -name 'Cargo.toml' | head -5"
        ]).stdout()
        
        # Check git status
        git_status = await ctx.deps.container.with_exec([
            "bash", "-c", "if [ -d .git ]; then git status --porcelain | head -10; else echo 'Not a git repository'; fi"
        ]).stdout()
        
        result = f"""Task Complexity Analysis:

Task: {ctx.deps.task_description}

Relevant Files Analysis:
{chr(10).join(file_analysis)}

Project Dependencies Found:
{deps_check if deps_check.strip() else 'No dependency files found'}

Git Status:
{git_status.strip() if git_status.strip() else 'Clean working directory'}

Complexity Factors:
- Number of files involved: {len(ctx.deps.relevant_files)}
- Task scope: {'High' if len(ctx.deps.task_description) > 100 else 'Medium' if len(ctx.deps.task_description) > 50 else 'Low'}
- Dependencies present: {'Yes' if deps_check.strip() else 'No'}"""
        
        print(green("✅ Task complexity analysis completed"))
        return result
        
    except Exception as e:
        error_msg = f"Error analyzing task complexity: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


async def create_execution_strategy(
    ctx: RunContext[ThinkerDependencies],
    complexity_analysis: str
) -> str:
    """Create a detailed execution strategy for the task."""
    print(blue("📋 Creating execution strategy"))
    
    try:
        # Check for test files
        test_files = await ctx.deps.container.with_exec([
            "bash", "-c", "find . -name '*test*' -o -name '*spec*' -o -name '__tests__' | head -10"
        ]).stdout()
        
        # Check project structure
        project_structure = await ctx.deps.container.with_exec([
            "bash", "-c", "ls -la | grep ^d | awk '{print $9}' | grep -v '^\\.\\.$\\|^\\.$' | head -10"
        ]).stdout()
        
        result = f"""Execution Strategy:

Task: {ctx.deps.task_description}

Project Structure:
{project_structure}

Existing Tests:
{test_files if test_files.strip() else 'No test files found'}

Complexity Analysis:
{complexity_analysis}

Recommended Execution Steps:
1. **Preparation Phase**
   - Backup current state (if git repo)
   - Review target files: {', '.join(ctx.deps.relevant_files[:3])}{'...' if len(ctx.deps.relevant_files) > 3 else ''}
   - Understand current implementation

2. **Planning Phase**
   - Identify required changes
   - Plan incremental modifications
   - Consider backward compatibility

3. **Implementation Phase**
   - Make changes in small, testable increments
   - Implement core functionality first
   - Add error handling and edge cases

4. **Validation Phase**
   - Run existing tests (if available)
   - Test new functionality
   - Verify no regressions introduced

5. **Review Phase**
   - Code review for quality
   - Documentation updates
   - Final integration check

Risk Assessment:
- File modification risk: {'High' if len(ctx.deps.relevant_files) > 5 else 'Medium' if len(ctx.deps.relevant_files) > 2 else 'Low'}
- Integration complexity: {'High' if 'api' in ctx.deps.task_description.lower() or 'database' in ctx.deps.task_description.lower() else 'Medium'}
- Testing coverage: {'Good' if test_files.strip() else 'Needs improvement'}"""
        
        print(green("✅ Execution strategy created"))
        return result
        
    except Exception as e:
        error_msg = f"Error creating strategy: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


def create_thinker_agent(model: OpenAIModel) -> Agent:
    """Create the Thinker/Planner agent."""
    system_prompt = """
You are a Thinker/Planner Agent, equivalent to Codebuff's strategic planning capabilities.

Your role:
- Analyze complex coding tasks and break them down into manageable steps
- Create detailed execution plans with proper sequencing
- Identify risks, dependencies, and potential issues
- Provide strategic guidance for implementation

Your tools:
1. analyze_task_complexity - Understand the scope and complexity
2. create_execution_strategy - Develop a detailed plan

Always provide:
- Clear, step-by-step execution plan
- Risk assessment and mitigation strategies
- Dependencies and prerequisites
- Testing and validation approach
- Consideration of edge cases and potential issues
"""
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=ThinkerDependencies,
        instrument=False,
        end_strategy="exhaustive",
        retries=3
    )
    
    agent.tool(analyze_task_complexity)
    agent.tool(create_execution_strategy)
    
    print(f"Thinker Agent created with model: {model.model_name}")
    return agent
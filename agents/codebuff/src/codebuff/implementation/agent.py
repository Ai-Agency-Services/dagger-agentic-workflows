from dataclasses import dataclass

import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from simple_chalk import blue, green, yellow, red


@dataclass
class ImplementationDependencies:
    config: YAMLConfig
    container: dagger.Container
    plan: str


async def run_command(
    ctx: RunContext[ImplementationDependencies],
    command: list[str]
) -> str:
    """Execute a command in the container."""
    print(blue(f"🔧 Executing: {' '.join(command)}"))
    
    try:
        # Ensure proper command format like other agents
        if len(command) < 3 or command[0] != "bash" or command[1] != "-c":
            if len(command) == 1:
                command = ["bash", "-c", command[0]]
            else:
                command = ["bash", "-c", " ".join(command)]
        
        container_with_exec = ctx.deps.container.with_exec(command)
        stdout = await container_with_exec.stdout()
        ctx.deps.container = container_with_exec
        
        print(green("✅ Command executed successfully"))
        return stdout
        
    except Exception as e:
        error_msg = f"Error executing command '{command}': {e}"
        print(red(f"❌ {error_msg}"))
        return error_msg


async def read_file(
    ctx: RunContext[ImplementationDependencies],
    file_path: str
) -> str:
    """Read the contents of a file."""
    print(blue(f"📄 Reading file: {file_path}"))
    
    try:
        file_content = await ctx.deps.container.file(file_path).contents()
        
        print(green(f"✅ File read: {len(file_content)} characters"))
        return file_content
        
    except Exception as e:
        error_msg = f"Error reading file '{file_path}': {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


async def write_file(
    ctx: RunContext[ImplementationDependencies],
    file_path: str,
    content: str
) -> str:
    """Write content to a file."""
    print(blue(f"✍️ Writing to file: {file_path}"))
    
    try:
        # Write file using heredoc to handle special characters
        container_with_write = ctx.deps.container.with_new_file(
            file_path, content
        )
        
        # Update container
        ctx.deps.container = container_with_write
        
        # Verify write
        verify_result = await container_with_write.with_exec([
            "bash", "-c", f"ls -la '{file_path}' && echo 'Content preview:' && head -3 '{file_path}'"
        ]).stdout()
        
        print(green(f"✅ File written successfully"))
        return f"Successfully wrote {len(content)} characters to {file_path}\n{verify_result}"
        
    except Exception as e:
        error_msg = f"Error writing file '{file_path}': {e}"
        print(red(f"❌ {error_msg}"))
        return error_msg


def create_implementation_agent(model: OpenAIChatModel) -> Agent:
    """Create the Implementation agent."""
    system_prompt = """
You are an Implementation Agent focused on implementing NEW features and writing NEW tests.

Your PRIMARY role:
- Implement NEW feature code based on the plan
- Create NEW unit tests for the features you implement
- Write clean, focused code that follows existing patterns
- Avoid modifying existing tests unless the feature necessarily changes behavior

IMPORTANT RESTRICTIONS:
- DO NOT run test suites yourself (pytest, npm test, etc.) - the orchestrator handles testing
- DO NOT modify existing tests unless the feature explicitly requires behavior changes
- DO NOT fix unrelated failing tests - focus only on implementing the requested feature
- PRIORITIZE implementing feature code first, then write new tests for that code

Your tools:
1. run_command - Execute shell commands (but NOT for running tests)
2. read_file - Read file contents
3. write_file - Write content to files

Implementation guidelines:
- Focus on NEW feature implementation
- Create corresponding NEW tests for your features
- Follow existing code patterns and conventions
- Make minimal, focused changes
- At least one non-test code file must be created or modified
- Add new tests in appropriate test directories/files
- Preserve existing functionality unless explicitly changing it
"""
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=ImplementationDependencies,
        instrument=False,
        end_strategy="exhaustive",
        retries=5
    )
    
    agent.tool(run_command)
    agent.tool(read_file)
    agent.tool(write_file)
    
    print(f"Implementation Agent created with model: {model.model_name}")
    return agent
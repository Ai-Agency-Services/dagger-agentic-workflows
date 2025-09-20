from dataclasses import dataclass

import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
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
        file_content = await ctx.deps.container.with_exec([
            "bash", "-c", f"cat '{file_path}'"
        ]).stdout()
        
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
        container_with_write = ctx.deps.container.with_exec([
            "bash", "-c", f"cat > '{file_path}' << 'EOF'\n{content}\nEOF"
        ])
        
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


def create_implementation_agent(model: OpenAIModel) -> Agent:
    """Create the Implementation agent."""
    system_prompt = """
You are an Implementation Agent, equivalent to Codebuff's code execution capabilities.

Your role:
- Execute the detailed plan created by the Thinker agent
- Make precise code modifications as specified
- Run commands and scripts as needed
- Ensure changes are implemented correctly

Your tools:
1. run_command - Execute shell commands in the container
2. read_file - Read file contents
3. write_file - Write content to files

Implementation guidelines:
- Follow the plan precisely
- Make incremental changes
- Verify each step before proceeding
- Handle errors gracefully
- Preserve existing functionality unless explicitly changing it
- Use proper error handling
- Test changes when possible
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
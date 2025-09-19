from dataclasses import dataclass
import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, green
from codebuff.constants import EXCLUDED_DIRS

@dataclass
class FileExplorerDependencies:
    config: YAMLConfig
    container: dagger.Container
    focus_area: str = "entire project"

async def scan_directory_structure(ctx: RunContext[FileExplorerDependencies], path: str = ".") -> str:
    print(blue(f"📁 Scanning: {path}"))
    try:
        # Build find command with common exclusions
        exclude_args = " ".join([f"-not -path '*/{dir}/*'" for dir in EXCLUDED_DIRS])
        
        tree_output = await ctx.deps.container.with_exec([
            "bash", "-c", f"find {path} -type f {exclude_args} \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' -o -name '*.java' -o -name '*.go' -o -name '*.rs' -o -name '*.cpp' -o -name '*.c' -o -name '*.h' \) | head -50"
        ]).stdout()
        print(green("✅ Directory scan completed"))
        return f"Directory scan results:\n{tree_output}"
    except Exception as e:
        return f"Error scanning directory: {e}"

def create_file_explorer_agent(model: OpenAIModel) -> Agent:
    system_prompt = """You are a File Explorer Agent equivalent to Codebuff's file exploration.
Your role: Map project structure, identify key files, provide codebase context.
Use scan_directory_structure to explore the codebase."""
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=FileExplorerDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=3
    )
    agent.tool(scan_directory_structure)
    return agent

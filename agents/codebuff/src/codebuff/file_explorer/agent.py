from dataclasses import dataclass
import dagger
from dagger import dag
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, green
from ..constants import EXCLUDED_DIRS

# Add imports for structured exploration
import os
import json
from typing import List

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
            "bash", "-c", rf"find {path} -type f {exclude_args} \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' -o -name '*.java' -o -name '*.go' -o -name '*.rs' -o -name '*.cpp' -o -name '*.c' -o -name '*.h' \) | head -50"
        ]).stdout()
        print(green("✅ Directory scan completed"))
        return f"Directory scan results:\n{tree_output}"
    except Exception as e:
        return f"Error scanning directory: {e}"

# New: Explore codebase with CodeMap Dagger module + language summary


async def explore_codebase(ctx: RunContext[FileExplorerDependencies], token_budget: int = 15000) -> str:
    """Build a structured snapshot of the repo using CodeMap (no CLI).
    Returns: JSON with focus_area, languages, truncation (approx), tree.
    """
    print(blue("🗺️ Building project context via CodeMap"))

    def _collect_paths(nodes: List[any]) -> List[str]:
        out: List[str] = []
        for n in nodes:
            if getattr(n, "type", "") == "file":
                out.append(getattr(n, "filePath", ""))
            elif getattr(n, "children", None):
                out.extend(_collect_paths(n.children))
        return out

    try:
        project_root = os.getcwd()

        # Keep fast language summary using local tree (cheap and robust)
        pctx = await dag.code_map().get_project_file_context(project_root)
        file_paths = _collect_paths(pctx.fileTree)
        lang_counts = {}
        for fp in file_paths:
            ext = os.path.splitext(fp)[1].lower() or ""
            if ext.startswith('.'):
                ext = ext[1:]
            lang_counts[ext or "none"] = lang_counts.get(ext or "none", 0) + 1

        # Build code map and print token-annotated tree
        import json
        code_map = await dag.code_map().set_config_from_string(json.dumps(ctx.deps.config.model_dump()))
        src_dir = ctx.deps.container.directory(".")
        map_dir = await code_map.build(source_dir=src_dir)
        tree_text = await code_map.print_tree(map_dir=map_dir, with_tokens=True)

        # Rough token estimate from output length
        estimated_tokens = max(0, len(tree_text) // 3)
        payload = {
            "focus_area": ctx.deps.focus_area,
            "project_root": project_root,
            "file_count": len(file_paths),
            "languages": dict(sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:12]),
            "truncation": {
                "level": "code-map",
                "estimated_tokens": estimated_tokens,
                "budget": token_budget,
            },
            "tree": tree_text[:100000],
        }
        print(green("✅ Project context built via CodeMap"))
        return json.dumps(payload)
    except Exception as e:
        return json.dumps({
            "error": f"Failed to explore codebase: {e}",
        })

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
    # New tool: structured exploration with token-aware truncated tree
    agent.tool(explore_codebase)
    return agent


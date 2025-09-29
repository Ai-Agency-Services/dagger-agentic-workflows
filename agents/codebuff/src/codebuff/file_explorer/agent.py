import json
import os
from dataclasses import dataclass
from typing import Optional

import dagger
from codebuff.file_picker.agent import (FilePickerDependencies,
                                        create_file_picker_agent)
from dagger import dag
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

from simple_chalk import blue, green


@dataclass
class FileExplorerDependencies:
    config_file: dagger.File
    container: dagger.Container
    focus_area: str
    code_map: Optional[dagger.Directory] = None
    query: Optional[str] = None


async def scan_directory_structure(ctx: RunContext[FileExplorerDependencies], path: str = ".") -> str:
    print(blue(f"📁 Scanning: {path}"))
    try:
        # Get file token scores for exploration
        code_map_service = dag.code_map(config_file=ctx.deps.config_file)
        src_dir = ctx.deps.container.directory(".")
        scores_json = await code_map_service.get_file_token_scores(source_dir=src_dir)
        
        # Parse and format output
        try:
            scores_data = json.loads(scores_json)
            file_scores = scores_data.get("fileTokenScores", {})
            output = f"Found {len(file_scores)} files with tokens\n"
            
            # Show top files by token diversity
            if file_scores:
                sorted_files = sorted(file_scores.items(), key=lambda x: len(x[1]), reverse=True)[:10]
                for path, tokens in sorted_files:
                    output += f"  {path}: {len(tokens)} unique tokens\n"
        except Exception:
            output = "File exploration completed"

        print(green("✅ Directory scan completed"))
        return f"Directory scan results:\n{output}"
    except Exception as e:
        return f"Error scanning directory: {e}"


async def explore_codebase(ctx: RunContext[FileExplorerDependencies], token_budget: int = 15000) -> str:
    """Build a structured snapshot of the repo using CodeMap (no CLI).
    Returns: JSON with focus_area, languages, truncation (approx), tree.
    """
    print(blue("🗺️ Building project context via CodeMap"))

    try:
        project_root = os.getcwd()

        # Build code map and analyze structure
        if not ctx.deps.config_file:
            return json.dumps({"error": "File Explorer missing config_file; orchestrator must pass a Dagger File."})

        code_map_service = dag.code_map(config_file=ctx.deps.config_file)
        src_dir = ctx.deps.container.directory(".")
        scores_json = await code_map_service.get_file_token_scores(source_dir=src_dir)
        
        # Parse scores and create tree summary
        try:
            scores_data = json.loads(scores_json)
            file_scores = scores_data.get("fileTokenScores", {})
            total_files = len(file_scores)
            total_tokens = sum(len(tokens) for tokens in file_scores.values())
            
            tree_text = f"Project Analysis Summary:\n"
            tree_text += f"Files analyzed: {total_files}\n"
            tree_text += f"Unique tokens found: {total_tokens}\n\n"
            
            # Add language distribution
            lang_counts = {}
            for file_path in file_scores.keys():
                ext = os.path.splitext(file_path)[1].lower()
                if ext:
                    ext = ext[1:]  # remove dot
                lang_counts[ext or "none"] = lang_counts.get(ext or "none", 0) + 1
            
            if lang_counts:
                tree_text += "Language distribution:\n"
                for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    tree_text += f"  {lang}: {count} files\n"
                tree_text += "\n"
            
            # Add top files by token diversity
            if file_scores:
                sorted_files = sorted(file_scores.items(), key=lambda x: len(x[1]), reverse=True)[:15]
                tree_text += "Top files by token diversity:\n"
                for path, tokens in sorted_files:
                    tree_text += f"  {path}: {len(tokens)} tokens\n"
        except Exception:
            tree_text = "File exploration completed (token analysis failed)"

        # Extract language information from tree_text for simplified analysis
        # This is a simplified approach - in a production system you might want more sophisticated parsing
        lang_counts = {}
        lines = tree_text.split('\n')
        file_count = 0
        for line in lines:
            if '.' in line and not line.strip().startswith('├─') and not line.strip().startswith('└─'):
                continue
            # Look for file extensions in the tree output
            parts = line.split('.')
            if len(parts) > 1:
                # Get extension before any spaces/metadata
                ext = parts[-1].split()[0].lower()
                if ext and len(ext) <= 5:  # Reasonable extension length
                    lang_counts[ext] = lang_counts.get(ext, 0) + 1
                    file_count += 1

        # Rough token estimate from output length
        estimated_tokens = max(0, len(tree_text) // 3)
        payload = {
            "focus_area": ctx.deps.focus_area,
            "project_root": project_root,
            "file_count": file_count,
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


def create_file_explorer_agent(model: OpenAIChatModel) -> Agent:
    system_prompt = """You are a File Explorer Agent equivalent to Codebuff's file exploration.
Your role: Map project structure, identify key files, provide codebase context.
Use scan_directory_structure to explore the codebase."""

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=FileExplorerDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=3,
        output_type=list[str]
    )

    file_picker_agent = create_file_picker_agent(model)
    agent.tool(file_picker_agent)
    agent.tool(scan_directory_structure)
    agent.tool(explore_codebase)
    return agent

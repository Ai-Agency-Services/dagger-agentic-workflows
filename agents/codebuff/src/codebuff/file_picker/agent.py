import json
import re
from dataclasses import dataclass
from typing import List, Optional

import dagger
import yaml
from ais_dagger_agents_config import YAMLConfig
from codebuff.utils.container_state import append_log, write_json
from dagger import dag  # Added for cross-module Dagger calls
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

from simple_chalk import blue, green, yellow

from codebuff.constants import EXCLUDED_DIRS

# Code file extensions that should be prioritized
CODE_EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.java', '.rs', 
    '.cpp', '.c', '.cc', '.cxx', '.h', '.hpp', '.cs', '.php',
    '.rb', '.swift', '.kt', '.scala', '.clj', '.hs', '.elm',
    '.vue', '.svelte', '.dart', '.r', '.jl', '.m', '.mm'
}

# Non-code files to exclude from selection
NON_CODE_EXTENSIONS = {
    '.md', '.txt', '.rst', '.csv', '.jsonl', '.log', '.out',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf',
    '.lock', '.yml', '.yaml', '.toml', '.xml', '.html', '.css',
    '.json', '.LICENSE', '.gitignore', '.gitkeep', '.env'
}

def _is_code_file(file_path: str) -> bool:
    """Check if a file is a code file based on extension."""
    if not file_path or '.' not in file_path:
        return False
    ext = '.' + file_path.split('.')[-1].lower()
    return ext in CODE_EXTENSIONS and ext not in NON_CODE_EXTENSIONS

def _filter_code_files(file_paths: list) -> list:
    """Filter list to only include code files."""
    return [path for path in file_paths if _is_code_file(path)]


@dataclass
class FilePickerDependencies:
    config: YAMLConfig
    container: dagger.Container
    task_description: str
    config_file: Optional[dagger.File] = None


# --- Tools ---
async def semantic_query(
    ctx: RunContext[FilePickerDependencies],
    query: str,
    top: int = 20
) -> str:
    """Semantic-lite ranking using code-map token scores.
    Returns JSON array: [{ path, score, reason }]
    """
    if not ctx.deps.config_file:
        return json.dumps({"error": "File Picker missing config_file; orchestrator must pass a Dagger File."})

    try:
        code_map = dag.code_map(config_file=ctx.deps.config_file)
        src_dir = ctx.deps.container.directory(".")
        scores_json = await code_map.get_file_token_scores(source_dir=src_dir)
        scores_data = json.loads(scores_json)
        file_scores = scores_data.get("fileTokenScores", {}) or {}

        # Tokenize query
        query_text = (query or ctx.deps.task_description or "").lower()
        q_tokens = [t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query_text) if len(t) > 1]
        if not q_tokens:
            return json.dumps([])

        ranked = []
        for path, token_map in file_scores.items():
            # Skip non-code files
            if not _is_code_file(path):
                continue
                
            # Skip excluded directories
            if any(ex in path for ex in EXCLUDED_DIRS):
                continue
                
            score = 0.0
            matched = []
            for qt in q_tokens:
                v = token_map.get(qt)
                if v:
                    score += float(v)
                    matched.append(qt)
            if score > 0:
                # Boost score for code files
                if _is_code_file(path):
                    score *= 1.5
                ranked.append({
                    "path": path,
                    "score": round(score, 4),
                    "reason": f"code file, matched: {', '.join(matched[:5])}"
                })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return json.dumps(ranked[: max(1, int(top))])
    except Exception as e:
        return json.dumps({"error": f"semantic_query failed: {e}"})


async def search_relevant_files(
    ctx: RunContext[FilePickerDependencies],
    pattern: str,
    cwd: Optional[str] = None,
    max_results: int = 100
) -> str:
    """Search for files by name/content using ripgrep/grep fallback. Returns JSON array of paths."""
    try:
        workdir = cwd or "."
        cmd = f"cd {workdir} && (rg -n --no-messages '{pattern}' || grep -R -n -I -E '{pattern}' . || true)"
        run = ctx.deps.container.with_exec(["bash", "-lc", cmd])
        out = await run.stdout()
        paths = []
        seen = set()
        for line in (out or "").splitlines():
            # rg/grep: path:line:content
            p = line.split(":", 1)[0]
            if not p:
                continue
            if any(ex in p for ex in EXCLUDED_DIRS):
                continue
            # Filter to only code files
            if not _is_code_file(p):
                continue
            if p not in seen:
                seen.add(p)
                paths.append(p)
            if len(paths) >= max_results:
                break
        # Filter to only code files before returning
        code_paths = _filter_code_files(paths)
        return json.dumps(code_paths)
    except Exception as e:
        return json.dumps({"error": f"search_relevant_files failed: {e}"})


async def analyze_file_relevance(
    ctx: RunContext[FilePickerDependencies],
    files: List[str]
) -> str:
    """Analyze files for task relevance using simple name/token overlap with task description.
    Returns JSON array: [{ path, score, reason }]
    """
    try:
        desc = (ctx.deps.task_description or "").lower()
        desc_tokens = set([t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", desc) if len(t) > 1])
        results = []
        for p in files or []:
            # Only analyze code files
            if not _is_code_file(p):
                continue
                
            base = p.split("/")[-1].lower()
            name_tokens = set([t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", base) if len(t) > 1])
            overlap = sorted(desc_tokens.intersection(name_tokens))
            score = float(len(overlap))
            
            # Boost score for code files
            if _is_code_file(p):
                score *= 1.2
                
            if score > 0:
                results.append({
                    "path": p,
                    "score": score,
                    "reason": f"code file, name overlap: {', '.join(overlap[:5])}"
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return json.dumps(results[:50])
    except Exception as e:
        return json.dumps({"error": f"analyze_file_relevance failed: {e}"})


# --- Agent ---
def create_file_picker_agent(model: OpenAIChatModel) -> Agent:
    """Create the File Picker agent."""
    system_prompt = """
You are a File Picker Agent, equivalent to Codebuff's file selection capabilities.

Your role:
- Identify the most relevant files for a given coding task
- Filter out irrelevant files to focus attention
- Prioritize files based on relevance to the task
- Provide a curated list of files to work with

Tools:
1. search_relevant_files - Search for files by name and content
2. analyze_file_relevance - Analyze files for task relevance
3. semantic_query - Semantic-lite ranking using code-map
"""

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=FilePickerDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=3
    )

    # Register tools
    agent.tool(search_relevant_files)
    agent.tool(analyze_file_relevance)
    agent.tool(semantic_query)

    print(f"File Picker Agent created with model: {model.model_name}")
    return agent


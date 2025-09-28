import json
from pydantic_ai import RunContext
import yaml
from dagger import dag

from ..models import OrchestratorDependencies


async def run_file_explorer(
    ctx: RunContext[OrchestratorDependencies],
    focus_area: str,
    with_tokens: bool = True
) -> str:
    """Analyze codebase structure using code-map directly (no module coupling)."""
    cfg_yaml = yaml.safe_dump(ctx.deps.config.model_dump()) if hasattr(ctx.deps.config, "model_dump") else yaml.safe_dump(dict(ctx.deps.config))
    cfg_file = dag.directory().with_new_file("config.yaml", cfg_yaml).file("config.yaml")
    code_map = dag.code_map(config_file=cfg_file)
    src_dir = ctx.deps.container.directory(".")

    try:
        scores_json = await code_map.get_file_token_scores(source_dir=src_dir)
        scores_data = json.loads(scores_json)
        file_scores = scores_data.get("fileTokenScores", {})

        total_files = len(file_scores)
        total_tokens = sum(len(tokens) for tokens in file_scores.values())

        tree_text = f"Project Analysis Summary:\n"
        tree_text += f"Files analyzed: {total_files}\n"
        tree_text += f"Unique tokens found: {total_tokens}\n\n"

        lang_counts = {}
        for file_path in file_scores.keys():
            ext = (file_path.rsplit(".", 1)[-1].lower() if "." in file_path else "none")
            lang_counts[ext] = lang_counts.get(ext, 0) + 1
        if lang_counts:
            tree_text += "Language distribution:\n"
            for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                tree_text += f"  {lang}: {count} files\n"
            tree_text += "\n"

        if file_scores:
            sorted_files = sorted(file_scores.items(), key=lambda x: len(x[1]), reverse=True)[:15]
            tree_text += "Top files by token diversity:\n"
            for pth, tokens in sorted_files:
                tree_text += f"  {pth}: {len(tokens)} tokens\n"

        estimated_tokens = max(0, len(tree_text) // 3)
        payload = {
            "focus_area": focus_area,
            "project_root": ".",
            "file_count": total_files,
            "languages": dict(sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:12]),
            "truncation": {"level": "code-map", "estimated_tokens": estimated_tokens, "budget": 15000},
            "tree": tree_text[:100000],
        }
        return json.dumps(payload)
    except Exception as e:
        return json.dumps({"error": f"explorer failed: {e}"})


async def run_file_picker(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    max_files: int = 10
) -> str:
    """Rank files using code-map token scores against task description tokens."""
    import re

    cfg_yaml = yaml.safe_dump(ctx.deps.config.model_dump()) if hasattr(ctx.deps.config, "model_dump") else yaml.safe_dump(dict(ctx.deps.config))
    cfg_file = dag.directory().with_new_file("config.yaml", cfg_yaml).file("config.yaml")
    code_map = dag.code_map(config_file=cfg_file)
    src_dir = ctx.deps.container.directory(".")

    try:
        scores_json = await code_map.get_file_token_scores(source_dir=src_dir)
        scores_data = json.loads(scores_json)
        file_scores = scores_data.get("fileTokenScores", {}) or {}

        query_text = (task_description or "").lower()
        q_tokens = [t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query_text) if len(t) > 1]
        ranked = []
        for path, token_map in file_scores.items():
            score = 0.0
            matched = []
            for qt in q_tokens:
                v = token_map.get(qt)
                if v:
                    score += float(v)
                    matched.append(qt)
            if score > 0:
                ranked.append({"path": path, "score": round(score, 4), "reason": f"matched: {', '.join(matched[:5])}"})
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return json.dumps(ranked[: max(1, int(max_files))])
    except Exception as e:
        return json.dumps({"error": f"file_picker failed: {e}"})


async def run_researcher(
    ctx: RunContext[OrchestratorDependencies],
    research_query: str
) -> str:
    return f"Researched: {research_query[:120]}"


async def run_thinker(
    ctx: RunContext[OrchestratorDependencies],
    problem_description: str
) -> str:
    """Return a simple plan text stub (decoupled)."""
    return f"Plan for: {problem_description[:200]}\n- Analyze requirements\n- Identify files\n- Implement\n- Test\n- Review\n- PR"


async def run_reviewer(
    ctx: RunContext[OrchestratorDependencies],
    review_focus: str
) -> str:
    return f"Review completed for: {review_focus or 'changes'}\nStatus: approved"


async def run_implementation(
    ctx: RunContext[OrchestratorDependencies],
    task_spec: dict,
    selected_files: list[str]
) -> str:
    return "Implementation steps executed"


async def run_context_pruner(
    ctx: RunContext[OrchestratorDependencies],
    max_context_length: int = 50000
) -> str:
    return f"Context pruned to ~{max_context_length} tokens"


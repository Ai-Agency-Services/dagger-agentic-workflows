from typing import Optional
import json
from pydantic_ai import RunContext

from ..models import OrchestratorDependencies
from codebuff.utils.container_state import append_log, write_text


async def create_plan(
    ctx: RunContext[OrchestratorDependencies],
    path: str,
    plan: str,
) -> str:
    """Write a plan document to .codebuff-state/plans/<path> and log it."""
    try:
        # Normalize user input to avoid double-prefixing '.codebuff-state/plans/'
        rel = (path or "").strip().lstrip("/")
        if rel.startswith(".codebuff-state/"):
            rel = rel[len(".codebuff-state/"):]
        if rel.startswith("plans/"):
            rel = rel[len("plans/"):]
        full_path = f"plans/{rel or 'plan.md'}"

        if getattr(ctx.deps, "container", None) is not None:
            ctx.deps.container = await write_text(ctx.deps.container, full_path, plan)
            ctx.deps.container = await append_log(ctx.deps.container, f"create_plan: wrote {full_path}")
        return f"Plan written: {full_path}"
    except Exception as e:
        return f"Error writing plan: {e}"


async def add_subgoal(
    ctx: RunContext[OrchestratorDependencies],
    id: str,
    objective: str,
    status: str
) -> str:
    """Append a subgoal entry into .codebuff-state/subgoals.json."""
    try:
        entry = {"id": id, "objective": objective, "status": status}
        subs_path = ".codebuff-state/subgoals.json"
        content = "[]"
        try:
            content = await ctx.deps.container.file(subs_path).contents()
        except Exception:
            pass
        try:
            arr = json.loads(content) if content else []
        except Exception:
            arr = []
        arr.append(entry)
        ctx.deps.container = ctx.deps.container.with_new_file(
            subs_path, json.dumps(arr, indent=2))
        ctx.deps.container = await append_log(ctx.deps.container, f"add_subgoal: {id}")
        return f"Subgoal added: {id}"
    except Exception as e:
        return f"Error adding subgoal: {e}"


async def update_subgoal(
    ctx: RunContext[OrchestratorDependencies],
    id: str,
    status: Optional[str] = None,
    log: Optional[str] = None
) -> str:
    """Update a subgoal in .codebuff-state/subgoals.json and append a log entry."""
    try:
        subs_path = ".codebuff-state/subgoals.json"
        content = "[]"
        try:
            content = await ctx.deps.container.file(subs_path).contents()
        except Exception:
            pass
        try:
            arr = json.loads(content) if content else []
        except Exception:
            arr = []
        for item in arr:
            if item.get("id") == id:
                if status is not None:
                    item["status"] = status
                if log:
                    item.setdefault("logs", []).append(log)
        ctx.deps.container = ctx.deps.container.with_new_file(
            subs_path, json.dumps(arr, indent=2))
        if log:
            ctx.deps.container = await append_log(ctx.deps.container, f"update_subgoal: {id} - {log}")
        return f"Subgoal updated: {id}"
    except Exception as e:
        return f"Error updating subgoal: {e}"


async def think_deeply(
    ctx: RunContext[OrchestratorDependencies],
    thought: str
) -> str:
    """Return a structured reflection string."""
    return f"Deep analysis: {thought}"

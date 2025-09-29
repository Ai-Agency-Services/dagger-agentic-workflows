from typing import Optional
import json
from pydantic_ai import RunContext

from ..models import OrchestratorDependencies


async def read_files(
    ctx: RunContext[OrchestratorDependencies],
    paths: list[str]
) -> str:
    out = []
    for p in paths or []:
        try:
            content = await ctx.deps.container.file(p).contents()
            out.append({"path": p, "content": content})
        except Exception as e:
            out.append({"path": p, "error": str(e)})
    return json.dumps(out)


async def write_file(
    ctx: RunContext[OrchestratorDependencies],
    path: str,
    instructions: str,
    content: str
) -> str:
    try:
        ctx.deps.container = ctx.deps.container.with_new_file(path, content)
        return f"Wrote: {path}"
    except Exception as e:
        return f"Error writing file {path}: {e}"


async def str_replace(
    ctx: RunContext[OrchestratorDependencies],
    path: str,
    replacements: list[dict]
) -> str:
    try:
        src = await ctx.deps.container.file(path).contents()
    except Exception as e:
        return f"Error reading {path}: {e}"
    changed = src
    for rep in (replacements or []):
        old = rep.get("old", "")
        new = rep.get("new", "")
        if old:
            changed = changed.replace(old, new)
    try:
        ctx.deps.container = ctx.deps.container.with_new_file(path, changed)
        return f"Replaced in: {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"


async def code_search(
    ctx: RunContext[OrchestratorDependencies],
    pattern: str,
    flags: Optional[str] = None,
    cwd: Optional[str] = None,
    max_results: int = 30
) -> str:
    try:
        workdir = cwd or "."
        cmd = f"cd {workdir} && (rg {pattern} -n || grep -R -n -I -E \"{pattern}\" . || true)"
        run = ctx.deps.container.with_exec(["bash", "-lc", cmd])
        out = await run.stdout()
        return out or ""
    except Exception as e:
        return f"Search error: {e}"

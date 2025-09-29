from typing import Optional
from pydantic_ai import RunContext

from ..models import OrchestratorDependencies


async def run_terminal_command(
    ctx: RunContext[OrchestratorDependencies],
    command: str,
    process_type: str = "SYNC",
    cwd: Optional[str] = None,
    timeout_seconds: int = 30
) -> str:
    try:
        cmd = command if not cwd else f"cd {cwd} && {command}"
        run = ctx.deps.container.with_exec(["bash", "-lc", cmd])
        out = await run.stdout()
        return out or ""
    except Exception as e:
        return f"Command error: {e}"


async def browser_logs(
    ctx: RunContext[OrchestratorDependencies],
    type: str,
    url: str,
    wait_until: str = "load"
) -> str:
    # Placeholder in this runtime
    return f"browser_logs not supported in orchestrator runtime (requested {type} {url})"

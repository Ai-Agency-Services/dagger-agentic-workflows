import json
from typing import Any, Optional
import dagger
from datetime import datetime, timezone

STATE_DIR = ".codebuff-state"

async def write_json(c: dagger.Container, rel_path: str, data: Any) -> dagger.Container:
    """Write JSON to .codebuff-state/<rel_path> and return updated container."""
    payload = json.dumps(data, indent=2)
    return c.with_new_file(f"{STATE_DIR}/{rel_path}", payload)

async def write_text(c: dagger.Container, rel_path: str, text: str) -> dagger.Container:
    """Write text to .codebuff-state/<rel_path> and return updated container."""
    return c.with_new_file(f"{STATE_DIR}/{rel_path}", text)

async def append_log(c: dagger.Container, line: str) -> dagger.Container:
    """Append a line to .codebuff-state/log.txt (best-effort)."""
    try:
        existing = await c.file(f"{STATE_DIR}/log.txt").contents()
        content = (existing + "\n" + line).rstrip("\n")
    except Exception:
        content = line
    return c.with_new_file(f"{STATE_DIR}/log.txt", content + "\n")

# Add new helper to persist current phase and status
async def write_current_phase(c: dagger.Container, phase: str, status: str, extra: Optional[dict] = None) -> dagger.Container:
    """Write current phase snapshot to .codebuff-state/current_phase.json."""
    payload = {
        "schema_version": 1,
        "phase": phase,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        payload.update(extra)
    return await write_json(c, "current_phase.json", payload)

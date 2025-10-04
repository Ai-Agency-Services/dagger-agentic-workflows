import json
from typing import Any
from dagger import dag

# Minimal async wrappers used in tests
aSYNC_OK = True

async def file_explorer_agent(ctx: Any, focus_area: str) -> str:
    """Return a simple JSON payload including the focus_area."""
    # In real implementation, this would run the file explorer sub-agent.
    payload = {
        "focus_area": focus_area,
        "status": "ok"
    }
    return json.dumps(payload)

async def run_file_picker(ctx: Any, query: str) -> str:
    """Return a JSON array of files (empty list by default)."""
    # In real implementation, this would call CodeMap and rank files.
    return json.dumps([])

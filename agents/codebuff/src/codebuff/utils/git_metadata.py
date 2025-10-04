from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def embed_state_metadata(header: str, *, task_id: str | None, phase: str | None, status: str | None) -> str:
    """Return a commit message with a JSON metadata footer for state resumption.

    Footer format:
    ---
    {"schema_version": 1, "task_id": "...", "phase": "...", "status": "...", "timestamp": "..."}
    """
    footer = {
        "schema_version": 1,
        "task_id": task_id,
        "phase": phase,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return f"{header}\n\n---\n{json.dumps(footer, separators=(',', ':'))}\n"


def extract_state_metadata(commit_message: str) -> Optional[Dict[str, Any]]:
    """Extract the JSON footer from a commit message, if present.

    Looks for the last line starting with '---' and parses the following line as JSON.
    Returns dict or None.
    """
    if not commit_message:
        return None
    try:
        lines = commit_message.strip().splitlines()
        # Find last '---'
        cut = None
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == '---':
                cut = i
                break
        if cut is None or cut + 1 >= len(lines):
            return None
        json_line = lines[cut + 1].strip()
        if not json_line:
            return None
        data = json.loads(json_line)
        if not isinstance(data, dict):
            return None
        return data
    except Exception:
        return None

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import json
from dagger import Container

STATE_DIR = ".codebuff-state"

SUPPORTED_ACTIONS = [
    "approve",
    "modify",
    "cancel",
    "add-files",
    "revise-plan",
]


def _normalize_comment(c: Any) -> Tuple[str, Optional[str], Optional[str]]:
    """Return (body, author, created_at) for dict or str comments."""
    if isinstance(c, str):
        return c, None, None
    if isinstance(c, dict):
        body = c.get("body") or c.get("text") or ""
        author = (c.get("user") or {}).get("login") if isinstance(c.get("user"), dict) else c.get("author")
        created = c.get("created_at") or c.get("timestamp")
        return str(body or ""), author, created
    return str(c), None, None


def parse_orchestrator_commands(comments: List[Any]) -> Optional[Dict[str, Any]]:
    """Parse a list of PR comments and return the latest structured orchestrator command.

    Returns: { action, args, by, created_at }
    """
    latest: Optional[Dict[str, Any]] = None
    for raw in comments:
        body, author, ts = _normalize_comment(raw)
        text = (body or "").strip().lower()
        if not text.startswith("@orchestrator"):
            continue
        # extract action and args
        after = text[len("@orchestrator"):].strip()
        if not after:
            continue
        # match supported actions in order
        action = None
        args = ""
        for a in SUPPORTED_ACTIONS:
            if after.startswith(a):
                action = a
                args = after[len(a):].strip()
                break
        if not action:
            continue
        cmd = {
            "action": action,
            "args": args,
            "by": author,
            "created_at": ts,
        }
        latest = cmd  # assume list is chronological or we always want last occurrence
    return latest


async def _read_json(container: Container, rel_path: str) -> Optional[dict]:
    try:
        raw = await container.file(f"{STATE_DIR}/{rel_path}").contents()
        return json.loads(raw) if raw else None
    except Exception:
        return None


async def load_feedback_sentinel(container: Container) -> dict:
    data = await _read_json(container, "feedback_sentinel.json")
    return data or {}


async def load_user_feedback(container: Container) -> Optional[dict]:
    return await _read_json(container, "user_feedback.json")


async def save_user_feedback(container: Container, feedback: Dict[str, Any]) -> Container:
    payload = json.dumps(feedback, indent=2)
    return container.with_new_file(f"{STATE_DIR}/user_feedback.json", payload)

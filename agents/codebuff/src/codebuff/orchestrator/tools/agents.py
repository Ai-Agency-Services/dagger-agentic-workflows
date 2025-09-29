import json
from typing import Optional
from pydantic_ai import RunContext

from ..models import OrchestratorDependencies


async def spawn_agents(
    ctx: RunContext[OrchestratorDependencies],
    agents: list[dict]
) -> str:
    try:
        return json.dumps({"spawned": len(agents)})
    except Exception as e:
        return f"spawn_agents error: {e}"


async def spawn_agent_inline(
    ctx: RunContext[OrchestratorDependencies],
    agent_type: str,
    prompt: Optional[str] = None,
    params: Optional[dict] = None
) -> str:
    try:
        return json.dumps({"spawned_inline": agent_type, "prompt": prompt or ""})
    except Exception as e:
        return f"spawn_agent_inline error: {e}"


async def lookup_agent_info(
    ctx: RunContext[OrchestratorDependencies],
    agent_type: Optional[str] = None
) -> str:
    info = {
        "sub_agents": [
            "codebuff/file-explorer@0.0.2",
            "codebuff/file-picker@0.0.2",
            "codebuff/researcher@0.0.2",
            "codebuff/thinker@0.0.2",
            "codebuff/reviewer@0.0.2",
            "codebuff/context-pruner@0.0.2",
            "implementation"
        ]
    }
    return json.dumps(info)

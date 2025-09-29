from pydantic_ai import RunContext

from ..models import OrchestratorDependencies


async def end_turn(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    return "END"

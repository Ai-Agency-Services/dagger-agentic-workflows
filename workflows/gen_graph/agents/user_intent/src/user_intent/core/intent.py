# Import original tools and functionality first
# Then add AG-UI specific functionality

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ag_ui.core import StateSnapshotEvent, EventType
from pydantic_ai.ag_ui import StateDeps
from user_intent.models import UserIntentState, GraphIntent


# Add the missing UserIntentAgentDependencies class
@dataclass
class UserIntentAgentDependencies:
    """Dependencies for the UserIntentAgent."""
    state: Dict = field(default_factory=dict)


# Add the standard tool functions that match the original pattern
async def set_perceived_user_goal(ctx: RunContext[UserIntentAgentDependencies], kind_of_graph: str, graph_description: str) -> str:
    """Sets the perceived user's goal, including the kind of graph and its description.

    Args:
        kind_of_graph: 2-3 word definition of the kind of graph, for example "recent US patents"
        graph_description: a single paragraph description of the graph, summarizing the user's intent
    """
    user_goal_data = {"kind_of_graph": kind_of_graph,
                      "graph_description": graph_description}
    ctx.deps.state["perceived_user_goal"] = user_goal_data
    return f"Successfully stored perceived user goal: {user_goal_data}"


async def approve_perceived_user_goal(ctx: RunContext[UserIntentAgentDependencies]) -> str:
    """Upon approval from user, will record the perceived user goal as the approved user goal.

    Only call this tool if the user has explicitly approved the perceived user goal.
    """
    if "perceived_user_goal" not in ctx.deps.state:
        return "Error: perceived_user_goal not set. Set perceived user goal first, or ask clarifying questions if you are unsure."

    ctx.deps.state["approved_user_goal"] = ctx.deps.state["perceived_user_goal"]
    return f"Successfully approved user goal: {ctx.deps.state['approved_user_goal']}"


# Add the original create_user_intent_agent function
def create_user_intent_agent(pydantic_ai_model: OpenAIModel) -> Agent:
    """Create a pydantic_ai.Agent instance for knowledge graph use case ideation.

    Args:
        pydantic_ai_model: An instance of pydantic_ai.models.OpenAIModel
                           configured with the desired provider and API key.

    Returns:
        A configured pydantic_ai.Agent instance.
    """
    base_system_prompt = """
    You are an expert at knowledge graph use cases. 
    Your primary goal is to help the user come up with a knowledge graph use case.
    
    If the user is unsure what to do, make some suggestions based on classic use cases like:
    - social network involving friends, family, or professional relationships
    - logistics network with suppliers, customers, and partners
    - recommendation system with customers, products, and purchase patterns
    - fraud detection over multiple accounts with suspicious patterns of transactions
    - pop-culture graphs with movies, books, or music
    
    A user goal has two components:
    - kind_of_graph: at most 3 words describing the graph, for example "social network" or "USA freight logistics"
    - description: a few sentences about the intention of the graph, for example "A dynamic routing and delivery system for cargo." or "Analysis of product dependencies and supplier alternatives."
    
    Think carefully and collaborate with the user:
    1. Understand the user's goal, which is a kind_of_graph with description
    2. Ask clarifying questions as needed
    3. When you think you understand their goal, use the 'set_perceived_user_goal' tool to record your perception
    4. Present the perceived user goal to the user for confirmation
    5. If the user agrees, use the 'approve_perceived_user_goal' tool to approve the user goal. This will save the goal in state.
    """

    agent = Agent(
        model=pydantic_ai_model,
        system_prompt=base_system_prompt,
        deps_type=UserIntentAgentDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=3,
        output_type=str,
    )

    agent.tool(set_perceived_user_goal)
    agent.tool(approve_perceived_user_goal)

    return agent


# Add AG-UI specific tools
async def set_perceived_user_goal_ag_ui(
    ctx: RunContext[StateDeps[UserIntentState]],
    kind_of_graph: str,
    graph_description: str
) -> StateSnapshotEvent:
    """Sets the perceived user's goal, including the kind of graph and its description.

    Args:
        kind_of_graph: 2-3 word definition of the kind of graph, for example "recent US patents"
        graph_description: a single paragraph description of the graph, summarizing the user's intent
    """
    user_goal_data = {"kind_of_graph": kind_of_graph,
                      "graph_description": graph_description}
    ctx.deps.state.perceived_user_goal = user_goal_data

    # Return a state snapshot event to update the UI
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot=ctx.deps.state.model_dump(),
    )


async def approve_perceived_user_goal_ag_ui(
    ctx: RunContext[StateDeps[UserIntentState]]
) -> StateSnapshotEvent:
    """Upon approval from user, will record the perceived user goal as the approved user goal.

    Only call this tool if the user has explicitly approved the perceived user goal.
    """
    # Trust, but verify.
    # Require that the perceived goal was set before approving it.
    if ctx.deps.state.perceived_user_goal is None:
        raise ValueError(
            "perceived_user_goal not set. Set perceived user goal first, or ask clarifying questions")

    # Convert to proper GraphIntent object
    ctx.deps.state.approved_user_goal = GraphIntent(
        kind_of_graph=ctx.deps.state.perceived_user_goal["kind_of_graph"],
        graph_description=ctx.deps.state.perceived_user_goal["graph_description"]
    )

    # Return a state snapshot event to update the UI
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot=ctx.deps.state.model_dump(),
    )


def create_user_intent_agent_with_ag_ui(pydantic_ai_model: OpenAIModel) -> Agent:
    """Create a pydantic_ai.Agent instance for knowledge graph use case ideation with AG-UI support.

    Args:
        pydantic_ai_model: An instance of pydantic_ai.models.OpenAIModel
                           configured with the desired provider and API key.

    Returns:
        A configured pydantic_ai.Agent instance with AG-UI support.
    """
    base_system_prompt = """
    You are an expert at knowledge graph use cases. 
    Your primary goal is to help the user come up with a knowledge graph use case.
    
    If the user is unsure what to do, make some suggestions based on classic use cases like:
    - social network involving friends, family, or professional relationships
    - logistics network with suppliers, customers, and partners
    - recommendation system with customers, products, and purchase patterns
    - fraud detection over multiple accounts with suspicious patterns of transactions
    - pop-culture graphs with movies, books, or music
    
    A user goal has two components:
    - kind_of_graph: at most 3 words describing the graph, for example "social network" or "USA freight logistics"
    - description: a few sentences about the intention of the graph, for example "A dynamic routing and delivery system for cargo." or "Analysis of product dependencies and supplier alternatives."
    
    Think carefully and collaborate with the user:
    1. Understand the user's goal, which is a kind_of_graph with description
    2. Ask clarifying questions as needed
    3. When you think you understand their goal, use the 'set_perceived_user_goal' tool to record your perception
    4. Present the perceived user goal to the user for confirmation
    5. If the user agrees, use the 'approve_perceived_user_goal' tool to approve the user goal. This will save the goal in state.
    """

    agent = Agent(
        model=pydantic_ai_model,
        system_prompt=base_system_prompt,
        deps_type=StateDeps[UserIntentState],
        instrument=True,
        end_strategy="exhaustive",
        retries=3,
        output_type=str
    )

    agent.tool(set_perceived_user_goal_ag_ui)
    agent.tool(approve_perceived_user_goal_ag_ui)

    return agent


# Export necessary components
__all__ = [
    "UserIntentAgentDependencies",
    "create_user_intent_agent",
    "create_user_intent_agent_with_ag_ui",
    "set_perceived_user_goal",
    "approve_perceived_user_goal"
]

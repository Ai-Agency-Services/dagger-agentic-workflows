from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any


class GraphIntent(BaseModel):
    """A Pydantic model representing the user's graph intent."""
    kind_of_graph: str = Field(
        description="Short phrase describing the graph type (2-3 words)")
    graph_description: str = Field(
        description="Detailed description of the graph purpose and components")


class UserIntentState(BaseModel):
    """State model for the user intent agent interaction."""
    perceived_user_goal: Optional[Dict[str, str]] = None
    approved_user_goal: Optional[GraphIntent] = None
    chat_history: List[Dict[str, Any]] = Field(default_factory=list)

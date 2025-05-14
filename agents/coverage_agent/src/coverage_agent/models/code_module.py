from typing import Optional  # Import Optional
from pydantic import BaseModel, Field


class CodeModule(BaseModel):
    """
    Represents a single code solution.
    Attributes:
        strategy: Optional[str]
        code: str
        error: Optional[str]
    """

    strategy: Optional[str] = Field(
        default=None,
        description="The strategy to improve test coverage.")
    code: str = Field(
        description="The complete code solution.")
    error: Optional[str] = Field(  # Keep error optional as well
        default=None,
        description="Error message if the code generation fails."
    )

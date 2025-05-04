from pydantic import BaseModel, Field


class CodeModule(BaseModel):
    """
    Represents a single code solution.
    Attributes:
        strategy: str
        imports: str
        code: str
    """

    strategy: str = Field(description="The strategy to improve test coverage.")
    imports: str = Field(
        description="The import statements for the code block.")
    code: str = Field(
        description="The code block excluding import statements.")

from pydantic import BaseModel, Field


class CodeModule(BaseModel):
    """
    Represents a single code solution.
    Attributes:
        strategy: str
        imports: str
        code: str
        test_path: str
        error: str
    """

    strategy: str = Field(description="The strategy to improve test coverage.")
    imports: str = Field(description="The import statements for the code block.")
    code: str = Field(description="The code block excluding import statements.")
    test_path: str = Field(description="Existing test paths for the file under test.")
    error: str = Field(
        description="The error message if the code block execution fails.", default=None
    )

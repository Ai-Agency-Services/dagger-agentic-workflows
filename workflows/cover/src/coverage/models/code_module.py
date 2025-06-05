from typing import Optional
from pydantic import BaseModel, Field


class CodeModule(BaseModel):
    """Represents a code module with strategy, imports and code."""
    strategy: str = Field(description="The strategy used to generate the code")
    imports: str = Field(description="The import statements for the code")
    code: str = Field(description="The generated code")
    error: Optional[str] = Field(
        default=None, description="Error message if test execution failed")
    test_path: Optional[str] = Field(
        default=None, description="Path where the test file was saved")

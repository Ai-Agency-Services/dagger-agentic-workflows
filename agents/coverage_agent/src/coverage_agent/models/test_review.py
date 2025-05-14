from typing import Optional
from pydantic import BaseModel, Field


class TestReview(BaseModel):
    """
    Represents the results of a test review.
    """

    test_result: bool = Field(
        description="Indicates True if all tests passed, False otherwise.",
        default=False
    )

    error: Optional[str] = Field(
        description="Error message if the test review failed.",
        default=None
    )

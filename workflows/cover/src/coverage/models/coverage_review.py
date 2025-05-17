from typing import Optional
from pydantic import BaseModel, Field


class CoverageReview(BaseModel):
    """
    Represents an analysis of the coverage report."""

    coverage_increased: bool = Field(
        description="Indicates if the coverage was increased after the review.",
        default=False
    )

    uncovered_code_segments: Optional[str] = Field(
        description="List of uncovered code segments in the coverage report.",
    )

    strategy: Optional[str] = Field(
        description="The strategy used to increase coverage.",
        default=None
    )

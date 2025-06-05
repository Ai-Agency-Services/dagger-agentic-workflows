from pydantic import BaseModel, Field
from typing import Optional


class CoverageReport(BaseModel):
    """
    Represents missing coverage in a codebase.
    Attributes:
        file: The file under test.
        coverage_report_path: The relevant coverage report path for the file under test.
        coverage_percentage: The overall coverage of the file under test.
        statements_percentage: The percentage of statements covered.
        branches_percentage: The percentage of branches covered.
        functions_percentage: The percentage of functions covered.
        lines_percentage: The percentage of lines covered.
    """

    file: str
    coverage_report_path: str
    coverage_percentage: float
    statements_percentage: Optional[float] = None
    branches_percentage: Optional[float] = None
    functions_percentage: Optional[float] = None
    lines_percentage: Optional[float] = None

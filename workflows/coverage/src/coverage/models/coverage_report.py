from pydantic import BaseModel, Field


class CoverageReport(BaseModel):
    """
    Represents missing coverage in a codebase.
    Attributes:
        file: The file under test.
        coverage_report_path: The relevant coverage report path for the file under test.
        coverage_percentage: The overall coverage of the file under test.
    """

    file: str = Field("The file under test.")
    coverage_report_path: str = Field(
        description="The relevant coverage report path for the file under test."
    )
    coverage_percentage: float = Field(
        description="The overall coverage of the file under test.", default=0.0
    )

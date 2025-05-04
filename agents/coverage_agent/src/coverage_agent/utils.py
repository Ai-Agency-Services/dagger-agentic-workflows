import json
import os
from typing import List, Tuple

import dagger
from simple_chalk import green

from .models.coverage_report import CoverageReport


def base_file_name(file_path: str, test_suffix: str):
    base_name = os.path.basename(file_path)
    file_name, file_extension = os.path.splitext(base_name)
    path = f"{file_name}.{test_suffix}{file_extension}"
    return path


def dagger_json_file_to_pydantic(json_file: dagger.File, pydantic_model: type) -> List:
    """
    Convert a Dagger JSON file to a list of Pydantic models.

    Args:
    json_file (dagger.File): The Dagger JSON file to convert.
    pydantic_model (type): The Pydantic model class to use for conversion.

    Returns:
    List: A list of Pydantic models.
    """

    async def convert():
        # Read the contents of the JSON file
        json_content = await json_file.contents()

        # Deserialize JSON content into a list of dictionaries
        data_list = json.loads(json_content)

        # Convert dictionaries back into Pydantic models
        return [pydantic_model.model_validate(item) for item in data_list]

    return convert()


def generate_code(code_module):
    """
    Combine the imports and code from a code module into a single string.

    Args:
        code_module: An object with `imports` and `code` attributes.

    Returns:
        str: The combined code as a string.
    """
    return f"{code_module.imports}\n{code_module.code}"


async def get_code_under_test_directory(
    test_container: dagger.Container, report: CoverageReport
) -> str:
    """
    Get the directory where the code under test is located.

    Args:
    test_container (dagger.Container): The test container.
    report (CoverageReport): The coverage report.

    Returns:
    str: The directory where the code under test is located.
    """
    print(f"Getting code under test directory for {report.file}")

    result = await test_container.with_exec(
        [
            "find",
            ".",
            "-type",
            "f",
            "-name",
            f"{report.file}",
            "-exec",
            "dirname",
            "{}",
            ";",
        ]
    ).stdout()

    code_under_test_dir = result.strip().replace("\n", "")
    print(f"Code under test directory: {code_under_test_dir}")
    return code_under_test_dir


def rank_reports_by_coverage(coverage_reports: List[CoverageReport]) -> List[str]:
    """
    Rank the modules based on the lack of coverage calculated by analyzing the statement, branches, and function percentages.

    Args:
        coverage_summary (list): The summary of the coverage report contained in a list.

    Returns:
        List[str]: The ranked files based on the lack of coverage.
    """

    # Sort the files based on coverage_percentage in ascending order (lowest coverage first)
    filtered_modules = [
        module for module in coverage_reports if module.coverage_percentage < 100.0
    ]
    sorted_modules = sorted(filtered_modules, key=lambda x: x.coverage_percentage)
    for module in sorted_modules:
        print(green(f"{module.file} - Coverage {module.coverage_percentage} %"))
    return sorted_modules

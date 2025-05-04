from typing import List, Optional, Tuple

import bs4
import dagger
from bs4 import BeautifulSoup
from jest_reporter_plugin.models.coverage_report import CoverageReport


def extract_coverage_data_from_table(
    index_html: str, report_directory: str, folder: Optional[str] = None
) -> List[CoverageReport]:
    """Extract coverage data from HTML coverage report."""
    soup = BeautifulSoup(index_html, "html.parser")
    coverage_data = []

    # Iterate through each row in the coverage summary table
    for row in soup.find_all("tr")[1:]:  # Skip the header row
        columns = row.find_all("td")
        if columns:
            file = columns[0].text.strip()
            path = columns[0].select("a")[0]["href"]
            coverage_report_path = (
                f"{report_directory}/{folder}/{path}"
                if folder
                else f"{report_directory}/{path}"
            )
            statements_percentage = float(
                columns[2].text.strip().replace("%", ""))
            branches_percentage = float(
                columns[4].text.strip().replace("%", ""))
            functions_percentage = float(
                columns[6].text.strip().replace("%", ""))
            lines_percentage = float(columns[8].text.strip().replace("%", ""))
            coverage_percentage = round(
                (
                    statements_percentage
                    + branches_percentage
                    + functions_percentage
                    + lines_percentage
                )
                / 4,
                2,
            )
            data = {
                "file": file,
                "coverage_report_path": coverage_report_path,
                "coverage_percentage": coverage_percentage,
            }
            coverage_data.append(data)
    return coverage_data


def extract_coverage_data_from_row(
    row: bs4.element.ResultSet,
    report_directory: str,
) -> List[CoverageReport]:
    """Extract coverage data from HTML coverage report."""
    # soup = BeautifulSoup(row, "html.parser")
    coverage_data = []

    # Iterate through each row in the coverage summary table
    columns = row.find_all("td")
    if columns:
        file = columns[0].text.strip()
        path = columns[0].select("a")[0]["href"]
        coverage_report_path = f"{report_directory}/{path}"
        statements_percentage = float(columns[2].text.strip().replace("%", ""))
        branches_percentage = float(columns[4].text.strip().replace("%", ""))
        functions_percentage = float(columns[6].text.strip().replace("%", ""))
        lines_percentage = float(columns[8].text.strip().replace("%", ""))
        coverage_percentage = round(
            (
                statements_percentage
                + branches_percentage
                + functions_percentage
                + lines_percentage
            )
            / 4,
            2,
        )
        data = {
            "file": file,
            "coverage_report_path": coverage_report_path,
            "coverage_percentage": coverage_percentage,
        }
        coverage_data.append(data)
    return coverage_data


async def find_index_html_files(
    container: dagger.Container, directory: str
) -> List[Tuple[str, str]]:
    """Find the index.html files in the test container and return a list of (dir_path, file_path) tuples."""
    print(f"Finding index.html files in {directory}")

    result = await container.with_exec(
        [
            "sh",
            "-c",
            f"""
                find "{directory}" -type f -name "index.html" | while read -r file_path; do
                dir_path=$(dirname "$file_path")
                echo "Directory: $dir_path, File Path: $file_path"
                done
            """,
        ]
    ).stdout()

    index_files: List[Tuple[str, str]] = []
    for line in result.strip().splitlines():
        parts = line.split(", ")
        dir_path = parts[0].replace("Directory: ", "").strip()
        file_path = parts[1].replace("File Path: ", "").strip()
        index_files.append((dir_path, file_path))

    return index_files


def parse_code(file: str):
    soup = BeautifulSoup(file, "html.parser")

    # Find all the code lines within the <pre> tags
    code_lines = soup.select("table.coverage tr td.text pre")

    # Check if code_lines is empty
    if not code_lines:
        raise ValueError("No code lines found in the provided HTML.")

    # Get the text from the first <pre> tag and strip leading/trailing whitespace
    lines = code_lines[0].text.splitlines()

    # Strip leading whitespace from each line
    stripped_lines = [line.strip() for line in lines]
    print("\n".join(stripped_lines))

    return "\n".join(stripped_lines)  # Join the lines back together

import json
from typing import List

import dagger
from bs4 import BeautifulSoup
from dagger import dag, function, object_type
from pytest_reporter_plugin.models.coverage_report import CoverageReport

from .utils import find_index_html_files, parse_code


@object_type
class PytestReporterPlugin:

    def __init__(self):
        self.coverage_reports = []

    def base(self, src: dagger.Directory = dag.directory()) -> dagger.Container:
        self.container = (
            dag.container()
            .from_("alpine:latest")
            .with_directory("/src", src)
            .with_workdir("/src")
        )
        return self.container

    def create_coverage_reports(self, data: List[dict]) -> List[CoverageReport]:
        """Create CoverageReport instances from extracted data."""
        return [CoverageReport(**item) for item in data]

    def extract_and_process_report(
        self,
        report_directory: str,
        index_html: str,
    ) -> None:
        """Extract coverage data from the given HTML and process it."""
        print(f"Extracting coverage data from {report_directory}")
        soup = BeautifulSoup(index_html, "html.parser")
        coverage_data = []
        try:
            for row in soup.find_all("tr")[1:-1]:
                columns = row.find_all("td")
                if columns:
                    file = columns[0].text.strip()
                    print(f"File: {file}")
                    path = columns[0].select("a")[0]["href"]
                    print(f"Path: {path}")
                    coverage_report_path = f"{report_directory}/{path}"
                    print(f"Coverage report path: {coverage_report_path}")
                    coverage_percentage = columns[4].text.strip().replace(
                        "%", "")
                    print(f"Coverage percentage: {coverage_percentage}")
                    data = {
                        "file": file,
                        "coverage_report_path": coverage_report_path,
                        "coverage_percentage": coverage_percentage,
                    }
                    coverage_data.append(data)
            if coverage_data:
                self.coverage_reports.extend(
                    self.create_coverage_reports(coverage_data)
                )
        except Exception as e:
            raise Exception(f"Error extracting coverage data: {e}")

    @function
    async def get_code_under_test(self, coverage_html: str) -> str:
        """Extract code under test from the coverage HTML report"""
        try:
            code = parse_code(html_content=coverage_html)
            return code
        except Exception as e:
            raise Exception(f"Error parsing code: {e}")

    @function
    async def get_coverage_html(
        self,
        html_report_path: str,
        test_container: dagger.Container,
    ) -> str:
        """Get the coverage HTML file from the report file"""
        coverage = ""
        coverage = await test_container.file(f"{html_report_path}").contents()
        return coverage

    @function
    async def get_coverage_reports(
        self, container: dagger.Container, report_directory: str
    ) -> dagger.File:
        """Extract coverage data from the HTML input and create a JSON file with the data"""

        try:
            # Extract coverage data from the HTML input
            index_files = await find_index_html_files(container, report_directory)
            print(f"Index files: {index_files} Type {type(index_files)}")
            for report_directory, index_file in index_files[:1]:
                index_html = await container.file(f"{index_file}").contents()
                print(f"Index HTML: Contents {index_html}")
                self.extract_and_process_report(report_directory, index_html)

            # Convert CoverageReport instances to a list of dictionaries
            self.coverage_reports_dicts = [
                report.model_dump() for report in self.coverage_reports
            ]

            # Create a JSON string from the list of dictionaries
            coverage_reports_json = json.dumps(self.coverage_reports_dicts)
            print(f"Coverage reports JSON: {coverage_reports_json}")

            # Create a new file with the JSON string and return the file
            container = self.base().with_new_file(
                "coverage.json", coverage_reports_json
            )
            return container.file("/src/coverage.json")

        except Exception as e:
            raise Exception(f"Error extracting coverage data: {e}")

    @function
    def parse_test_results(self, content: str) -> str:
        """
        Extracts any errors found in the coverage report HTML markup.

        Parameters:
            content (str): The HTML content of the coverage report.

        Returns:
            str: A string containing error details, if any.
        """
        soup = BeautifulSoup(content, "html.parser")
        errors = []

        # Extract JSON data from the data-container
        data_container = soup.find("div", id="data-container")
        if not data_container or "data-jsonblob" not in data_container.attrs:
            print(
                "Error: No data container found or 'data-jsonblob' attribute is missing."
            )
            return "No data container found."  # More informative return message

        json_blob = data_container["data-jsonblob"]

        # Attempt to load the JSON data
        try:
            report_data = json.loads(json_blob)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {e}")
            return "Invalid JSON format."  # More informative return message

        # Extract test results
        tests = report_data.get("tests", {})
        if not tests:
            print("Warning: No test results found in the report.")
            return "No test results found."  # Informative return message

        for test_name, test_results in tests.items():
            for test_result in test_results:
                result_status = test_result.get("result", "").lower()
                if result_status in ["failed", "error"]:
                    log_message = test_result.get(
                        "log", "No log output available.")
                    errors.append(f"Test: {test_name}\n{log_message}")

        if not errors:
            print("Info: All tests passed.")
            return "All tests passed."  # Informative return message if no errors found

        return "\n".join(errors).strip()

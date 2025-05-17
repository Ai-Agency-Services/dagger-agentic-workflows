import json
from typing import List

import dagger
from bs4 import BeautifulSoup
from dagger import dag, function, object_type
from jest_reporter_plugin.models.coverage_report import CoverageReport

from .utils import (extract_coverage_data_from_row,
                    extract_coverage_data_from_table, find_index_html_files,
                    parse_code)


@object_type
class JestReporterPlugin:

    def __init__(self):
        self.coverage_reports = []

    def base(self, src: dagger.Directory = dag.directory()) -> dagger.Container:
        self.container = (
            dag.container()
            .from_(
                "alpine:latest"
            )
            .with_directory("/src", src)
            .with_workdir("/src")
        )
        return self.container

    def create_coverage_reports(self, data: List[dict]) -> List[CoverageReport]:
        """Create CoverageReport instances from extracted data."""
        return [CoverageReport(**item) for item in data]

    async def extract_and_process_report(
        self, report_directory: str, index_html: str, container: dagger.Container
    ) -> None:
        """Extract coverage data from the given HTML and process it."""
        soup = BeautifulSoup(index_html, "html.parser")
        for row in soup.find_all("tr")[1:]:
            columns = row.find_all("td")
            if columns:
                folder_or_file = columns[0].text.strip()
                link = columns[0].select_one("a")
                if link and "href" in link.attrs:
                    path = link["href"]
                    print(
                        f"Processing coverage report: {report_directory}/{path}")
                    coverage_report_data = None  # Initialize

                    try:
                        if path.endswith("index.html"):
                            next_index_html = await container.file(
                                f"{report_directory}/{path}"
                            ).contents()
                            coverage_report_data = extract_coverage_data_from_table(
                                next_index_html, report_directory, folder_or_file
                            )
                        elif path.endswith("ts.html") or path.endswith("js.html"):
                            coverage_report_data = extract_coverage_data_from_row(
                                row, report_directory
                            )

                        if coverage_report_data:  # Check if data was extracted
                            self.coverage_reports.extend(
                                self.create_coverage_reports(
                                    coverage_report_data)
                            )
                    except Exception as e:
                        print(f"Error processing {path}: {e}")

    @function
    async def get_code_under_test(self, coverage_html: str) -> str:
        """Extract code under test from the coverage HTML report"""
        try:
            code = parse_code(file=coverage_html)
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
        try:
            coverage = await test_container.file(f"{html_report_path}").contents()
            return coverage
        except Exception as e:
            raise Exception(f"{e}")

    @function
    async def get_coverage_reports(
        self, container: dagger.Container, report_directory: str
    ) -> dagger.File:
        """Extract coverage data from the HTML input and create a JSON file with the data"""

        try:
            # Extract coverage data from the HTML input
            index_files = await find_index_html_files(container, report_directory)
            for report_directory, index_file in index_files[:1]:
                index_html = await container.file(f"{index_file}").contents()
                await self.extract_and_process_report(
                    report_directory, index_html, container
                )

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
    async def parse_test_results(self, result_json: str) -> str:
        """Parse the test results JSON file and return a str with the failed tests"""
        data = json.loads(result_json)
        message = ""
        if data["numFailedTestSuites"] > 0:
            for suite in data["testResults"]:
                if suite["status"] == "failed":
                    message += suite["message"]
        return message

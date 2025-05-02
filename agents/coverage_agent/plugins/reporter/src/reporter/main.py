import json
import os
from typing import Annotated

import dagger
import jsonschema
import yaml
from dagger import Doc, dag, function, object_type

switch_reporter = {
    "jest": dag.jest_reporter_plugin,
    "pytest": dag.pytest_reporter_plugin,
}


@object_type
class Reporter:
    name: Annotated[str, Doc("Reporter to use")]

    def __post_init__(self):
        self.reporter = switch_reporter[self.name]

    @function
    def get_code_under_test(
        self,
        coverage_html: str,
    ) -> str:
        """Extract code under test from the coverage HTML report"""
        return self.reporter().get_code_under_test(coverage_html)

    @function
    async def get_coverage_html(
        self,
        html_report_path: str,
        test_container: dagger.Container,
    ) -> str:
        """Get the coverage HTML file from the report file"""
        return await self.reporter().get_coverage_html(html_report_path, test_container)

    @function
    def get_coverage_reports(
        self,
        container: Annotated[
            dagger.Container,
            Doc(
                "The container to extract the coverage reports from. Must be of type Dagger.Container"
            ),
        ],
        report_directory: Annotated[
            str,
            Doc(
                "The directory to extract the coverage reports from. Must be of type str"
            ),
        ],
    ) -> dagger.File:
        """Extract coverage data from the HTML input and create a JSON file with the data"""
        return self.reporter().get_coverage_reports(container, report_directory)

    @function
    def parse_test_results(
        self,
        result_json: Annotated[
            str,
            Doc("The test results in JSON format. Must be of type str"),
        ],
    ) -> str:
        """Parse the test results JSON file and return a str with the failed tests"""
        return self.reporter().parse_test_results(result_json)

    @function
    def validate_config(self, config: str) -> None:
        """Validate the configuration file"""
        config_dict = yaml.safe_load(config)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        with open(current_dir + "/config.schema.json") as file:
            schema = json.load(file)
            print(f"config", config_dict)
            print(f"schema", schema)

        # Validate the configuration against the schema
        jsonschema.validate(config_dict, schema)

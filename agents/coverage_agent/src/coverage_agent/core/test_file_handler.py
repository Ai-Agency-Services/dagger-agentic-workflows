from datetime import datetime

import dagger
from coverage_agent.models.config import YAMLConfig
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.utils import base_file_name, get_code_under_test_directory


class TestFileHandler:
    def __init__(self, config: YAMLConfig):
        """
        Initialize the TestFileHandler with the configuration.
        """
        self.config = config
        self.file_name = None  # Store the generated file name for reference.
        self.save_path = None  # Store the save path for the test file.

    def get_save_path(self, code_under_test_directory):
        """
        Determine the save path based on the configuration.

        Args:
            code_under_test_directory: The directory where the code under test resides.

        Returns:
            str: The path where the test file will be saved.
        """
        return (
            code_under_test_directory
            if self.config.test_generation.save_next_to_code_under_test
            else self.config.test_generation.test_directory
        )

    async def handle_test_file(
        self, container: dagger.Container, code, report: CoverageReport
    ) -> dagger.Container:
        """
        Handles the creation of a test file and execution of a command.

        Args:
            test_container: The container object to operate on.
            code_under_test_directory: The directory where the code under test resides.
            code: The content of the test file.
            report: CoverageReport object used to generate the base file name.

        Returns:
            The updated test container with the new file.
        """
        # Generate a unique base file name using the report and timestamp
        code_under_test_directory = await get_code_under_test_directory(
            container, report
        )
        name = base_file_name(
            report.file, test_suffix=self.config.test_generation.test_suffix
        )
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.file_name = f"generated_{timestamp}_{name}"

        # Determine the save path based on the configuration
        self.save_path = self.get_save_path(code_under_test_directory)

        # Create the new file in the container and return the updated container
        return await container.with_new_file(f"{self.save_path}/{self.file_name}", code)

import json
import os
from typing import Tuple

import dagger
import jsonschema
import yaml
from coverage.models.config import YAMLConfig
from dagger import dag
from dagger.client.gen import Reporter


class ConfigurationLoader:
    """Handles loading and validating configuration."""

    @staticmethod
    async def load(config: dagger.File) -> Tuple[YAMLConfig, Reporter]:
        """Load the configuration file and return raw string and parsed object."""
        config_str = await config.contents()
        config_dict = yaml.safe_load(config_str)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        with open(current_dir + "/config.schema.json") as f:
            schema = json.load(f)
        jsonschema.validate(config_dict, schema)
        reporter_name = config_dict["reporter"]["name"]
        reporter = dag.reporter(name=reporter_name)
        return config_dict, reporter

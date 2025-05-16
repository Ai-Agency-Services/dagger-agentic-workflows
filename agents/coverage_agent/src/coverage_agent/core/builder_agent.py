from dataclasses import dataclass

import dagger
from coverage_agent.models.config import YAMLConfig


@dataclass
class BuilderAgentDependencies:
    config: YAMLConfig
    container: dagger.Container

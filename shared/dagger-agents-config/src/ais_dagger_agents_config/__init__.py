"""Shared configuration models for Dagger Agents."""

from .models import (
    YAMLConfig,
    ContainerConfig,
    GitConfig,
    LLMConfig,
    IndexingConfig,
    GenerationConfig,
    ReporterConfig,
    CoreAPIConfig,
)

__version__ = "0.1.0"

__all__ = [
    "YAMLConfig",
    "ContainerConfig", 
    "GitConfig",
    "LLMConfig",
    "IndexingConfig",
    "GenerationConfig",
    "ReporterConfig",
    "CoreAPIConfig",
]
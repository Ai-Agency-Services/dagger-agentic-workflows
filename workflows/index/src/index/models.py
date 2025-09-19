from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Optional

import dagger


@dataclass
class ProcessingConfig:
    """Configuration for file processing operations."""
    max_semantic_chunk_lines: int = 200
    fallback_chunk_size: int = 50
    max_file_size: int = 1_000_000
    batch_size: int = 5
    max_concurrent: int = 5
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 10


@dataclass
class ChunkData:
    """Data structure for code chunks."""
    content: str
    filepath: str
    start_line: int
    end_line: int
    language: str
    symbols: List[Dict]
    context: str


class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: dagger.Secret

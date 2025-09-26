"""Type definitions for code map module."""

from typing import Optional
from pydantic import BaseModel


class BuildOptions(BaseModel):
    out_dir: str = ".code-map"
    ignore_dirs: list[str] = [".git", "node_modules", "__pycache__", ".venv"]
    max_file_size: int = 1_000_000
    languages: list[str] = ["python", "javascript", "typescript"]
    incremental: bool = True
    verbose: bool = False
    chunk_lines: int = 100
    concurrency: int = 1


class QueryOptions(BaseModel):
    query_text: str
    top_k: int = 20


class FileEntry(BaseModel):
    path: str
    size: int
    language: str
    tokens_estimate: int
    mtime: float


class SymbolEntry(BaseModel):
    file: str
    name: str
    type: str  # function, class, method, variable
    start_line: int
    end_line: int
    signature: Optional[str] = None


class ChunkEntry(BaseModel):
    file: str
    start_line: int
    end_line: int
    tokens_estimate: int
    symbol_refs: list[str] = []
    content_hash: str


class CodeMapSummary(BaseModel):
    total_files: int
    total_symbols: int
    total_chunks: int
    languages: dict[str, int]
    build_time: float
    version: str = "0.1.0"


class RankedFile(BaseModel):
    path: str
    score: float
    reason: str


class RelationEntry(BaseModel):
    source: str  # source file path (relative)
    target: str  # imported module/path
    relation_type: str = "import"


"""File tree printing utilities."""

import json
from pathlib import Path
from typing import Dict, List

from ..types import FileEntry, SymbolEntry


def load_file_data(map_dir: str) -> tuple[List[FileEntry], List[SymbolEntry]]:
    """Load file and symbol data from map directory."""
    map_path = Path(map_dir)
    
    files = []
    symbols = []
    
    # Load files
    files_path = map_path / "files.jsonl"
    if files_path.exists():
        for line in files_path.read_text().strip().split('\n'):
            if line:
                files.append(FileEntry.model_validate_json(line))
    
    # Load symbols
    symbols_path = map_path / "symbols.jsonl"
    if symbols_path.exists():
        for line in symbols_path.read_text().strip().split('\n'):
            if line:
                symbols.append(SymbolEntry.model_validate_json(line))
    
    return files, symbols


def build_file_tokens(symbols: List[SymbolEntry]) -> Dict[str, List[str]]:
    """Build mapping of file -> top token names."""
    file_tokens: Dict[str, List[str]] = {}
    
    for symbol in symbols:
        if symbol.file not in file_tokens:
            file_tokens[symbol.file] = []
        file_tokens[symbol.file].append(symbol.name)
    
    # Limit to top tokens per file
    for file_path in file_tokens:
        file_tokens[file_path] = file_tokens[file_path][:10]
    
    return file_tokens


def build_directory_tree(files: List[FileEntry]) -> Dict:
    """Build directory tree structure from file list."""
    tree = {}
    
    for file_entry in files:
        parts = Path(file_entry.path).parts
        current = tree
        
        # Navigate/create directory structure
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add file
        filename = parts[-1] if parts else file_entry.path
        current[filename] = file_entry
    
    return tree


def format_tree(tree: Dict, file_tokens: Dict[str, List[str]], with_tokens: bool, indent: int = 0) -> str:
    """Format directory tree as string."""
    lines = []
    prefix = "  " * indent
    
    # Sort: directories first, then files
    items = list(tree.items())
    dirs = [(k, v) for k, v in items if isinstance(v, dict)]
    files = [(k, v) for k, v in items if not isinstance(v, dict)]
    
    dirs.sort(key=lambda x: x[0])
    files.sort(key=lambda x: x[0])
    
    # Add directories
    for name, subtree in dirs:
        lines.append(f"{prefix}{name}/")
        lines.append(format_tree(subtree, file_tokens, with_tokens, indent + 1))
    
    # Add files
    for name, file_entry in files:
        line = f"{prefix}{name}"
        
        if with_tokens and file_entry.path in file_tokens:
            tokens = file_tokens[file_entry.path]
            if tokens:
                token_str = " ".join(tokens[:8])  # Limit display
                line += f"\n{prefix}  {token_str}"
        
        lines.append(line)
    
    return "\n".join(lines)


def print_file_tree(map_dir: str, with_tokens: bool = True) -> str:
    """Print file tree from code map data."""
    files, symbols = load_file_data(map_dir)
    
    if not files:
        return "No files found in code map."
    
    file_tokens = build_file_tokens(symbols) if with_tokens else {}
    tree = build_directory_tree(files)
    
    result = format_tree(tree, file_tokens, with_tokens)
    
    # Add summary header
    total_files = len(files)
    total_symbols = len(symbols)
    languages = {}
    for f in files:
        languages[f.language] = languages.get(f.language, 0) + 1
    
    header = f"Code Map Summary: {total_files} files, {total_symbols} symbols\n"
    header += f"Languages: {', '.join(f'{k}({v})' for k, v in sorted(languages.items()))}\n\n"
    
    return header + result

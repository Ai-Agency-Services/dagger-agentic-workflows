"""Query engine for code map."""

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from ..types import QueryOptions, RankedFile, FileEntry, SymbolEntry, ChunkEntry


def tokenize_query(text: str) -> List[str]:
    """Simple tokenization of query text."""
    import re
    # Extract words and identifiers
    tokens = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', text.lower())
    return list(set(tokens))  # Remove duplicates


def load_code_map(map_dir: str) -> tuple[List[FileEntry], List[SymbolEntry], List[ChunkEntry]]:
    """Load code map data from directory."""
    map_path = Path(map_dir)
    
    files = []
    symbols = []
    chunks = []
    
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
    
    # Load chunks
    chunks_path = map_path / "chunks.jsonl"
    if chunks_path.exists():
        for line in chunks_path.read_text().strip().split('\n'):
            if line:
                chunks.append(ChunkEntry.model_validate_json(line))
    
    return files, symbols, chunks


def build_inverted_index(symbols: List[SymbolEntry]) -> Dict[str, Dict[str, float]]:
    """Build TF-IDF index from symbols."""
    # File -> term -> frequency
    term_freq: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # Term -> number of files containing it
    doc_freq: Dict[str, int] = defaultdict(int)
    
    # Collect terms from symbol names
    file_terms: Dict[str, set] = defaultdict(set)
    
    for symbol in symbols:
        # Simple camelCase/snake_case splitting
        import re
        terms = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)|\d+', symbol.name)
        terms = [t.lower() for t in terms if len(t) > 1]
        
        for term in terms:
            term_freq[symbol.file][term] += 1
            file_terms[symbol.file].add(term)
    
    # Calculate document frequency
    for file_path, terms in file_terms.items():
        for term in terms:
            doc_freq[term] += 1
    
    # Calculate TF-IDF scores
    tfidf_scores: Dict[str, Dict[str, float]] = defaultdict(dict)
    total_docs = len(file_terms)
    
    for file_path, terms in term_freq.items():
        for term, tf in terms.items():
            df = doc_freq[term]
            idf = math.log((total_docs + 1) / (df + 1))
            tfidf_scores[file_path][term] = tf * idf
    
    return dict(tfidf_scores)


def score_files(query_tokens: List[str], tfidf_index: Dict[str, Dict[str, float]]) -> List[tuple[str, float]]:
    """Score files based on query tokens."""
    file_scores: Dict[str, float] = defaultdict(float)
    
    for file_path, file_terms in tfidf_index.items():
        for token in query_tokens:
            if token in file_terms:
                file_scores[file_path] += file_terms[token]
    
    # Sort by score descending
    scored_files = [(path, score) for path, score in file_scores.items() if score > 0]
    scored_files.sort(key=lambda x: x[1], reverse=True)
    
    return scored_files


def query_code_map(map_dir: str, options: QueryOptions) -> str:
    """Query code map and return ranked files as JSON."""
    files, symbols, chunks = load_code_map(map_dir)
    
    if not symbols:
        return json.dumps([])
    
    # Tokenize query
    query_tokens = tokenize_query(options.query_text)
    if not query_tokens:
        return json.dumps([])
    
    # Build index and score
    tfidf_index = build_inverted_index(symbols)
    scored_files = score_files(query_tokens, tfidf_index)
    
    # Create ranked results
    results = []
    for file_path, score in scored_files[:options.top_k]:
        # Find matching tokens for reason
        matched_tokens = []
        if file_path in tfidf_index:
            for token in query_tokens:
                if token in tfidf_index[file_path]:
                    matched_tokens.append(token)
        
        reason = f"matched: {', '.join(matched_tokens[:5])}"
        
        results.append(RankedFile(
            path=file_path,
            score=round(score, 4),
            reason=reason,
        ))
    
    return json.dumps([r.model_dump() for r in results], indent=2)

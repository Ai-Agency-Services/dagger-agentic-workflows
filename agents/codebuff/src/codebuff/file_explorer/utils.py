"""File explorer utility functions."""

from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import re
from functools import lru_cache
from ..file_picker.agent import _is_code_file


async def find_files(
    prompt: str,
    # Enhanced format only: {file_path: {token: score}}
    file_scores: Dict[str, Dict[str, float]],
    token_callers: Dict[str, Dict[str, List[Dict]]] = None,
    task_goal: str = None,
) -> List[str]:
    """
    Finds relevant files in the codebase based on a prompt using enhanced file token scores.

    Args:
        prompt: User prompt for file search
        file_scores: Enhanced file token scores from CodeMap {file_path: {token: score}}
        token_callers: Token caller relationships
        task_goal: Overall task goal for additional context

    Returns:
        List of relevant file paths
    """
    print(f"Finding files for prompt: '{prompt}'")

    try:
        if not file_scores:
            print("No file scores provided, returning empty list")
            return []

        # Extract keywords from the prompt and task goal for filtering
        keywords = _extract_keywords_from_prompt(prompt, task_goal)
        print(f"Using keywords for search: {keywords}")

        # Calculate file relevance using enhanced token scores
        scored_files = []

        for file_path, token_scores in file_scores.items():
            # Skip non-code files
            if _is_non_code_file(file_path):
                continue

            # Calculate relevance score based on keyword matches and token scores
            relevance = 0.0

            # Path-based scoring
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in file_path.lower():
                    relevance += 3.0

            # Token-based scoring with enhanced scores
            for token, token_score in token_scores.items():
                token_lower = token.lower()
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower == token_lower:
                        relevance += token_score * 5.0  # Exact match gets full score boost
                    elif keyword_lower in token_lower:
                        relevance += token_score * 2.0  # Partial match gets moderate boost
                    elif len(token_lower) > 3 and token_lower in keyword_lower:
                        relevance += token_score * 1.0  # Token is part of keyword gets small boost

            # Token caller relationship scoring
            if token_callers:
                for token, token_score in token_scores.items():
                    if token in token_callers:
                        callers = token_callers[token]
                        for keyword in keywords:
                            keyword_lower = keyword.lower()
                            if keyword_lower in token.lower():
                                # Add bonus based on number of callers
                                caller_count = sum(len(caller_list) for caller_list in callers.values()
                                                   if isinstance(caller_list, list))
                                score_boost = min(
                                    token_score * (caller_count * 0.1), token_score * 3)
                                relevance += score_boost

            if relevance > 0:
                scored_files.append((file_path, relevance))

        # Sort by relevance score
        sorted_files = [file for file, _ in sorted(
            scored_files, key=lambda x: x[1], reverse=True)]

        # Return top results (maximum 20)
        result_files = sorted_files[:20]
        print(f"Found {len(result_files)} relevant files")
        return result_files

    except Exception as e:
        print(f"Error finding files: {e}")
        import traceback
        print(traceback.format_exc())
        return [f"Error: Unexpected error finding files: {str(e)}"]


@lru_cache(maxsize=64)
def _extract_keywords_from_prompt(prompt: str, task_goal: str = None) -> Tuple[str, ...]:
    """
    Extract relevant keywords from the prompt and task goal for file filtering.
    Cached for better performance when the same prompts are used repeatedly.

    Args:
        prompt: The specific search prompt
        task_goal: The overall task goal to extract domain keywords from

    Returns:
        Tuple of relevant keywords for file matching (immutable for cache)
    """
    stop_words = {'and', 'or', 'the', 'for', 'in', 'on', 'with', 'that',
                  'this', 'to', 'a', 'an', 'be', 'is', 'are', 'was', 'were',
                  'from', 'as', 'at', 'by', 'of'}

    # Combine text sources for keyword extraction
    text_sources = [prompt.lower()]
    if task_goal:
        text_sources.append(task_goal.lower())

    # Extract all potential keywords
    all_words = []
    for text in text_sources:
        words = text.replace(',', ' ').replace(
            '.', ' ').replace(':', ' ').replace(';', ' ').split()
        all_words.extend(words)

    # Filter words: keep words longer than 2 characters that aren't stop words
    keywords = [word for word in all_words if len(
        word) > 2 and word not in stop_words]

    # Count word frequency to identify important domain terms
    word_counts = {}
    for word in keywords:
        word_counts[word] = word_counts.get(word, 0) + 1

    # Sort by frequency to prioritize repeated keywords
    sorted_keywords = sorted(
        word_counts.items(), key=lambda x: x[1], reverse=True)

    # Take the top keywords, with more weight given to task_goal keywords
    selected_keywords = [word for word, _ in sorted_keywords[:30]]

    # Ensure we don't have too many keywords (which could dilute relevance)
    return tuple(selected_keywords[:20])  # Return as tuple for cacheability


@lru_cache(maxsize=256)
def _is_non_code_file(file_path: str) -> bool:
    """Determines if a file is likely not a code file. Cached for performance."""
    non_code_extensions = {
        '.md', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
        '.json', '.lock', '.yml', '.yaml', '.toml', '.license'
    }
    excluded_patterns = {'.git', 'node_modules',
                         '.venv', 'dist', 'build', '__pycache__'}

    file_ext = '.' + file_path.split('.')[-1] if '.' in file_path else ''

    return (
        file_ext.lower() in non_code_extensions or
        any(pattern in file_path for pattern in excluded_patterns)
    )

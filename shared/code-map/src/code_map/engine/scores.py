"""Token scoring and accumulation utilities."""

from collections import defaultdict
from typing import Dict, List, Tuple, Any, Set, Optional
from pathlib import Path
import math


def calculate_token_relevance(
    token: str,
    file_path: str,
    token_data: Dict[str, Any],
    line_count: int,
    token_callers: Optional[Dict[str, Any]] = None,
    use_path_depth: bool = True,
    use_code_density: bool = True,
) -> float:
    """
    Calculate token relevance using the enhanced algorithm inspired by TypeScript implementation.
    
    Args:
        token: The token being scored
        file_path: File path where token appears (used for depth calculation)
        token_data: Information about the token (counts, locations, etc)
        line_count: Number of lines in the file (for density calculation)
        token_callers: Information about callers of tokens (optional)
        use_path_depth: Whether to apply path depth weighting (deeper paths get less weight)
        use_code_density: Whether to use code density in scoring (tokens per line)
    
    Returns:
        Float score representing token relevance
    """
    # Start with base score (can be from frequency or other metrics)
    base_score = 1.0

    # Apply path depth factor if enabled
    if use_path_depth:
        path_depth = len(Path(file_path).parts)
        depth_factor = 0.8 ** path_depth  # Deeper files get less weight
        base_score *= depth_factor

    # Apply code density factor if enabled
    if use_code_density and line_count > 0:
        # Get token count (fallback to 1 if not available)
        token_count = token_data.get("count", 1)
        density_factor = math.sqrt(line_count / (token_count + 1))
        base_score *= density_factor

    # Add logarithmic call frequency boost if we have caller information
    call_boost = 0
    if token_callers and token in token_callers:
        callers = token_callers.get(token, {})
        # Count total calls across all callers
        num_calls = sum(len(caller_list) for caller_list in callers.values()
                        if isinstance(caller_list, list))
        if num_calls > 0:
            call_boost = math.log(1 + num_calls)

    # Combine base score with call boost
    final_score = base_score * (1 + call_boost)

    return final_score


def accumulate_token_scores(
    file_token_data: List[Tuple[str, Dict]],
    max_callers: int = 50,
    use_path_depth: bool = True,
    use_code_density: bool = True,
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, List[Dict]]]]:
    """
    Accumulate token scores and caller information across all files.
    
    Args:
        file_token_data: List of (file_path, tokens_dict) tuples
        max_callers: Maximum number of callers to track per token (prevents memory issues)
        use_path_depth: Whether to apply path depth weighting
        use_code_density: Whether to use code density in scoring
    
    Returns:
        Tuple of (file_token_scores, token_callers)
    """
    file_token_scores = {}
    token_callers = {}
    
    # First pass: collect all tokens and their callers
    for file_path, tokens_dict in file_token_data:
        identifiers = tokens_dict.get("identifiers", [])
        calls = tokens_dict.get("calls", [])
        line_count = tokens_dict.get("line_count", 0)
        
        # Process file identifiers
        file_scores = {}
        file_token_scores[file_path] = file_scores

        # Process declared identifiers
        for token in identifiers:
            if not token or not isinstance(token, str):
                continue

            # Skip common tokens that add noise
            if token.lower() in ("self", "this", "super", "constructor", "tostring", "hasownproperty"):
                continue

            # Initialize token data
            token_data = {"count": 1}

            # Calculate token relevance using our new function
            score = calculate_token_relevance(
                token=token,
                file_path=file_path,
                token_data=token_data,
                line_count=line_count,
                token_callers=token_callers,
                use_path_depth=use_path_depth,
                use_code_density=use_code_density
            )

            file_scores[token] = score

        # Process function calls to build caller relationships
        for call_info in calls:
            if not isinstance(call_info, dict):
                continue

            caller = call_info.get("caller")
            callee = call_info.get("callee")
            line = call_info.get("line", 0)
            col = call_info.get("col", 0)

            if not caller or not callee or not isinstance(caller, str) or not isinstance(callee, str):
                continue

            # Skip common methods that add noise
            if callee.lower() in ("tostring", "hasownproperty", "constructor"):
                continue

            # Initialize token caller structure if needed
            if callee not in token_callers:
                token_callers[callee] = {}

            if caller not in token_callers[callee]:
                token_callers[callee][caller] = []

            # Add caller info with location
            caller_list = token_callers[callee][caller]

            # Respect max_callers limit
            if len(caller_list) < max_callers:
                caller_list.append({
                    "path": file_path,
                    "line": line,
                    "col": col
                })
    
    # Second pass: now that we have complete token_callers data, update scores
    # to include call frequency boost
    for file_path, tokens_dict in file_token_data:
        file_scores = file_token_scores[file_path]
        line_count = tokens_dict.get("line_count", 0)

        # Update scores for each token with complete caller information
        for token in list(file_scores.keys()):
            token_data = {"count": 1}  # Simple token data for now

            # Recalculate with full token_callers information
            updated_score = calculate_token_relevance(
                token=token,
                file_path=file_path,
                token_data=token_data,
                line_count=line_count,
                token_callers=token_callers,
                use_path_depth=use_path_depth,
                use_code_density=use_code_density
            )

            file_scores[token] = updated_score

    return file_token_scores, token_callers

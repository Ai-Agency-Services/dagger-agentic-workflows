"""Token scoring and accumulation utilities."""

from collections import defaultdict
from typing import Dict, List, Tuple


def accumulate_token_scores(
    items: List[Tuple[str, dict]]
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, List[Dict]]]:
    """Accumulate token scores and caller locations.
    
    Args:
        items: List of (file_path, token_data) tuples
    
    Returns:
        Tuple of (fileTokenScores, tokenCallers)
        - fileTokenScores: {"path": {"token": float}}
        - tokenCallers: {"token": [{"path": str, "line": int, "col": int}]}
    """
    file_token_scores: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    token_callers: Dict[str, List[Dict]] = defaultdict(list)
    
    for file_path, token_data in items:
        identifiers = token_data.get("identifiers", [])
        calls = token_data.get("calls", [])
        
        # Score identifiers (definitions)
        for identifier in identifiers:
            name = identifier.get("name", "")
            if name:
                # Weight by kind (functions/classes score higher)
                weight = 2.0 if identifier.get("kind") in ["function", "class"] else 1.0
                file_token_scores[file_path][name] += weight
                
                # Add to callers (where defined)
                start = identifier.get("start", {})
                token_callers[name].append({
                    "path": file_path,
                    "line": start.get("line", 1),
                    "col": start.get("col", 0)
                })
        
        # Score calls (usages)
        for call in calls:
            callee = call.get("callee", "")
            if callee:
                # Split qualified names (e.g., "module.function" -> ["module", "function"])
                parts = callee.split(".")
                for part in parts:
                    if part:
                        file_token_scores[file_path][part] += 0.5  # Lower weight for calls
                        
                        # Add to callers (where used)
                        location = call.get("location", {})
                        token_callers[part].append({
                            "path": file_path,
                            "line": location.get("line", 1),
                            "col": location.get("col", 0)
                        })
    
    # Convert defaultdicts to regular dicts
    return dict(file_token_scores), dict(token_callers)


def split_camel_snake_case(name: str) -> List[str]:
    """Split camelCase/snake_case identifiers into component words."""
    import re
    
    # Handle snake_case
    parts = name.split("_")
    result = []
    
    for part in parts:
        # Handle camelCase within each part
        camel_parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)|\d+', part)
        result.extend([p.lower() for p in camel_parts if len(p) > 1])
    
    return [r for r in result if r and len(r) > 1]


def enhance_token_scores(
    file_token_scores: Dict[str, Dict[str, float]],
    token_callers: Dict[str, List[Dict]]
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, List[Dict]]]:
    """Enhance token scores by splitting compound names and applying TF-like weighting."""
    enhanced_scores = defaultdict(lambda: defaultdict(float))
    enhanced_callers = defaultdict(list)
    
    # Copy existing and add split variants
    for file_path, tokens in file_token_scores.items():
        for token, score in tokens.items():
            # Keep original token
            enhanced_scores[file_path][token] += score
            
            # Add split variants with reduced weight
            parts = split_camel_snake_case(token)
            for part in parts:
                enhanced_scores[file_path][part] += score * 0.3
    
    # Copy callers and add for split variants
    for token, callers in token_callers.items():
        enhanced_callers[token].extend(callers)
        
        # Add callers for split variants
        parts = split_camel_snake_case(token)
        for part in parts:
            enhanced_callers[part].extend(callers)
    
    return dict(enhanced_scores), dict(enhanced_callers)

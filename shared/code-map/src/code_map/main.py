import os
import math
import tempfile
import json
from pathlib import Path
from typing import Annotated, Optional, Dict, List, Any

import anyio
import dagger
from dagger import Doc, dag, function, object_type
from .engine.tokens import parse_tokens_from_text, detect_language
from .engine.scores import (
    accumulate_token_scores,
    calculate_token_relevance,  # This will be a new function we need to add
)
from .types import BuildOptions, QueryOptions, RankedFile


@object_type
class CodeMap:
    """Code mapping and analysis using Tree-sitter."""
    config: Optional[dict] = None
    config_file: Optional[dagger.File] = None

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("Path to the YAML config file")],
    ) -> "CodeMap":
        """Create a CodeMap object from a YAML config file (Dagger-safe)."""
        import yaml
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str) if config_str else {}
        return cls(config=config_dict or {}, config_file=config_file)

    @function
    async def get_file_token_scores(
        self,
        source_dir: Annotated[dagger.Directory, Doc("Source directory to analyze")],
        glob_patterns: Annotated[list[str], Doc(
            "File patterns to include")] = [],
        max_file_size: Annotated[int, Doc("Max file size in bytes")] = 1_000_000,
        max_files: Annotated[int, Doc("Maximum files to process")] = 5000,
    ) -> str:
        """Get token scores for all files in source directory.
        
        Returns JSON: {"fileTokenScores": {"path": {"token": float}}, "tokenCallers": {"token": {"caller": [{"path": str, "line": int, "col": int}]}}}
        """
        # Resolve config defaults
        cm = self.config.get("code_map", {}) if self.config else {}
        ignore_dirs = cm.get("ignore_dirs", [
            ".git", "node_modules", "__pycache__", ".venv", "dist", "build"
        ])
        language_overrides = cm.get("language_overrides", {})
        unknown_policy = cm.get("unknown_policy", "skip")
        default_language = cm.get("default_language")

        # New option: max callers per token (to prevent memory issues)
        max_callers = cm.get("max_callers_per_token", 50)

        with tempfile.TemporaryDirectory() as tmp:
            local_src = os.path.join(tmp, "src")
            await source_dir.export(local_src)

            # Walk files and parse tokens
            file_token_data = []
            file_count = 0
            source_path = Path(local_src)

            for file_path in source_path.rglob("*"):
                if not file_path.is_file():
                    continue

                # Skip ignored directories
                if any(part in ignore_dirs for part in file_path.parts):
                    continue

                # Skip large files
                if file_path.stat().st_size > max_file_size:
                    continue

                # Apply glob patterns if specified
                rel_path = str(file_path.relative_to(source_path))
                if glob_patterns:
                    import fnmatch
                    if not any(fnmatch.fnmatch(rel_path, pattern) for pattern in glob_patterns):
                        continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, PermissionError):
                    continue

                # Count lines for code density calculation (new feature)
                line_count = content.count('\n') + 1

                # Parse tokens
                tokens = parse_tokens_from_text(
                    text=content,
                    path=rel_path,
                    language_hint=None,
                    overrides=language_overrides,
                    unknown_policy=unknown_policy,
                    default_language=default_language,
                )

                # Add line count for code density calculation
                tokens["line_count"] = line_count

                file_token_data.append((rel_path, tokens))
                file_count += 1

                # Limit number of files processed
                if file_count >= max_files:
                    break

            # Accumulate scores with enhanced algorithm
            file_token_scores, token_callers = accumulate_token_scores(
                file_token_data,
                max_callers=max_callers,
                use_path_depth=True,  # Enable path depth weighting
                use_code_density=True  # Enable code density factor
            )

            return json.dumps({
                "fileTokenScores": file_token_scores,
                "tokenCallers": token_callers,
                "stats": {
                    "files_processed": file_count,
                    "unique_tokens": len(token_callers)
                }
            })

    @function
    async def find_related_files(
        self,
        source_dir: Annotated[dagger.Directory, Doc("Source directory to analyze")],
        target_file: Annotated[str, Doc("Target file path (relative)")],
        max_results: Annotated[int, Doc(
            "Maximum number of related files")] = 20,
    ) -> str:
        """Find files related to a specific file based on token relationships.
        
        Returns a JSON array of related files with scores and reasoning.
        """
        # First get token scores for the entire directory
        scores_json = await self.get_file_token_scores(source_dir)
        scores_data = json.loads(scores_json)

        file_token_scores = scores_data.get("fileTokenScores", {})
        token_callers = scores_data.get("tokenCallers", {})

        # Ensure the target file exists
        if target_file not in file_token_scores:
            return json.dumps({
                "error": f"Target file {target_file} not found in analyzed files",
                "related_files": []
            })

        # Get tokens from the target file
        target_tokens = set(file_token_scores[target_file].keys())

        # Find files that share tokens with the target
        related_scores = {}

        # For each token in the target file
        for token in target_tokens:
            # Skip common tokens that might cause noise
            if token in ("self", "this", "super", "constructor", "toString"):
                continue

            # Find files that also use this token
            if token in token_callers:
                # Get all file paths that call or define this token
                for caller_info in token_callers[token]:
                    caller_path = caller_info.get("path", "")

                    # Skip the target file itself
                    if caller_path == target_file:
                        continue

                    # Calculate relationship strength
                    # Higher if the token is important in both files
                    target_token_score = file_token_scores[target_file].get(
                        token, 0)
                    caller_token_score = 0

                    if caller_path in file_token_scores and token in file_token_scores[caller_path]:
                        caller_token_score = file_token_scores[caller_path][token]

                    # Calculate relationship score using geometric mean
                    if target_token_score > 0 and caller_token_score > 0:
                        rel_score = math.sqrt(
                            target_token_score * caller_token_score)

                        # Accumulate scores
                        if caller_path not in related_scores:
                            related_scores[caller_path] = {
                                "score": 0,
                                "shared_tokens": []
                            }

                        related_scores[caller_path]["score"] += rel_score
                        related_scores[caller_path]["shared_tokens"].append(
                            token)

        # Format the results
        results = []
        for path, info in related_scores.items():
            # Only include top shared tokens in the reason
            top_tokens = sorted(info["shared_tokens"],
                                key=lambda t: file_token_scores[target_file].get(t, 0) *
                                (file_token_scores[path].get(
                                    t, 0) if path in file_token_scores else 0),
                                reverse=True)[:5]

            results.append({
                "path": path,
                "score": info["score"],
                "reason": f"Shares tokens: {', '.join(top_tokens)}",
                "shared_token_count": len(info["shared_tokens"])
            })

        # Sort by score (descending)
        results = sorted(results, key=lambda x: x["score"], reverse=True)[
            :max_results]

        return json.dumps({
            "target_file": target_file,
            "related_files": results,
            "total_candidates": len(related_scores)
        })

    @function
    async def parse_tokens(
        self,
        file: Annotated[dagger.File, Doc("File to parse")],
        language_hint: Annotated[Optional[str], Doc(
            "Language hint for parsing")] = None,
    ) -> str:
        """Parse tokens from a single file.
        
        Returns JSON: {"identifiers": [...], "calls": [...], "language": str}
        """
        # Resolve config defaults
        cm = self.config.get("code_map", {}) if self.config else {}
        language_overrides = cm.get("language_overrides", {})
        unknown_policy = cm.get("unknown_policy", "skip")
        default_language = cm.get("default_language")

        try:
            contents = await file.contents()
            # Use a generic path for single file parsing
            path = "/virtual_file"

            # Auto-detect file extension if no language hint
            if not language_hint:
                filename = (await file.name()) or "unknown"
                language_hint = detect_language(filename)

            tokens = parse_tokens_from_text(
                text=contents,
                path=path,
                language_hint=language_hint,
                overrides=language_overrides,
                unknown_policy=unknown_policy,
                default_language=default_language,
            )

            return json.dumps(tokens)

        except Exception as e:
            return json.dumps({
                "identifiers": [],
                "calls": [],
                "language": "unknown",
                "error": str(e)
            })

    @function
    async def get_token_relevance(
        self,
        source_dir: Annotated[dagger.Directory, Doc("Source directory to analyze")],
        target_file: Annotated[str, Doc("Target file path (relative)")],
    ) -> str:
        """Calculate token relevance scores for a specific file.
        
        Returns JSON with token relevance scores and information about token usage.
        """
        # First get token scores for the entire directory
        scores_json = await self.get_file_token_scores(source_dir)
        scores_data = json.loads(scores_json)

        file_token_scores = scores_data.get("fileTokenScores", {})
        token_callers = scores_data.get("tokenCallers", {})

        # Ensure the target file exists
        if target_file not in file_token_scores:
            return json.dumps({
                "error": f"Target file {target_file} not found in analyzed files",
                "tokens": []
            })

        # Get token scores for this file
        file_scores = file_token_scores[target_file]

        # Prepare detailed token information
        token_details = []
        for token, score in sorted(file_scores.items(), key=lambda x: x[1], reverse=True):
            # Get caller information if available
            caller_count = 0
            unique_callers = set()

            if token in token_callers:
                for caller, instances in token_callers[token].items():
                    caller_count += len(instances)
                    for instance in instances:
                        if "path" in instance:
                            unique_callers.add(instance["path"])

            token_details.append({
                "token": token,
                "score": score,
                "caller_count": caller_count,
                "unique_caller_files": len(unique_callers),
            })

        return json.dumps({
            "file": target_file,
            "tokens": token_details,
            "total_tokens": len(token_details)
        })

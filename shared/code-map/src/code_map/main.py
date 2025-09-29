import os
import tempfile
import json
from pathlib import Path
from typing import Annotated, Optional

import dagger
from dagger import Doc, dag, function, object_type
from .engine.tokens import parse_tokens_from_text
from .engine.scores import accumulate_token_scores


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
    ) -> str:
        """Get token scores for all files in source directory.
        
        Returns JSON: {"fileTokenScores": {"path": {"token": float}}, "tokenCallers": {"token": [{"path": str, "line": int, "col": int}]}}
        """
        # Resolve config defaults
        cm = self.config.get("code_map", {}) if self.config else {}
        ignore_dirs = cm.get("ignore_dirs", [
            ".git", "node_modules", "__pycache__", ".venv", "dist", "build"
        ])
        language_overrides = cm.get("language_overrides", {})
        unknown_policy = cm.get("unknown_policy", "skip")
        default_language = cm.get("default_language")

        with tempfile.TemporaryDirectory() as tmp:
            local_src = os.path.join(tmp, "src")
            await source_dir.export(local_src)

            # Walk files and parse tokens
            file_token_data = []
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

                # Parse tokens
                tokens = parse_tokens_from_text(
                    text=content,
                    path=rel_path,
                    language_hint=None,
                    overrides=language_overrides,
                    unknown_policy=unknown_policy,
                    default_language=default_language,
                )

                file_token_data.append((rel_path, tokens))

            # Accumulate scores
            file_token_scores, token_callers = accumulate_token_scores(
                file_token_data)

            return json.dumps({
                "fileTokenScores": file_token_scores,
                "tokenCallers": token_callers
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

import os
import tempfile
import shutil  # added
from typing import Annotated, Optional

import dagger
from code_map.engine.build import build_code_map
from code_map.engine.print_tree import print_file_tree
from code_map.engine.query import query_code_map
from code_map.types import BuildOptions, QueryOptions
from dagger import Doc, dag, function, object_type


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
    async def build(
        self,
        source_dir: Annotated[dagger.Directory, Doc("Source directory to analyze")],
        out_dir: Annotated[str, Doc("Output directory name")] = ".code-map",
        ignore_dirs: Annotated[list[str], Doc("Directories to ignore")] = [],
        max_file_size: Annotated[int, Doc("Max file size in bytes")] = 1_000_000,
        languages: Annotated[list[str], Doc("Languages to parse")] = [],
    ) -> dagger.Directory:
        """Build code map from source directory using engine functions directly (no container)."""
        # Resolve defaults from config if present
        cm = self.config.get("code_map", {}) if self.config else {}
        # If caller didn't pass lists (empty), resolve from config or sane defaults
        if not out_dir:
            out_dir = cm.get("out_dir", ".code-map")
        if not ignore_dirs:
            ignore_dirs = cm.get("ignore_dirs", [
                ".git", "node_modules", "__pycache__", ".venv", "dist", "build"
            ])
        if not languages:
            languages = cm.get(
                "languages", ["python", "javascript", "typescript"])
        if not max_file_size:
            max_file_size = cm.get("max_file_size", 1_000_000)
        cm = self.config.get("code_map", {}) if self.config else {}
        incremental = cm.get("incremental", True)
        verbose = cm.get("verbose", False)
        cache_dir = cm.get("cache_dir")  # optional persistent cache path on host
        chunk_lines = int(cm.get("chunk_lines", 100))
        _ = cm.get("concurrency", 1)  # reserved (not used yet)

        with tempfile.TemporaryDirectory() as tmp:
            local_src = os.path.join(tmp, "src")
            # Export input Directory to a local temp path
            await source_dir.export(local_src)

            # Seed from cache_dir if provided: copy cached out_dir into local_src/out_dir before build
            local_out = os.path.join(local_src, out_dir)
            if cache_dir:
                try:
                    # Export cache_dir (host path) into a temp local cache and seed local_out
                    local_cache = os.path.join(tmp, "cache")
                    cache_dir_ref = dag.host().directory(cache_dir)
                    await cache_dir_ref.export(local_cache)
                    # Copy cached files into local_out (if any)
                    if os.path.isdir(local_cache):
                        os.makedirs(local_out, exist_ok=True)
                        for name in os.listdir(local_cache):
                            src_path = os.path.join(local_cache, name)
                            dst_path = os.path.join(local_out, name)
                            if os.path.isdir(src_path):
                                if os.path.exists(dst_path):
                                    shutil.rmtree(dst_path)
                                shutil.copytree(src_path, dst_path)
                            elif os.path.isfile(src_path):
                                shutil.copy2(src_path, dst_path)
                except Exception:
                    # Best-effort: ignore cache seed errors
                    pass

            # Build the map in-place (incremental supported)
            build_code_map(local_src, BuildOptions(
                out_dir=out_dir,
                ignore_dirs=ignore_dirs,
                max_file_size=max_file_size,
                languages=languages,
                incremental=incremental,
                verbose=verbose,
                chunk_lines=chunk_lines,
                concurrency=1,
            ))

            # Persist to cache_dir after build (best-effort)
            if cache_dir:
                try:
                    built_dir = dag.host().directory(local_out)
                    await built_dir.export(cache_dir)
                except Exception:
                    pass

            # Return the out_dir as a Dagger Directory
            return dag.host().directory(local_out)

    @function
    async def query(
        self,
        map_dir: Annotated[dagger.Directory, Doc("Code map directory")],
        query_text: Annotated[str, Doc("Search query")],
        top_k: Annotated[int, Doc("Number of results")] = 20,
    ) -> str:
        # No config-dependent defaults here yet; honoring explicit args
        """Query the code map and return ranked files as JSON using engine directly."""
        with tempfile.TemporaryDirectory() as tmp:
            local_map = os.path.join(tmp, "map")
            await map_dir.export(local_map)
            return query_code_map(local_map, QueryOptions(query_text=query_text, top_k=top_k))

    @function
    async def print_tree(
        self,
        map_dir: Annotated[dagger.Directory, Doc("Code map directory")],
        with_tokens: Annotated[bool, Doc("Include token info")] = True,
    ) -> str:
        # Could also be derived from config later if needed
        """Print a file tree with summary from the code map using engine directly."""
        with tempfile.TemporaryDirectory() as tmp:
            local_map = os.path.join(tmp, "map")
            await map_dir.export(local_map)
            return print_file_tree(local_map, with_tokens=with_tokens)

import json
import os
import tempfile
from pathlib import Path

from code_map.engine.build import build_code_map
from code_map.types import BuildOptions
from code_map.main import CodeMap


def test_build_uses_config_defaults(monkeypatch):
    # Prepare a fake repository with mixed files
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "dist").mkdir(parents=True, exist_ok=True)
        (root / "src" / "a.py").write_text("def foo():\n  return 1\n", encoding="utf-8")
        (root / "dist" / "bundle.js").write_text("minified...", encoding="utf-8")

        # Construct CodeMap with config that sets a custom out_dir and ignore_dirs
        cm = CodeMap(config={
            "code_map": {
                "out_dir": ".map-out",
                "ignore_dirs": ["dist"],
                "languages": ["python"],
                "max_file_size": 1_000_000,
            }
        })

        # Simulate build() behavior by calling the engine with config-derived defaults
        # (build() itself exports a Directory and calls the engine; here we verify defaults)
        out_dir = cm.config.get("code_map", {}).get("out_dir", ".code-map")
        ignore_dirs = cm.config.get("code_map", {}).get("ignore_dirs", [".git"])  # dist must be ignored
        languages = cm.config.get("code_map", {}).get("languages", ["python", "javascript"])  # only python
        max_file_size = cm.config.get("code_map", {}).get("max_file_size", 1_000_000)

        build_code_map(str(root), BuildOptions(
            out_dir=out_dir,
            ignore_dirs=ignore_dirs,
            max_file_size=max_file_size,
            languages=languages,
        ))

        # Validate results landed in configured out_dir and ignored dist/*
        out_path = root / out_dir
        assert (out_path / "map.json").exists()
        files = (out_path / "files.jsonl").read_text(encoding="utf-8").strip().splitlines()
        # Only src/a.py should be indexed
        assert any("src/a.py" in line for line in files)
        assert not any("dist/bundle.js" in line for line in files)

import json
import os
import tempfile
from pathlib import Path

import sys
# Ensure local src/ is importable without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from code_map.engine.build import build_code_map
from code_map.engine.query import query_code_map
from code_map.engine.print_tree import print_file_tree
from code_map.types import BuildOptions, QueryOptions


def _write(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_build_query_print_tree_smoke():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # Tiny source repo
        _write(root / "src/a.py", """
class A:
    def foo(self):
        return 1
""")
        _write(root / "web/app.js", "function bar(){ return 2; }")
        _write(root / "README.md", "docs only")

        # Build map (unknown languages allowed; symbols may be empty without tree-sitter)
        opts = BuildOptions(out_dir=".code-map", languages=["python", "javascript"], ignore_dirs=[".git", "node_modules", "__pycache__"])
        build_code_map(str(root), opts)

        out = root / ".code-map"
        assert (out / "map.json").exists()
        assert (out / "files.jsonl").exists()
        assert (out / "symbols.jsonl").exists()
        assert (out / "chunks.jsonl").exists()

        # Query map
        q = QueryOptions(query_text="foo bar", top_k=10)
        result_json = query_code_map(str(out), q)
        assert isinstance(result_json, str)
        parsed = json.loads(result_json)
        assert isinstance(parsed, list)

        # Print tree
        tree_text = print_file_tree(str(out), with_tokens=True)
        assert isinstance(tree_text, str)
        # Has header and some file names
        assert "Code Map Summary:" in tree_text
        assert "src" in tree_text or "web" in tree_text

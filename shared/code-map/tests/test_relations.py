import json
import tempfile
from pathlib import Path

from code_map.engine.build import build_code_map
from code_map.types import BuildOptions


def _read_jsonl(p: Path):
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_relations_python_and_js_imports():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        src = root / "src"
        src.mkdir(parents=True, exist_ok=True)
        # Python files
        (src / "mod.py").write_text("def x():\n  return 1\n", encoding="utf-8")
        (src / "main.py").write_text("import src.mod\nfrom src import mod\n", encoding="utf-8")
        # JS files
        (src / "lib.js").write_text("export const z = 1;", encoding="utf-8")
        (src / "app.js").write_text("import { z } from './lib.js'\n", encoding="utf-8")

        build_code_map(str(root), BuildOptions(out_dir=".map", languages=["python", "javascript"], incremental=False))

        rels = _read_jsonl(root / ".map" / "relations.jsonl")
        # Expect at least one import edge for each language
        py_edges = [r for r in rels if r.get("source") == "src/main.py"]
        js_edges = [r for r in rels if r.get("source") == "src/app.js"]
        assert py_edges, f"Expected python import edges, got: {rels}"
        assert js_edges, f"Expected js import edges, got: {rels}"
        # relation_type should be 'import'
        assert all(r.get("relation_type") == "import" for r in py_edges + js_edges)

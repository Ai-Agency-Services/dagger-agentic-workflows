import tempfile
from pathlib import Path
import json

from code_map.engine.build import build_code_map
from code_map.types import BuildOptions


def read_jsonl(p: Path):
    if not p.exists():
        return []
    lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    return lines


def load_symbols_by_file(symbols_jsonl: Path):
    out = {}
    for line in read_jsonl(symbols_jsonl):
        try:
            obj = json.loads(line)
            out.setdefault(obj.get("file", ""), 0)
            out[obj.get("file", "")] += 1
        except Exception:
            pass
    return out


def test_incremental_no_changes_is_stable():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # repo
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "src" / "a.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        (root / "src" / "b.py").write_text("class C:\n    pass\n", encoding="utf-8")

        opts = BuildOptions(out_dir=".map", languages=["python"], incremental=True)
        build_code_map(str(root), opts)

        out_dir = root / ".map"
        files1 = read_jsonl(out_dir / "files.jsonl")
        symbols1 = read_jsonl(out_dir / "symbols.jsonl")
        chunks1 = read_jsonl(out_dir / "chunks.jsonl")

        # Run again without changes; outputs should be identical
        build_code_map(str(root), opts)
        files2 = read_jsonl(out_dir / "files.jsonl")
        symbols2 = read_jsonl(out_dir / "symbols.jsonl")
        chunks2 = read_jsonl(out_dir / "chunks.jsonl")

        assert files1 == files2
        assert symbols1 == symbols2
        assert chunks1 == chunks2


def test_incremental_single_change_affects_only_changed_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # repo
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "src" / "a.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        (root / "src" / "b.py").write_text("def bar():\n    return 2\n", encoding="utf-8")

        opts = BuildOptions(out_dir=".map", languages=["python"], incremental=True)
        build_code_map(str(root), opts)

        out_dir = root / ".map"
        symbols1_by_file = load_symbols_by_file(out_dir / "symbols.jsonl")

        # Modify only b.py (add another function)
        (root / "src" / "b.py").write_text("def bar():\n    return 2\n\nclass D:\n    pass\n", encoding="utf-8")
        build_code_map(str(root), opts)

        symbols2_by_file = load_symbols_by_file(out_dir / "symbols.jsonl")

        # a.py symbol count should remain same; b.py should increase or stay >= previous
        assert symbols2_by_file.get("src/a.py", 0) == symbols1_by_file.get("src/a.py", 0)
        assert symbols2_by_file.get("src/b.py", 0) >= symbols1_by_file.get("src/b.py", 0)

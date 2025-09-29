# shared/code-map knowledge

Purpose
- Provide a Tree-sitter–powered code map as a Python Dagger module.
- Share with other modules through `dagger install` (no containerized CLI).

Install (as dependency)
- In a consuming module’s dagger.json, add:
  ```json
  {
    "dependencies": ["../../shared/code-map"]
  }
  ```
- Then: `dagger install`

Dagger object
- Object: `code_map.CodeMap`
- Functions:
  - build(source_dir, out_dir=".code-map", ignore_dirs=[...], max_file_size=1_000_000, languages=["python","javascript","typescript"]) -> dagger.Directory
  - query(map_dir, query_text, top_k=20) -> str (JSON array of {path, score, reason})
  - print_tree(map_dir, with_tokens=True) -> str (summary + tree text)

Implementation notes
- No CLI image. Functions execute engine code inside a minimal python:3.13-slim container with the module’s src mounted and on PYTHONPATH.
- Tree-sitter optional: when grammars are missing, symbols.jsonl may be empty; build/query/print still work.

Tests
- Engine smoke test: `shared/code-map/tests/test_engine_smoke.py` (build → query → print_tree).
- Run locally:
  ```bash
  cd shared/code-map
  uv pip install pytest pytest-asyncio pytest-cov pytest-timeout
  uv run pytest -q tests/test_engine_smoke.py
  ```

Next improvements
- Add Tree-sitter query (.scm) captures per language for more accurate symbols and imports.
- Add AST-aware chunking (by top-level symbol) instead of fixed-size windows.

Decision Plan: Standalone Python Dagger module for code-map

Context
- Do not reference any source files from the TS codebuff implementation.
- Prefer Python (Dagger supports TS, but Python is requested).
- Modules initialized with `dagger init`; inter-module deps via dagger.json; `dagger install` supported.
- Option to provide a Dockerfile-built CLI container (mirror cypher client pattern) for reuse.

Option A (Recommended): Standalone Python Dagger module (no TS)
- What: Create a new module (e.g., shared/code-map) implemented in Python using tree-sitter-languages.
- Expose Dagger functions:
  - build_map: walk repo, parse files via Tree-sitter, emit code map artifacts (map.json, files.jsonl, symbols.jsonl, chunks.jsonl, relations.jsonl) under a configurable out_dir.
  - query_map: load the on-disk map and rank files for a text query (semantic-lite: token-based TF-IDF over identifiers/comments/imports).
  - print_tree: render a file tree with token estimates and optional per-file top token names.
- Provide optional CLI (Typer) inside the module for local/CI usage (code-map build|query|print-tree), but the primary interface is Dagger functions.
- Packaging:
  - Directory: shared/code-map/
  - dagger.json with dependencies (optionally shared/agent-utils if we reuse utility pieces)
  - pyproject.toml using uv; dependencies: tree-sitter-languages, typer, pydantic, fast-glob-like equivalent if needed
  - src/code_map/main.py: Dagger object_type with functions above
  - src/code_map/engine/: parsing (Tree-sitter init, grammars, queries), chunking, ranking; types.py for Pydantic models
- Pros:
  - Python-native, consistent with your stack
  - No dependency on TS source at all
  - Consumers call Dagger functions directly; easy to orchestrate
- Cons:
  - Need to vendor/maintain Tree-sitter grammar and query coverage in Python

Option B: TypeScript Dagger module (fresh, not referencing codebuff sources)
- What: New TS module using web-tree-sitter/WASM, library+CLI and Dagger functions.
- Pros: Great ecosystem for Tree-sitter in TS
- Cons: You prefer Python; adds Node runtime to your module set

Option C: Python Dagger module + dedicated CLI container (cypher client style)
- What: Implement Option A and ALSO ship a Dockerfile-built CLI image. Other modules can depend on this image to run commands (code-map build/query) via builder helpers.
- Pros: Encapsulated runtime; reproducible CLI usage; mirrors cypher-shell pattern
- Cons: Slightly more infra (Dockerfile), but familiar pattern to your team

Recommended path: Option C (A + CLI container)
- Primary interface: Python Dagger functions (for orchestrations)
- Secondary interface: Containerized CLI (for workflows/CI or cross-language callers)
- Zero references to TS code. Only Python tree-sitter-languages with curated grammars/queries.

Implementation outline
1) Module scaffolding (Python Dagger module)
- Path: shared/code-map/
- Files:
  - dagger.json: name code_map, sdk python, dependencies: ["../../shared/agent-utils"] optional
  - pyproject.toml: uv build; deps: tree-sitter-languages==1.8.0, typer, pydantic, anyio
  - src/code_map/main.py: Dagger object_type CodeMap with functions:
    - build_map(root_dir: str, out_dir: str = ".code-map", ignore_dirs: list[str], max_size: int, langs: list[str]) -> dagger.Directory
    - query_map(map_dir: dagger.Directory|str, text: str, top: int = 20) -> str (JSON array)
    - print_tree(map_dir: dagger.Directory|str, with_tokens: bool = True) -> str
  - src/code_map/engine/{treesitter.py, parse.py, chunk.py, rank.py, print_tree.py, types.py}
  - src/code_map/queries/{python.scm, javascript.scm, typescript.scm} (extend later)

2) Tree-sitter engine (Python)
- Use tree-sitter-languages for initial set (python, js, ts)
- queries/*.scm define captures: functions, classes, methods, variables/constants, imports, docstrings
- parse.py: load language, parse source, run queries → SymbolEntry[] and Import[]; collect identifiers/comments
- chunk.py: chunks by top-level symbols; fallback fixed-size windows with overlap
- rank.py: build TF-IDF index over chunk tokens; query pipeline → chunk scores → roll up to files
- print_tree.py: directory tree with per-file token names (top N); estimate tokens text_length/3

3) Dagger functions
- build_map():
  - Walk host directory with ignore rules; skip binaries; cap file size
  - Parse per file (streamed) and write JSONL artifacts and map.json summary into out_dir
  - Return out_dir as a Dagger Directory for composition/export
- query_map():
  - Read artifacts; build in-memory index if needed; run query; return JSON string list [{path, score, reason}]
- print_tree():
  - Read files.jsonl + token summaries to render text tree; optional with tokens

4) CLI image (optional but recommended)
- Dockerfile (similar to cypher client style):
  - FROM python:3.11-alpine (or slim); install build-base/git if needed for tree-sitter-languages
  - COPY src/ /app/src, install via uv/pip into venv
  - ENTRYPOINT ["code-map"] using Typer commands: build/query/print-tree mirroring Dagger functions
- Builder integration:
  - Add helper in builder module: build_code_map_cli() that builds and caches the CLI image
  - Other modules can run container.with_exec(["code-map", ...])

5) Integration plan
- agents/codebuff: switch File Picker to call code_map.query_map (Dagger function) instead of ad-hoc CLI, preserving JSON output
- agents/codebuff: File Explorer can optionally call code_map.print_tree to render the tree (or continue using Python util we already wrote) — both are Python, either is okay
- orchestrator: stays unchanged; it consumes agents’ structured outputs

6) Tests
- Unit (Python): treesitter parsing for py/js/ts; TF-IDF ranking correctness; print_tree token counts
- Integration: build_map on a tiny fixture repo → validate file/symbol/chunk counts; query_map returns sensible top files
- Dagger: module create + simple calls under uv test; builder helper builds CLI image and runs a sample command

7) dagger.json wiring
- New module dagger.json with dependencies array referencing builder (for optional CLI build) and shared/agent-utils if you want to share utilities
- Other modules add dependency: "code_map": "../../shared/code-map"

Migration notes
- Remove all remaining references to TS code-map prototype we created earlier (we’ll keep the Python agent-utils tree utilities; they are orthogonal)
- If desired, consolidate token pruning/printing from agent-utils into code-map’s print_tree for a single source of truth

Milestones
- M1: Scaffold module + minimal treesitter parsing for python → build_map emits files.jsonl + map.json; print_tree works
- M2: Add js/ts and query_map ranking
- M3: CLI container + builder helper; switch agents to code_map functions
- M4: Tests and docs

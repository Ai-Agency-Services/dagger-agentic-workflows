Title: Code Map TS-Compat Port — Auto Language Detection, Snake_case API only (wrappers removed)

Decision
- Remove legacy wrappers (build/query/print_tree) now and update agents to new API in this PR (aggressive Option B).
- Do NOT require a languages list; detect per-file language automatically with a utility function and allow lightweight overrides.

Objective
- Expose Pythonic API functionally equivalent to TS package:
  - get_file_token_scores (TS: getFileTokenScores)
  - parse_tokens (TS: parseTokens)
- Dagger-safe I/O only (no dag.host()), constructor-first config.

1) API surface (final)
- shared/code-map/src/code_map/main.py (@object_type CodeMap)
  - keep constructor-first:
    - create(config_file: dagger.File) -> CodeMap
    - set_config_from_string(config_str: str) -> CodeMap
  - new functions (only):
    - @function async def get_file_token_scores(self, source_dir: dagger.Directory, glob_patterns: list[str] = [], max_file_size: int = 1_000_000) -> str
    - @function async def parse_tokens(self, file: dagger.File, language_hint: str | None = None) -> str
  - delete legacy: build, query, print_tree

2) Return shapes (TS-compatible semantics)
- parse_tokens(file):
  {
    "identifiers": [ { "name": str, "kind": "function"|"class"|"var"|..., "start": {"line": int, "col": int}, "end": {"line": int, "col": int} }... ],
    "calls": [ { "callee": str, "location": {"line": int, "col": int}, "file": str }... ],
    "language": str
  }
- get_file_token_scores(source_dir):
  {
    "fileTokenScores": { "path": { "token": float }, ... },
    "tokenCallers": { "token": [ { "path": str, "line": int, "col": int } ] }
  }

3) Config (no languages list)
- Resolve defaults from self.config.get("code_map", {}):
  - ignore_dirs: [".git","node_modules","__pycache__", ".venv","dist","build"]
  - max_file_size: 1_000_000
  - language_overrides: Optional[dict[str,str]] (e.g., {".tsx":"typescript",".mjs":"javascript"})
  - default_language: Optional[str] (used only when detection fails and unknown_policy = "best-effort")
  - unknown_policy: "skip" | "best-effort" (default: "skip")

4) Language detection utility (no caller-provided list)
- engine/detect.py
  - def detect_language(path: str, text_head: str, overrides: dict[str,str] | None) -> str | None
    - Strategy (short-circuit when resolved):
      1) Extension map (fast): ext → canonical grammar (e.g., .py → python, .ts/.tsx → typescript, .js/.mjs/.cjs → javascript)
      2) Shebang (first line starts with #!): python, node, bash
      3) Modelines (vim/emacs): language hints
      4) Lightweight keyword heuristics (optional best-effort): small sets for python/js/ts
    - Apply language_overrides first; cache ext→lang in-process per call
- If detection fails:
  - unknown_policy == "skip": omit file from tokenization
  - unknown_policy == "best-effort": use default_language if provided; else skip

5) Engine (Python-only; module-safe)
- shared/code-map/src/code_map/engine/
  - tokens.py
    - def parse_tokens_from_text(text: str, path: str, language_hint: str | None, overrides: dict[str,str] | None, unknown_policy: str, default_language: str | None) -> dict
      - lang = language_hint or detect_language(path, text_head, overrides)
      - If lang is None and unknown_policy == "skip": return {identifiers:[], calls:[], language: "unknown"}
      - Extract identifiers and calls. Option A (fast): delegate per-file to shared/agent-utils container parser and normalize JSON; Option B (later): direct Python tree-sitter.
  - scores.py
    - def accumulate_token_scores(items: list[tuple[str, dict]]) -> tuple[dict, dict]
      - fileTokenScores[path][token] += 1 (simple TF)
      - tokenCallers[token].append({path, line, col})

6) Implementation details
- get_file_token_scores:
  - Export source_dir → local_src (temp)
  - Walk local_src respecting ignore_dirs, glob_patterns, max_file_size
  - For each file: read small head (e.g., 8KB) for detection + full text if ≤ max size
  - tokens = parse_tokens_from_text(text, path, None, overrides, unknown_policy, default_language)
  - Accumulate with scores.accumulate_token_scores
  - return json.dumps({fileTokenScores, tokenCallers})
- parse_tokens:
  - contents = await file.contents(); head = contents[:8192]
  - tokens = parse_tokens_from_text(contents, path="/virtual", language_hint, overrides, unknown_policy, default_language)
  - return json.dumps(tokens)
- No dag.host(); use tempfile and Dagger Directory/File I/O only.

7) Remove wrappers now
- Delete build/query/print_tree from CodeMap and any unused imports in main.py
- Ensure __init__ only re-exports CodeMap

8) Agents update (same PR)
- agents/codebuff/file_explorer:
  - Replace prior build/print_tree path with get_file_token_scores; render a summarized tree from scores if needed; persist exploration.json as before
- agents/codebuff/file_picker:
  - Replace build/query with get_file_token_scores; rank files by tokens matching query terms; keep lexical blend as fallback
- The existing config_file flow remains (we already pass a Dagger File)

9) Tests
- shared/code-map/tests/
  - test_parse_tokens_py_file: trivial python code → identifiers and calls present; language == "python"
  - test_get_file_token_scores_two_files: two small files; scores includes both paths; tokenCallers contain expected tokens
  - test_ignore_and_max_size: ignored dirs and oversized files are skipped
  - test_detection_shebang_and_override: shebang and language_overrides honored

10) Knowledge
- shared/code-map/knowledge.md:
  - Document snake_case API only; detection happens automatically; languages list not required
  - Show overrides example:
    code_map:
      language_overrides:
        ".tsx": "typescript"
      unknown_policy: "skip"

11) Acceptance
- CodeMap exposes only: create, set_config_from_string, get_file_token_scores, parse_tokens
- No dag.host() usage
- Detection removes need for caller-provided languages list; overrides available when needed
- Agents updated to new API; tests pass in shared/code-map and agents/codebuff

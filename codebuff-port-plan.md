Port Plan: Codebase Understanding + Code Generation (Python Dagger stack)

A) Port project-files.ts behavior with code-map into Python + Dagger

1) What project-files.ts does (for parity)
- Build ProjectFileContext on demand (cached by projectRoot):
  - fileTree: getProjectFileTree(projectRoot) respecting .gitignore/.codebuffignore and defaults
  - fileTokenScores + tokenCallers: getFileTokenScores(projectRoot, allFilePaths) from @codebuff/code-map
  - knowledgeFiles: {knowledge.md, CLAUDE.md, codebuff.json, backup} minus agent templates; add scraped URL content
  - userKnowledgeFiles: scan ~ for *knowledge.md
  - gitChanges: status, diff, diffCached, lastCommitMessages
  - changesSinceLastChat: map of file→patch using createPatch
  - systemInfo/shellConfigFiles: host info and discovered configs
- Utilities: safe file reads (size cap, ignore), toAbsolutePath, getFiles* helpers, deleteFile, cache invalidation on directory change, optional worker to assemble context.

2) TS side: expose code-map APIs needed by Python
- Add/confirm public API in @codebuff/code-map:
  - getFileTokenScores(projectRoot: string, allFilePaths: string[]): Promise<{ tokenScores: Record<string, Record<string, number>>, tokenCallers?: Record<string, Record<string, string[]>> }>
    - tokenScores keys: relative file path; values: token→score (from Tree-sitter symbols/identifiers/imports)
    - tokenCallers: optional reason/source buckets (e.g., symbol/import/identifier/comment)
- Add CLI for Python to call from Dagger container:
  - code-map tokens --root <path> --paths @filelist.txt --out tokens.json
    - tokens.json: { tokenScores, tokenCallers }
  - Implementation pulls from the Tree-sitter build artifacts (see code-map plan below).

3) Python: implement ProjectFileContext builder (shared/agent-utils/project_files.py)
- Define Pydantic model mirroring TS schema:
  class ProjectFileContext(BaseModel):
    projectRoot: str
    cwd: str
    fileTree: list[FileTreeNode]  # {name,type,filePath,lastReadTime?,children?}
    fileTokenScores: dict[str, dict[str, float]]
    tokenCallers: dict[str, dict[str, list[str]]] | None
    knowledgeFiles: dict[str, str]
    userKnowledgeFiles: dict[str, str] | None
    agentTemplates: dict[str, Any]
    customToolDefinitions: dict[str, Any]
    codebuffConfig: dict[str, Any] | None
    gitChanges: { status: str, diff: str, diffCached: str, lastCommitMessages: str }
    changesSinceLastChat: dict[str, str]
    shellConfigFiles: dict[str, str]
    systemInfo: { platform: str, shell: str, nodeVersion: str, arch: str, homedir: str, cpus: int }

- Functions (parity with TS):
  - set_project_root(dir: str, set_cwd: bool=False) -> str (triggers cache clear if changed)
  - get_project_root() -> str
  - get_working_directory()/set_working_directory()
  - initialize_project_root_and_workdir(cwd: str|None) -> {project_root, working_dir}
  - to_absolute_path(filepath: str, project_root: str) -> str
  - get_project_file_tree(project_root: str, max_files=10_000, max_depth=20) -> list[FileTreeNode]
    - Implement parse_gitignore(project_root) (use pathspec or custom loader) and DEFAULT_IGNORED_PATHS
    - Performance: early termination if max_files reached; max_depth prevents infinite symlink loops
    - Skip binary files via magic number detection (first 512 bytes)
    - Handle permission errors gracefully (log warning, continue)
  - flatten_tree(nodes) -> list[FileTreeNode]
  - get_all_file_paths(nodes) -> list[str]
  - get_files(file_paths: list[str]) -> dict[str, str|status]
    - MAX_FILE_SIZE=1MB; statuses: OUTSIDE_PROJECT, IGNORED, ERROR, TOO_LARGE[size], DOES_NOT_EXIST
  - get_files_or_null / get_existing_files
  - add_scraped_content_to_files(files: dict[str,str]) -> dict[str,str]
    - Extract URLs; optionally fetch (requests/bs4) if enabled; otherwise no-op with toggle
  - find_knowledge_files_in_dir(dir: str) -> dict[str,str]
  - get_changes_since_last_file_version(last_versions: dict[str,str]) -> dict[str,patch]
    - Use difflib.unified_diff or unidiff to generate patches
  - get_git_changes() -> {status,diff,diffCached,lastCommitMessages}
    - Run via container: ["bash","-c","git status"], etc.; tolerate non-git dirs
  - set_files(files: dict[path,content]) and delete_file(abs_path: str) with safeguards

- Caching
  - Module-level _cached_project_file_context: Optional[ProjectFileContext]
  - clear_cached_project_file_context()
  - cache keyed by project_root; refresh token scores when file list changes (hash of allFilePaths)

- Entry point
  - async def get_project_file_context(project_root: str, last_file_version: dict[str,str]) -> ProjectFileContext:
    - file_tree = get_project_file_tree(project_root)
    - all_file_paths = [node.filePath for node in flatten_tree(file_tree) if node.type=='file']
    - knowledge files collected + scraped
    - user knowledge files (~)
    - token_scores = await get_file_token_scores_via_cli(project_root, all_file_paths)
    - codebuff_config = load_yaml/json if in repo (optional)
    - return ProjectFileContext(...)

- code-map wrapper (with error handling)
  - async def get_file_token_scores_via_cli(project_root: str, all_file_paths: list[str]) -> tuple[tokenScores, tokenCallers|None]
    - Write file list to /tmp/filelist.txt in container
    - Runtime detection: check `which bun`, `which node`, `which npx` in order
    - Execute with timeout (120s default) and capture stderr
    - Fallback strategies:
      1. Bun: bun x code-map tokens --root "{project_root}" --paths @/tmp/filelist.txt --out /tmp/tokens.json
      2. Node: npx code-map tokens (if package available) or node /path/to/code-map/dist/cli.js
      3. If code-map fails: return empty dicts with warning log
    - Validate JSON structure before parsing; handle corrupted output gracefully
    - Return empty tokenScores/tokenCallers on any failure (don't crash the agent)

4) Agents/orchestrator consume ProjectFileContext
- file_explorer: use fileTree + fileTokenScores with truncate_file_tree_based_on_token_budget to produce pretty, token-rich tree
- file_picker: can also factor token scores (e.g., weight files with more relevant tokens) in addition to code-map query results
- thinker: include knowledgeFiles and token-rich file tree in planning context when helpful
- reviewer: unchanged (but can show diff/changesSinceLastChat if needed)

5) Dagger integration (enhanced)
- Container requirements: ensure Node/Bun present with fallback detection
- Mount repo at /work (same as existing agents); emit code-map outputs to .codebuff-map (configurable)
- Inject OPENAI/OPENROUTER only for LLM agents; code-map operates locally
- Container optimization: cache node_modules volume across runs for code-map package
- Memory limits: set reasonable limits for large repos (4GB default, configurable)
- Timeout handling: graceful degradation if code-map takes >2min on large codebases

6) Tests (Python) - Comprehensive
- Unit:
  - parse_gitignore behavior with nested .gitignore files and negation patterns
  - get_project_file_tree: small fixture, symlinks, permission errors, binary detection
  - get_changes_since_last_file_version: patch formats, deleted files, encoding issues
  - to_absolute_path: edge cases, Windows paths, relative navigation (..)
  - caching: refresh triggers, cache invalidation, concurrent access
  - Error handling: code-map CLI failures, malformed JSON, timeout scenarios
- Integration:
  - get_project_file_context on fixture repos (Python, JS/TS, multi-language)
  - Code-map CLI integration: mock successful/failed scenarios
  - File tree truncation: various token budgets and strategies
  - Performance: large repo simulation (1000+ files)
- E2E:
  - Explorer agent: returns truncated tree with tokens for various project types
  - Picker: merges semantic-lite + name/content matches with proper ranking
  - Full workflow: explorer → picker → thinker with realistic project context
- Performance benchmarks:
  - File tree building: target <2s for 10k files
  - Token scoring: target <30s for medium repos
  - Memory usage: monitor and alert if >4GB
- Error scenario testing:
  - Network failures during WASM downloads
  - Corrupted code-map outputs
  - Permission denied on directories
  - Binary files mixed with source code

B) code-map (Tree-sitter) enhanced with robustness
- Keep the Tree-sitter design from the previous plan (build/query/print-tree/tokens CLI). Ensure tokens CLI produces the exact { tokenScores, tokenCallers } shape expected by Python.
- Enhanced error handling:
  - Graceful degradation: if Tree-sitter parsing fails for a file, fallback to regex-based symbol extraction
  - Grammar loading: retry mechanism for WASM downloads; local cache for offline scenarios
  - Memory management: streaming processing for large files; configurable batch sizes
- Performance optimizations:
  - Incremental parsing: only reprocess changed files based on mtime/hash
  - Parallel processing: worker threads for CPU-intensive parsing (limit based on cores)
  - File tree algorithm: optimized depth-based pruning with statistical sampling
- tokenScores semantics (refined):
  - token names extracted from symbols (functions/classes/methods), identifiers, imports, docstrings; scores TF-IDF-like by file; normalize 0..1
  - Score weighting: symbols=1.0, imports=0.8, identifiers=0.6, comments=0.4
  - Deduplication: merge similar tokens (e.g., camelCase variants)
- tokenCallers semantics:
  - { [filePath]: { [token]: ["symbol","identifier","import","comment"] } } — reason buckets for transparency
  - Include confidence scores and source locations for debugging

C) Port mapping table (TS → Python)
- getProjectFileTree → get_project_file_tree (shared/agent-utils/project_files.py)
- parseGitignore → parse_gitignore using pathspec/custom
- getFileTokenScores → get_file_token_scores_via_cli (calls code-map tokens)
- getExistingFiles/getFilesOrNull → same names with Pythonic return types
- addScrapedContentToFiles → add_scraped_content_to_files (toggle via config)
- getChangesSinceLastFileVersion → get_changes_since_last_file_version (difflib)
- getGitChanges (exec git) → get_git_changes (container exec)
- toAbsolutePath → to_absolute_path
- cache: cachedProjectFileContext → module-level cache with clear_cached_project_file_context
- setProjectRoot/WorkingDirectory → set_project_root/set_working_directory

D) Minimal interface changes in Python agents
- Provide a helper in agents/codebuff/main.py:
  async def build_project_file_context(container, project_root: str, last_file_version: dict[str,str]) -> ProjectFileContext:
    - wrapper calling shared/agent-utils/project_files.get_project_file_context with Dagger container operations
- Orchestrator can store this once at start_task and pass to subsequent phases

E) Acceptance checks - Enhanced validation
- Core functionality (project-files.ts parity):
  - build_project_file_context on this repo returns complete context
  - Non-empty fileTree and fileTokenScores (with fallback behavior on errors)
  - knowledgeFiles includes repo knowledge.md files (and optionally scraped URL content)
  - gitChanges populated (or empty strings on non-git repos)
  - changesSinceLastChat generates proper diff patches when last_file_version provided
- Performance validation:
  - File tree generation completes in <2s for this repo size
  - Token scoring completes in <30s or gracefully degrades
  - Memory usage stays under configured limits
- Error resilience:
  - Code-map CLI failures don't crash agents (fallback to empty tokens)
  - Large binary files are properly skipped
  - Malformed .gitignore files don't break tree generation
  - Network issues during setup are handled gracefully
- Agent integration:
  - Explorer: prints truncated tree with tokens for several directories
  - Picker: ranking improves when relevant tokens appear in candidate files
  - Orchestrator: flows end-to-end with ProjectFileContext integration
- Cross-platform compatibility:
  - Works on Linux containers (primary)
  - Handles Windows path separators in file processing
  - Node/Bun detection works across different base images

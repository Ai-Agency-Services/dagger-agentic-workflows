# Code Map (Dagger module)

Tree-sitter–powered code map for repositories, published as a Python Dagger module to be consumed via `dagger install`. No containerized CLI.

## Install (as a Dagger dependency)

In the module that will use code-map, add to `dagger.json`:

```json
{
  "dependencies": [
    "../../shared/code-map"
  ]
}
```

Then run:

```bash
dagger install
```

## Exposed API (Dagger object)

Object: `code_map.CodeMap`

Functions (constructor-first, config-driven):
- create(config_file: dagger.File) -> CodeMap  [classmethod]
- set_config_from_string(config_str: str) -> CodeMap
- build(source_dir: dagger.Directory, out_dir?: str, ignore_dirs?: list[str], max_file_size?: int, languages?: list[str]) -> dagger.Directory
- query(map_dir: dagger.Directory, query_text: str, top_k?: int) -> str
- print_tree(map_dir: dagger.Directory, with_tokens?: bool) -> str

Notes:
- No CLI container — functions call the Python engine directly.
- Defaults are resolved from self.config["code_map"] when args aren’t provided (list params never default to None; use [] and merge from config).

## Outputs
The build step produces the following artifacts in the configured out_dir (default .code-map):

- map.json (summary: total_files, total_symbols, total_chunks, languages, build_time)
- files.jsonl (one per file: path, size, language, tokens_estimate, mtime)
- symbols.jsonl (one per symbol: file, name, type, start_line, end_line; includes docstrings for Python)
- chunks.jsonl (one per chunk: file, start_line, end_line, tokens_estimate, content_hash)
- relations.jsonl (one per import edge: source file -> target module/path, relation_type="import")

### Usage: classmethod create with a YAML file
```python
code_map = await dag.code_map().create(config_file)
src_dir = container.directory(".")
map_dir = await code_map.build(source_dir=src_dir)
results_json = await code_map.query(map_dir=map_dir, query_text="add auth middleware", top_k=20)
summary_tree = await code_map.print_tree(map_dir=map_dir, with_tokens=True)
```

### Usage: cross-module injection (string)
```python
import json
code_map = await dag.code_map().set_config_from_string(json.dumps(config.model_dump()))
src_dir = container.directory(".")
map_dir = await code_map.build(source_dir=src_dir)
```

## Engine usage (for reference and tests)

- Build a map:
  ```python
  from code_map.engine.build import build_code_map
  from code_map.types import BuildOptions
  build_code_map("/path/to/repo", BuildOptions(out_dir=".code-map", languages=["python","javascript"]))
  ```

- Query it:
  ```python
  from code_map.engine.query import query_code_map
  from code_map.types import QueryOptions
  print(query_code_map("/path/to/repo/.code-map", QueryOptions(query_text="foo bar", top_k=10)))
  ```

- Print a tree:
  ```python
  from code_map.engine.print_tree import print_file_tree
  print(print_file_tree("/path/to/repo/.code-map", with_tokens=True))
  ```

## Testing

Run the engine smoke test (no Tree-sitter required):

```bash
cd shared/code-map
uv pip install pytest pytest-asyncio pytest-cov pytest-timeout
uv run pytest -q tests/test_engine_smoke.py
```

## Notes
- No CLI container — this module is intended to be consumed via Dagger dependency injection (`dagger install`).
- Tree-sitter is optional at runtime (engine gracefully falls back if grammars aren’t available).
- The Dagger functions already call the engine directly (no container), exporting inputs to tmp paths.

### Incremental build
- Enabled by default (config.code_map.incremental: true)
- Uses files.jsonl + symbols.jsonl + chunks.jsonl to reuse results for unchanged files (based on size + mtime)
- Configure verbosity with config.code_map.verbose: true

### Performance toggles (config.code_map)
- incremental: bool (default true) — reuse previous outputs based on size+mtime
- verbose: bool (default false)
- chunk_lines: int (default 100) — lines per chunk for chunks.jsonl
- cache_dir: string (optional) — host path to persist .code-map artifacts across runs; if present, build() seeds from and writes back to this path
- concurrency: int (reserved) — parsed but not used yet

Example YAML:
```yaml
code_map:
  out_dir: .code-map
  ignore_dirs: [".git", "node_modules", "__pycache__", ".venv", "dist", "build"]
  max_file_size: 1000000
  languages: ["python", "javascript", "typescript"]
  incremental: true
  verbose: false
  chunk_lines: 120
  cache_dir: ./tmp/code-map-cache
  concurrency: 4
```

## CLI examples (Dagger)

Using a YAML with a code_map section (see demo YAML in agents/codebuff/demo):

```bash
# Install the module (from repo root)
dagger install --mod shared/code-map

# Create the object from YAML and build the map from current directory
# Returns a Directory; export it locally
cd /path/to/your/repo

dagger call --mod /absolute/path/to/shared/code-map \
  create --config-file /absolute/path/to/agents/codebuff/demo/codebuff-feature-demo.yaml \
  build --source-dir . \
  export --path ./.code-map
```

Notes:
- __init__.py must only import from .main (no comments or extra exports)
- Non-nullable list params must not default to None; pass [] and read defaults from self.config

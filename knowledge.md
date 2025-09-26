# Dagger Agents Knowledge Base

## Quick Start

Build Graph (remote clone):
```bash
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-repository \
  --github-access-token=env:GITHUB_TOKEN \
  --repository-url https://github.com/Ai-Agency-Services/web.git \
  --branch feat/loveable-pairing \
  --neo-auth=env:NEO_AUTH \
  --neo-password=env:NEO4J_PASSWORD \
  --open-router-api-key=env:OPEN_ROUTER_API_KEY
```

Analyze Smells (always-verbose):
```bash
dagger call --cloud --mod workflows/smell \
  --config-file demo/agencyservices.yaml \
  --neo-data ./tmp/neo4j-data \
  analyze-codebase \
  --github-access-token=env:GITHUB_TOKEN \
  --neo-password=env:NEO4J_PASSWORD \
  --neo-auth=env:NEO_AUTH
```

Attached Directory (Graph only):
```bash
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-directory \
  --github-access-token=env:GITHUB_TOKEN \
  --local-path /absolute/path/to/target-repo \
  --neo-auth=env:NEO_AUTH \
  --neo-password=env:NEO4J_PASSWORD
```

### Export Cypher batches (dry-run; no execution)
Repository (exports to ./neo-batches):
```bash
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-repository-export \
  --github-access-token=env:GITHUB_TOKEN \
  --repository-url https://github.com/user/repo \
  --branch main \
  --neo-auth=env:NEO_AUTH \
  --neo-password=env:NEO4J_PASSWORD \
  --open-router-api-key=env:OPEN_ROUTER_API_KEY \
  --dry-run true \
  export --path ./neo-batches
```

Attached directory (exports to ./neo-batches):
```bash
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-directory-export \
  --github-access-token=env:GITHUB_TOKEN \
  --local-path /absolute/path/to/target-repo \
  --neo-auth=env:NEO_AUTH \
  --neo-password=env:NEO4J_PASSWORD \
  --open-router-api-key=env:OPEN_ROUTER_API_KEY \
  --dry-run true \
  export --path ./neo-batches
```

What gets exported:
- batches/setup/constraints_and_indexes.cypher (semicolon-separated)
- batches/node-symbol_*.cypher, defined-in_*.cypher, import_*.cypher, symbol-relationship_*.cypher
  - Each file contains // BATCH headers and chunked statements (≤20 files per type)
- batches/summary.json (includes batch_counts and dry_run)

## Project Overview

This repository contains AI-powered development automation agents built with Dagger. The system provides end-to-end automation for software development workflows including code analysis, feature development, testing, and pull request creation.

## Architecture

### Core Components
- **Agents**: Specialized AI agents for different development tasks
- **Services**: Backend services (Neo4j graph DB, query service)
- **Workflows**: Automated development workflows (indexing, graph building, code analysis)
- **Shared**: Common utilities and configuration

### Key Technologies
- **Dagger**: Container orchestration and CI/CD
- **Neo4j**: Graph database for code structure analysis
- **Supabase**: Vector database for semantic search
- **OpenAI/OpenRouter**: LLM providers
- **Python**: Primary language with Pydantic models

## Development Workflow

### Getting Started
1. All modules use `uv` for Python package management
2. Each module has its own `dagger.json` configuration
3. Configuration is centralized via YAML files
4. Use `dagger call` to interact with modules

### Key Agents
- **Codebuff**: Multi-agent orchestrator for feature development
- **Builder**: Environment setup and containerization
- **Pull Request**: Automated PR creation with AI descriptions

### Configuration
- Use `shared/dagger-agents-config` for common config models
- YAML configuration supports container, git, indexing, and LLM settings
- API keys should be passed as Dagger secrets

#### Code Map and File Picker
- code_map:
  - incremental: true|false (default true)
  - verbose: true|false (default false)
  - chunk_lines: int (default 100)
  - cache_dir: string (optional host path to persist .code-map outputs)
- file_picker:
  - semantic_weight: 0..1 (default 1.0; blend semantic with lexical when < 1.0)
  - fallback_when_empty: true|false (default true; use lexical when semantic is empty)

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

file_picker:
  semantic_weight: 0.8
  fallback_when_empty: true
```

## Best Practices

### Code Structure
- Follow the established agent pattern with dependency injection
- Use Pydantic models for all data structures
- Implement proper error handling with structured exceptions
- Keep agents focused on single responsibilities

### Dagger Integration
- Use `@object_type` for main classes
- Use `@function` for exposed methods
- Handle secrets properly with `dagger.Secret`
- Leverage Dagger's caching for efficiency

#### Module layout (Python)
- src/<module>/main.py: define all `@object_type` classes and `@function` methods
- src/<module>/__init__.py: must only import from `.main` and nothing else (no `__version__`, no constants, no helpers, no docstrings or comments)
  - Keep it to just one or more lines like `from .main import <PublicObject>`; importing anything else breaks Dagger introspection

Examples:
- CodeMap
  - src/code_map/main.py defines `@object_type class CodeMap`
  - src/code_map/__init__.py contains exactly:
    ```python
    from .main import CodeMap
    ```
- Graph
  - src/graph/main.py defines `@object_type class Graph`
  - src/graph/__init__.py contains exactly:
    ```python
    from .main import Graph
    ```

### LLM Integration
- Support both OpenAI and OpenRouter providers
- Use structured prompts and response validation
- Implement token usage tracking
- Configure appropriate models per agent type

## Testing

### Pytest Setup
- Root-level pytest configuration in `pyproject.toml`
- Module-specific pytest configs in each component
- Comprehensive test fixtures in `tests/conftest.py`
- Custom markers for different test types: `unit`, `integration`, `neo4j`, `llm`, `dagger`, `slow`

### Running Tests
```bash
# Install test dependencies
make install

# Run all unit tests
make test-unit

# Run integration tests
make test-integration

# Run with coverage
make test-coverage

# Run specific module tests (short names)
make test-neo
make test-query
make test-codebuff
make test-graph
make test-smell
make test-cover
make test-builder

# Run specific module tests (full path names)
make test-services/neo
make test-services/query
make test-workflows/index
make test-workflows/graph
make test-workflows/smell
make test-workflows/cover
make test-agents/codebuff
make test-agents/builder
make test-agents/pull_request
make test-shared/agent-utils

# Run tests requiring Neo4j
make test-neo4j

# Run tests requiring LLM APIs
make test-llm

# Use test runner script
python scripts/run_tests.py --type unit --module neo
```

### Run tests locally like CI
- Prereqs: uv installed (and dagger if you want to run 'develop' for modules with a dagger.json)
- One-liner:

```bash
bash scripts/run_tests_local.sh
```

- Limit to specific modules:

```bash
MODULES="services/query agents/codebuff" bash scripts/run_tests_local.sh
```

Notes:
- Mirrors CI: per-module uv environments, excludes markers (integration, neo4j, llm, dagger, slow)
- For modules with dagger.json, runs `dagger develop` first (if dagger is installed)
- PYTHONPATH is set to the repo root so shared fixtures are importable
- Coverage: generated per-module by default (HTML at `htmlcov/index.html`, XML at `coverage.xml`). Set `COVERAGE=0` to disable:

```bash
COVERAGE=0 make test-local
MODULES="services/query" COVERAGE=0 make test-local
```

- Aggregated coverage (default ON): all module .coverage.* files are combined into one report at `coverage_html/index.html` and `coverage.xml`. Disable with `AGGREGATE=0`:

```bash
AGGREGATE=0 make test-local
MODULES="agents/codebuff" AGGREGATE=0 make test-local
```

## Dagger Config Injection Pattern (constructor-first)

Use only Dagger-safe types in function signatures. Do NOT expose Pydantic models in @function params.

Required for all @object_type modules:
- Properties:
  - config: dict (stores parsed YAML/JSON)
  - config_file: dagger.File (optional)
- Class methods:
  - create(config_file: dagger.File) -> Self: reads contents and sets `config` via yaml.safe_load
  - set_config_from_string(config_str: str) -> Self: parses YAML/JSON string to `config`
- Function params must never require YAMLConfig (or other Pydantic types). Resolve defaults from `self.config` inside the function.
- Non-nullable list params must not default to None. Use [] and resolve config defaults when empty.

Example (object):
- class MyModule:
  - config: dict | None
  - config_file: dagger.File | None
  - create(config_file)
  - set_config_from_string(config_str)
  - do_work(...): merge function args with config defaults from self.config

Consumers:
- In modules, pass the raw config content as a string:
  - await dag.my_module().set_config_from_string(json.dumps(config.model_dump()))
  - Or use `.create(config_file)` when called from CLI with `--config-file`

### Pattern example: Graph module create()

```python
from typing import Annotated, Optional
import yaml
import dagger
from dagger import Doc, object_type, function

@object_type
class Graph:
    # Dagger-safe properties
    config: Optional[dict] = None
    config_file: Optional[dagger.File] = None
    neo_data: Optional[dagger.CacheVolume] = None

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("Path to the YAML config file")],
        neo_data: Annotated[dagger.CacheVolume, Doc("Neo4j data cache volume")],
    ) -> "Graph":
        """Create a Graph object from a YAML config file."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str) if config_str else {}
        return cls(config=config_dict or {}, config_file=config_file, neo_data=neo_data)
```

- Functions should ONLY use Dagger-safe parameters and read defaults from self.config.
- For list parameters, never use `None` defaults. Use [] for lists then: `if not my_list: my_list = cm.get("my_list", ["default"])`

### Pattern example: CodeMap module create()

```python
from typing import Annotated, Optional
import yaml
import dagger
from dagger import Doc, object_type, function

@object_type
class CodeMap:
    config: Optional[dict] = None
    config_file: Optional[dagger.File] = None

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("Path to the YAML config file")],
    ) -> "CodeMap":
        cfg_str = await config_file.contents()
        cfg = yaml.safe_load(cfg_str) if cfg_str else {}
        return cls(config=cfg or {}, config_file=config_file)

    @function
    async def build(self,
        source_dir: Annotated[dagger.Directory, Doc("Source to analyze")],
        ignore_dirs: Annotated[list[str], Doc("Dirs to ignore")] = [],
        languages: Annotated[list[str], Doc("Languages to parse")] = [],
    ) -> dagger.Directory:
        cfg = self.config or {}
        cm = cfg.get("code_map", {})
        if not ignore_dirs:
            ignore_dirs = cm.get("ignore_dirs", [".git","node_modules","__pycache__", ".venv","dist","build"]) 
        if not languages:
            languages = cm.get("languages", ["python","javascript","typescript"]) 
        # ... rest of function ...
```

### Pattern checklist (for every @object_type)
- config and config_file properties exist on the @object_type
- create classmethod loads YAML to dict and returns cls(...)
- All functions accept only Dagger-safe types
- Non-nullable list params default to [] (never None); merge from config when empty

## Dagger Config Injection Pattern (constructor-first)

Use only Dagger-safe types in function signatures. Do NOT expose Pydantic types in @function params.

Pattern requirements for every @object_type:
- Properties:
  - config: dict | None
  - config_file: dagger.File | None
  - Module-specific resources (e.g., neo_data: dagger.CacheVolume | None)
- Dagger-safe constructors:
  - @classmethod async def create(cls, config_file: dagger.File, ...resources) -> Self
    - Reads contents with await config_file.contents()
    - Parses dict via yaml.safe_load(config_str)
    - Returns cls(config=config_dict, config_file=config_file, ...)

### Pattern example: Graph module
```python
from typing import Annotated, Optional
import yaml
import dagger
from dagger import Doc, object_type

@object_type
class Graph:
    config: Optional[dict] = None
    config_file: Optional[dagger.File] = None
    neo_data: Optional[dagger.CacheVolume] = None

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("Path to the YAML config file")],
        neo_data: Annotated[dagger.CacheVolume, Doc("Neo4j data cache volume")],
    ) -> "Graph":
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str) if config_str else {}
        return cls(config=config_dict or {}, config_file=config_file, neo_data=neo_data)
```

Example: CodeMap module
```python
from typing import Annotated, Optional
import yaml
import dagger
from dagger import Doc, object_type, function

@object_type
class CodeMap:
    config: Optional[dict] = None
    config_file: Optional[dagger.File] = None

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("Path to the YAML config file")],
    ) -> "CodeMap":
        cfg_str = await config_file.contents()
        cfg = yaml.safe_load(cfg_str) if cfg_str else {}
        return cls(config=cfg or {}, config_file=config_file)

    @function
    async def build(
        self,
        source_dir: Annotated[dagger.Directory, Doc("Source to analyze")],
        ignore_dirs: Annotated[list[str], Doc("Dirs to ignore")] = [],
        languages: Annotated[list[str], Doc("Languages to parse")] = [],
    ) -> dagger.Directory:
        cm = (self.config or {}).get("code_map", {})
        if not ignore_dirs:
            ignore_dirs = cm.get("ignore_dirs", [".git","node_modules","__pycache__", ".venv","dist","build"]) 
        if not languages:
            languages = cm.get("languages", ["python","javascript","typescript"]) 
        # ... call engine with resolved defaults ...
```

Checklist
- config and config_file properties present
- classmethod create reads YAML and returns cls(...)
- Functions accept only Dagger-safe types
- List params default to [] and merge from config when empty

Note: This is the canonical pattern. Older duplicate sections should be removed.

### Dagger module verification vs install
- Use `dagger functions --mod <module-dir>` to verify a module and list callable objects/functions (loads the module).
- Use `dagger call --mod <module-dir> <object-or-function> ...` to execute functions.
- Do NOT use `dagger install` to verify modules — it’s only for adding a module as a dependency to another module (updates dagger.json).

Examples:
```bash
# Verify CodeMap module
dagger functions --mod shared/code-map

# Call a function (constructor-first)
dagger call --mod shared/code-map create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml
```

### Verification checklist
- List callable objects/functions (loads the module):
  - dagger functions --mod shared/code-map
  - dagger functions --mod agents/codebuff
- Minimal end-to-end check (constructor-first):
  - dagger call --mod shared/code-map create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml
  - dagger call --mod shared/code-map build --source-dir . export --path ./.code-map

## Common Commands (constructor-first order)

```bash
# Build and test an agent (constructor-first + --mod)
dagger call --mod <module-dir> --config-file=config.yaml create

# Run complete feature development (constructor-first + --mod)
dagger call --mod agents/codebuff \
  --config-file config.yaml \
  orchestrate-feature-development \
  --task-description="Feature description" \
  --openai-api-key=env:OPENAI_API_KEY

# Build code graph from a repository (constructor-first + --mod)
dagger call --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  --neo-data ./tmp/neo4j-data \
  build-graph-for-repository \
  --github-access-token=env:GITHUB_TOKEN \
  --repository-url https://github.com/user/repo \
  --neo-auth=env:NEO_AUTH \
  --neo-password=env:NEO4J_PASSWORD

# Generate tests with coverage (constructor-first + --mod)
dagger call --mod workflows/cover \
  --config-file=config.yaml \
  generate-tests
```

## Development Notes

### Testing
- Each module includes demo configurations
- Use local containers for development testing
- Test agents individually before orchestration

### Debugging
- Check container logs for execution issues
- Validate YAML configuration syntax
- Ensure API keys have proper permissions
- Use debug flags in Dagger calls

### Performance
- Graph operations can be memory intensive
- Use appropriate concurrency limits
- Consider token usage costs for LLM calls
- Cache results where possible

## Module Dependencies

### Agents depend on:
- `builder` for environment setup
- `shared/dagger-agents-config` for configuration
- LLM providers for AI capabilities

### Workflows depend on:
- `services/neo` for graph database
- `shared/agent-utils` for code parsing
- Various analysis tools and libraries

## Security Considerations

- Never commit API keys to version control
- Use Dagger secrets for sensitive data
- Validate all external inputs
- Limit container permissions appropriately
- Review AI-generated code before deployment

## Smell configuration (thresholds and detectors)

Add a smell block in your YAML (used by workflows/smell). Global thresholds apply; include/exclude tunes signal.

```yaml
smell:
  thresholds:
    long_function_lines: 150      # lines
    long_param_count: 6           # params
    large_class_loc: 300          # lines
    god_class_methods: 25         # methods
    high_fan_out: 20              # files
    high_fan_in: 10               # files
  detectors:
    include: []                   # empty means all enabled
    exclude: []                   # e.g., ["DeadCodeDetector", "BarrelFileDetector"]
```

## File Picker configuration (agents/codebuff)

Control how semantic results (from CodeMap.query) are combined with lexical matches.

- file_picker.semantic_weight: 0..1 (default 1.0)
  - 1.0: use only semantic results
  - 0.0: use only lexical (name/content) results
  - between 0 and 1: blend results (filename matches weighted 0.6, content matches weighted 0.4)
- file_picker.fallback_when_empty: bool (default true)
  - If semantic results are empty/invalid, fall back to lexical results automatically

YAML example:
```yaml
file_picker:
  semantic_weight: 0.8        # blend in 20% lexical
  fallback_when_empty: true   # if semantic produces no files, use lexical

code_map:
  out_dir: .code-map
  incremental: true
  verbose: false
  chunk_lines: 120
  cache_dir: ./tmp/code-map-cache
```

## Dagger Errors (Python SDK) quick reference
- Cloud auth: set DAGGER_CLOUD_TOKEN; use --cloud
- Module not found: run from module dir or pass --mod <module-dir>
- Constructor vs method: constructor first, then function, then method args
- Export errors: function must return File/Directory; use `export --path`
- GHA multiline output: avoid big content in GITHUB_OUTPUT—export artifacts instead
- Debug: `await c.stdout()/stderr()`, Dagger Cloud trace URL, `DAGGER_LOG_LEVEL=debug`

# Delete the trailing web_scraped_content blocks and any pasted HTML from here


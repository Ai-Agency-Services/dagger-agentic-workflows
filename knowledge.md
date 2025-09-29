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

### PydanticAI Agent Development Patterns

PydanticAI is the Python framework we use for building AI agents. Key patterns:

#### Agent Definition
```python
from pydantic_ai import Agent

# Basic agent with instructions and dependencies
agent = Agent(
    model='openai:gpt-4o',
    deps_type=MyDependencies,
    instructions="You are a helpful agent that...",
    retries=2
)
```

#### Dependencies (Structured Data Injection)
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class MyDependencies:
    config: dict
    container: dagger.Container
    # Lazy-loaded sub-agents
    file_explorer: Optional[Agent] = None
```

#### Tool Registration
```python
# Direct tool decorator
@agent.tool
async def my_tool(
    ctx: RunContext[MyDependencies],
    param: str
) -> str:
    """Tool description for the LLM."""
    # Access dependencies via ctx.deps
    return f"Result: {param}"

# Toolset organization
from pydantic_ai import Toolset

toolset = Toolset()

@toolset.tool
async def grouped_tool(ctx: RunContext[MyDependencies]) -> str:
    # Implementation
    pass

# Register toolset with agent
agent = Agent(
    model='openai:gpt-4o',
    deps_type=MyDependencies,
    toolsets=[toolset]
)
```

#### Multi-Agent Coordination
```python
# Agent-as-Tool Pattern
@orchestrator.tool
async def run_sub_agent(
    ctx: RunContext[OrchestratorDeps],
    task: str
) -> str:
    if ctx.deps.sub_agent is None:
        ctx.deps.sub_agent = create_sub_agent()
    
    result = await ctx.deps.sub_agent.run(
        task,
        deps=SubAgentDeps(container=ctx.deps.container)
    )
    return result.output
```

#### Streaming and Real-time Updates
```python
# Stream agent execution
async with agent.iter(prompt, deps=deps) as it:
    async for step in it:
        if step.is_tool_call:
            print(f"🔧 Running: {step.tool_name}")
        elif step.is_model_response:
            print(f"🤖 Agent: {step.content}")
    
    final_result = it.final_result()
```

#### Error Handling and Retries
- Use `retries=N` in Agent() for automatic retry of failed tool calls
- Handle errors gracefully in tools and return structured messages
- PydanticAI automatically validates tool parameters using type hints

#### Best Practices
- Keep agents narrow; compose via orchestrator
- Use structured deps and typed tool I/O
- Persist state in containers; pass explicit deps rather than global state
- Prefer deterministic tool interfaces with clear error handling
- Use toolsets to organize related functionality
- Leverage streaming for long-running workflows

#### References
- [Agent Instructions](https://ai.pydantic.dev/agents/#instructions)
- [Dependencies](https://ai.pydantic.dev/dependencies/#defining-dependencies)
- [Tools](https://ai.pydantic.dev/tools/) and [Advanced Tools](https://ai.pydantic.dev/tools-advanced/)
- [Toolsets](https://ai.pydantic.dev/toolsets/)
- [Multi-Agent Applications](https://ai.pydantic.dev/multi-agent-applications/)

### Available Development Tools

When working with the codebase, the following tools are available for agents and development workflows:

#### Planning and Documentation
- `create_plan`: Generate detailed markdown plans for complex tasks
- `add_subgoal`/`update_subgoal`: Track progress on complex multi-step tasks

#### File Operations
- `read_files`: Read multiple files from the codebase
- `write_file`: Create or edit files (use edit snippets, not full rewrites)
- `str_replace`: Make precise string replacements in existing files
- `code_search`: Search for patterns across the codebase using ripgrep

#### Execution and Testing
- `run_terminal_command`: Execute CLI commands (SYNC or BACKGROUND)
- `browser_logs`: Navigate to URLs and capture console logs/errors for web apps

#### Agent Coordination
- `spawn_agents`: Spawn multiple agents in parallel for complex tasks
- `spawn_agent_inline`: Spawn a single agent within current message history
- `lookup_agent_info`: Get information about available agent types

#### Analysis and Research
- `think_deeply`: Perform detailed step-by-step analysis for complex problems
- Available spawnable agents:
  - `codebuff/file-explorer@0.0.2`: Comprehensive codebase exploration
  - `codebuff/file-picker@0.0.2`: Find relevant files for specific tasks
  - `codebuff/researcher@0.0.2`: Web search and documentation research
  - `codebuff/thinker@0.0.2`: Deep thinking on specific problems
  - `codebuff/reviewer@0.0.2`: Code review and feedback
  - `codebuff/context-pruner@0.0.2`: Context management for long conversations

#### Session Management
- `end_turn`: Signal completion and hand control back to user

### Orchestrator Toolsets (agents/codebuff)
- Planning & Docs: create_plan, add_subgoal, update_subgoal, think_deeply
- File Ops: read_files, write_file, str_replace, code_search
- Execution & Testing: run_terminal_command, browser_logs
- Agent Coordination: spawn_agents, spawn_agent_inline, lookup_agent_info
- Sub-Agents: run_file_explorer, run_file_picker, run_researcher, run_thinker, run_reviewer, run_implementation, run_context_pruner
- Session: end_turn

#### Best Practices for Tool Usage
- Use `read_files` extensively before making changes (20+ files is fine)
- Use `code_search` to find patterns and understand dependencies
- Always spawn `file-explorer` first for complex tasks
- Use `spawn_agents` for parallel work, `spawn_agent_inline` for sequential
- Spawn `reviewer` agent after significant code changes
- Use `write_file` with edit snippets, not full file rewrites
- Use `str_replace` for precise edits in existing files

### Code Structure
- Follow the established agent pattern with dependency injection
- Use Pydantic models for all data structures
- Implement proper error handling with structured exceptions
- Keep agents focused on single responsibilities

#### Python import hygiene (avoid UnboundLocalError)
- Do not import json (or other stdlib modules) inside functions that also use json earlier in the function.
- Keep a single module-level `import json` and reference it everywhere in the file.
- Never assign to a local variable named `json` (shadows the module). This can cause `UnboundLocalError` at runtime.

### Dagger Integration

#### Test Environment Configurator pattern (agents/codebuff)
- Purpose: detect project language/framework/package manager, configure the container, and return a shell test command.
- Dagger-safe flow:
  - In Codebuff main, expose three @function proxies:
    - detect_test_env(container) -> str (TestEnvConfig JSON)
    - configure_test_env(container, cfg_json) -> dagger.Container
    - get_test_command(cfg_json) -> str
  - In orchestrate-feature-development, call detect → configure → get_test_command and pass into OrchestratorDependencies:
    - test_env_cfg_json: str
    - test_command: str (None when skipped)
  - In execute_implementation, prefer deps.test_command:
    - If absent → soft-pass (tests skipped)
    - If it errors with “no tests collected” → soft-pass
    - Otherwise gate commit/PR on success
- Config propagation: pass config_file (dagger.File) via dependency objects; no YAML fallback in agents.
- YAML overrides (optional):
```yaml
testing:
  enable: true
  working_dir: apps/api
  test_command: pnpm test --filter api
  install_command: pnpm install --frozen-lockfile
  timeout_seconds: 900
```
- State writes: .codebuff-state/test_env.json + timeline log entries.

#### Dagger-safe config_file propagation (agents/codebuff)
- Pass a Dagger File for configuration through dependency objects (required at runtime).
- Dependencies: include `config_file: Optional[dagger.File]`, but agents treat it as required — no YAML fallback.
- Agents (File Explorer/Picker) must use `ctx.deps.config_file` when constructing downstream modules (e.g., `dag.code_map(config_file=...)`). If missing, return a clear error.
- In main objects, pass `getattr(self, "config_file", None)` into dependency constructors (mock-safe), but ensure real runs provide a config file.
- No in-function YAML serialization paths — orchestration provides the config file.
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

## Orchestrator runtime guard pattern

- Always pass deps to pydantic_ai Agent.run when tools reference ctx.deps:
  - result = await agent.run(prompt, deps=deps)
- Initialize orchestration state before the first tool call:
  - deps.state = OrchestrationState(task_spec=TaskSpec(id=str(uuid.uuid4()), goal=task_description, focus_area=focus_area))
- Use relative imports for orchestrator submodules inside agents/codebuff (avoid shadowing by root TS folder):
  - from .orchestrator.agent import create_orchestrator_agent
  - from .orchestrator.models import OrchestrationState, OrchestratorDependencies, TaskSpec

Example (main.py critical lines):
```python
import uuid
from datetime import datetime, UTC
from .orchestrator.models import (
    OrchestrationState, OrchestratorDependencies, TaskSpec, Phase, Status
)

# Build valid initial state (all required fields present)
initial_state = OrchestrationState(
    task_id=str(uuid.uuid4()),
    current_phase=Phase.EXPLORATION,
    status=Status.IN_PROGRESS,
    start_time=datetime.now(UTC),
    last_update=datetime.now(UTC),
    task_spec=TaskSpec(
        id=str(uuid.uuid4()),
        goal=task_description,
        focus_area=focus_area,
    ),
)

# Always pass deps
result = await agent.run(workflow_prompt, deps=deps)
```

## Container-backed Orchestration State (agents/codebuff)

- State directory: .codebuff-state (relative to workdir)
- Files written during workflow:
  - task.json: { id, goal, focus_area, created_at }
  - exploration.json: { language_counts, with_tokens }
  - selected_files.json: [ { path, score, reason } ]
  - plan.json: serialized plan
  - implementation/
    - test_results.json: { tests_passed, test_output, exit_code }
    - summary.json: serialized change_set
    - diffs/commit.diff
  - review.json: reviewer summary
  - pull_request.json: { branch, status, message }
  - log.txt: append-only timeline (start_task → explore → select → plan → implement → review → PR)

Test-gated PR flow
- execute_implementation runs the test suite in the container; commit only if tests pass
- If tests fail: no commit, no PR
- PR step reuses the same container (includes code + .codebuff-state)

Implementation pattern
- Always reassign dependencies with the updated container:
  - ctx.deps.container = await write_json(ctx.deps.container, "plan.json", plan)
  - ctx.deps.container = await append_log(ctx.deps.container, "create_plan: done")

## Common Commands (constructor-first order)

```bash
# Build and test an agent (constructor-first + --mod)
dagger call --mod <module-dir> --config-file=config.yaml create

# Run complete feature development (constructor-first + --mod)
dagger call --mod agents/codebuff \
  --config-file config.yaml \
  orchestrate-feature-development \
  --feature-task-description="Feature description" \
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

## PR Orchestrator Commands (agents/codebuff)

Trigger feature development workflow directly from a PR comment using the new command processor.

- Supported command:
  - `@orchestrator feature - kickoff feature-development-workflow`

- CLI invocation (process PR comment text):
```bash
dagger call --mod agents/codebuff \
  --config-file config.yaml \
  process-orchestrator-command \
  --github-token=secret:GITHUB_TOKEN \
  --repository-url https://github.com/org/repo \
  --branch main \
  --command-text "@orchestrator feature - kickoff feature-development-workflow" \
  --feature-task-description "Add user profile management with avatar upload" \
  --openai-api-key=env:OPENAI_API_KEY
```

Notes:
- Uses `feature_task_description` (or defaults to "Feature from PR" if omitted).
- Provider is chosen based on provided keys (OpenRouter preferred when available).
- Integrates with the Git-based feedback gates you enabled (PLANNING stop + PR).

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

<!-- Delete any web_scraped_content blocks appended below. They were placeholder 404 pages. -->

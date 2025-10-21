# Dagger Agents Knowledge Base

## Quick Start

Build Graph (remote clone):
```bash
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-repository \
  --github-access-token=env:GITHUB_TOKEN \
  --repository-url https://github.com/user/repo.git \
  --branch main \
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
  --repository-url https://github.com/user/repo.git \
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

### Spec-Kit Integration (NEW)

Codebuff now uses the **Spec-Kit methodology** for feature development:

- **Constitution → Spec → Tasks workflow**: Structured, validated planning
- **Implementation-review loops**: Each task iterates up to 3 times for quality
- **Atomic task execution**: Topologically sorted with dependency validation
- **Automatic migration**: Old plan.md files converted to spec-kit format
- **Comprehensive state**: JSON files for constitution, spec, tasks, logs

See:
- `agents/codebuff/SPEC_KIT_GUIDE.md` - Complete methodology guide
- `agents/codebuff/SPEC_KIT_MIGRATION.md` - Migration from legacy workflow
- `agents/codebuff/src/codebuff/orchestrator/speckit_workflow.py` - Implementation

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
- **CRITICAL**: RunContext has no `run_tool()` method - directly call tool functions instead
  - ❌ Wrong: `await ctx.run_tool('check_syntax')`
  - ✅ Correct: `await check_syntax(ctx)`

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

## Dagger Git Auth API change (Migration Note)

Dagger updated the Git module API. Replace the deprecated `.with_auth_token(...)` with the new `http_auth_token` parameter on `dag.git(...)`.

Old (LEGACY — do not copy/paste):

```python
source = (
    await dag.git(url=repo_url, keep_git_dir=True)
    .with_auth_token(github_token)
    .branch(branch)
    .tree()
)
```

New:

```python
source = (
    await dag.git(url=repo_url, keep_git_dir=True, http_auth_token=github_token)
    .branch(branch)
    .tree()
)
```

## Branch Safety Policy (Automation)
- Never commit or push on protected branches: main, master, develop, the configured base_pull_request_branch, OR the exact branch we cloned as the source (persisted to .codebuff-state/source_branch.json).
- Before any git add/commit/push, the workflow checks the current branch; if protected, it auto-creates a working branch using branch_prefix (default: feature/codebuff-<timestamp>) and switches to it.
- PRs are created against the configured base branch (template enforces develop in PR agent).
- Configuration knobs:
  - orchestrator.branch_prefix (string)
  - git.base_pull_request_branch (string)

## Codebuff Resume & Feedback – Quick Reference

New functions (agents/codebuff):
- orchestrate_feature_development: end-to-end feature workflow; if feedback enabled in YAML (orchestrator.feedback.enabled), stops at configured phase and opens a PR to collect @orchestrator commands.
- setup_environment: prepare repo-backed container and test environment.
- request_feedback / request_feedback_from_self: write feedback_request.json + feedback_sentinel.json (requested=true) and create/update a draft PR.
- resume_workflow: rebuild container from a working branch and load .codebuff-state; returns loaded/missing summary and phase (falls back to commit footer if task_spec missing).
- process_orchestrator_command: fast path to store a single PR comment (e.g., "@orchestrator approve") into user_feedback.json.
- process_pr_feedback: parse a JSON array of comments and save the latest @orchestrator command.
- continue_workflow: gate on sentinel + user_feedback; if approved, proceed to the next tool based on saved phase/status.
- export_state / export_state_from_self: export .codebuff-state for local inspection.

Common CLI usage:
- Resume:
  ```bash
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    resume-workflow \
    --github-token=secret:GITHUB_TOKEN \
    --repository-url https://github.com/user/repo.git \
    --branch-name <working-branch> \
    --provider openrouter \
    --open-router-api-key=env:OPEN_ROUTER_API_KEY
  ```
- Approve (PR feedback):
  ```bash
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    process-orchestrator-command \
    --github-token=secret:GITHUB_TOKEN \
    --repository-url https://github.com/user/repo.git \
    --branch <working-branch> \
    --command-text "@orchestrator approve"
  ```
- Continue:
  ```bash
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    continue-workflow \
    --github-token=secret:GITHUB_TOKEN \
    --repository-url https://github.com/user/repo.git \
    --branch-name <working-branch> \
    --provider openrouter \
    --open-router-api-key=env:OPEN_ROUTER_API_KEY
  ```
- Export .codebuff-state:
  ```bash
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    export-state-from-self export --path ./.codebuff-state
  ```

Tips:
- If resume shows missing task_spec, it still recovers phase/status via commit footer.
- Feedback gate: continue-workflow will wait if feedback_sentinel.requested=true and user_feedback.json is absent; run approval first.
- A full, copy-paste walkthrough is available at `agents/codebuff/RESUME_TEST.md`.

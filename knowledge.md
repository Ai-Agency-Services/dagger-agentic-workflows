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
  --neo-auth=env:NEO4J_AUTH \
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

Notes:
- Detector names are class names (normalized). If include is non‑empty, only those run (minus excluded).

---

## Dagger Filesystems (Python SDK) quick reference
- Host access: `dag.host().directory("./path")`, `dag.host().file("./file.txt")`
- Create in-pipeline: `dag.directory().with_new_file("out/a.txt","A").file("out/a.txt")`
- Mount into container: `.with_mounted_directory("/work", dag.host().directory("."))`
- Return artifacts: return dagger.File/Directory and export via CLI `export --path`
- Read: `await file.contents()`, `await directory.entries()`

## Dagger Containers (Python SDK) quick reference
- Start/run:
  ```python
  c = dag.container().from_("alpine:3.20").with_exec(["sh","-lc","echo ok"])  # await c.stdout()
  ```
- Workdir/env: `.with_workdir("/work").with_env_variable("APP_ENV","dev")`
- Mounts: dir/file/temp dir; secrets via `.with_secret_variable("TOKEN", token)`
- Immutability: every `.with_*` returns a new container; reassign each step
- Debug: `await c.stdout()/stderr()`, `pwd && ls -la`, `env | sort`

## Dagger Services (Python SDK) quick reference
- Service + client:
  ```python
  pg = (dag.container().from_("postgres:16")
          .with_env_variable("POSTGRES_PASSWORD","pass")
          .with_exposed_port(5432)
          .as_service())
  client = (dag.container().from_("postgres:16")
              .with_service_binding("db", pg)
              .with_exec(["sh","-lc","pg_isready -h db -p 5432"]))
  ```
Tips: expose ports before `.as_service()`, bind via `.with_service_binding("name", svc)`, use app‑native readiness checks.

## Dagger Builds (Python SDK) quick reference
- Host context:
  ```python
  context = dag.host().directory(".")
  img = dag.container().build(context)
  file_out = img.file("/app/out/report.txt")  # export via CLI
  ```
- Git context:
  ```python
  src = dag.git("https://github.com/org/repo").branch("main").tree()
  img = dag.container().build(src.directory(""))
  ```
- Publish: `ref = await img.publish("ttl.sh/your-image:1h")`

## Dagger Secrets (Python SDK) quick reference
- CLI sources: `secret:NAME`, `env:NAME`, `file:./path`
- Inject: `.with_secret_variable("TOKEN", token)` (avoid writing secrets to disk)

## Dagger Errors (Python SDK) quick reference
- Cloud auth: set DAGGER_CLOUD_TOKEN; use --cloud
- Module not found: run from module dir or pass --mod <module-dir>
- Constructor vs method: constructor first, then function, then method args
- Export errors: function must return File/Directory; use `export --path`
- GHA multiline output: avoid big content in GITHUB_OUTPUT—export artifacts instead
- Debug: `await c.stdout()/stderr()`, Dagger Cloud trace URL, `DAGGER_LOG_LEVEL=debug`

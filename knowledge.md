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

## Common Commands

Important: Run dagger calls from the module directory that contains its dagger.json (e.g., workflows/graph, workflows/smell) or pass --mod <module-dir>. Constructor args (e.g., --config-file, --neo-data) come before the function; method args come after.

```bash
# Build and test an agent
# (constructor-first + --mod)
dagger call --mod <module-dir> --config-file=config.yaml create

# Run complete feature development
# (constructor-first + --mod)
dagger call --mod agents/codebuff \
  --config-file config.yaml \
  orchestrate-feature-development \
  --task-description="Feature description" \
  --openai-api-key=env:OPENAI_API_KEY

# Analyze codebase (Graph build for a repository)
# (constructor-first + --mod)
dagger call --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-repository \
  --repository-url https://github.com/user/repo

# Generate tests with coverage
# (constructor-first + --mod)
dagger call --mod workflows/cover \
  --config-file=config.yaml \
  generate-tests
```

## Dagger CLI quick reference (constructor-first order)

- Constructor args (module-level), e.g. --config-file, --neo-data, come before the function
- Method args (function params) come after the function
- Run from module dir or pass --mod <module-dir>

Examples (robust: use --mod from repo root)

Smell (analyze-codebase):
```bash
dagger call --cloud --mod workflows/smell \
  --config-file demo/agencyservices.yaml \
  --neo-data ./tmp/neo4j-data \
  analyze-codebase \
  --github-access-token=env:GITHUB_TOKEN \
  --neo-password=env:NEO4J_PASSWORD \
  --neo-auth=env:NEO_AUTH
```

Graph (build-graph-for-repository):
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

Graph (attached directory mode):
```bash
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-directory \
  --github-access-token=env:GITHUB_TOKEN \
  --local-path /absolute/path/to/target-repo \
  --neo-auth=env:NEO_AUTH \
  --neo-password=env:NEO4J_PASSWORD
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

## CI Workflows

### Unit Tests (develop)
Runs unit tests automatically on:
- push to develop (covers merges into develop)
- pull_request targeting develop (pre-merge checks)

Workflow file: .github/workflows/unit-tests-develop.yml

What it does:
- Installs uv
- Installs test dependencies (make install)
- Runs unit tests only (make test-unit → pytest -m "unit")

How to customize:
- Edit Makefile targets if you want to change markers or args
- Add caching steps if you need speed (e.g., actions/cache for uv wheels)
- Expand to matrix strategy if you want multiple OS/Python versions

### Smell Graph Report

Dagger Cloud auth:
- Set repo secret DAGGER_CLOUD_TOKEN (or DAGGER_TOKEN)
- The workflow exports it to the job as env DAGGER_CLOUD_TOKEN
- Calls use `--cloud` and are authenticated automatically
- See .github/workflows/smell-graph.yml for running Graph + Smell against:
  - remote mode (repository_url/branch)
  - attached mode (checkout external repo to path and analyze)
- HTML artifact report (smell_report.html) is generated and uploaded (no GITHUB_OUTPUT usage)
- skip_graph input: set to true in workflow_dispatch to run Smell only while troubleshooting
- PR comment includes a link to the workflow run; download the smell-report artifact to view
- Export API: you can write the report directly to the host via export:
  ```bash
  dagger call --mod workflows/smell \
    --config-file demo/agencyservices.yaml \
    --neo-data ./tmp/neo4j-data \
    analyze-codebase-export \
    --github-access-token=env:GITHUB_TOKEN \
    --neo-password=env:NEO4J_PASSWORD \
    --neo-auth=env:NEO_AUTH \
    --format html \
    export --path smell_report.html
  ```

## Exporting files to host with Dagger (export --path)

Use the export subcommand to write files returned by a function directly to the host runner. Constructor args (e.g., --config-file, --neo-data) come before the function; method args come after. Then append the export subcommand:

Smell report (HTML) — export to host runner:
```bash
dagger call --cloud --mod $GITHUB_WORKSPACE/workflows/smell \
  --config-file=demo/agencyservices.yaml \
  --neo-data=./tmp/neo4j-data \
  analyze-codebase-export \
  --github-access-token=env:GH_PAT \
  --neo-password=env:NEO4J_PASSWORD \
  --neo-auth=env:NEO_AUTH \
  --format html \
  export --path smell_report.html
```

Reference: https://docs.dagger.io/cookbook/filesystems

### Dagger Filesystems (Python SDK) quick reference

- Access host filesystem
  - Host directory: `dag.host().directory("./some/dir")`
  - Host file: `dag.host().file("./path/to/file.txt")`

- Create in-pipeline files/directories (virtual, content-addressed)
  - New file: `dag.directory().with_new_file("path/in/dir.txt", "content").file("path/in/dir.txt")`
  - Include a host file: `dag.directory().with_file("dst/name.txt", dag.host().file("./src/name.txt")).file("dst/name.txt")`
  - Include a directory: `dag.directory().with_directory("dst/", dag.host().directory("./src"))`
  - Select subpaths: `directory.file("sub/file.ext")`, `directory.directory("sub/folder")`

- Mount directories into a container
  - `container.with_mounted_directory("/work", dag.host().directory("."))`
  - Combine with `with_exec()` to process files inside the container

- Read content during a run
  - File contents: `await file.contents()`
  - Directory entries: `await directory.entries()`

- Return files/directories from functions
  - Return a single file: annotate return type as `dagger.File` and return `dag.directory().with_new_file("out/report.html", html).file("out/report.html")`
  - Return a directory: annotate return type as `dagger.Directory` and return a directory node
  - CLI export (recommended): use the `export` subcommand to write to the host

- CLI export (constructor-first order + export subcommand)
  - Example (Smell report):
    ```bash
    dagger call --cloud --mod workflows/smell \
      --config-file=demo/agencyservices.yaml \
      --neo-data=./tmp/neo4j-data \
      analyze-codebase-export \
      --github-access-token=env:GH_PAT \
      --neo-password=env:NEO4J_PASSWORD \
      --neo-auth=env:NEO_AUTH \
      --format html \
      export --path smell_report.html
    ```

- Best practices
  - Keep constructor args (e.g., `--config-file`, `--neo-data`) before the function; method args after
  - Return `dagger.File`/`dagger.Directory` to enable `export --path` via the CLI
  - Prefer `--mod <module-dir>` in CI/local so Dagger finds the correct module dagger.json
  - For Dagger Cloud, set `DAGGER_CLOUD_TOKEN` and call with `--cloud`

- Troubleshooting
  - “Cannot export”: ensure your function returns a `File` or `Directory` (not a string), then call with `export --path <dest>`
  - “Module not found”: run from the module dir or pass `--mod $GITHUB_WORKSPACE/<module-dir>`
  - “Login/token errors”: set `DAGGER_CLOUD_TOKEN` (or `DAGGER_TOKEN`) as a repo secret; we export it to the job in CI


### Filesystems (Python) examples

Return a file from a function and export to host:
```python
from dagger import function, dag

@function
async def build_report(self) -> dagger.File:
    content = "Hello from Dagger!\n"
    # Create a virtual directory, add a file, return it as dagger.File
    return (
        dag.directory()
          .with_new_file("out/report.txt", content)
          .file("out/report.txt")
    )
```
CLI (constructor-first + export subcommand):
```bash
dagger call --mod <module-dir> --config-file config.yaml build-report \
  export --path report.txt
```

Return a directory of results and export it:
```python
@function
async def build_bundle(self) -> dagger.Directory:
    d = (dag.directory()
          .with_new_file("bundle/a.txt", "A")
          .with_new_file("bundle/b.txt", "B"))
    # Return the sub-directory that contains the files
    return d.directory("bundle")
```
CLI:
```bash
dagger call --mod <module-dir> --config-file config.yaml build-bundle \
  export --path out-dir
```

Read host files and list entries:
```python
host_readme = dag.host().file("README.md")
text = await host_readme.contents()

root = dag.host().directory(".")
entries = await root.entries()  # list[str]
```

Mount a host directory into a container and produce output:
```python
@function
async def process_repo(self) -> dagger.File:
    src = dag.host().directory(".")
    c = (dag.container().from_("alpine:3.20")
           .with_mounted_directory("/src", src)
           .with_workdir("/src")
           .with_exec(["sh", "-lc", "mkdir -p out && echo ok > out/result.txt"]))
    return c.file("/src/out/result.txt")
```

Notes:
- Constructor args (e.g., --config-file, --neo-data) go before the function; method args after the function.
- To export to the host, your function must return dagger.File or dagger.Directory; then use the CLI export subcommand with --path.
- Prefer --mod <module-dir> in CI/local so Dagger finds the module’s dagger.json.
- Dagger Cloud: set DAGGER_CLOUD_TOKEN in repo secrets and use --cloud.

## Troubleshooting Dagger module errors
- Symptom: Error: module not found the commands need to be executed in the root folder containing the dagger.json file
- Cause: dagger call was run from the wrong directory (not the module containing dagger.json)
- Fix (local):
  - cd workflows/graph && dagger call build-graph-for-repository ...
  - or dagger call --mod workflows/graph build-graph-for-repository ...
- Fix (CI):
  - Set working-directory to the module directory, or
  - Use --mod $GITHUB_WORKSPACE/<module-dir>
- Quick preflight (optional):
  - test -f "$GITHUB_WORKSPACE/workflows/graph/dagger.json" || exit 1
  - test -f "$GITHUB_WORKSPACE/workflows/smell/dagger.json" || exit 1

Local examples:
- dagger call --mod workflows/graph build-graph-for-repository --repository-url=https://github.com/org/repo --branch=main
- dagger call --mod workflows/smell analyze-codebase --config-file=demo/agencyservices.yaml --neo-data=cache:neo4j-data

### GitHub Actions multiline outputs
- Symptom: Error: Invalid value. Matching delimiter not found '__EOF__'
- Cause: Mismatched/unterminated heredoc when writing to $GITHUB_OUTPUT
- Fix: Use a safe heredoc block and append in one group, e.g.:
```bash
{
  echo 'report<<EOF'
  cat smell_report.txt
  echo 'EOF'
} >> "$GITHUB_OUTPUT"
```

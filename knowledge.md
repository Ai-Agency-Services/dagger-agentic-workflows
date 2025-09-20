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

### Publish shared config to PyPI
- Workflow: .github/workflows/publish-config.yml
- Triggers: release published or manual dispatch
- Secret required: PYPI_TOKEN (PyPI API token)
- Manual run parameters:
  - publish: true (default)
  - version: optional sanity check against pyproject/__init__
- Steps:
  - Builds package in shared/dagger-agents-config
  - Validates version consistency
  - Uploads with twine to PyPI

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
- Text artifact (smell_report.txt) is exported for gating/parse
- skip_graph input: set to true in workflow_dispatch to run Smell only while troubleshooting
- fail_on_severity input: none|high|critical — optionally fail the job when HIGH/CRITICAL smells exist
- Job Summary: adds a short Markdown summary with repo/branch and artifact pointer
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

### Smell configuration (thresholds and detectors)
Add a smell block to your YAML (used by workflows/smell). Global thresholds apply to all languages; include/exclude lets you tune signal.

Example (demo):
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
- Detector names are class names (e.g., LongFunctionDetector). Case/spacing is normalized.
- If include is non-empty, only listed detectors run (minus any excluded).
- Threshold keys map directly to detectors wired in the Smell service.


### Dagger Filesystems (Python) quick reference

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

### Dagger Containers (Python SDK) quick reference

Start a container and run commands
```python
c = (dag.container().from_("alpine:3.20")
       .with_exec(["sh", "-lc", "echo hello world"]))
out = await c.stdout()  # "hello world\n"
```

Working directory and environment variables
```python
c = (dag.container().from_("alpine:3.20")
       .with_workdir("/work")
       .with_env_variable("APP_ENV", "dev")
       .with_exec(["sh", "-lc", "pwd && echo $APP_ENV"]))
```

Mount host files/directories into container
```python
host_dir = dag.host().directory(".")
c = (dag.container().from_("python:3.11-alpine")
       .with_mounted_directory("/src", host_dir)
       .with_workdir("/src")
       .with_exec(["python", "-c", "print('ok')"]))
```

Use caches (persist tool caches across runs)
```python
pip_cache = dag.cache_volume("pip-cache")
c = (dag.container().from_("python:3.11-alpine")
       .with_mounted_cache("/root/.cache/pip", pip_cache)
       .with_exec(["sh", "-lc", "pip install -q requests"]))
```

Secrets (inject without writing to disk)
```python
# assume you pass dagger.Secret into the function (e.g., token: dagger.Secret)
c = (dag.container().from_("alpine:3.20")
       .with_secret_variable("TOKEN", token)
       .with_exec(["sh", "-lc", "test -n \"$TOKEN\" && echo ok"]))
```

Return files/directories from a container
```python
c = (dag.container().from_("alpine:3.20")
       .with_exec(["sh", "-lc", "mkdir -p /out && echo report > /out/report.txt"]))
file_out = c.file("/out/report.txt")          # dagger.File
# Export via CLI: ... build-report export --path report.txt
```

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
dagger call --mod <module-dir> --config-file config.yaml build_report \
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
dagger call --mod <module-dir> --config-file config.yaml build_bundle \
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
- Dagger Cloud: set DAGGER_CLOUD_TOKEN in repo secrets and call with --cloud

#### Container entrypoint and args
```python
c = (dag.container().from_("alpine:3.20")
       .with_entrypoint(["/bin/sh","-lc"])   # override entrypoint
       .with_default_args(["-e"]))            # default args (appended when no args provided)
```

#### Mount a single host file
```python
readme = dag.host().file("README.md")
c = dag.container().from_("alpine:3.20").with_mounted_file("/work/README.md", readme)
```

#### Temporary directory shared across execs
```python
c = (dag.container().from_("alpine:3.20")
       .with_mounted_temporary_directory("/tmp/shared")
       .with_exec(["sh","-lc","echo hi > /tmp/shared/msg"]) 
       .with_exec(["sh","-lc","cat /tmp/shared/msg"]))
```

#### Streams & logs
```python
out = await c.stdout()   # capture stdout
err = await c.stderr()   # capture stderr
```

#### User switching
```python
c = dag.container().from_("alpine:3.20").with_user("1000:1000")
```

Reference: https://docs.dagger.io/cookbook/containers?sdk=python

Containers – FAQ (Python)
- How do I set entrypoint and default args?
  ```python
  c = (dag.container().from_("alpine:3.20")
         .with_entrypoint(["/bin/sh","-lc"])  # override entrypoint
         .with_default_args(["-e"]))           # args when none supplied
  ```
- How do I mount a single host file?
  ```python
  readme = dag.host().file("README.md")
  c = dag.container().from_("alpine:3.20").with_mounted_file("/work/README.md", readme)
  ```
- How do I share a temporary directory across multiple execs?
  ```python
  c = (dag.container().from_("alpine:3.20")
         .with_mounted_temporary_directory("/tmp/shared")
         .with_exec(["sh","-lc","echo hi > /tmp/shared/msg"]) 
         .with_exec(["sh","-lc","cat /tmp/shared/msg"]))
  ```
- How do I capture logs?
  ```python
  out = await c.stdout()
  err = await c.stderr()
  ```
- How do I switch users?
  ```python
  c = dag.container().from_("alpine:3.20").with_user("1000:1000")
  ```
- What’s the difference between host and container paths?
  - Paths inside `.with_exec()` are container filesystem paths.
  - Use `dag.host().file(...)` / `dag.host().directory(...)` for host paths and mount them.
- How do I persist artifacts from a container?
  - Select files/dirs: `c.file("/out/file")`, `c.directory("/out")`
  - Return them from the function as `dagger.File`/`dagger.Directory`
  - Export to host via CLI: `export --path <dest>`

Containers – Quick checklist (Python)
- Choose base image: `dag.container().from_("alpine:3.20")` (or language image)
- Set working dir if needed: `.with_workdir("/work")`
- Set environment: `.with_env_variable("NAME", "value")`
- Mount host content:
  - Directory: `.with_mounted_directory("/src", dag.host().directory("."))`
  - File: `.with_mounted_file("/work/README.md", dag.host().file("README.md"))`
  - Temporary dir: `.with_mounted_temporary_directory("/tmp/shared")`
- Run commands immutably: `.with_exec(["sh","-lc","your command"])` (chain returns new containers)
- Capture logs: `await c.stdout()` / `await c.stderr()`
- Persist artifacts: select `c.file("/out/file")` or `c.directory("/out")`; return from function to export with `export --path`
- Secrets: inject with `.with_secret_variable("TOKEN", token)` (not with_env_variable)
- Caches: mount cache volumes (`dag.cache_volume("pip-cache")`) for package managers
- Services: for networking between containers, turn containers into services with `.as_service()` and bind via `.with_service_binding()`
- Cloud auth (CI): set `DAGGER_CLOUD_TOKEN` and call with `--cloud`

Common gotchas (Containers)
- Immutability: every `.with_*` returns a new container; reuse the returned variable
- Wrong paths: create parent dirs or write under a mounted/known path; set `.with_workdir()` explicitly
- Missing tools: install before use (e.g., `apk add --no-cache curl bash`)
- Permissions: switch users with `.with_user("1000:1000")` after privileged steps; beware read-only mounts
- Large or noisy outputs: don’t stuff into GITHUB_OUTPUT; return dagger.File/Directory and use `export --path`
- Host vs container FS: paths inside `.with_exec()` are container paths; use `dag.host()` for host files/dirs
- Module resolution: run from module dir or pass `--mod <module-dir>` so Dagger finds dagger.json

Containers – Artifact selection & transfer
```python
# Select artifacts from a container filesystem
c = (dag.container().from_("alpine:3.20")
       .with_exec(["sh","-lc","mkdir -p /out && echo data > /out/a.txt && mkdir -p /out/sub && echo b > /out/sub/b.txt"]))
file_a = c.file("/out/a.txt")           # dagger.File
subdir = c.directory("/out/sub")        # dagger.Directory

# Move artifacts between containers using rootfs()
builder = (dag.container().from_("alpine:3.20")
             .with_exec(["sh","-lc","mkdir -p /build && echo bin > /build/app"]))
# Mount builder rootfs into a second container for post-processing
packager = (dag.container().from_("alpine:3.20")
              .with_mounted_directory("/builder", builder.rootfs())  # read-only snapshot
              .with_exec(["sh","-lc","mkdir -p /out && cp /builder/build/app /out/app.tar"]))
app_pkg = packager.file("/out/app.tar")
```

Containers – Deterministic pipelines & immutability
- Each `.with_*` returns a new immutable container; always reassign the variable (e.g., `c = c.with_exec(...)`).
- Keep layers small and deterministic; install tools before copying source to maximize cache reuse.
- Prefer explicit workdirs (`.with_workdir(...)`) and fully-qualified paths in `.with_exec(...)`.

Containers – Debug tips
- Inspect filesystem state:
  ```python
  c = c.with_exec(["sh","-lc","pwd && ls -la"])
  logs = await c.stdout()
  ```
- Print environment quickly:
  ```python
  c = c.with_exec(["sh","-lc","env | sort | sed -n '1,80p'"])
  ```
- Verify tools and network:
  ```python
  c = c.with_exec(["sh","-lc","apk add --no-cache curl || true && curl -fsS https://example.com || true"])
  ```

Containers – Exit/fail patterns
```python
# Use strict shell options so any failing command fails the step
c = (dag.container().from_("alpine:3.20")
       .with_exec(["sh","-lc","set -euo pipefail; your_cmd_1; your_cmd_2"]))
# Alternatively, explicitly guard each command
c = c.with_exec(["sh","-lc","your_cmd || { echo 'failed'; exit 1; }"])
```

Containers – Networking & Ports
```python
# Expose a port in a standalone container (useful when turning into a service later)
web = dag.container().from_("nginx:alpine").with_exposed_port(80)
# For inter-container networking, prefer services + bindings (see Services cookbook)
```

Containers – Env, Labels, Workdir
```python
c = (dag.container().from_("alpine:3.20")
       .with_workdir("/work")
       .with_env_variable("APP_ENV", "dev")
       .with_label("org.example.component", "smell-workflow"))
```

Containers – File vs Directory mounts (cheat sheet)
- Single file: `.with_mounted_file("/dst/file.txt", dag.host().file("./src/file.txt"))`
- Directory: `.with_mounted_directory("/dst", dag.host().directory("./src"))`
- Temp dir: `.with_mounted_temporary_directory("/tmp/shared")`
- Host vs container: paths in `.with_exec()` are container FS; use `dag.host()` for host FS

Containers – Exec chaining reminders
- Every `.with_*` returns a new immutable container. Always reassign:
  ```python
  c = dag.container().from_("alpine:3.20")
  c = c.with_exec(["sh","-lc","apk add --no-cache curl"])  # reassign
  c = c.with_exec(["sh","-lc","curl -fsS https://example.com > /out/index.html"])  # reassign
  artifact = c.file("/out/index.html")
  ```

Containers – Cookbook link
- Full guide: https://docs.dagger.io/cookbook/containers?sdk=python

### Dagger Secrets (Python SDK) quick reference

Set secrets (local/engine):
- CLI (engine-scoped):
  ```bash
  dagger secret set GH_PAT
  # then paste your token; or:
  printf '%s' "$GITHUB_TOKEN" | dagger secret set GH_PAT
  ```
- GitHub Actions: add repository/org secrets (e.g., GH_PAT, DAGGER_CLOUD_TOKEN, NEO4J_PASSWORD, NEO4J_AUTH)

Pass secrets to functions (CLI):
- You can reference secrets in three ways:
  - From engine secret store: `--token=secret:GH_PAT`
  - From environment: `--token=env:GH_PAT`
  - From file: `--token=file:./path/to/secret.txt`

Python (inject secrets safely into containers):
```python
from dagger import function, dag
import dagger

@function
async def use_secret(self, token: dagger.Secret) -> str:
    # Prefer with_secret_variable so it never writes to disk
    c = (dag.container().from_("alpine:3.20")
           .with_secret_variable("TOKEN", token)
           .with_exec(["sh", "-lc", "test -n \"$TOKEN\" && echo ok || echo missing && exit 1"]))
    return await c.stdout()
```

In our workflows (examples):
- Graph build (remote clone):
  ```bash
  dagger call --cloud --mod workflows/graph \
    --config-file demo/agencyservices.yaml \
    build-graph-for-repository \
    --github-access-token=env:GH_PAT \
    --repository-url https://github.com/org/repo \
    --branch main \
    --neo-auth=env:NEO_AUTH \
    --neo-password=env:NEO4J_PASSWORD
  ```
- Smell report (export HTML):
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

Best practices
- Never print secrets; rely on with_secret_variable to keep them out of layers/logs
- Prefer passing via CLI as `env:NAME` (from CI secrets) or `secret:NAME` (engine secrets)
- Avoid writing secrets to disk (inside container or on host). If a file is unavoidable, ensure it’s ephemeral and never committed/exported
- Dagger Cloud: set DAGGER_CLOUD_TOKEN (or DAGGER_TOKEN) as a repo secret and run with `--cloud`
- In CI, mask secrets automatically; never echo values

Troubleshooting
- "Invalid token type" when using `--cloud`: ensure DAGGER_CLOUD_TOKEN is a Dagger Cloud session token, not a platform PAT
- "please run dagger login <org>": missing token; set DAGGER_CLOUD_TOKEN in repo secrets (we export it to the job in CI)

### Dagger Builds (Python SDK) quick reference

Build from host directory (Dockerfile in context)
```python
context = dag.host().directory(".")
img = dag.container().build(context)  # build Dockerfile in context
```

Build from subdirectory
```python
repo = dag.host().directory(".")
context = repo.directory("apps/service")
img = dag.container().build(context)
```

Build from a Git repository
```python
src = dag.git("https://github.com/org/repo").branch("main").tree()
context = src.directory("")  # repo root
img = dag.container().build(context)
```

Extract artifacts from the built image
```python
artifact_file = img.file("/app/out/report.txt")
artifact_dir  = img.directory("/app/out")
```

Publish the image (returns image ref/digest)
```python
ref = await img.publish("ttl.sh/your-image:1h")
```

Post-process build output with a second container (read-only rootfs)
```python
context = dag.host().directory(".")
img = dag.container().build(context)
processed = (dag.container().from_("alpine:3.20")
              .with_mounted_directory("/imgfs", img.rootfs())
              .with_exec(["sh", "-lc", "cp /imgfs/app/out/report.txt /out/report.txt"]))
file_out = processed.file("/out/report.txt")
```

Best practices
- Keep Dockerfile close to build context; use subdirectory contexts when appropriate
- Builds are cached/immutable; keep layers focused for fast incremental rebuilds
- Return dagger.File/Directory to enable artifact export via `export --path`
- Use Git contexts (`dag.git(...).branch(...).tree()`) for reproducible builds
- Combine with Filesystems/Containers/Secrets for mounts, caches, and secret-injection

Reference: https://docs.dagger.io/cookbook/builds?sdk=python

Quick checklist
- Pick a build context:
  - Host: `context = dag.host().directory(".")` or a subdir `repo.directory("apps/svc")`
  - Git: `context = dag.git("https://github.com/org/repo").branch("main").tree().directory("")`
- Keep Dockerfile near context; minimize context size (use subdir context)
- Extract artifacts from built image via `img.file(...)` / `img.directory(...)`
- Export artifacts to host: return `dagger.File`/`dagger.Directory` and use CLI `export --path <dest>`
- Publish images when needed: `await img.publish("ttl.sh/your-image:1h")`

Advanced topics
- Pin Git context to a specific commit for reproducibility:
  - `dag.git("https://github.com/org/repo").commit("<sha>").tree()` (or use branch/tag as needed)
- Multi-stage Dockerfiles:
  - Build once, then extract artifacts from the final/target stage via `img.file(...)` or `img.directory(...)`
  - If needed, mount `img.rootfs()` into a second container for post-processing
- Build args and target stages:
  - Pass build-time args and optionally target a stage (see Python SDK `container.build` parameters in the docs)
  - Pattern: keep ARGs near usage; small layers improve cache hits
- Reuse build outputs:
  - Mount `img.rootfs()` read-only into another container to copy out files or run validations
- Caching:
  - BuildKit cache is leveraged by default; keep layers focused and deterministic
  - Prefer dependency install before copying source where possible to maximize cache reuse
- Context selection:
  - Use subdirectory contexts to avoid sending large roots: `dag.host().directory(".").directory("apps/svc")`
- Multi-platform images:
  - If registry supports it, publish multi-arch images (check Python SDK options for `platforms` support)
- Export artifacts to host:
  - Return dagger.File/Directory from your function and use CLI `export --path <dest>`
- Combine with Filesystems/Containers/Secrets for mounts, caches, and secret-injection

#### Build parameters (Python)

Common `container.build` options (Python SDK):
```python
context = dag.host().directory(".")
img = dag.container().build(
    context,
    dockerfile="Dockerfile",          # optional alternative path
    target="final",                   # target stage in multi-stage Dockerfile
    build_args={"VERSION": "1.2.3"}, # ARGs passed at build-time
    # platforms=["linux/amd64", "linux/arm64"],  # if supported/published
    build_contexts={                  # additional named contexts (FROM --mount=type=bind,source=context://deps,...)
        "deps": dag.host().directory("./deps")
    }
)
```
Notes:
- Keep ARGs near their usage to maximize cache reuse.
- Prefer small, deterministic layers; install deps before copying the app to improve cache hits.
- Use subdirectory contexts to avoid shipping large roots.
- Combine with Filesystems/Containers/Secrets: mount host dirs, inject secrets via `with_secret_variable`, and use cache volumes for package managers.

#### Build troubleshooting
- Dockerfile not found / wrong path
  - Error: "failed to find a Dockerfile" or similar
  - Fix: ensure Dockerfile is within the selected build context, or pass `dockerfile="Dockerfile"` (alternate path supported) when calling `container.build()`.
- `failed to solve`: process "/bin/sh -c ..." returned non-zero
  - Cause: command in a Dockerfile layer failed (missing tools, bad path, network issues)
  - Fix: check the layer order, verify tools are installed (`apk/apt`), and inspect logs; run the same commands in a dev container first.
- Network errors during build (e.g., pip/npm timeouts)
  - Fix: retry or add mirrors; keep dependency layers cached (install deps before copying app code to maximize cache hits).
- Context too large / slow builds
  - Fix: build from a subdirectory context (e.g., `repo.directory("apps/svc")`) to avoid shipping the entire repo to build.
- Permission denied during COPY/RUN
  - Fix: run as root during build or adjust ownership/permissions (`chown --from`, `--chown=...` on COPY if supported), or `with_user("1000:1000")` after privileged steps.
- Platform mismatch
  - Symptom: image runs locally but not on target arch
  - Fix: publish multi-arch (if supported) or build for a specific `platforms=[...]` set; ensure base image supports the target arch.
- Git auth and repo URLs
  - Error: auth required, 404
  - Fix: use public repos, or add auth (e.g., `--github-access-token=env:GH_PAT` for private repos) and confirm branch/commit exists.
- Build ARGs not set
  - Error: `ARG NAME not set`
  - Fix: pass `build_args={"NAME": "value"}` and keep ARGs near usage for cache efficiency.
- OOM / disk space
  - Fix: reduce layer sizes, clear caches, split the build, or increase runner resources. Prefer smaller base images.

Reference: https://docs.dagger.io/cookbook/builds?sdk=python

### Dagger Services (Python SDK) quick reference

Start a service (e.g., Postgres):
```python
pg = (dag.container().from_("postgres:16")
        .with_env_variable("POSTGRES_PASSWORD", "pass")
        .with_exposed_port(5432)
        .as_service())
```

Multiple services (compose-like pattern):
```python
redis = dag.container().from_("redis:7").with_exposed_port(6379).as_service()
api = (
  dag.container().from_("python:3.11-alpine")
    .with_service_binding("redis", redis)  # DB available inside client
    .with_exec(["sh", "-lc", "apk add --no-cache curl && curl -fsS http://redis:6379 || true"])  # sample check
)
```

Optional: get a service endpoint URL (if your SDK exposes one):
```python
# Some SDKs expose an endpoint helper; if present:
# url = await pg.endpoint()   # e.g., "tcp://<host>:<port>"
# Otherwise, prefer with_service_binding and access by bound host name inside a client container.
```

Inject secrets safely into services/clients:
```python
# token: dagger.Secret passed into your function
svc = (dag.container().from_("alpine:3.20")
        .with_secret_variable("TOKEN", token)
        .with_exposed_port(8080)
        .as_service())
client = (dag.container().from_("postgres:16")
            .with_service_binding("db", pg)  # service available at host "db" inside client
            .with_exec(["sh", "-lc", "pg_isready -h db -p 5432 || exit 1"]))
```

Health checks and readiness strategies:
- Use app-native probes (e.g., `pg_isready`, `curl -fsS http://svc/health`)
- Add retries with small sleeps, or loop until the port is open
- Keep the service reference in-scope while clients run (services stop when the run ends)

Tips for services:
- Always expose required ports (`.with_exposed_port(port)`) before `.as_service()`
- Bind into clients with `.with_service_binding("name", service)` and use `name` as the hostname inside client containers
- For multiple services, bind each with a distinct name (`db`, `cache`, `broker`, ...)
- Prefer runtime readiness checks (curl/pg_isready) over fixed sleeps
- Inject secrets via `.with_secret_variable()` to avoid writing secrets to disk
- Use cache volumes (e.g., for package managers) to speed up client/service setup work

#### Extended service patterns (Python)
- Chaining multiple clients against the same service
  ```python
  db = (dag.container().from_("postgres:16")
           .with_env_variable("POSTGRES_PASSWORD","pass")
           .with_exposed_port(5432)
           .as_service())

  migrator = (dag.container().from_("postgres:16")
                .with_service_binding("db", db)
                .with_exec(["sh","-lc","psql postgresql://postgres:pass@db:5432 -c 'select 1' "]))

  app = (dag.container().from_("python:3.11-alpine")
           .with_service_binding("db", db)
           .with_exec(["sh","-lc","apk add --no-cache curl && echo 'app ready' "]))
  ```

- Readiness loops (client-side) – prefer app-native probes over sleeps
  ```python
  web = dag.container().from_("nginx:alpine").with_exposed_port(80).as_service()
  smoke = (dag.container().from_("alpine:3.20")
             .with_service_binding("web", web)
             .with_exec(["sh","-lc",
               "for i in $(seq 1 60); do wget -qO- http://web || sleep 1; done"])
          )
  ```

- Mount host data into a service (e.g., seed files) and probe via client
  ```python
  seeds = dag.host().directory("./seed")
  svc = (dag.container().from_("alpine:3.20")
           .with_mounted_directory("/seed", seeds)
           .with_exposed_port(8080)
           .as_service())
  probe = (dag.container().from_("alpine:3.20")
             .with_service_binding("svc", svc)
             .with_exec(["sh","-lc","wget -qO- http://svc:8080 || true"]))
  ```

- Secrets in services and clients – never write to disk
  ```python
  api_key: dagger.Secret
  svc = (dag.container().from_("alpine:3.20")
           .with_secret_variable("API_KEY", api_key)
           .with_exposed_port(8080)
           .as_service())

  client = (dag.container().from_("alpine:3.20")
              .with_service_binding("svc", svc)
              .with_exec(["sh","-lc","wget -qO- http://svc:8080/health || true"]))
  ```

- Service lifetime
  - Services exist for the duration of the pipeline run; keep a reference to the service while clients execute.
  - When the run ends, services stop automatically.

#### Common gotchas (services)
- Port not reachable in client
  - Ensure `.with_exposed_port(PORT)` is called on the service container before `.as_service()`.
  - In the client, bind the service with `.with_service_binding("name", service)` and use `name` as the hostname.
- Name resolution issues
  - The hostname inside the client is exactly the binding name you provided (e.g., `db`, `cache`, `svc`).
- Readiness
  - Avoid fixed sleeps; curl/pg_isready loops are more reliable.
- Secrets
  - Use `.with_secret_variable()` for in-memory env injection; avoid `with_env_variable` for secrets.
- Logs
  - Read `stdout/stderr` from client execs (e.g., `await client.stdout()`); services themselves are long-lived, so probe via clients.

Reference: https://docs.dagger.io/cookbook/services?sdk=python

### Dagger Errors (Python SDK) quick reference

Engine/Cloud auth
- Errors: "please run `dagger login <org>` first", "invalid token type", "failed to provision a remote Engine"
  - Cause: Missing or wrong Dagger Cloud token
  - Fix: Set repo secret DAGGER_CLOUD_TOKEN (or DAGGER_TOKEN). In CI, export it as env DAGGER_CLOUD_TOKEN and call with --cloud.
  - Preflight (CI):
    ```bash
    test -n "$DAGGER_CLOUD_TOKEN" || { echo 'Set DAGGER_CLOUD_TOKEN'; exit 1; }
    ```

Module not found / wrong module
- Errors: "module not found", "commands need to be executed in the root folder containing the dagger.json file"
  - Cause: Running dagger call outside module directory
  - Fix: cd into the module dir, or pass --mod $GITHUB_WORKSPACE/<module-dir>
  - Preflight (CI):
    ```bash
    test -f "$GITHUB_WORKSPACE/workflows/graph/dagger.json" || exit 1
    ```

Constructor args vs method args
- Errors: "required flag(s) 'config-file' not set", "unknown flag"
  - Cause: Flags ordered after the function when they are constructor arguments
  - Fix: Constructor args (e.g., --config-file, --neo-data) come BEFORE the function; method args after
  - Example:
    ```bash
    dagger call --mod workflows/smell \
      --config-file demo/agencyservices.yaml \
      --neo-data ./tmp/neo4j-data \
      analyze-codebase \
      --github-access-token=env:GITHUB_TOKEN
    ```

Exporting artifacts to host
- Errors: "Cannot export" or GHA delimiter failures
  - Cause: Function returns a string instead of dagger.File/Directory, or using GITHUB_OUTPUT for large/multiline content
  - Fix: Return dagger.File/Directory and use export subcommand
  - Example:
    ```bash
    dagger call --mod workflows/smell \
      --config-file demo/agencyservices.yaml \
      --neo-data ./tmp/neo4j-data \
      analyze-codebase-export \
      --format html \
      export --path smell_report.html
    ```

OCI filesystem path semantics (neo-data)
- Symptom: Smell cannot see Graph’s DB or path mismatch
  - Cause: The path is inside the OCI container; must match across steps
  - Fix: Use the same in-container path for --neo-data in both steps (e.g., ./tmp/neo4j-data)

Secrets
- Issues: Missing secrets, leaked secrets in logs, secret not visible in container
  - Use with_secret_variable (not with_env_variable) for injection inside containers
  - Pass secrets via env:NAME, secret:NAME, or file:path
  - Example:
    ```python
    c = dag.container().from_("alpine:3.20").with_secret_variable("TOKEN", token)
    ```

Services/networking
- Issues: Client cannot reach service, ports not exposed
  - Fix: Use `.as_service()`, `.with_service_binding("name", service)`, expose ports if needed
  - Example:
    ```python
    db = dag.container().from_("postgres:16").with_env_variable("POSTGRES_PASSWORD","pass").with_exposed_port(5432).as_service()
    client = dag.container().from_("postgres:16").with_service_binding("db", db).with_exec(["sh","-lc","pg_isready -h db -p 5432"]) 
    ```

GHA multiline output errors
- Error: "Invalid value. Matching delimiter not found 'EOF'"
  - Fix: Avoid GITHUB_OUTPUT for big content; export artifact with export --path or upload as artifact

## GitHub Actions multiline outputs
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

# Dagger Agents Knowledge Base (Synced)

## Quick Start

Build Graph (remote clone):
```bash
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  --neo-data ./tmp/neo4j-data \
  build-graph-for-repository \
  --github-access-token=env:GITHUB_TOKEN \
  --repository-url https://github.com/org/repo.git \
  --branch main \
  --neo-auth=env:NEO4J_AUTH \
  --neo-password=env:NEO4J_PASSWORD \
  --open-router-api-key=env:OPENROUTER_API_KEY
```

Analyze Smells (HTML export):
```bash
dagger call --cloud --mod workflows/smell \
  --config-file demo/agencyservices.yaml \
  --neo-data ./tmp/neo4j-data \
  analyze-codebase-export \
  --github-access-token=env:GITHUB_TOKEN \
  --neo-password=env:NEO4J_PASSWORD \
  --neo-auth=env:NEO4J_AUTH \
  --format html \
  export --path smell_report.html
```

Attached Directory (Graph only):
```bash
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  --neo-data ./tmp/neo4j-data \
  build-graph-for-directory \
  --github-access-token=env:GITHUB_TOKEN \
  --local-path /absolute/path/to/target-repo \
  --neo-auth=env:NEO4J_AUTH \
  --neo-password=env:NEO4J_PASSWORD
```

## Dagger CLI quick reference (constructor-first order)

- Constructor args (e.g., --config-file, --neo-data) come before the function
- Method args (function params) come after the function
- Run from module dir or pass --mod <module-dir>
- Export to host via export --path (function must return dagger.File/Directory)

Examples:
```bash
# Smell (HTML export)
dagger call --cloud --mod workflows/smell \
  --config-file demo/agencyservices.yaml \
  --neo-data ./tmp/neo4j-data \
  analyze-codebase-export \
  --github-access-token=env:GITHUB_TOKEN \
  --neo-password=env:NEO4J_PASSWORD \
  --neo-auth=env:NEO4J_AUTH \
  --format html \
  export --path smell_report.html

# Graph (remote clone)
dagger call --cloud --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  --neo-data ./tmp/neo4j-data \
  build-graph-for-repository \
  --github-access-token=env:GITHUB_TOKEN \
  --repository-url https://github.com/org/repo.git \
  --branch main \
  --neo-auth=env:NEO4J_AUTH \
  --neo-password=env:NEO4J_PASSWORD
```

## Smell Graph Report

- Artifacts: smell_report.html (HTML) and smell_report.txt (text)
- Inputs:
  - skip_graph: true to run Smell-only (fast troubleshooting)
  - fail_on_severity: none|high|critical to fail on HIGH/CRITICAL smells
- Job Summary: short Markdown summary with artifact pointer
- PR comment: links back to the run and artifacts
- Dagger Cloud: set DAGGER_CLOUD_TOKEN and use --cloud

## Smell configuration (thresholds and detectors)

Add a smell block in your YAML used by workflows/smell:
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
- Detector names are class names (normalized); if include is non-empty, only those run (minus excluded)

## Dagger Filesystems (Python SDK) quick reference

- Host access: `dag.host().directory("./path")`, `dag.host().file("./f.txt")`
- In-pipeline: `dag.directory().with_new_file("out/a.txt","A").file("out/a.txt")`
- Mount into container: `.with_mounted_directory("/work", dag.host().directory("."))`
- Return artifacts: return dagger.File/Directory and export with `export --path`
- Read: `await file.contents()`, `await directory.entries()`

## Dagger Containers (Python SDK) quick reference

- Start/run: `(dag.container().from_("alpine:3.20").with_exec(["sh","-lc","echo ok"]))`
- Workdir/env: `.with_workdir("/work").with_env_variable("APP_ENV","dev")`
- Mounts: dir/file/temp dir; secrets via `.with_secret_variable("TOKEN", token)`
- Immutability: every `.with_*` returns a new container; reassign each step
- Debug: `await c.stdout()/stderr()`, `pwd && ls -la`, `env | sort`
- Exit/fail: `set -euo pipefail; step1; step2`

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
Tips: expose ports before `.as_service()`, bind via `.with_service_binding("name", svc)`, use app-native readiness

## Dagger Builds (Python SDK) quick reference

- Host context: `img = dag.container().build(dag.host().directory("."))`
- Git context: `img = dag.container().build(dag.git("https://...").branch("main").tree().directory(""))`
- Extract: `img.file("/app/out/report.txt")` then export
- Publish: `await img.publish("ttl.sh/your-image:1h")`

## Dagger Secrets (Python SDK) quick reference

- CLI sources: `secret:NAME`, `env:NAME`, `file:./path`
- Inject: `.with_secret_variable("TOKEN", token)` (avoid writing to disk)

## Dagger Errors (Python SDK) quick reference

- Cloud auth: set DAGGER_CLOUD_TOKEN; use --cloud
- Module not found: run from module dir or pass --mod <module-dir>
- Constructor vs method: constructor first, then function, then method args
- Export errors: return File/Directory; use `export --path`
- GHA multiline output: avoid writing big content to GITHUB_OUTPUT—export artifacts instead
- Debug: `await c.stdout()/stderr()`, Dagger Cloud trace URL, `DAGGER_LOG_LEVEL=debug`

## CI Workflows

### Smell Graph Report
- Artifacts: HTML + text
- Inputs: skip_graph, fail_on_severity
- Job Summary and optional PR comment

### Publish shared config to PyPI
- Workflow: .github/workflows/publish-config.yml
- Triggers: release published, manual dispatch, tags (config-v* / ais-dagger-agents-config-*)
- Secret: PYPI_TOKEN

### Unit Tests (develop)
- Matrix across modules; per-module uv sync
- Runs tests not marked integration/neo4j/llm/dagger/slow
- PYTHONPATH is set to repo root for consistent imports

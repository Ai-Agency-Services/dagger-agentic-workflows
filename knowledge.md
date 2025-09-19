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

Important: Run dagger calls from the module directory that contains its dagger.json (e.g., workflows/graph, workflows/smell) or pass --mod <module-dir>. In CI, either set working-directory or use --mod $GITHUB_WORKSPACE/<module-dir>. Also ensure repo URLs are unquoted (e.g., https://github.com/org/repo without quotes).

```bash
# Build and test an agent
dagger call --mod <module-dir> --config-file=config.yaml create

# Run complete feature development
dagger call --mod agents/codebuff \
  --config-file config.yaml \
  orchestrate-feature-development \
  --task-description="Feature description" \
  --openai-api-key=env:OPENAI_API_KEY

# Analyze codebase
dagger call --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-repository \
  --repository-url https://github.com/user/repo

# Generate tests with coverage
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
- See .github/workflows/smell-graph.yml for running Graph + Smell against:
  - remote mode (repository_url/branch)
  - attached mode (checkout external repo to path and analyze)
- Posts a PR comment with a detailed report and GitHub links (if configured)

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

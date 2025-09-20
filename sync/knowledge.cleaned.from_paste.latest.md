# Dagger Agents Knowledge Base

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
- Comprehensive test fixtures in `tests/conftest.py` (or shared plugin)
- Custom markers: `unit`, `integration`, `neo4j`, `llm`, `dagger`, `slow`

### Running Tests
```bash
# Install deps
make install

# Run all unit tests
make test-unit

# Run integration tests
make test-integration

# Coverage (repo root)
make test-coverage

# Short names
make test-neo
make test-query
make test-codebuff
make test-graph
make test-smell
make test-cover
make test-builder

# Full path names
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

# Neo4j-required
make test-neo4j

# LLM-required
make test-llm

# Runner
python scripts/run_tests.py --type unit --module neo
```

## Common Commands (constructor-first order)

```bash
# Build and test an agent (constructor-first + --mod)
dagger call --mod <module-dir> --config-file=config.yaml create

# Feature development (constructor-first + --mod)
dagger call --mod agents/codebuff \
  --config-file config.yaml \
  orchestrate-feature-development \
  --task-description="Feature description" \
  --openai-api-key=env:OPENAI_API_KEY

# Build code graph from a repository (constructor-first + --mod)
dagger call --mod workflows/graph \
  --config-file demo/agencyservices.yaml \
  build-graph-for-repository \
  --repository-url https://github.com/user/repo

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

# Dagger Agents Config Shared Module Knowledge

## Purpose
Provides centralized configuration management for all Dagger agents using Pydantic models and YAML configuration files.

## Architecture

### Core Models: `YAMLConfig`
- **Structured Configuration**: Pydantic validation for all settings
- **Type Safety**: Strong typing for configuration parameters
- **Default Values**: Sensible defaults for all optional settings
- **Validation**: Runtime validation of configuration correctness

## Configuration Models

### TestingConfig (new)
Use to control how tests are detected/run by agents (e.g., Implementation step):

```yaml
testing:
  enable: true
  working_dir: apps/api          # optional subdir
  test_command: pnpm test --filter api
  install_command: pnpm install --frozen-lockfile
  timeout_seconds: 900
```

- Fields:
  - enable: toggle tests on/off
  - working_dir: run tests from this directory
  - test_command: exact shell command to run tests
  - install_command: pre-test install command
  - timeout_seconds: override test run timeout

Agents can read config.testing to shape detection/configuration and test command selection.



### Core Configuration

Note: container and git now have safe defaults so minimal YAML files do not fail validation. You can still override all fields.

- **`LLMCredentials`**: API keys and provider settings
- **`ContainerConfig`**: Docker and runtime environment settings
- **`GitConfig`**: Version control and repository settings
- **`CoreAPIConfig`**: Default LLM provider and model settings

### Workflow-Specific
- **`IndexingConfig`**: File processing and embedding settings
- **`ConcurrencyConfig`**: Parallel processing limits
- **`TestGenerationConfig`**: Test automation settings
- **`ReporterConfig`**: Coverage analysis settings
- **`Neo4jConfig`**: Graph database connection settings

## Configuration Structure

### Complete YAML Example
```yaml
# Container environment
container:
  work_dir: "/app"
  docker_file_path: "./Dockerfile"

# Git settings
git:
  user_name: "AI Assistant"
  user_email: "ai@example.com"
  base_pull_request_branch: "main"

# Default LLM settings
core_api:
  model: "openai/gpt-4o"
  provider: "openai"

# Neo4j database
neo4j:
  uri: "neo4j://localhost:7687"
  username: "neo4j"
  database: "neo4j"

# File processing
indexing:
  batch_size: 50
  max_concurrent: 5
  embedding_batch_size: 100
  file_extensions: ["py", "js", "ts"]

# Performance settings
concurrency:
  max_concurrent: 3

# Integration settings
integration:
  cache_enabled: true
  cache_ttl: 3600
  parallel_processing: true
  embedding_dimension: 1536

# Coverage analysis
reporter:
  framework: "pytest"
  coverage_threshold: 80
```

## Model Definitions

### `LLMCredentials`
```python
class LLMCredentials(BaseModel):
    base_url: Optional[str] = None
    api_key: str
```

### `ContainerConfig`
```python
class ContainerConfig(BaseModel):
    work_dir: str = "/app"
    docker_file_path: str = "./Dockerfile"
```

### `GitConfig`
```python
class GitConfig(BaseModel):
    user_name: str
    user_email: str
    base_pull_request_branch: str = "main"
```

### `IndexingConfig`
```python
class IndexingConfig(BaseModel):
    batch_size: int = 50
    max_concurrent: int = 5
    embedding_batch_size: int = 100
    file_extensions: List[str] = ["py", "js", "ts"]
```

## Validation Features

### Type Safety
- Automatic type conversion and validation
- Required field enforcement
- Optional field defaults
- Custom validator methods

### Configuration Validation
```python
# Load and validate configuration
config = YAMLConfig(**yaml_data)

# Access validated settings
max_concurrent = config.concurrency.max_concurrent
model_name = config.core_api.model
```

### Error Handling
- Clear validation error messages
- Field-specific error reporting
- Type mismatch detection
- Missing required field identification

## Usage Patterns

### Configuration Loading
```python
# From YAML file
with open("config.yaml") as f:
    yaml_data = yaml.safe_load(f)
config = YAMLConfig(**yaml_data)

# In Dagger agents
config_str = await config_file.contents()
config_dict = yaml.safe_load(config_str)
config = YAMLConfig(**config_dict)
```

### Setting Access
```python
# Safe access with defaults
max_concurrent = getattr(config.concurrency, 'max_concurrent', 3)

# Direct access (validated)
batch_size = config.indexing.batch_size
model = config.core_api.model
```

## Default Values

### Performance Defaults
- Concurrency: 3 concurrent operations
- Batch size: 50 items per batch
- Embedding batch: 100 embeddings per API call
- Cache TTL: 3600 seconds (1 hour)

### LLM Defaults
- Provider: "openai"
- Model: "gpt-4o" for complex tasks, "gpt-4o-mini" for simple tasks
- Embedding dimension: 1536 (OpenAI standard)

## SDK Integration

### Dagger Module Support
- Configuration loading in all modules
- Type-safe parameter passing
- Consistent error handling
- Documentation generation

### Python SDK Features
- Pydantic model integration
- Async/await support
- Container orchestration
- Secret management

## Testing
- Unit tests: `shared/dagger-agents-config/tests/`
- Validation tests for all model types
- YAML parsing error scenarios
- Default value verification

## Common Configuration Patterns

### Development Environment
```yaml
container:
  work_dir: "/workspace"
  docker_file_path: "./dev.Dockerfile"
concurrency:
  max_concurrent: 1  # Conservative for development
```

### Production Environment
```yaml
concurrency:
  max_concurrent: 10
indexing:
  batch_size: 100
integration:
  cache_enabled: true
  parallel_processing: true
```

### Testing Environment
```yaml
neo4j:
  uri: "neo4j://localhost:7687"
  username: "neo4j"
  database: "test"
integration:
  cache_enabled: false
```

## Integration Points
- **All Dagger Modules**: Configuration loading and validation
- **Agent Orchestration**: Settings for agent coordination
- **Database Connections**: Connection parameter management
- **Performance Tuning**: Resource allocation settings

## Extension Guidelines

### Adding New Config Sections
1. Define Pydantic model with validation
2. Add to `YAMLConfig` as optional field
3. Provide sensible defaults
4. Document usage patterns
5. Add validation tests

### Model Best Practices
- Use descriptive field names
- Provide helpful docstrings
- Include validation constraints
- Define reasonable defaults
- Handle optional configurations gracefully

## Dependencies
- **Pydantic**: Data validation and settings management
- **YAML**: Configuration file parsing
- **Dagger SDK**: Integration with Dagger modules

## Code Map Configuration

Add a `code_map` block to your YAML to drive shared/code-map defaults.

```yaml
code_map:
  out_dir: .code-map
  ignore_dirs: [".git", "node_modules", "__pycache__", ".venv", "dist", "build"]
  max_file_size: 1000000
  languages: ["python", "javascript", "typescript"]
```

- Fields (CodeMapConfig):
  - out_dir: where map.json, files.jsonl, symbols.jsonl, chunks.jsonl are written
  - ignore_dirs: directory names to skip when scanning
  - max_file_size: maximum bytes per file
  - languages: language IDs to parse

Consumers can call constructor-first and let defaults flow:
```python
code_map = await dag.code_map().with_config(config)
map_dir = await code_map.build(source_dir=container.directory("."))
```

## Troubleshooting

### Configuration Errors
- Check YAML syntax and structure
- Verify required fields are present
- Validate data types match model definitions
- Review field names for typos

### Validation Failures
- Read Pydantic error messages carefully
- Check field constraints and limits
- Verify nested object structure
- Ensure all required configurations present

### Integration Issues
- Confirm configuration model versions match
- Check import paths in dependent modules
- Verify configuration file accessibility
- Review secret and parameter passing
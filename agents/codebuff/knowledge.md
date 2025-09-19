# Codebuff Agent Module Knowledge

## Purpose
Multi-agent orchestrator that replicates Codebuff's AI-powered development workflow, from code exploration to feature implementation to pull request creation.

## Architecture

### Core Class: `Codebuff`
- **Agent Orchestration**: Coordinates specialized AI agents
- **LLM Management**: Handles multiple providers (OpenAI, OpenRouter)
- **Workflow Automation**: End-to-end feature development
- **Environment Setup**: Container and repository management

### Specialized Agents
- **File Explorer**: Scans and maps codebase structure
- **File Picker**: Selects relevant files for tasks
- **Thinker**: Creates detailed implementation plans
- **Implementation**: Executes code changes
- **Reviewer**: Validates changes and provides feedback
- **Context Pruner**: Manages conversation context size

## Core Workflow

### Complete Feature Development
```python
codebuff = await Codebuff.create(config_file)
result = await codebuff.orchestrate_feature_development(
    github_token=github_token,
    task_description="Add user authentication",
    repo_url="https://github.com/user/repo",
    openai_api_key=api_key
)
```

### Individual Agent Operations
```python
# Explore codebase
exploration = await codebuff.explore_files(
    focus_area="authentication",
    container=container,
    openai_api_key=api_key
)

# Pick relevant files
files = await codebuff.pick_files(
    task_description="implement login system",
    container=container,
    openai_api_key=api_key
)

# Create implementation plan
plan = await codebuff.create_plan(
    task_description="add JWT authentication",
    relevant_files="auth.py,user.py",
    exploration_results=exploration,
    container=container,
    openai_api_key=api_key
)
```

## Agent Configuration

### LLM Model Selection
```yaml
agents:
  file_explorer:
    model: "openai/gpt-4o-mini"
  thinker:
    model: "openai/gpt-4o"
  implementation:
    model: "openai/gpt-4o"
core_api:
  model: "openai/gpt-4o"  # Default fallback
  provider: "openai"
```

### Model Fallbacks
- Agent-specific config takes priority
- Falls back to `core_api.model`
- Ultimate fallbacks by agent type:
  - File Explorer: `gpt-4o-mini`
  - Thinker/Implementation: `gpt-4o`
  - Context Pruner: `gpt-4o-mini`

## Provider Management

### API Key Priority
1. **OpenRouter**: Preferred when available (supports more models)
2. **OpenAI**: Fallback for direct OpenAI access
3. **Auto-detection**: Based on available secrets

### LLM Creation
```python
# Provider selection logic
if open_router_api_key:
    provider = "openrouter"
    base_url = "https://openrouter.ai/api/v1"
elif openai_api_key:
    provider = "openai"
    base_url = None  # Default OpenAI endpoint
```

## Environment Setup

### Repository Integration
```python
# Clone and setup repository
source = await dag.git(url=repo_url, keep_git_dir=True)
    .with_auth_token(github_token)
    .branch(branch)
    .tree()

# Build container environment
container = await dag.builder(config_file).build_test_environment(
    source=source,
    dockerfile_path=config.container.docker_file_path
)
```

### Container Management
- Stores container for reuse across agents
- Configures GitHub authentication
- Manages Docker environment setup

## Agent Dependencies

### Required Modules
- **Builder**: Container environment setup
- **Pull Request Agent**: PR creation functionality
- **Agent Utils**: Code parsing utilities

### Agent Implementations
```python
# Located in agent-specific directories:
# - file_explorer/agent.py
# - file_picker/agent.py  
# - thinker/agent.py
# - implementation/agent.py
# - reviewer/agent.py
# - context_pruner/agent.py
```

## Pull Request Integration

### PR Creation Workflow
1. **Setup Authentication**: Configure GitHub token in container
2. **Create PR Context**: Combine task and changes descriptions
3. **Execute PR Agent**: Generate PR title, description, and create
4. **Status Validation**: Check PR creation success/failure

### Error Handling
- Status file checking (`/status.txt`, `/error.txt`)
- Graceful failure reporting
- Partial workflow completion tracking

## Orchestration Features

### State Management
- Tracks workflow progress through phases
- Maintains context between agent calls
- Handles partial failures and recovery

### Context Pruning
- Automatic context size management
- Configurable pruning strategies
- Maintains essential information while reducing token usage

## Configuration

### Container Setup
```yaml
container:
  work_dir: "/app"
  docker_file_path: "./Dockerfile"
```

### Git Integration
```yaml
git:
  user_name: "AI Assistant"
  user_email: "ai@example.com"
  base_pull_request_branch: "main"
```

## Testing
- Unit tests: `agents/codebuff/tests/`
- Markers: `@pytest.mark.agent`, `@pytest.mark.orchestration`
- Mock all external agents and services
- Test error handling and edge cases

## Usage Patterns

### Development Workflow
1. **Exploration**: Understand codebase structure
2. **Planning**: Create detailed implementation plan
3. **Implementation**: Execute planned changes
4. **Review**: Validate changes and code quality
5. **Integration**: Create pull request for review

### Error Recovery
- Individual agent failures don't stop workflow
- Graceful degradation with partial results
- Detailed error reporting for debugging

## Performance Optimization

### Agent Selection
- Use appropriate model sizes for each agent type
- Balance cost vs capability
- Configure timeouts and retry logic

### Context Management
- Prune context proactively to prevent token limits
- Maintain essential information across agents
- Use structured data for inter-agent communication

## Integration Points
- **Builder Module**: Environment and container setup
- **Pull Request Module**: Automated PR creation
- **Query Service**: Code understanding and search
- **Index Workflow**: Codebase semantic analysis
# Codebuff Agents - Multi-Agent Feature Development System

A comprehensive multi-agent system that replicates Codebuff's internal workflow patterns using the dagger-agents technology stack.

## Overview

This module provides a complete feature development workflow orchestrated by specialized AI agents:

- 🔍 **File Explorer** - Maps and understands codebase structure
- 📂 **File Picker** - Selects relevant files for tasks
- 🧠 **Thinker/Planner** - Creates detailed execution strategies
- ⚡ **Implementation** - Executes plans with file operations
- 🔍 **Reviewer** - Reviews changes for quality and correctness
- ✂️ **Context Pruner** - Manages context size for efficiency
- 🎯 **Orchestrator** - Coordinates the complete workflow

## Architecture

### Multi-Agent Orchestration

The system uses a **linear supervisor pattern** with structured communication:

```
Orchestrator Agent
    ├── File Explorer Agent
    ├── File Picker Agent  
    ├── Thinker Agent
    ├── Implementation Agent
    ├── Reviewer Agent
    └── Context Pruner Agent
```

### Key Design Principles

1. **Agent-as-Tool**: Each agent is called as a tool with strict input/output contracts
2. **Structured Communication**: All inter-agent communication uses Pydantic models
3. **Deterministic Control**: Workflow logic is deterministic Python, AI handles reasoning
4. **Error Handling**: Comprehensive error classification and recovery strategies
5. **State Management**: Complete workflow state tracking and persistence

## Usage

### Quick Start - Orchestrated Workflow

```bash
# Complete feature development in one command
dagger call codebuff create --config-file=config.yaml orchestrate-feature-development \
  --container=<your-container> \
  --task-description="Add user profile management with avatar upload" \
  --focus-area="user management" \
  --openai-api-key=env:OPENAI_API_KEY
```

### Individual Agent Usage

```bash
# 1. Explore codebase
dagger call codebuff create --config-file=config.yaml explore-files \
  --container=<container> \
  --focus-area="authentication system" \
  --openai-api-key=env:OPENAI_API_KEY

# 2. Pick relevant files
dagger call codebuff create --config-file=config.yaml pick-files \
  --container=<container> \
  --task-description="Add OAuth 2.0 authentication" \
  --openai-api-key=env:OPENAI_API_KEY

# 3. Create implementation plan
dagger call codebuff create --config-file=config.yaml create-plan \
  --container=<container> \
  --task-description="Add OAuth 2.0 authentication" \
  --relevant-files="auth/oauth.py,config/settings.py" \
  --openai-api-key=env:OPENAI_API_KEY

# 4. Implement the plan
dagger call codebuff create --config-file=config.yaml implement-plan \
  --container=<container> \
  --plan="<detailed-plan>" \
  --openai-api-key=env:OPENAI_API_KEY

# 5. Review changes
dagger call codebuff create --config-file=config.yaml review-changes \
  --container=<container> \
  --changes-description="Added OAuth 2.0 authentication" \
  --openai-api-key=env:OPENAI_API_KEY
```

## Configuration

Create a configuration file (e.g., `config.yaml`):

```yaml
container:
    work_dir: "/app"
    docker_file_path: "./Dockerfile"

core_api:
    model: "openai/gpt-4o"
    fallback_models:
        - "openai/gpt-4o-mini"
        - "openai/gpt-3.5-turbo"
    provider: "openai"

git:
    user_email: "dev@example.com"
    user_name: "Feature Developer"
```

## Orchestration Workflow

The orchestrator manages a complete 6-phase workflow:

### Phase 1: Task Initialization
- Creates unique task ID
- Defines success criteria
- Initializes workflow state

### Phase 2: Exploration
- Maps codebase structure
- Identifies key patterns and architecture
- Builds file index with relevance scoring

### Phase 3: File Selection
- Analyzes task requirements
- Selects most relevant files
- Provides rationale for selections

### Phase 4: Planning
- Creates detailed implementation plan
- Identifies risks and dependencies
- Estimates complexity and effort

### Phase 5: Implementation
- Executes planned changes
- Tracks file modifications and commands
- Maintains rollback information

### Phase 6: Review
- Validates syntax and logic
- Runs tests and checks
- Provides approval recommendations

## Data Models

All agent communication uses strongly-typed Pydantic models:

```python
class TaskSpec(BaseModel):
    id: str
    goal: str
    focus_area: Optional[str]
    constraints: Dict[str, Any]
    success_criteria: List[str]

class ExplorationReport(BaseModel):
    areas_explored: List[str]
    file_index: List[PathInfo]
    confidence: float

class Plan(BaseModel):
    steps: List[PlanStep]
    risks: List[str]
    confidence: float

class ChangeSet(BaseModel):
    edits: List[FileEdit]
    commands: List[CommandExecution]
    rollback_instructions: Optional[str]

class ReviewReport(BaseModel):
    findings: List[ReviewFinding]
    overall_status: Status
    approval_status: str
```

## Error Handling

The system includes comprehensive error handling:

- **Error Classification**: Tool, validation, model, resource, and policy errors
- **Retry Strategies**: Configurable retry logic with exponential backoff
- **Graceful Degradation**: Fallback strategies for partial failures
- **Recovery Patterns**: State preservation for workflow resume

## Best Practices

### 1. Start with Orchestration

Use the orchestrated workflow for most features:
- Handles complexity automatically
- Ensures proper error handling
- Maintains workflow state
- Provides comprehensive logging

### 2. Model Selection

- **Orchestrator**: `gpt-4o` (requires sophisticated reasoning)
- **File Explorer**: `gpt-4o-mini` (efficient for analysis)
- **File Picker**: `gpt-4o-mini` (pattern matching)
- **Thinker**: `gpt-4o` (complex planning)
- **Implementation**: `gpt-4o` (precision required)
- **Reviewer**: `gpt-4o` (critical quality checks)

### 3. Configuration Management

- Use environment variables for API keys
- Configure appropriate timeouts and retries
- Set up proper logging levels
- Monitor token usage and costs

### 4. Integration Patterns

```bash
# Integration with existing workflows
dagger call cover generate-tests \
  --container=$(dagger call codebuff create --config-file=config.yaml orchestrate-feature-development ...) \
  --config-file=config.yaml
```

## Monitoring and Observability

The orchestrator provides detailed metrics:

- **Workflow State**: Current phase and status
- **Performance**: Request counts, token usage, phase durations
- **Quality**: Error rates, retry counts, review outcomes
- **Progress**: Step completion, confidence scores

## Advanced Features

### Context Pruning

Automatic context management for large codebases:
- Smart pruning strategies
- Token budget management
- Important content preservation

### State Persistence

Workflow state can be persisted for:
- Long-running tasks
- Resume after interruption
- Audit trails and debugging

### Concurrent Execution

Safe parallelization of independent phases:
- Review and context pruning
- Multiple file analysis
- Batch operations

## Troubleshooting

### Common Issues

1. **"No API key provided"**
   - Set `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
   - Pass key explicitly in command

2. **"Container not ready"**
   - Ensure container has source code mounted
   - Verify required tools (git, bash) are available

3. **"Workflow state lost"**
   - Check orchestration status regularly
   - Implement state persistence if needed

### Debug Commands

```bash
# Check orchestrator status
dagger call codebuff create --config-file=config.yaml orchestrate-feature-development \
  --task-description="status check" \
  --openai-api-key=env:OPENAI_API_KEY

# Test individual agents
dagger call codebuff create --config-file=config.yaml explore-files \
  --container=$TEST_CONTAINER \
  --focus-area="test"
```

## Development

### Extending the System

1. **Add New Agents**: Follow the existing agent pattern
2. **Modify Workflows**: Update orchestrator logic
3. **Custom Models**: Extend Pydantic base models
4. **Error Handling**: Add new error types and recovery

### Testing

```bash
# Run agent tests
python -m pytest tests/

# Test orchestration workflow
dagger call codebuff create --config-file=test-config.yaml orchestrate-feature-development \
  --task-description="test feature" \
  --container=$TEST_CONTAINER
```

The Codebuff agents provide a powerful, production-ready multi-agent system for automated feature development that rivals Codebuff's internal capabilities while running on your own infrastructure.
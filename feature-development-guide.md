# Feature Development with Codebuff Agents

This guide shows how to use the Codebuff-equivalent agents to build features systematically, following Codebuff's proven workflow patterns.

## Overview

The Codebuff agents replicate the multi-agent approach that Codebuff uses internally:

1. **File Explorer** - Maps and understands the codebase
2. **File Picker** - Selects relevant files for the task
3. **Thinker/Planner** - Creates detailed execution plans
4. **Implementation** - Executes the plan with file operations
5. **Reviewer** - Reviews changes for quality and correctness
6. **Context Pruner** - Manages context size for efficiency

## Step-by-Step Feature Development Workflow

### Prerequisites

1. **Setup Configuration**: Create a config file (see `workflows/cover/demo/config.yaml` for examples)
2. **Container Ready**: Have a Dagger container with your source code
3. **API Keys**: OpenAI or OpenRouter API key for LLM access

### Phase 1: Exploration & Discovery

```bash
# 1. Explore the codebase to understand the current structure
dagger call codebuff create --config-file=config.yaml explore-files \
  --container=<your-container> \
  --focus-area="authentication system" \
  --openai-api-key=env:OPENAI_API_KEY
```

**When to use**: Beginning of any feature development to understand:
- Current architecture patterns
- Existing similar features
- Key directories and files
- Project conventions

### Phase 2: File Selection

```bash
# 2. Pick relevant files for your specific feature
dagger call codebuff create --config-file=config.yaml pick-files \
  --container=<your-container> \
  --task-description="Add OAuth 2.0 authentication with Google provider" \
  --openai-api-key=env:OPENAI_API_KEY
```

**When to use**: After exploration, to focus on specific files that need modification.

### Phase 3: Strategic Planning

```bash
# 3. Create a detailed implementation plan
dagger call codebuff create --config-file=config.yaml create-plan \
  --container=<your-container> \
  --task-description="Add OAuth 2.0 authentication with Google provider" \
  --relevant-files="auth/oauth.py,config/settings.py,routes/auth.py" \
  --openai-api-key=env:OPENAI_API_KEY
```

**When to use**: Before implementation to:
- Break down complex features into steps
- Identify risks and dependencies
- Plan proper testing strategy
- Sequence changes logically

### Phase 4: Implementation

```bash
# 4. Implement the planned changes
dagger call codebuff create --config-file=config.yaml implement-plan \
  --container=<your-container> \
  --plan="<detailed-plan-from-step-3>" \
  --openai-api-key=env:OPENAI_API_KEY
```

**When to use**: Execute the plan with:
- File modifications
- Command execution
- Environment setup
- Configuration changes

### Phase 5: Quality Review

```bash
# 5. Review the implemented changes
dagger call codebuff create --config-file=config.yaml review-changes \
  --container=<your-container> \
  --changes-description="Added OAuth 2.0 authentication with Google provider" \
  --openai-api-key=env:OPENAI_API_KEY
```

**When to use**: After implementation to:
- Check syntax and code quality
- Run tests
- Validate requirements
- Identify potential issues

### Phase 6: Context Management (Optional)

```bash
# 6. Prune context if working with large codebases
dagger call codebuff create --config-file=config.yaml prune-context \
  --container=<your-container> \
  --context-data="<large-context-string>" \
  --max-tokens=4000 \
  --strategy="smart" \
  --openai-api-key=env:OPENAI_API_KEY
```

**When to use**: When context becomes too large for efficient processing.

## Real-World Example: Adding a Feature

Let's walk through adding a "User Profile Management" feature:

### 1. Explore Current User System

```bash
dagger call codebuff explore-files \
  --container=$(dagger call builder build-test-environment \
    --source=. \
    --dockerfile-path="Dockerfile" \
    --open-router-api-key=env:OPENROUTER_API_KEY \
    --provider="openrouter") \
  --focus-area="user management and authentication" \
  --openai-api-key=env:OPENAI_API_KEY
```

### 2. Identify Relevant Files

```bash
dagger call codebuff pick-files \
  --container=<container-from-step-1> \
  --task-description="Add user profile management with avatar upload, bio editing, and privacy settings" \
  --openai-api-key=env:OPENAI_API_KEY
```

### 3. Create Implementation Plan

```bash
dagger call codebuff create-plan \
  --container=<container> \
  --task-description="Add user profile management with avatar upload, bio editing, and privacy settings" \
  --relevant-files="models/user.py,views/profile.py,templates/profile.html,static/css/profile.css" \
  --openai-api-key=env:OPENAI_API_KEY
```

### 4. Implement the Feature

```bash
dagger call codebuff implement-plan \
  --container=<container> \
  --plan="[Detailed plan from step 3]" \
  --openai-api-key=env:OPENAI_API_KEY
```

### 5. Review Implementation

```bash
dagger call codebuff review-changes \
  --container=<container> \
  --changes-description="Added user profile management with avatar upload, bio editing, and privacy settings" \
  --openai-api-key=env:OPENAI_API_KEY
```

## Advanced Usage Patterns

### Chaining Agents in Complex Workflows

For complex features, you can chain multiple agent calls:

```bash
# Step 1: Explore architecture
EXPLORATION=$(dagger call codebuff explore-files --container=$CONTAINER --focus-area="API layer")

# Step 2: Use exploration results to pick files
FILES=$(dagger call codebuff pick-files --container=$CONTAINER --task-description="Add REST API endpoints")

# Step 3: Create plan based on files
PLAN=$(dagger call codebuff create-plan --container=$CONTAINER --relevant-files="$FILES")

# Step 4: Implement
dagger call codebuff implement-plan --container=$CONTAINER --plan="$PLAN"
```

### Integration with Existing Workflows

The Codebuff agents integrate well with existing dagger-agents workflows:

```bash
# Use with Cover workflow for test generation
dagger call cover generate-tests \
  --container=$(dagger call codebuff implement-plan --container=$CONTAINER --plan="$PLAN") \
  --config-file=config.yaml

# Use with Graph workflow for dependency analysis
dagger call graph build-graph-for-repository \
  --repository-url="https://github.com/user/repo" \
  --config-file=config.yaml
```

## Best Practices

### 1. **Start Small**
- Begin with file exploration to understand the codebase
- Break large features into smaller, manageable pieces
- Use the thinker agent to plan before implementing

### 2. **Iterative Development**
- Implement → Review → Refine cycle
- Use the reviewer agent after each significant change
- Prune context when it becomes unwieldy

### 3. **Leverage Context**
- Pass relevant file lists between agents
- Use focused exploration areas
- Maintain context across agent calls

### 4. **Error Handling**
- Always review agent outputs for errors
- Use the reviewer agent to catch issues early
- Have rollback plans for complex changes

### 5. **Configuration Management**
- Use proper config files (YAML)
- Set up environment variables for API keys
- Configure appropriate models for different tasks

## Model Recommendations

- **File Explorer**: `gpt-4o-mini` (efficient for analysis)
- **File Picker**: `gpt-4o-mini` (good for pattern matching)
- **Thinker/Planner**: `gpt-4o` (needs reasoning capabilities)
- **Implementation**: `gpt-4o` (requires precision)
- **Reviewer**: `gpt-4o` (critical for quality)
- **Context Pruner**: `gpt-4o-mini` (efficient for text processing)

## Troubleshooting

### Common Issues

1. **"Error: No API key provided"**
   - Ensure you pass `--openai-api-key` or `--open-router-api-key`
   - Check environment variables are set correctly

2. **Container issues**
   - Verify container has source code mounted
   - Check container has necessary tools (git, bash, etc.)

3. **Large context issues**
   - Use the context pruner agent
   - Break tasks into smaller pieces
   - Focus exploration areas

### Debug Commands

```bash
# Check agent availability
dagger call codebuff --help

# Test basic functionality
dagger call codebuff explore-files --container=$TEST_CONTAINER --focus-area="test"
```

## Next Steps

1. Try the basic workflow with a simple feature
2. Experiment with different focus areas and strategies
3. Integrate with your existing development pipeline
4. Customize agent prompts for your specific needs

The Codebuff agents provide a powerful, Codebuff-like development experience using your existing dagger-agents infrastructure!
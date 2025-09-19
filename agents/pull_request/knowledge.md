# Pull Request Agent Module Knowledge

## Purpose
Automates GitHub pull request creation with AI-generated titles, descriptions, and proper formatting based on code changes and context.

## Architecture

### Core Class: `PullRequestAgent`
- **PR Generation**: Creates comprehensive PR descriptions
- **GitHub Integration**: Handles repository operations and authentication
- **LLM Integration**: Uses AI for intelligent PR content generation
- **Change Analysis**: Analyzes code changes for meaningful descriptions

## Core Functions

### Main Operations
- `run()`: Main entry point for PR creation workflow
- `_run_agent()`: Internal agent execution with LLM interaction

### Template System
- `get_pull_request_agent_template()`: Defines AI prompt template
- Structured prompts for consistent PR generation
- Context-aware descriptions based on changes

## Workflow Process

### 1. Environment Setup
```python
pr_agent = await dag.pull_request_agent(config_file)
result_container = await pr_agent.run(
    container=authenticated_container,
    provider="openai",
    openai_api_key=api_key,
    insight_context="Feature: Add user authentication"
)
```

### 2. Change Analysis
- Analyzes git diff and file changes
- Extracts meaningful patterns and modifications
- Identifies affected components and functionality

### 3. PR Content Generation
- **Title**: Concise, descriptive summary
- **Description**: Detailed explanation of changes
- **Technical Details**: Implementation approach and considerations
- **Testing Notes**: How changes were validated

### 4. GitHub Operations
- Creates feature branch if needed
- Commits changes with proper messaging
- Opens pull request with generated content
- Sets appropriate labels and reviewers

## Configuration

### Required Config
```yaml
git:
  user_name: "AI Assistant"
  user_email: "ai@codebuff.com"
  base_pull_request_branch: "main"
```

### LLM Settings
- Supports OpenAI and OpenRouter providers
- Model selection for PR description quality
- Token usage optimization for cost control

## PR Template Structure

### Generated Content Format
```markdown
# Feature: [AI-generated title]

## Summary
[High-level description of changes]

## Changes Made
- [Specific change 1]
- [Specific change 2]
- [Specific change 3]

## Technical Details
[Implementation approach and architecture]

## Testing
[How changes were validated]

## Related Issues
[Links to relevant issues if detected]
```

### Context Integration
- Uses `insight_context` parameter for additional context
- Incorporates task descriptions and change summaries
- References related files and components

## GitHub Integration

### Authentication
- Requires GitHub token with repository write access
- Configured via Builder module's `setup_pull_request_container`
- Validates permissions before PR operations

### Repository Operations
```bash
# Commands executed in container:
git checkout -b feature/ai-generated-branch
git add .
git commit -m "AI-generated commit message"
gh pr create --title "Title" --body "Description"
```

### Branch Management
- Creates feature branches with descriptive names
- Uses timestamp or task-based naming
- Ensures clean branch state before operations

## Error Handling

### PR Creation Failures
- Network connectivity issues
- Authentication problems
- Repository permission errors
- Conflicting branch names

### Status Reporting
- Success: Creates `/status.txt` with "success"
- Failure: Creates `/error.txt` with error details
- Result validation via file existence checks

## LLM Prompt Engineering

### Context Formatting
- Combines task description with change analysis
- Provides repository context and file structure
- Includes relevant code snippets when helpful

### Output Formatting
- Structured prompts for consistent results
- Markdown formatting for GitHub compatibility
- Technical detail inclusion for reviewer context

## Testing
- Unit tests: `agents/pull_request/tests/`
- Markers: `@pytest.mark.pr`, `@pytest.mark.llm`
- Mock GitHub operations for isolation
- Test PR content generation quality

## Dependencies

### External Services
- **GitHub API**: Repository and PR operations
- **LLM Provider**: PR content generation
- **Git**: Version control operations

### Internal Dependencies
- **Builder Module**: Container authentication setup
- **Dagger Engine**: Container orchestration
- **YAML Config**: Configuration management

## Usage Patterns

### Automated Feature Development
```python
# Part of larger workflow
changes_made = await implement_feature()
pr_result = await create_pull_request(
    container=container,
    task_description="Add user authentication",
    changes_description=changes_made
)
```

### Standalone PR Creation
```python
# Direct PR creation from existing changes
result = await pr_agent.run(
    container=container_with_changes,
    insight_context="Bug fix: Resolve memory leak in cache"
)
```

## Best Practices

### PR Quality
- Provide clear task descriptions for better PR content
- Include technical context in insight_context
- Review generated content before merging

### Security
- Use minimal GitHub token permissions
- Validate repository access before operations
- Secure handling of authentication tokens

### Integration
- Always use Builder module for container auth setup
- Validate container state before PR operations
- Handle partial failures gracefully
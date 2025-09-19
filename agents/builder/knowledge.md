# Builder Agent Module Knowledge

## Purpose
Sets up containerized development environments, manages dependencies, and configures containers for AI agent execution and pull request workflows.

## Architecture

### Core Class: `Builder`
- **Environment Setup**: Creates containerized development environments
- **Dependency Management**: Installs required packages and tools
- **GitHub Integration**: Configures containers for PR operations
- **Multi-OS Support**: Handles different operating systems and package managers

## Core Functions

### Environment Building
- `build_test_environment()`: Creates complete development container
- `setup_pull_request_container()`: Configures container with GitHub auth
- `build_cypher_shell()`: Sets up Neo4j cypher-shell access

### Dependency Installation
- `_install_dependencies()`: OS-detection and package installation
- `_install_alpine_deps()`: Alpine Linux package management
- `_install_debian_deps()`: Debian/Ubuntu package management
- `_configure_git()`: Git configuration with user credentials

## Container Setup Workflow

### 1. Base Container Creation
```python
builder = await dag.builder(config_file)
container = await builder.build_test_environment(
    source=repository_source,
    dockerfile_path="./Dockerfile",
    provider="openai"
)
```

### 2. Development Environment
- Installs language runtimes and package managers
- Configures Git with user credentials
- Sets up working directory and permissions
- Installs project dependencies

### 3. GitHub Authentication
```python
auth_container = await builder.setup_pull_request_container(
    base_container=container,
    token=github_token
)
```

## Dependency Management

### OS Detection
```python
# Automatic OS detection for package management
if alpine_detected:
    await _install_alpine_deps(container, packages)
elif debian_detected:
    await _install_debian_deps(container, packages)
else:
    await _install_generic_deps(container, packages)
```

### Package Managers
- **Python**: pip, poetry, pipenv
- **Node.js**: npm, yarn, pnpm
- **Rust**: cargo
- **Go**: go mod
- **System**: apt, apk, yum

### Required Tools
- Git for version control
- Language-specific package managers
- Build tools and compilers
- Testing frameworks

## Configuration

### Container Config
```yaml
container:
  work_dir: "/app"
  docker_file_path: "./Dockerfile"
  base_image: "ubuntu:22.04"  # Optional override
```

### Git Config
```yaml
git:
  user_name: "AI Assistant"
  user_email: "ai@codebuff.com"
  base_pull_request_branch: "main"
```

## Agent Integration

### Builder Template
- Uses LLM to analyze repository and suggest dependencies
- Generates install commands based on project structure
- Handles edge cases and compatibility issues

### Dependency Detection
```python
# Scans for dependency files
files_found = await container.with_exec([
    "find", ".", "-name", "requirements.txt",
    "-o", "-name", "package.json",
    "-o", "-name", "pyproject.toml"
]).stdout()
```

## GitHub Integration

### Authentication Setup
- Configures GitHub CLI with token
- Sets up SSH keys if needed
- Validates repository access
- Configures Git user for commits

### PR Container Features
- Full GitHub API access
- Repository write permissions
- Branch creation and management
- PR creation and update capabilities

## Error Handling

### Installation Failures
- Retry logic for network issues
- Alternative package manager attempts
- Graceful degradation when tools unavailable

### Authentication Issues
- Token validation before operations
- Clear error messages for auth failures
- Fallback authentication methods

## Testing
- Unit tests: `agents/builder/tests/`
- Markers: `@pytest.mark.builder`, `@pytest.mark.dagger`
- Mock container operations for isolation
- Test dependency detection and installation

## Performance Considerations

### Container Optimization
- Layer caching for repeated builds
- Minimal base images when possible
- Efficient dependency installation order

### Resource Management
- Memory limits for large repositories
- CPU allocation for build operations
- Disk space monitoring

## Common Usage Patterns

### Test Environment
```python
# Standard test environment setup
container = await builder.build_test_environment(
    source=repo_source,
    dockerfile_path="./Dockerfile"
)
```

### PR Workflow
```python
# Setup for automated PR creation
auth_container = await builder.setup_pull_request_container(
    base_container=test_container,
    token=github_token
)
```

### Neo4j Access
```python
# Setup cypher-shell for database operations
cypher_container = await builder.build_cypher_shell(
    neo_auth=neo_auth,
    neo_data=neo_data
)
```

## Dependencies
- **Dagger Engine**: Container orchestration
- **GitHub CLI**: Repository and PR operations
- **Language Runtimes**: Python, Node.js, etc.
- **Package Managers**: pip, npm, cargo, etc.

## Troubleshooting

### Build Failures
- Check Dockerfile syntax and base image availability
- Verify package manager and dependency specifications
- Review container resource limits

### Authentication Issues
- Validate GitHub token permissions
- Check repository access rights
- Verify Git configuration

### Dependency Problems
- Check package availability in target OS
- Verify version compatibility
- Review network connectivity for downloads
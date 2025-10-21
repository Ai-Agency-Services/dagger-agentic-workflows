# Spec-Kit Migration Guide

## Overview

Codebuff has been upgraded from an ad-hoc planning workflow to the **Spec-Kit methodology** (Constitution → Spec → Tasks). This guide helps you understand the changes and migrate existing workflows.

## What Changed?

### Old Workflow (Legacy)

```
1. Start task with description
2. Explore codebase
3. Create implementation plan (plan.md)
4. Execute implementation
5. Review changes
6. Create PR
```

### New Workflow (Spec-Kit)

```
1. Explore codebase
2. Create Constitution (values, constraints, quality gates)
3. Create Spec (requirements with acceptance criteria)
4. Create Tasks (atomic, with dependencies)
5. Execute tasks (implementation-review loop per task)
6. Create PR
```

## Key Improvements

| Feature | Legacy | Spec-Kit |
|---------|--------|----------|
| Planning structure | Unstructured markdown | Validated Pydantic models |
| Quality assurance | Single review at end | Review loop per task (max 3 iterations) |
| Task breakdown | Manual in plan.md | Automated with dependency validation |
| Error handling | Generic exceptions | Specific exceptions per phase |
| State persistence | plan.md only | Full state: constitution, spec, tasks, logs |
| Resume capability | Limited | Full state recovery with migration |
| Validation | None | Multi-level (constitution, spec, tasks) |

## Automatic Migration

### How It Works

When you run a new workflow:

1. Checks for `.codebuff-state/plan.md`
2. If found, uses LLM to convert:
   - Plan → Constitution
   - Plan steps → Spec requirements
   - Requirements → Atomic tasks
3. Validates all converted data
4. Backs up as `plan.md.old`
5. Proceeds with spec-kit workflow

### What's Migrated

From `plan.md`:

```markdown
# Implementation Plan

## Steps

1. Create User model with email and password_hash
2. Add authentication endpoint to API
3. Implement JWT token generation
4. Add login tests
```

To:

**constitution.json**:
```json
{
  "values": ["Code quality", "Security"],
  "constraints": ["No breaking changes"],
  "quality_gates": ["All tests pass", "Security audit passes"]
}
```

**spec.json**:
```json
{
  "objective": "Add secure user authentication with JWT",
  "requirements": [
    {
      "id": "REQ-001",
      "description": "User model with secure password storage",
      "acceptance_criteria": ["Uses bcrypt", "Email unique"],
      "priority": "must"
    }
  ],
  "success_criteria": ["Tests pass", "No security warnings"],
  "out_of_scope": ["Social auth", "2FA"]
}
```

**tasks.json**:
```json
{
  "tasks": [
    {
      "id": "TASK-001",
      "description": "Create User model",
      "acceptance_criteria": ["Has email and password_hash fields"],
      "dependencies": [],
      "estimated_complexity": "simple",
      "files_to_modify": ["src/models/user.py"]
    },
    {
      "id": "TASK-002",
      "description": "Add auth endpoint",
      "dependencies": [{"task_id": "TASK-001", "dependency_type": "blocks"}],
      ...
    }
  ]
}
```

## Manual Migration

If automatic migration fails or you want more control:

### Step 1: Review Old Plan

1. Export current state:
   ```bash
   dagger call --mod agents/codebuff export-state-from-self export --path ./state-backup
   ```

2. Review `plan.md.old` or existing `.codebuff-state/plan.md`

### Step 2: Create Constitution

Analyze your feature and codebase:

```json
{
  "values": [
    "What principles guide this feature?",
    "What makes this feature successful?",
    "What coding standards must we uphold?"
  ],
  "constraints": [
    "What can't we change?",
    "What limitations exist?"
  ],
  "quality_gates": [
    "How do we measure success?",
    "What tests must pass?",
    "What metrics must improve?"
  ]
}
```

Save as `.codebuff-state/constitution.json`

### Step 3: Create Spec

Break down the feature:

```json
{
  "objective": "One sentence: what are we building?",
  "requirements": [
    {
      "id": "REQ-001",
      "description": "First distinct requirement",
      "acceptance_criteria": [
        "Specific, testable condition 1",
        "Specific, testable condition 2"
      ],
      "priority": "must"
    }
  ],
  "success_criteria": [
    "Measurable outcome 1",
    "Measurable outcome 2"
  ],
  "out_of_scope": [
    "What we're NOT doing"
  ]
}
```

Save as `.codebuff-state/spec.json`

### Step 4: Create Tasks

Atomic work units:

```json
{
  "tasks": [
    {
      "id": "TASK-001",
      "description": "One sentence: what does this task do?",
      "acceptance_criteria": [
        "Verifiable condition 1",
        "Verifiable condition 2"
      ],
      "dependencies": [],
      "estimated_complexity": "simple",
      "test_requirements": ["tests/test_something.py"],
      "files_to_modify": ["src/file1.py", "src/file2.py"]
    }
  ]
}
```

Key rules:
- No circular dependencies
- Each task <2 hours of work
- Specific file paths
- Testable acceptance criteria

Save as `.codebuff-state/tasks.json`

### Step 5: Resume Workflow

```bash
dagger call --mod agents/codebuff \
  create --config-file demo/config.yaml \
  resume-workflow \
  --github-token env:GITHUB_TOKEN \
  --repository-url https://github.com/user/repo.git \
  --branch-name <working-branch> \
  --provider openrouter \
  --open-router-api-key env:OPEN_ROUTER_API_KEY
```

The workflow will detect the spec-kit state files and continue from where it left off.

## Configuration Changes

### New Configuration Options

Add to your `config.yaml`:

```yaml
orchestrator:
  speckit:
    enabled: true  # Use spec-kit workflow (default: true)
    planning_model: "openai:gpt-4o-mini"  # Cheaper model for planning
    max_tasks_per_spec: 20  # Max tasks to generate (default: 20)
    max_review_iterations: 3  # Max impl-review loops per task (default: 3)
    auto_migrate: true  # Auto-migrate old plan.md (default: true)
```

### Backward Compatibility

Legacy workflow still available:

```yaml
orchestrator:
  speckit:
    enabled: false  # Disable spec-kit, use legacy workflow
```

But spec-kit is recommended for all new work.

## Common Migration Issues

### Issue: "Migration incomplete - missing data"

**Cause**: Old plan.md too complex for LLM to parse reliably

**Solution**:
1. Set `auto_migrate: false` in config
2. Manually create constitution/spec/tasks using templates above
3. Use simpler, more structured plans in future

### Issue: "Validation failed: circular dependency"

**Cause**: LLM created cyclic task dependencies during migration

**Solution**:
1. Check `.codebuff-state/tasks.json`
2. Find the circular reference
3. Edit to remove cycle (e.g., remove one dependency)
4. Resume workflow

### Issue: "Task execution failed after 3 iterations"

**Cause**: Task too complex for implementation-review loop

**Solution**:
1. Check `.codebuff-state/task_log.jsonl` for review feedback
2. Manually split the task into subtasks in `tasks.json`
3. Resume workflow

## FAQ

### Q: Can I still use the old workflow?

**A**: Yes, set `orchestrator.speckit.enabled: false`. But spec-kit is recommended.

### Q: What happens to my existing plan.md files?

**A**: Automatically migrated to spec-kit format and backed up as `plan.md.old`.

### Q: How do I inspect the spec-kit state?

**A**: Export state:
```bash
dagger call --mod agents/codebuff export-state-from-self export --path ./state
```

Inspect:
- `constitution.json`: Core values and gates
- `spec.json`: Requirements
- `tasks.json`: Task breakdown
- `task_log.jsonl`: Execution history

### Q: Can I modify the generated constitution/spec/tasks?

**A**: Yes!
1. Export state
2. Edit JSON files manually
3. Validate using test suite (if available)
4. Resume workflow - it will use your modifications

### Q: What if I don't like the generated plan?

**A**: Two options:
1. **Feedback mode**: If enabled, approve/reject at each phase
2. **Manual override**: Export, edit JSON files, resume

### Q: How do I roll back to legacy workflow mid-flight?

**A**: Not recommended. Instead:
1. Complete current workflow (or abort)
2. Next run: set `speckit.enabled: false`

## Best Practices

### Writing Better Constitutions

❌ **Bad** (too generic):
```json
{
  "values": ["Quality", "Speed"],
  "quality_gates": ["Good code", "Works well"]
}
```

✅ **Good** (specific):
```json
{
  "values": ["Fast page loads (<500ms)", "Accessible (WCAG 2.1 AA)"],
  "quality_gates": ["Lighthouse score >90", "Zero a11y errors on axe scan"]
}
```

### Writing Better Specs

❌ **Bad** (vague):
```json
{
  "acceptance_criteria": ["Works", "Is fast", "Users like it"]
}
```

✅ **Good** (testable):
```json
{
  "acceptance_criteria": [
    "API returns 200 status with valid JSON schema",
    "Response time p95 <100ms under load",
    "User survey NPS >8/10"
  ]
}
```

### Writing Better Tasks

❌ **Bad** (too broad):
```json
{
  "id": "TASK-001",
  "description": "Implement authentication",
  "files_to_modify": ["src/"]  // Too broad!
}
```

✅ **Good** (atomic):
```json
{
  "id": "TASK-001",
  "description": "Create User model with password hashing",
  "files_to_modify": ["src/models/user.py", "src/models/__init__.py"]
}
```

## Support

For issues:
1. Check `task_log.jsonl` for execution history
2. Review `progress.json` for current phase
3. Export state for debugging
4. File issue with state export attached

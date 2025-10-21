# Spec-Kit Methodology Guide

## Overview

Spec-Kit is Codebuff's structured approach to feature development, replacing ad-hoc planning with a validated, atomic workflow.

## Workflow Phases

### Phase 1: Constitution

Defines the **why** and **how** of your feature.

**Components**:

1. **Values** (2-4): What matters most?
   - Example: "Maintainability", "Performance", "User Privacy"
   - Guides implementation decisions
   - Specific to this feature, not generic

2. **Constraints** (1-3): What must we respect?
   - Example: "No breaking API changes", "Must work offline"
   - Technical and business limitations

3. **Quality Gates** (2-4): How do we know we succeeded?
   - Example: "All tests pass", "Performance <100ms", "Code coverage >80%"
   - Must be measurable and verifiable

**Example Constitution**:

```json
{
  "values": [
    "Code maintainability",
    "Backward compatibility",
    "Performance"
  ],
  "constraints": [
    "No breaking changes to public API",
    "Must work with Python 3.11+"
  ],
  "quality_gates": [
    "All existing tests pass",
    "New feature has >90% code coverage",
    "Performance within 10% of baseline"
  ]
}
```

### Phase 2: Specification

Defines **what** to build, aligned with the Constitution.

**Components**:

1. **Objective**: Clear 1-2 sentence goal

2. **Requirements**: Distinct requirements (3-10 items)
   - Format: REQ-001, REQ-002, etc.
   - Each has:
     - Description: What needs to be built
     - Acceptance Criteria: 2-4 testable conditions
     - Priority: must/should/could (MoSCoW)

3. **Success Criteria**: How we measure completion (2-5 items)
   - Must align with Constitution quality gates

4. **Out of Scope**: What we're NOT doing (2-4 items)
   - Prevents scope creep

**Example Spec**:

```json
{
  "objective": "Add user authentication with email/password using JWT tokens",
  "requirements": [
    {
      "id": "REQ-001",
      "description": "User can register with email and password",
      "acceptance_criteria": [
        "Email validation follows RFC 5322",
        "Password minimum 8 chars with complexity rules",
        "Registration returns 201 with user ID",
        "Duplicate email returns 409 error"
      ],
      "priority": "must"
    },
    {
      "id": "REQ-002",
      "description": "User can login with credentials",
      "acceptance_criteria": [
        "Login returns JWT token on success",
        "Token expires after 24 hours",
        "Invalid credentials return 401"
      ],
      "priority": "must"
    }
  ],
  "success_criteria": [
    "All tests pass including new auth tests",
    "Auth endpoints respond in <100ms",
    "Code coverage remains >80%"
  ],
  "out_of_scope": [
    "Social authentication (OAuth)",
    "Two-factor authentication",
    "Password reset via email"
  ]
}
```

### Phase 3: Task Planning

Breaks spec into **atomic, executable tasks**.

**Each Task**:

1. **ID**: TASK-001, TASK-002, etc.
2. **Description**: One-sentence summary
3. **Acceptance Criteria**: 2-4 testable conditions
4. **Dependencies**: Other tasks this depends on
   - Types: "blocks" (must finish first) or "requires" (needs output from)
5. **Complexity**: simple/moderate/complex
6. **Test Requirements**: Test files to create/run
7. **Files to Modify**: Specific file paths

**Example Task**:

```json
{
  "id": "TASK-001",
  "description": "Create User model with email and password hash fields",
  "acceptance_criteria": [
    "User model has email (unique) and password_hash fields",
    "Model includes created_at timestamp",
    "Password setter automatically hashes with bcrypt"
  ],
  "dependencies": [],
  "estimated_complexity": "simple",
  "test_requirements": ["tests/test_user_model.py"],
  "files_to_modify": [
    "src/models/user.py",
    "src/models/__init__.py"
  ]
}
```

### Phase 4: Task Execution

**Implementation-Review Loop** (max 3 iterations per task):

1. Implementation agent makes changes
2. Reviewer agent checks:
   - Acceptance criteria met?
   - Constitution values upheld?
   - Code quality acceptable?
   - Tests adequate?
3. If approved → next task
4. If changes needed → repeat with feedback

**Topological Ordering**:

- Tasks executed in dependency order
- Independent tasks could run in parallel (future enhancement)
- Circular dependencies detected and rejected during validation

### Phase 5: Delivery

1. All changes committed with spec-kit metadata:
   ```
   feat: <task_description>
   
   <spec.objective>
   
   Implemented X tasks following spec-kit methodology:
   - TASK-001: ...
   - TASK-002: ...
   
   Constitution values: ...
   
   🤖 Generated with Codebuff (spec-kit)
   Co-Authored-By: Codebuff <noreply@codebuff.com>
   ```

2. Pull request created against base branch
3. State exported to `.codebuff-state/` for resumption

## Validation Rules

### Constitution Validation

- ✅ At least 2 values
- ✅ At least 1 constraint
- ✅ At least 1 quality gate
- ✅ No empty strings

### Spec Validation

- ✅ Non-empty objective
- ✅ At least 1 requirement
- ✅ No duplicate requirement IDs
- ✅ Each requirement has acceptance criteria
- ✅ Acceptance criteria are specific (>10 chars)
- ✅ Success criteria align with quality gates
- ✅ At least 1 success criterion

### Task Validation

- ✅ At least 1 task
- ✅ No duplicate task IDs
- ✅ No circular dependencies (validated via topological sort)
- ✅ All dependencies reference existing tasks
- ✅ Each task has acceptance criteria
- ✅ Each task has files to modify
- ✅ All spec requirements covered by at least one task

## Error Handling

Spec-kit introduces structured exceptions:

- `ValidationError`: Validation failed (includes list of issues)
- `LLMGenerationError`: LLM failed to generate valid output after retries
- `TaskExecutionError`: Task failed after max review iterations
- `StateError`: State persistence/loading failed
- `MigrationError`: Old plan.md conversion failed

## Migration from Legacy Workflow

### Automatic Migration

If `.codebuff-state/plan.md` exists:

1. LLM extracts values/constraints → Constitution
2. LLM converts plan steps → Spec requirements
3. LLM breaks into atomic tasks with dependencies
4. Validates all converted data
5. Backs up as `plan.md.old`
6. Proceeds with spec-kit workflow

### Manual Migration

If auto-migration fails:

1. Review `.codebuff-state/plan.md.old`
2. Manually create `constitution.json`, `spec.json`, `tasks.json`
3. Restart workflow - it will detect and use new format

## CLI Usage

### Run Spec-Kit Workflow

```bash
dagger call --mod agents/codebuff \
  create --config-file demo/codebuff-feature-demo.yaml \
  orchestrate-feature-development \
  --feature-task-description "Add user authentication" \
  --github-token env:GITHUB_TOKEN \
  --repository-url https://github.com/user/repo.git \
  --branch main \
  --open-router-api-key env:OPEN_ROUTER_API_KEY \
  --provider openrouter
```

The orchestrator will automatically use spec-kit if `orchestrator.speckit.enabled: true` (default).

### Export State for Inspection

```bash
dagger call --mod agents/codebuff \
  create --config-file demo/config.yaml \
  export-state-from-self \
  export --path ./.codebuff-state
```

Inspect:
- `constitution.json`: Core values and gates
- `spec.json`: Requirements and success criteria
- `tasks.json`: Task breakdown
- `task_log.jsonl`: Execution history

## Best Practices

### Constitution

- **Be specific**: "Fast page loads" → "Page load <500ms"
- **Align with codebase**: Review existing patterns before defining values
- **Quality gates must be measurable**: "Good code" → "Code coverage >80% and passes linter"

### Spec

- **One concern per requirement**: Split complex requirements
- **Testable acceptance criteria**: "Works well" → "Function returns 200 status with valid JSON"
- **Clear out-of-scope**: Prevents feature creep and clarifies boundaries

### Tasks

- **Atomic**: Each task should be <2 hours of work
- **Independent when possible**: Minimize dependencies for parallelization
- **Specific file paths**: "Update auth module" → "src/auth/routes.py, src/auth/models.py"
- **Test requirements**: Specify exact test files to create/run

### Review Loop

- First iteration usually needs minor fixes
- Second iteration typically passes
- If third iteration fails, task may be too complex - consider splitting

## Troubleshooting

### Validation Failures

**Problem**: "Spec validation failed: success criteria may not align with quality gates"

**Solution**: Ensure success criteria explicitly mention quality gates. Example:
- Quality gate: "Performance <100ms"
- Success criterion: "All API endpoints respond in <100ms"

**Problem**: "Circular dependency detected"

**Solution**: Review task dependencies - ensure no cycles. Use:
- TASK-001 → TASK-002 → TASK-003 ✅
- TASK-001 → TASK-002 → TASK-001 ❌

### Task Execution Failures

**Problem**: Task fails after 3 review iterations

**Solution**:
1. Check task_log.jsonl for review feedback
2. Task may be too complex - consider splitting into subtasks
3. Acceptance criteria may be unclear - make more specific

### Migration Issues

**Problem**: "Migration incomplete - missing data"

**Solution**:
1. Check plan.md.old content - may be too complex for auto-conversion
2. Manually create constitution.json, spec.json, tasks.json
3. Use examples above as templates
4. Restart workflow

## Future Enhancements

- **Parallel task execution**: Run independent tasks concurrently
- **Smart retry strategies**: Task-specific retry logic based on error type
- **Checkpoint/resume**: Resume from any task in the plan
- **Interactive refinement**: Allow user feedback between phases
- **Metrics tracking**: Time per task, review iterations, etc.

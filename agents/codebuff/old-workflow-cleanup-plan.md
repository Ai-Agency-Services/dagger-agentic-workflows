# Old Workflow Cleanup Plan

## Overview
Remove all remnants of the old ad-hoc workflow and ensure only the spec-kit methodology remains.

## Files to Modify

### 1. `orchestrator/agent.py`
**Remove these functions entirely:**
- `start_task()` - Legacy task initialization
- `explore_codebase()` - Replaced by spec-kit exploration
- `create_implementation_plan()` - Replaced by spec-kit spec/tasks
- `execute_implementation()` - Replaced by spec-kit task execution
- `review_changes()` - Replaced by spec-kit review iteration
- `create_pull_request()` - Replaced by spec-kit PR creation
- `get_orchestration_status()` - Legacy status reporting

**Keep only:**
- `run_speckit_workflow()` - The new main entry point
- Helper functions used by spec-kit

### 2. `orchestrator/models.py`
**Remove these models:**
- `Plan` - Old planning model
- `PlanStep` - Old plan step model
- `FileEdit` - Old file editing model
- `CommandExecution` - Old command execution model
- `ChangeSet` - Old changeset model
- `ReviewFinding` - Old review finding model
- `ReviewReport` - Old review report model
- `ContextSummary` - Old context summary model

**Keep only:**
- `Phase` - Still used for spec-kit phases
- `Status` - Still used for spec-kit status
- `ErrorKind` - Still used for errors
- `TaskSpec` - Replaced by spec-kit Constitution/Spec/Task
- `Constitution`, `Spec`, `Task`, `Requirement` - New spec-kit models
- `OrchestrationState` - Updated for spec-kit
- `OrchestratorDependencies` - Updated for spec-kit

### 3. `orchestrator/tools/` directory
**Review and update:**
- Remove any tool functions that were specific to old workflow
- Ensure all tools work with spec-kit workflow

### 4. `main.py`
**Remove these @function methods:**
- `orchestrate_feature_development()` - Legacy entry point
- Any other legacy workflow entry points

**Keep only:**
- `run_speckit_workflow()` - New main entry point
- State management functions (resume, feedback, export)
- Environment setup functions

### 5. Configuration
**Update `shared/dagger-agents-config`:**
- Remove any old workflow config references
- Ensure only spec-kit config remains

## Implementation Steps

### Step 1: Clean orchestrator/agent.py
```python
# Remove all these function definitions:
# - start_task
# - explore_codebase  
# - create_implementation_plan
# - execute_implementation
# - review_changes
# - create_pull_request
# - get_orchestration_status

# Keep only:
# - run_speckit_workflow and its helpers
# - add_project_file_tree_to_context
# - add_file_token_scores_token_callers_to_context
```

### Step 2: Clean orchestrator/models.py
```python
# Remove all these model definitions:
# - Plan
# - PlanStep (and _coerce_steps)
# - FileEdit
# - CommandExecution
# - ChangeSet
# - ReviewFinding
# - ReviewReport
# - ContextSummary

# Update OrchestrationState to remove:
# - plan: Optional[Plan] field
# - changeset: Optional[ChangeSet] field
# - review_report: Optional[ReviewReport] field
# - context_summary: Optional[ContextSummary] field

# Keep spec-kit specific fields:
# - constitution: Optional[Constitution]
# - spec: Optional[Spec]
# - current_task: Optional[Task]
# - completed_tasks: list[Task]
```

### Step 3: Clean main.py
```python
# Remove @function:
# - orchestrate_feature_development (old entry point)

# Keep @function:
# - run_speckit_workflow (new entry point)
# - setup_environment
# - resume_workflow
# - request_feedback / request_feedback_from_self
# - process_orchestrator_command
# - process_pr_feedback
# - continue_workflow
# - export_state / export_state_from_self
```

### Step 4: Update Documentation
- Update knowledge.md to remove old workflow references
- Update SPEC_KIT_GUIDE.md to be the primary guide
- Remove or archive old implementation plans

### Step 5: Update Tests
- Remove tests for old workflow functions
- Keep/add tests for spec-kit workflow

## Verification Checklist

- [ ] No references to `start_task` in codebase
- [ ] No references to `explore_codebase` (except in spec-kit context)
- [ ] No references to `create_implementation_plan`
- [ ] No references to `execute_implementation`
- [ ] No references to `review_changes`
- [ ] No references to old `Plan` model
- [ ] No references to `PlanStep` model
- [ ] `OrchestrationState` only has spec-kit fields
- [ ] Only one main entry point: `run_speckit_workflow`
- [ ] Documentation updated
- [ ] Tests updated

## Breaking Changes

**CLI Impact:**
Old command:
```bash
dagger call --mod agents/codebuff orchestrate-feature-development ...
```

New command:
```bash
dagger call --mod agents/codebuff run-speckit-workflow ...
```

**API Impact:**
All old workflow functions removed. Users must migrate to `run_speckit_workflow`.

## Migration Path for Users

1. Replace `orchestrate-feature-development` calls with `run-speckit-workflow`
2. Update any scripts or CI/CD pipelines
3. Review SPEC_KIT_GUIDE.md for new methodology
4. Test with a sample feature request

## Estimated Impact

- **Lines removed:** ~500-800 lines
- **Models removed:** 7-8 legacy models
- **Functions removed:** 6-7 legacy workflow functions
- **Breaking changes:** All old workflow entry points
- **Migration effort:** Medium (CLI command changes, no code changes for users)
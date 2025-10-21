# Remove Old Workflow Migration Logic

## Objective
Completely remove the old workflow migration logic, making spec-kit the only supported workflow.

## Changes Required

### 1. Remove Migration Functions (`speckit_workflow.py`)

**Delete these functions:**
- `migrate_old_state()` - Entry point for migration
- `convert_plan_to_constitution()` - LLM-based plan → constitution converter
- `convert_plan_to_spec()` - LLM-based plan → spec converter  
- `convert_plan_to_tasks()` - LLM-based plan → tasks converter

**Keep:**
- All validation functions (validate_constitution, validate_spec, validate_tasks)
- All workflow execution functions (explore_codebase, create_constitution, etc.)
- State persistence functions (save_to_state, load_from_state, append_to_log)

### 2. Simplify Main Workflow (`agent.py:run_speckit_workflow`)

**Remove:**
```python
# Check for migration from old plan.md format
migrated, msg = await migrate_old_state(ctx, task_description)
if migrated:
    # Load migrated data
    ...
else:
    # Fresh workflow
```

**Replace with:**
```python
# Always run fresh spec-kit workflow
print(blue("Phase 1: Codebase Exploration"))
# ... rest of fresh workflow
```

### 3. Clean Up Imports

**In `agent.py`:**
- Remove import of `migrate_old_state` from speckit_workflow
- Remove `MigrationError` from models imports

**In `speckit_workflow.py`:**
- No import cleanup needed (functions are self-contained)

### 4. Remove Migration Models (`models.py`)

**Delete:**
- `class MigrationError(Exception)` - Exception for migration failures

**Keep:**
- All other error classes (ValidationError, LLMGenerationError, TaskExecutionError, StateError)
- All spec-kit models (Constitution, Spec, Task, Requirement, etc.)

### 5. Update Error Handling

**In `agent.py:run_speckit_workflow`:**
- Remove `except MigrationError` block from error handlers
- Keep all other exception handlers (ValidationError, LLMGenerationError, TaskExecutionError)

### 6. Clean Up Tests

**Search for and update:**
- Any tests that reference migration functions
- Any tests that create mock plan.md files
- Update test fixtures if they reference migration

**Test files to check:**
- `agents/codebuff/tests/test_orchestrator_critical_paths.py`
- `agents/codebuff/tests/test_plan_models.py`
- Any other test files in agents/codebuff/tests/

### 7. Update Documentation

**Files to update:**
- `agents/codebuff/knowledge.md` - Remove migration references
- `agents/codebuff/OLD_WORKFLOW_CLEANUP_SUMMARY.md` - Archive or delete
- `agents/codebuff/SPEC_KIT_MIGRATION.md` - Update to reflect no migration needed
- `agents/codebuff/SPEC_KIT_GUIDE.md` - Clean up any migration mentions

**Add note:**
"Migration from old plan.md format is no longer supported. All workflows use spec-kit methodology exclusively."

### 8. Verify Clean State

**Check for remaining references:**
```bash
grep -r "migrate" agents/codebuff/src/
grep -r "plan.md" agents/codebuff/src/
grep -r "MigrationError" agents/codebuff/
```

**Expected:**
- No references to migration logic in source code
- Documentation clearly states spec-kit is the only workflow
- Tests pass without migration test cases

## Implementation Order

1. Remove migration functions from `speckit_workflow.py` (bottom-up)
2. Remove migration call from `agent.py` (simplify workflow)
3. Remove MigrationError from `models.py`
4. Clean up imports in both files
5. Update/remove affected tests
6. Update documentation
7. Verify with grep searches
8. Run tests to confirm nothing broke

## Success Criteria

- ✅ No migration code in `speckit_workflow.py`
- ✅ No migration logic in `agent.py:run_speckit_workflow`
- ✅ No MigrationError in `models.py`
- ✅ Clean imports (no migration-related)
- ✅ Tests pass (migration tests removed/updated)
- ✅ Documentation updated
- ✅ No grep matches for migration logic in src/

## Notes

- This is a breaking change for anyone with existing .codebuff-state/plan.md files
- Users will need to start fresh workflows
- Simplifies codebase significantly (~200 lines removed)
- Reduces maintenance burden
- Clearer separation: spec-kit is THE workflow
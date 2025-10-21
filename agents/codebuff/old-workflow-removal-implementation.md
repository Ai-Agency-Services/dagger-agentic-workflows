# Old Workflow Removal Implementation Plan

## Phase 1: Remove Legacy Functions from agent.py

### Functions to Remove Entirely:
1. `start_task()` - DONE (already removed)
2. `explore_codebase()` - Keep minimal stub with deprecation warning
3. `create_implementation_plan()` - Remove entirely
4. `execute_implementation()` - Remove entirely  
5. `review_changes()` - Remove entirely
6. `address_review_feedback()` - Remove entirely
7. `orchestrate_review_cycle()` - Remove entirely
8. `create_pull_request()` - Remove entirely
9. `get_orchestration_status()` - Remove entirely

### Functions to Keep:
- `run_speckit_workflow()` - Main entry point
- `add_project_file_tree_to_context()` - Used by spec-kit
- `add_file_token_scores_token_callers_to_context()` - Used by spec-kit
- `create_orchestrator_agent()` - Main agent factory

## Phase 2: Remove Legacy Models from models.py

### Models to Remove:
1. `Plan` - Old planning model
2. `PlanStep` - Old plan steps
3. `FileEdit` - Old file editing
4. `CommandExecution` - Old commands
5. `ChangeSet` - Old changeset
6. `ReviewFinding` - Old review findings
7. `ReviewReport` - Old review report (keep minimal for backward compat)
8. `ReviewSeverity` - Old review severity
9. `ReviewCategory` - Old review category  
10. `ReviewStatus` - Old review status
11. `ContextSummary` - Old context summary
12. `PullRequestResult` - Keep (still used)

### Models to Keep:
- All Spec-Kit models (Constitution, Spec, Task, etc.)
- `Phase`, `Status`, `ErrorKind` - Core enums
- `TaskSpec` - Keep for backward compat
- `PathInfo`, `ExplorationReport`, `FileSet` - Used by spec-kit
- `OrchestrationState` - Update to remove legacy fields
- `OrchestratorDependencies` - Update

## Phase 3: Update OrchestrationState

### Fields to Remove:
```python
plan: Optional[Plan] = None
change_set: Optional[ChangeSet] = None
review_report: Optional[ReviewReport] = None
context_summary: Optional[ContextSummary] = None
```

### Fields to Keep:
```python
# Spec-kit fields (if they exist)
constitution: Optional[Constitution] = None
spec: Optional[Spec] = None  
current_task: Optional[Task] = None
completed_tasks: list[Task] = []

# Core fields
task_spec: Optional[TaskSpec] = None
exploration_report: Optional[ExplorationReport] = None
file_set: Optional[FileSet] = None
pull_request_result: Optional[PullRequestResult] = None
```

## Phase 4: Update create_orchestrator_agent

### Tool Registrations to Remove:
```python
agent.tool(start_task)
agent.tool(explore_codebase)
agent.tool(create_implementation_plan)
agent.tool(execute_implementation)
agent.tool(review_changes)
agent.tool(address_review_feedback)
agent.tool(orchestrate_review_cycle)
agent.tool(create_pull_request)
agent.tool(get_orchestration_status)
```

### Tool Registrations to Keep:
```python
agent.tool(run_speckit_workflow)  # Main workflow
agent.tool(create_plan)  # Planning tool
agent.tool(add_subgoal)  # Progress tracking
agent.tool(update_subgoal)  # Progress tracking
agent.tool(read_files_tool)  # File ops
agent.tool(write_file_tool)  # File ops
agent.tool(str_replace_tool)  # File ops
agent.tool(code_search_tool)  # File ops
agent.tool(run_terminal_command_tool)  # Execution
agent.tool(think_deeply)  # Analysis
```

## Phase 5: Update main.py

### Remove:
- `orchestrate_feature_development()` - Legacy entry point
  - OR mark as DEPRECATED and redirect to run_speckit_workflow

### Keep:
- `setup_environment()`
- `resume_workflow()`  
- `continue_workflow()`
- `request_feedback()`
- `process_pr_feedback()`
- `export_state()`

## Phase 6: Verification

1. Run code search to find any remaining references
2. Check test files for legacy function calls
3. Update knowledge.md with deprecation notes
4. Run type checking
5. Test basic workflow execution

## Implementation Order

1. Remove legacy functions from agent.py (bottom to top to avoid line number issues)
2. Remove legacy models from models.py
3. Update OrchestrationState fields
4. Update create_orchestrator_agent tool registrations
5. Update main.py (deprecate or remove orchestrate_feature_development)
6. Clean up imports
7. Verify and test
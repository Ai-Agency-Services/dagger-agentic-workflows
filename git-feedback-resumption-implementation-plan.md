# Git Feedback Resumption Implementation Plan

## Overview
Implement comprehensive state persistence and resumption for the Codebuff orchestrator to enable reliable workflow resumption after process termination and GitHub PR comment-based feedback.

## Current State Analysis

### What's Currently Written
- `task.json` - task spec from start_task
- `plan_metadata.json` + `IMPLEMENTATION_PLAN.md` - from planning
- `implementation/targets.json`, `implementation/test-results.json`, `implementation/summary.json`, `implementation/diffs/commit.diff` - from implementation
- `review.json` - from review phase
- `pull_request.json` - from PR creation
- `feedback_sentinel.json` (always empty `{}`)
- `log.txt` - timeline entries

### What the Plan Expects
- `current_phase.json` - phase tracking
- `task_spec.json` - standardized task definition
- `exploration_results.json` - codebase analysis
- `selected_files.json` - file selection with scores
- `implementation_plan.json` - structured plan
- `user_feedback.json` - parsed PR comments
- Commit message metadata with embedded JSON
- PR comment parsing and processing

## Phase 1: Core State Persistence (Critical)

### 1.1 Standardize State File Names
**File: `agents/codebuff/src/codebuff/orchestrator/agent.py`**
- Update `start_task()`: Write `task_spec.json` instead of `task.json`
- Update `explore_codebase()`: Add `exploration_results.json` persistence
- Update `explore_codebase()`: Add `selected_files.json` persistence
- Update `create_implementation_plan()`: Add `implementation_plan.json` alongside markdown
- Update `execute_implementation()`: Rename `test-results.json` to `test_results.json`
- Add `current_phase.json` persistence on every phase transition

### 1.2 Add Phase Transition Tracking
**File: `agents/codebuff/src/codebuff/utils/container_state.py`**
- Add helper function `write_current_phase(container, phase, status, metadata)`
- Add helper function `write_orchestration_snapshot(container, state)`

### 1.3 Implement OrchestrationState Serialization
**File: `agents/codebuff/src/codebuff/orchestrator/models.py`**
- Add `schema_version` field to all state models
- Add serialization/deserialization helpers for OrchestrationState
- Add validation methods for state consistency

## Phase 2: Enhanced Resume Workflow

### 2.1 State Reconstruction Logic
**File: `agents/codebuff/src/codebuff/main.py`**
- Rewrite `resume_workflow()` to:
  - Load and parse canonical state files
  - Reconstruct OrchestrationState object from JSON files
  - Handle backward compatibility (map old→new file names)
  - Validate state consistency and phase progression
  - Return reconstructed state object, not summary string

### 2.2 Tolerant State Loading
**New File: `agents/codebuff/src/codebuff/orchestrator/state_loader.py`**
- Implement `load_orchestration_state(container, branch_name)`
- Handle missing files gracefully with fallbacks
- Map legacy file names to canonical names
- Validate loaded state and report inconsistencies

### 2.3 Continue Execution After Resume
**File: `agents/codebuff/src/codebuff/main.py`**
- Add `continue_workflow()` function
- Determine next action based on current phase and feedback gates
- Support CLI override for resume-from-phase

## Phase 3: PR Comment Processing

### 3.1 GitHub API Integration
**New File: `agents/codebuff/src/codebuff/orchestrator/pr_feedback.py`**
- Implement `fetch_pr_comments(github_token, repo_url, pr_number)`
- Implement `parse_orchestrator_commands(comments)`
- Handle rate limiting and pagination
- Track `last_processed_comment_id` to avoid reprocessing

### 3.2 Command Processing
**File: `agents/codebuff/src/codebuff/orchestrator/pr_feedback.py`**
- Parse `@orchestrator approve|modify|cancel|add-files|revise-plan` commands
- Validate commands against current phase
- Write structured decisions to `user_feedback.json`
- Include timestamp and commenter information

### 3.3 Feedback Gate Integration
**File: `agents/codebuff/src/codebuff/main.py`**
- Update `request_feedback()` to write non-empty `feedback_sentinel.json`
- Check for PR comments in resume logic
- Process feedback and continue workflow based on user commands

## Phase 4: Git Persistence and Metadata

### 4.1 Commit State to Branches
**File: `agents/codebuff/src/codebuff/orchestrator/agent.py`**
- Update `execute_implementation()` to commit `.codebuff-state` files
- Add structured metadata to commit message footers
- Ensure all state files are included in commits

### 4.2 Commit Metadata Embedding
**New File: `agents/codebuff/src/codebuff/utils/git_metadata.py`**
- Implement `embed_state_metadata(commit_message, state)`
- Implement `extract_state_metadata(commit_message)`
- Use as fallback when state files are missing

### 4.3 Branch Management
**File: `agents/codebuff/src/codebuff/main.py`**
- Store working branch name in state
- Handle branch conflicts and divergence detection
- Support deterministic branch naming

## Phase 5: Atomic Operations and Validation

### 5.1 Atomic State Writes
**File: `agents/codebuff/src/codebuff/utils/container_state.py`**
- Implement atomic file operations (temp + rename pattern)
- Add `write_orchestration_snapshot()` for full state dumps
- Ensure consistency across multiple file writes

### 5.2 State Validation
**File: `agents/codebuff/src/codebuff/orchestrator/state_validator.py`**
- Implement validation for phase progression
- Check timestamp consistency
- Validate model relationships and references
- Generate validation reports

## Phase 6: Testing and Integration

### 6.1 Unit Tests
**File: `agents/codebuff/tests/test_state_persistence.py`**
- Test state file writing and reading
- Test backward compatibility with old file names
- Test partial state recovery
- Test atomic operations

### 6.2 Integration Tests
**File: `agents/codebuff/tests/test_resume_workflow.py`**
- Test full resume cycle from each phase
- Test PR comment processing
- Test feedback gate behavior
- Test error recovery scenarios

### 6.3 End-to-End Tests
**File: `agents/codebuff/tests/test_feedback_cycle.py`**
- Test complete feedback cycle: stop → PR → comment → resume
- Test multiple resume cycles
- Test conflict resolution

## Implementation Checklist

### Immediate (Phase 1)
- [ ] Update orchestrator agent to write canonical file names
- [ ] Add current_phase.json writing on phase transitions
- [ ] Implement exploration_results.json and selected_files.json persistence
- [ ] Add schema_version to all state models

### Short-term (Phase 2)
- [ ] Rewrite resume_workflow() for state reconstruction
- [ ] Implement state loader with backward compatibility
- [ ] Add continue_workflow() function

### Medium-term (Phase 3-4)
- [ ] Implement PR comment fetching and parsing
- [ ] Add feedback gate processing logic
- [ ] Ensure Git persistence of state files
- [ ] Add commit metadata embedding

### Long-term (Phase 5-6)
- [ ] Implement atomic operations and validation
- [ ] Create comprehensive test suite
- [ ] Add observability and debugging tools

## Success Criteria
- `resume_workflow()` successfully reconstructs `OrchestrationState` from `.codebuff-state`
- Workflow can be interrupted at any phase and resumed reliably
- PR comments with `@orchestrator` commands are parsed and executed
- State persists across container/process termination via Git commits
- Backward compatibility maintained for existing workflows
- All state files use consistent naming convention
- State validation catches and reports inconsistencies
- Atomic operations prevent partial state corruption
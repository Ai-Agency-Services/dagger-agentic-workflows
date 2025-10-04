# Fix Implementation Agent for Test-Driven Development

## Problem
The `execute_implementation` function in `orchestrator/agent.py` immediately fails and stops the workflow when targeted tests fail. In TDD, failing tests are expected and should drive additional implementation cycles.

## Root Cause Analysis
In `execute_implementation()` around lines 315-325:
```python
# Gate commit on test results
if not tests_passed:
    state.status = Status.FAILED
    error = OrchestrationError(...)
    state.errors.append(error)
    return "Implementation failed: targeted tests did not pass"
```

This hard-stops the workflow on any test failure, preventing TDD cycles.

## Solution: TDD-Aware Implementation Loop

### 1. Add TDD Configuration
Add to YAML config:
```yaml
orchestrator:
  testing:
    tdd:
      enabled: true
      max_cycles: 5
      time_budget_seconds: 1800  # 30 minutes
      allow_tests_only_first_cycle: true
```

### 2. Modify execute_implementation Function
Replace test gating logic with TDD cycle loop:

```python
# TDD Cycle Loop
tdd_config = getattr(ctx.deps.config, 'orchestrator', {}).get('testing', {}).get('tdd', {})
tdd_enabled = tdd_config.get('enabled', False)
max_cycles = tdd_config.get('max_cycles', 3)
cycle_count = 0

while not tests_passed and cycle_count < max_cycles:
    cycle_count += 1
    
    # On first cycle, allow tests-only changes
    if cycle_count == 1 and not code_files and test_files and tdd_config.get('allow_tests_only_first_cycle', False):
        print(yellow(f"🔄 TDD Cycle {cycle_count}: Tests-only changes allowed in first cycle"))
    elif not code_files and test_files:
        # Subsequent cycles must have implementation code
        break
    
    if not tests_passed and cycle_count > 1:
        # Parse test failures and provide feedback to implementation agent
        failure_context = extract_test_failure_context(per_file_results)
        
        # Re-run implementation agent with failure context
        retry_prompt = (
            "Fix the failing tests by implementing the required functionality.\n"
            f"Test failures from cycle {cycle_count-1}:\n"
            f"{failure_context}\n"
            "Focus on making the failing tests pass without breaking existing functionality."
        )
        
        impl_result = await impl_agent.run(retry_prompt, deps=impl_deps)
        # ... re-run test detection and execution ...
    
    if tests_passed:
        break

# Final gating: commit only if tests pass OR if TDD disabled
if not tests_passed and tdd_enabled:
    print(yellow(f"⚠️ TDD cycles exhausted ({max_cycles}). Tests still failing."))
    # Don't fail the workflow, but don't commit either
    return f"Implementation cycles completed but tests still failing after {cycle_count} attempts"
elif not tests_passed:
    # Original behavior when TDD disabled
    state.status = Status.FAILED
    return "Implementation failed: targeted tests did not pass"
```

### 3. Test Failure Context Extraction
Add helper function:
```python
def extract_test_failure_context(per_file_results):
    """Extract useful failure information for implementation agent"""
    failures = []
    for result in per_file_results:
        if result.get('status') == 'failed':
            error = result.get('error', '')
            # Extract key failure info
            failures.append(f"File: {result['file']}\nError: {error[:500]}")
    return "\n\n".join(failures[:3])  # Limit to top 3 failures
```

### 4. State Management for TDD Cycles
Update state tracking:
```python
state.tdd_cycle = cycle_count
state.last_test_failures = per_file_results
```

### 5. Configuration Integration
Update `orchestrator/models.py` to include TDD state:
```python
@dataclass
class OrchestrationState:
    # ... existing fields ...
    tdd_cycle: int = 0
    last_test_failures: List[dict] = field(default_factory=list)
```

## Implementation Steps
1. Add TDD configuration models
2. Modify execute_implementation with TDD cycle loop
3. Add test failure context extraction
4. Update state models for TDD tracking
5. Test with simple TDD scenario
6. Add logging and progress indicators

## Expected Behavior After Fix
1. Agent creates failing tests → TDD cycle 1 begins
2. Implementation agent gets test failure feedback
3. Agent implements code to make tests pass
4. Tests pass → commit and continue workflow
5. If tests still fail after max cycles → workflow continues but no commit

## Benefits
- Supports proper TDD workflow (red → green → refactor)
- Bounded by cycles and time to prevent infinite loops
- Configurable - can disable for non-TDD workflows
- Preserves existing behavior when TDD disabled
- Provides meaningful feedback to implementation agent
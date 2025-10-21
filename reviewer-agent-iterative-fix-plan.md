# Reviewer Agent Iterative Fix Plan

## Problem Statement
The reviewer agent is never instantiated and the review phase always returns success. We need to implement a proper back-and-forth review loop where:
1. The reviewer agent actually runs and analyzes changes
2. The reviewer provides feedback using its existing tools (check_syntax, run_tests, analyze_changes)
3. The implementation agent addresses feedback
4. This continues until the reviewer is satisfied

## Current Reviewer Agent Capabilities

Based on the existing reviewer agent tools:
- `check_syntax`: Validates code syntax
- `run_tests`: Executes test suite
- `analyze_changes`: Analyzes code quality and suggests improvements

The reviewer should use these tools to provide structured feedback.

## Architecture Overview

### Review Loop Flow
```
1. Implementation Phase completes
2. Orchestrator calls review_changes tool
3. Reviewer agent spawns and uses its tools:
   - check_syntax() → syntax errors?
   - run_tests() → test failures?
   - analyze_changes() → code quality issues?
4. Reviewer returns ReviewReport with findings
5. If findings exist:
   a. Orchestrator calls implementation agent with feedback
   b. Implementation agent fixes issues
   c. Return to step 2
6. If no critical findings:
   a. Mark review as complete
   b. Proceed to PR creation
```

## Implementation Steps

### Phase 1: Investigation (Read existing code)

1. **Read orchestrator files**
   - `agents/codebuff/src/codebuff/orchestrator/agent.py`
   - `agents/codebuff/src/codebuff/orchestrator/models.py`
   - `agents/codebuff/src/codebuff/main.py`

2. **Read reviewer agent files**
   - `agents/codebuff/src/codebuff/reviewer/agent.py`
   - `agents/codebuff/src/codebuff/reviewer/__init__.py`

3. **Search for review-related code**
   - Pattern: "review_changes" in orchestrator
   - Pattern: "ReviewerDependencies" usage
   - Pattern: "ReviewReport" model definition

### Phase 2: Design the Iterative Loop

1. **Update ReviewReport model** (if needed)
   Ensure it captures:
   - `findings: list[ReviewFinding]` - Issues found
   - `status: str` - "approved" | "needs_changes" | "critical_issues"
   - `summary: str` - Overall feedback
   - `iteration: int` - Which review iteration this is

2. **Define ReviewFinding model** (if not exists)
   ```python
   class ReviewFinding:
       severity: str  # "error" | "warning" | "suggestion"
       category: str  # "syntax" | "tests" | "quality"
       message: str
       file_path: Optional[str]
       suggested_fix: Optional[str]
   ```

### Phase 3: Implement Reviewer Agent Integration

1. **Create/Update review_changes tool in orchestrator**
   ```python
   @orchestrator.tool
   async def review_changes(
       ctx: RunContext[OrchestratorDependencies],
       change_summary: str,
       iteration: int = 0
   ) -> ReviewReport:
       # Create ReviewerDependencies with container access
       reviewer_deps = ReviewerDependencies(
           run_command=lambda cmd: ctx.deps.container.with_exec(cmd.split()),
           read_file=lambda path: ctx.deps.container.file(path).contents(),
           write_file=lambda path, content: ctx.deps.container.with_new_file(path, content)
       )
       
       # Spawn reviewer agent
       reviewer_agent = create_reviewer_agent()
       
       # Run with context about what changed
       result = await reviewer_agent.run(
           f"Review iteration {iteration}. Changes: {change_summary}",
           deps=reviewer_deps
       )
       
       return result.output
   ```

2. **Update ReviewerDependencies**
   Ensure it provides:
   - Access to run commands (for check_syntax, run_tests)
   - File read/write capabilities
   - Container context

3. **Enhance reviewer agent tools** (in `agents/codebuff/src/codebuff/reviewer/agent.py`)
   
   Make sure these tools return structured findings:
   ```python
   @reviewer_agent.tool
   async def check_syntax(ctx: RunContext[ReviewerDependencies]) -> list[ReviewFinding]:
       # Run syntax checks
       # Parse output into findings
       return findings
   
   @reviewer_agent.tool
   async def run_tests(ctx: RunContext[ReviewerDependencies]) -> list[ReviewFinding]:
       # Execute tests
       # Parse failures into findings
       return findings
   
   @reviewer_agent.tool
   async def analyze_changes(ctx: RunContext[ReviewerDependencies]) -> list[ReviewFinding]:
       # Analyze code quality
       # Return suggestions
       return findings
   ```

### Phase 4: Implement Feedback Loop in Orchestrator

1. **Create address_review_feedback tool**
   ```python
   @orchestrator.tool
   async def address_review_feedback(
       ctx: RunContext[OrchestratorDependencies],
       review_report: ReviewReport
   ) -> str:
       # Create ImplementationDependencies
       impl_deps = ImplementationDependencies(...)
       
       # Spawn implementation agent
       impl_agent = create_implementation_agent()
       
       # Format feedback for implementation agent
       feedback_prompt = format_review_feedback(review_report)
       
       # Run implementation agent to fix issues
       result = await impl_agent.run(
           feedback_prompt,
           deps=impl_deps
       )
       
       return result.output  # Summary of changes made
   ```

2. **Update orchestrate_feature_development main loop**
   
   Add review iteration logic:
   ```python
   # After implementation phase
   if state.phase == Phase.REVIEW:
       max_review_iterations = 3
       review_iteration = 0
       
       while review_iteration < max_review_iterations:
           # Run review
           review_report = await ctx.run_tool(
               'review_changes',
               change_summary=state.change_set.summary,
               iteration=review_iteration
           )
           
           # Check status
           if review_report.status == "approved":
               state.phase = Phase.CREATE_PR
               break
           elif review_report.status == "critical_issues":
               # Log critical issues
               logger.error(f"Critical review issues: {review_report.summary}")
               # Decide: retry or abort?
               if review_iteration >= max_review_iterations - 1:
                   state.phase = Phase.ERROR
                   break
           
           # Address feedback
           if review_report.findings:
               fix_summary = await ctx.run_tool(
                   'address_review_feedback',
                   review_report=review_report
               )
               logger.info(f"Addressed feedback: {fix_summary}")
           
           review_iteration += 1
       
       # Save final review report
       state.review_report = review_report
   ```

### Phase 5: Configuration and Limits

1. **Add review config to OrchestratorConfig**
   ```python
   class ReviewConfig:
       enabled: bool = True
       max_iterations: int = 3
       require_tests_pass: bool = True
       require_syntax_valid: bool = True
       quality_threshold: str = "warning"  # error, warning, suggestion
   ```

2. **Update orchestrator to respect config**
   - Use `config.review.max_iterations`
   - Skip review if `config.review.enabled = False`
   - Enforce quality thresholds

### Phase 6: State Persistence

1. **Update OrchestrationState model**
   ```python
   class OrchestrationState:
       # ... existing fields ...
       review_iteration: int = 0
       review_reports: list[ReviewReport] = []
       last_review_status: Optional[str] = None
   ```

2. **Persist state between iterations**
   - Save after each review iteration
   - Load previous review reports when resuming

### Phase 7: Logging and Observability

1. **Add detailed logging**
   - Log when reviewer agent spawns
   - Log each tool call (check_syntax, run_tests, analyze_changes)
   - Log findings and feedback
   - Log implementation agent responses

2. **Update progress tracking**
   - Show review iteration number
   - Display finding count by severity
   - Show improvement over iterations

## Testing Strategy

1. **Unit tests**
   - Test ReviewReport model
   - Test ReviewFinding model
   - Test review_changes tool
   - Test address_review_feedback tool

2. **Integration tests**
   - Test full review loop with mock findings
   - Test iteration limits
   - Test approval path
   - Test critical issues path

3. **End-to-end test**
   - Introduce deliberate issues (syntax error, failing test, code smell)
   - Verify reviewer detects them
   - Verify implementation agent fixes them
   - Verify approval after fixes

## Success Criteria

- [ ] Reviewer agent spawns when review phase starts
- [ ] Reviewer uses check_syntax, run_tests, analyze_changes tools
- [ ] Reviewer returns structured ReviewReport with findings
- [ ] Implementation agent receives and addresses feedback
- [ ] Loop continues until approval or max iterations
- [ ] State persists between iterations
- [ ] Logs show review activity
- [ ] Tests verify the loop works

## Files to Create/Modify

1. `agents/codebuff/src/codebuff/orchestrator/models.py`
   - Add/update ReviewReport, ReviewFinding models
   - Update OrchestrationState

2. `agents/codebuff/src/codebuff/orchestrator/agent.py`
   - Implement review_changes tool
   - Implement address_review_feedback tool
   - Update orchestration loop with review iterations

3. `agents/codebuff/src/codebuff/reviewer/agent.py`
   - Ensure tools return structured findings
   - Update agent output type to ReviewReport

4. `agents/codebuff/src/codebuff/implementation/agent.py`
   - Ensure agent can process review feedback

5. `agents/codebuff/src/codebuff/main.py`
   - Update config to include ReviewConfig
   - Pass review config to orchestrator

6. `agents/codebuff/tests/test_review_loop.py` (new)
   - Add integration tests for review loop

## Migration Path

1. Phase 1: Implement basic review_changes that spawns reviewer
2. Phase 2: Add single feedback iteration
3. Phase 3: Extend to multiple iterations with limits
4. Phase 4: Add state persistence
5. Phase 5: Add configuration options
6. Phase 6: Add comprehensive logging

## Notes

- Keep the review loop simple initially - focus on spawning and basic feedback
- The reviewer agent already has the tools; we just need to wire it up
- Don't over-engineer - 3 iterations max should be sufficient
- Make review configurable so it can be disabled for debugging
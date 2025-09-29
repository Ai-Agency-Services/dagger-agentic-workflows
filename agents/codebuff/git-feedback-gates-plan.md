Title: Config-driven Git Feedback Gates (Branch + Draft PR + Resume)

Objective
- Allow orchestrated workflows to pause at deterministic phases (e.g., after PLANNING) and request feedback via branch + PR.
- On resume, rebuild from branch and continue from saved state.

Summary of approach
- Add config toggle, have the orchestrator stop after a configured phase and write state.
- After agent completes (stops early), main.py calls request_feedback_from_self to open a draft PR with .codebuff-state.
- Users comment on PR; repeat runs resume from branch using resume_workflow.

1) Config additions (YAMLConfig)
- Path: shared/dagger-agents-config (Python models)
- Extend config (backwards-compatible):
  yaml
  orchestrator:
    feedback:
      enabled: true               # default false
      stop_after_phase: PLANNING  # one of: PLANNING, IMPLEMENTATION (default: null)
      branch_prefix: "feature/orchestrator-"

- No breaking changes: default to disabled when not provided.

2) Orchestrator stop points (agent side)
- Path: agents/codebuff/src/codebuff/orchestrator/agent.py
- In create_implementation_plan() tool:
  - After writing plan and updating state, check deps.config.orchestrator.feedback.stop_after_phase == 'PLANNING'
  - If matched, write a small sentinel file: .codebuff-state/feedback_sentinel.json
    {
      "phase": "PLANNING",
      "status": "STOPPED_FOR_FEEDBACK",
      "timestamp": "..."
    }
  - Return early with a distinct message: "STOPPED_AFTER_PLANNING"
- Optional future: hook similar stop after execute_implementation if stop_after_phase == 'IMPLEMENTATION'

3) Main integration (request feedback call)
- Path: agents/codebuff/src/codebuff/main.py
- In orchestrate_feature_development():
  - After agent.run(workflow_prompt, deps=deps), inspect: 
    - Either result.output contains the STOPPED_AFTER_PLANNING token
    - Or check for the sentinel file in self.container.directory(".codebuff-state").file("feedback_sentinel.json")
  - If orchestrator.feedback.enabled and a stop sentinel is present:
    - Call request_feedback_from_self(github_token=self.github_token, feature_task_description=feature_task_description, focus_phase=<from sentinel/phase>)
    - Return the feedback acknowledgment string (do not proceed further)

4) Resume flow (already implemented)
- Users run:
  dagger call --mod agents/codebuff resume-workflow \
    --github-token=secret:GITHUB_TOKEN \
    --repository-url https://github.com/org/repo \
    --branch-name feature/orchestrator-<slug>-<ts>
- The function rebuilds container from branch and lists available .codebuff-state files for the user. In a future iteration, we can add a continue-orchestration method that consumes this state and resumes the next phase.

5) Minimal code changes
- shared/dagger-agents-config: add orchestrator.feedback model (enabled: bool, stop_after_phase: Optional[str], branch_prefix: str)
- orchestrator/agent.py: add small check + sentinel write + early return in create_implementation_plan
  Python pseudo:
  if cfg.orchestrator and cfg.orchestrator.feedback and cfg.orchestrator.feedback.stop_after_phase == 'PLANNING':
      await write_text(ctx.deps.container, "feedback_sentinel.json" under .codebuff-state, json)
      return "STOPPED_AFTER_PLANNING"
- main.py: after agent.run(...), detect stop condition and call request_feedback_from_self; return the acknowledgment.

6) Test plan (smoke tests)
- Unit: simulate config with feedback.stop_after_phase='PLANNING', assert create_implementation_plan returns STOPPED_AFTER_PLANNING and writes sentinel.
- Integration-lite: run orchestrate_feature_development with feedback enabled; mock PR agent; assert request_feedback_from_self is called and the function returns the PR prompt message.

7) Future (not in this change)
- Parse PR comments and update a state file (user_feedback.json) to drive resume decisions.
- Add stop_after_phase='IMPLEMENTATION' gate after tests pass, before PR creation.

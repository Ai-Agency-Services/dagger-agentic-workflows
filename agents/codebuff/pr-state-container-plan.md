Title: Container-backed Orchestration State + PR with Code Changes

1) State model and file layout inside the container
- Use a single state directory inside the repo working directory:
  - STATE_DIR = ".codebuff-state" (relative to workdir; workdir-agnostic)
- Files to write during workflow:
  - task.json: { id, goal, focus_area, created_at }
  - exploration.json: { areas_explored, file_index, key_patterns, confidence }
  - selected_files.json: [ { path, reason, score } ]
  - plan.json: { steps: [...], risks: [...], dependencies: [...], confidence, complexity }
  - implementation/
    - diffs/: generated patches or git diff snapshots per step
    - commands.jsonl: JSONL of executed commands
    - summary.json: { edits, commands, notes }
    - test_results.json: { tests_written, tests_passed, test_output, coverage }
  - review.json: review agent output
  - pull_request.json: { branch, pr_number, pr_url, status, message }
  - log.txt: append-only human-readable timeline

2) Shared helper: write JSON/text into container (immutability-safe)
- utils/container_state.py (new):
```py
from __future__ import annotations
import json
import dagger
from typing import Any

STATE_DIR = ".codebuff-state"

def write_json(c: dagger.Container, rel_path: str, data: Any) -> dagger.Container:
    payload = json.dumps(data, indent=2)
    return c.with_new_file(f"{STATE_DIR}/{rel_path}", payload)

def write_text(c: dagger.Container, rel_path: str, text: str) -> dagger.Container:
    return c.with_new_file(f"{STATE_DIR}/{rel_path}", text)

def append_log(c: dagger.Container, line: str) -> dagger.Container:
    """Append to log.txt (best-effort; fallback to new file if read fails)."""
    try:
        existing = await c.file(f"{STATE_DIR}/log.txt").contents()
        content = existing + "\n" + line
    except Exception:
        content = line  # fallback to new file
    return c.with_new_file(f"{STATE_DIR}/log.txt", content)
```
- All agent tools should use these helpers and then set ctx.deps.container = returned_container

3) Extend orchestrator dependencies
- agents/codebuff/src/codebuff/orchestrator/models.py:
  - Ensure OrchestratorDependencies has:
    - container: dagger.Container (already exists)
    - state: OrchestrationState (already present)
    - (optional) state_dir: str = STATE_DIR (if useful)

4) Write state in each step (tool hooks)
- start_task(ctx, task_description, focus_area):
```py
# Pseudo-code
from utils.container_state import write_json, append_log
spec = {"id": state.task_spec.id, "goal": state.task_spec.goal, "focus_area": state.task_spec.focus_area, "created_at": now_iso()}
ctx.deps.container = write_json(ctx.deps.container, "task.json", spec)
ctx.deps.container = append_log(ctx.deps.container, f"start_task: {spec}")
```
- explore_codebase(ctx):
```py
# after agent builds exploration result `report`
ctx.deps.container = write_json(ctx.deps.container, "exploration.json", report)
ctx.deps.container = append_log(ctx.deps.container, "explore_codebase: done")
```
- select_files(ctx):
```py
# after semantic/lexical blend `files` (list of {path, score, reason})
ctx.deps.container = write_json(ctx.deps.container, "selected_files.json", files)
ctx.deps.container = append_log(ctx.deps.container, f"select_files: {len(files)} files")
```
- create_implementation_plan(ctx):
```py
# after generating plan `plan_data`
ctx.deps.container = write_json(ctx.deps.container, "plan.json", plan_data)
ctx.deps.container = append_log(ctx.deps.container, "create_plan: done")
```
- implement_plan(ctx):
```py
# Execute changes inside container
# - run commands to implement feature code
# - generate unit tests for the new feature
# - run test suite to verify tests pass
# - stage/commit changes on a feature branch only if tests pass
# - capture diffs and summary
ctx.deps.container = write_text(ctx.deps.container, "implementation/commands.jsonl", commands_jsonl)
ctx.deps.container = write_json(ctx.deps.container, "implementation/summary.json", summary)
ctx.deps.container = write_json(ctx.deps.container, "implementation/test_results.json", test_results)
# optionally write git patch into implementation/diffs/
ctx.deps.container = append_log(ctx.deps.container, "implement_plan: committed changes with passing tests")
```
- review_changes(ctx):
```py
ctx.deps.container = write_json(ctx.deps.container, "review.json", review)
ctx.deps.container = append_log(ctx.deps.container, "review_changes: done")
```
- create_pull_request(ctx):
```py
# PR agent expects an authenticated container; re-use the working container
# builder.setup_pull_request_container(base_container=ctx.deps.container,...)
# PR module pushes branch and opens PR, returns status and metadata
ctx.deps.container = write_json(ctx.deps.container, "pull_request.json", pr_meta)
ctx.deps.container = append_log(ctx.deps.container, f"PR: {pr_meta}")
```

5) Container mutation pattern (critical)
- Always reassign ctx.deps.container = ctx.deps.container.with_new_file(...)
- This preserves immutability semantics but carries forward the latest container snapshot in dependencies
- Ensure every tool returns string output for agent UX, but side-effect is updating ctx.deps.container

6) Orchestrator wiring changes (minimal)
- In agents/codebuff/src/codebuff/orchestrator/agent.py tools:
  - Import utils/container_state helpers
  - After computing outputs, call write_json/append_log and assign ctx.deps.container
- In agents/codebuff/src/codebuff/main.py:
  - Orchestration calls already pass deps=deps; no further change needed beyond ensuring the initial container is set before the first step
- In create_pull_request() (main.py):
  - Pass the latest ctx.deps.container to builder.setup_pull_request_container(base_container=...)
  - This ensures the repo state + .codebuff-state are present when pushing a branch and creating the PR

7) Git/branching in implement_plan
- Inside implement_plan tool:
  - Setup git config (user.name/email) from config before branching
  - Create feature branch name (e.g., feature/<task_id>)
  - Stage and commit generated changes
  - Write patch into implementation/diffs/<n>.patch (optional convenience)

Pseudo-code:
```py
# Setup git config first (prevent commit failures)
git_config = ctx.deps.config.git
user_name = git_config.get("user_name", "Codebuff Agent")
user_email = git_config.get("user_email", "codebuff@example.com")

# Generate unit tests for the implemented feature
test_cmds = [
  # Implementation agent should generate test files alongside feature code
  # Run test suite to verify functionality
  ["python", "-m", "pytest", "-v", "--tb=short"],
  # Or use project-specific test command from config
]

# Only proceed with git operations if tests pass
branch = f"feature/{state.task_spec.id[:8]}"
git_cmds = [
  ["git", "config", "user.name", user_name],
  ["git", "config", "user.email", user_email],
  ["git", "checkout", "-b", branch],
  ["git", "add", "-A"],
  ["git", "commit", "-m", f"feat: {state.task_spec.goal}\n\nIncludes unit tests with passing test suite"],
]

# Run tests first, only commit if they pass
test_output = ""
for cmd in test_cmds:
  result = await ctx.deps.container.with_exec(["bash", "-lc", " ".join(cmd)])
  test_output += await result.stdout()
  exit_code = await result.exit_code()
  if exit_code != 0:
    return f"Tests failed (exit {exit_code}): {test_output}"

# Tests passed, proceed with git operations
for cmd in git_cmds:
  ctx.deps.container = ctx.deps.container.with_exec(["bash", "-lc", " ".join(cmd)])

# Write test results and diff for debugging/review
ctx.deps.container = write_json(ctx.deps.container, "implementation/test_results.json", {
  "tests_passed": True,
  "test_output": test_output[:5000],  # truncated
  "exit_code": 0
})
stdout = await ctx.deps.container.with_exec(["bash", "-lc", "git diff HEAD~1..HEAD"]).stdout()
ctx.deps.container = write_text(ctx.deps.container, "implementation/diffs/commit.diff", stdout)
```

8) PR creation
- Use builder.setup_pull_request_container(base_container=ctx.deps.container, token=...)
- In PR agent:
  - detect current branch; push to origin
  - open PR (base from config)
  - return pr_number, pr_url, status, message
- Write pull_request.json in STATE_DIR; return a success string to the agent

9) Minimal unit tests (agents/codebuff)
- test_container_state_writes: run fake start_task/select_files/plan; inspect container.files via export() or file(...).contents() to assert state files exist
- test_implement_plan_writes_patch: after a small file modification, ensure implementation/summary.json and diffs exist
- test_end_to_end_orchestrate_writes_pr_json: simulate PR agent returning pr meta; assert pull_request.json exists
- test_final_container_has_code_and_state: export final container and verify both code changes AND .codebuff-state files are present
- test_implementation_includes_tests: verify implementation step generates unit tests and test_results.json shows tests_passed: true

10) Guardrails
- Always handle exceptions writing state files (append to log with error: ...)
- Keep JSON dumps compact and deterministic (sort_keys=True when helpful)
- Avoid in-function imports; import json at module top (we already standardized)
- append_log should handle missing log.txt gracefully (fallback to new file)
- Git setup (user.name/email) must run before any commit operations
- Unit tests must be generated for new features and must pass before committing/creating PR
- Test failure should prevent git commit and PR creation

11) Knowledge updates
- Add a brief section to knowledge.md: "Container-backed Orchestration State" with file layout and the assignment pattern (ctx.deps.container = write_json(...))

12) Deliverables
- utils/container_state.py (new)
- Edits in agents/codebuff/src/codebuff/orchestrator/agent.py tools to write state + reassign container
- Main PR flow uses the working container (already wired via base_container) to include actual code changes
- 2–3 unit tests verifying state writes and PR metadata

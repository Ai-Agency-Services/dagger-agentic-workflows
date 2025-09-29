# Git-based Feedback Demo (agents/codebuff)

This demo shows how to run the orchestrator with a feedback gate after PLANNING. The run stops, creates a working branch + draft PR, and you can resume later from that branch.

## Prerequisites
- Dagger CLI installed and logged in (for --cloud if you use it)
- uv installed
- GitHub token with repo access available as a Dagger secret
- OpenAI or OpenRouter API key available as a Dagger secret or env

## Config
We provide a ready config that enables the PLANNING feedback gate:
- agents/codebuff/demo/feedback-demo.yaml

Key block:
```yaml
orchestrator:
  feedback:
    enabled: true
    stop_after_phase: "PLANNING"
    branch_prefix: "feature/orchestrator-"
```

## 1) Run orchestration with feedback gate
Replace repo URL and branch as needed.
```bash
dagger call --mod agents/codebuff \
  --config-file agents/codebuff/demo/feedback-demo.yaml \
  orchestrate-feature-development \
  --github-token=secret:GITHUB_TOKEN \
  --repository-url https://github.com/YourOrg/your-repo \
  --branch main \
  --feature-task-description "Add user profile management with avatar upload" \
  --openai-api-key=env:OPENAI_API_KEY
```
What happens:
- Orchestrator runs through PLANNING
- Writes .codebuff-state/feedback_sentinel.json
- The module automatically calls request_feedback_from_self
- A working branch + draft PR are created (via PR agent)
- Command returns: "Feedback requested via PR. Working branch: ..."

## 2) Provide feedback on the PR
Comment with one of the supported commands:
- `@orchestrator approve` – proceed
- `@orchestrator modify <instructions>` – adjust plan
- `@orchestrator add-files <paths>` – include files
- `@orchestrator revise-plan <changes>` – update plan
- `@orchestrator cancel` – stop

## 3) Resume from the working branch
Use the branch printed in the previous step (example shown):
```bash
dagger call --mod agents/codebuff \
  --config-file agents/codebuff/demo/feedback-demo.yaml \
  resume-workflow \
  --github-token=secret:GITHUB_TOKEN \
  --repository-url https://github.com/YourOrg/your-repo \
  --branch-name feature/orchestrator-add-user-profile-management-with-avatar-upload-20250126-143022 \
  --openai-api-key=env:OPENAI_API_KEY
```
This recreates the container from that branch, loads .codebuff-state, and returns a summary of available state files.

## Notes
- State sentinel: `.codebuff-state/feedback_sentinel.json` (written at PLANNING gate)
- PR payload: `.codebuff-state/feedback_request.json` (instructions for reviewers)
- To change the stop phase or branch naming, edit feedback-demo.yaml
- Keep Git as your source of truth for workflow state; the PR is where feedback lives

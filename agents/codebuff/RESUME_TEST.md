# Codebuff Resume Flow - Quick Test Guide

## Prerequisites
- Dagger 0.19.0
- A working branch created by a prior run (or your own) that contains `.codebuff-state` in the repo.
- `GITHUB_TOKEN` available as a Dagger secret, and an OpenRouter or OpenAI key if you want to run LLM steps.
- Config file: `agents/codebuff/demo/codebuff-feature-demo.yaml` (or your own)

## 1) Resume from a branch
- Command:
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    resume-workflow \
    --github-token=secret:GITHUB_TOKEN \
    --repository-url https://github.com/<org>/<repo>.git \
    --branch-name <working-branch> \
    --provider openrouter \
    --open-router-api-key=env:OPEN_ROUTER_API_KEY

- Expected output:
  - "Resumed from branch <branch>. Phase: <PHASE>. Loaded: [...], Missing: [...]"
  - If task_spec is missing, it will show a fallback summary using commit metadata.

## 2) Provide approval via PR comment (fast path)
- (A) Quick path using single command text:
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    process-orchestrator-command \
    --github-token=secret:GITHUB_TOKEN \
    --repository-url https://github.com/<org>/<repo>.git \
    --branch <working-branch> \
    --command-text "@orchestrator approve"

- (B) Alternative using parsed comments JSON:
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    process-pr-feedback \
    --comments-json '[{"body":"@orchestrator approve","user":{"login":"you"},"created_at":"2025-10-03T00:00:00Z"}]'

- Expected output: "Saved user_feedback.json: action=approve"

## 3) Continue workflow
- Command:
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    continue-workflow \
    --github-token=secret:GITHUB_TOKEN \
    --repository-url https://github.com/<org>/<repo>.git \
    --branch-name <working-branch> \
    --provider openrouter \
    --open-router-api-key=env:OPEN_ROUTER_API_KEY

- Behaviors:
  - If `.codebuff-state/feedback_sentinel.json` has requested=true and there is no `user_feedback.json`, you’ll see: "Feedback gate active... Waiting for PR feedback".
  - If `user_feedback.action == approve`, it proceeds to the next tool based on the saved phase/status.
  - If `modify/add-files/revise-plan`, it pauses and returns instruction text.

## 4) Handy inspection commands
- Export `.codebuff-state` from the current object’s container:
  dagger call --mod agents/codebuff \
    create --config-file agents/codebuff/demo/codebuff-feature-demo.yaml \
    export-state-from-self export --path ./.codebuff-state

- After resume-workflow/continue-workflow, this lets you inspect state files locally.

## 5) Troubleshooting tips
- Missing state: If `task_spec.json` is missing, you still get phase/status from the last commit footer.
- No targeted tests: Implementation phase handles "no tests collected" as soft-pass.
- Feedback not triggering: Ensure your config enables feedback and that `feedback_sentinel.json` contains `{ "requested": true }`.
- Branch name: If unsure, check `.codebuff-state/feedback_request.json` (key: `proposed_branch`) or your PR branch.


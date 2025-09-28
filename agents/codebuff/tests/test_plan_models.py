import asyncio
import json
from datetime import datetime
from types import SimpleNamespace

import pytest

from codebuff.orchestrator.models import Plan, PlanStep, OrchestrationState, TaskSpec, Phase, Status
from codebuff.orchestrator import agent as orch_agent


class DummyContainer:
    """Minimal stub container used by monkeypatched write helpers."""
    def __init__(self):
        self.files = {}
    def with_new_file(self, path, content):
        self.files[path] = content
        return self


@pytest.mark.unit
def test_plan_steps_string_coercion():
    # list[str] should be coerced into list[PlanStep]
    steps = [
        "Review selected files and understand current implementation",
        "Implement main functionality based on task requirements",
    ]
    plan = Plan(steps=steps, confidence=0.7)
    assert len(plan.steps) == 2
    assert isinstance(plan.steps[0], PlanStep)
    assert plan.steps[0].id == "step-1"
    assert plan.steps[0].description.startswith("Review selected files")
    assert plan.steps[1].id == "step-2"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_implementation_plan_builds_plan_with_plansteps(monkeypatch):
    # Prepare dependencies/state
    task_spec = TaskSpec(
        id="t-123",
        goal="Add user profile management with avatar upload",
        focus_area="auth/profile",
        success_criteria=["tests pass", "feature works"]
    )
    state = OrchestrationState(
        task_id=task_spec.id,
        current_phase=Phase.PLANNING,
        status=Status.PENDING,
        start_time=datetime.now(),
        last_update=datetime.now(),
        task_spec=task_spec,
    )

    deps = SimpleNamespace(
        state=state,
        container=DummyContainer(),
        config=None,
        config_file=None,
        api_key=None,
    )
    ctx = SimpleNamespace(deps=deps)

    # Monkeypatch write helpers used in create_implementation_plan
    async def _noop_write_text(container, path, content):
        container.with_new_file(path, content)
        return container
    async def _noop_write_json(container, path, obj):
        container.with_new_file(path, json.dumps(obj))
        return container
    async def _noop_append_log(container, msg):
        container.with_new_file(".codebuff-state/logs.txt", (container.files.get(".codebuff-state/logs.txt", "") + msg + "\n"))
        return container

    monkeypatch.setattr(orch_agent, "write_text", _noop_write_text)
    monkeypatch.setattr(orch_agent, "write_json", _noop_write_json)
    monkeypatch.setattr(orch_agent, "append_log", _noop_append_log)

    # Execute the planning tool
    out = await orch_agent.create_implementation_plan(ctx, path="TEST_PLAN.md", plan="")
    assert "Implementation plan created" in out

    # Validate state.plan exists and contains PlanStep items
    assert deps.state.plan is not None
    assert len(deps.state.plan.steps) >= 4
    assert all(isinstance(s, PlanStep) for s in deps.state.plan.steps)

    # Validate that the plan markdown was saved
    assert "TEST_PLAN.md" in deps.container.files
    assert deps.container.files["TEST_PLAN.md"].startswith("# Implementation Plan")

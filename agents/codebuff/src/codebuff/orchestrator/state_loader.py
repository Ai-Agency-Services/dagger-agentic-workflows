from typing import Optional, Tuple
import json
from pydantic import ValidationError
from dagger import Container

from .models import TaskSpec, ExplorationReport, FileSet, Plan, OrchestrationState, Phase, Status, PathInfo

STATE_DIR = ".codebuff-state"

async def _read_json(container: Container, rel_path: str) -> Optional[dict]:
    try:
        raw = await container.file(f"{STATE_DIR}/{rel_path}").contents()
        return json.loads(raw) if raw else None
    except Exception:
        return None

async def load_orchestration_state(container: Container) -> Tuple[Optional[OrchestrationState], dict]:
    """Load state files from .codebuff-state with legacy fallbacks; return (state, report)."""
    report = {"loaded": [], "missing": []}

    # Task spec (legacy: task.json)
    task_data = await _read_json(container, "task_spec.json") or await _read_json(container, "task.json")
    if task_data:
        try:
            task_spec = TaskSpec(**task_data)
            report["loaded"].append("task_spec.json")
        except ValidationError:
            task_spec = None
            report["missing"].append("task_spec.json:invalid")
    else:
        task_spec = None
        report["missing"].append("task_spec.json")

    # Exploration and selection
    exploration = await _read_json(container, "exploration_results.json")
    file_sel = await _read_json(container, "selected_files.json")

    exploration_report = None
    if exploration:
        try:
            # Normalize PathInfo list if needed
            if "file_index" in exploration and exploration["file_index"] and isinstance(exploration["file_index"][0], str):
                exploration["file_index"] = [
                    PathInfo(path=p).__dict__ for p in exploration["file_index"]
                ]
            exploration_report = ExplorationReport(**exploration)
            report["loaded"].append("exploration_results.json")
        except ValidationError:
            report["missing"].append("exploration_results.json:invalid")

    file_set = None
    if file_sel:
        try:
            # Normalize FileSet.files to PathInfo if strings
            if "files" in file_sel and file_sel["files"] and isinstance(file_sel["files"][0], str):
                file_set = FileSet(
                    files=[PathInfo(path=p) for p in file_sel["files"]],
                    rationale=file_sel.get("rationale", "selection"),
                    total_files_considered=file_sel.get("total_files_considered", len(file_sel["files"])),
                    confidence=file_sel.get("confidence", 0.7),
                )
            else:
                file_set = FileSet(**file_sel)
            report["loaded"].append("selected_files.json")
        except ValidationError:
            report["missing"].append("selected_files.json:invalid")

    # Plan (canonical)
    plan_json = await _read_json(container, "implementation_plan.json")
    plan = None
    if plan_json:
        try:
            plan = Plan(**plan_json)
            report["loaded"].append("implementation_plan.json")
        except ValidationError:
            report["missing"].append("implementation_plan.json:invalid")

    # Phase snapshot
    phase_json = await _read_json(container, "current_phase.json") or {}
    phase_val = phase_json.get("phase")
    status_val = phase_json.get("status")

    # Build minimal OrchestrationState (defensive defaults)
    if task_spec is None:
        return None, report

    try:
        state = OrchestrationState(
            task_id=task_spec.id,
            current_phase=Phase(phase_val) if phase_val else Phase.EXPLORATION,
            status=Status(status_val) if status_val else Status.IN_PROGRESS,
            start_time=phase_json.get("start_time") or phase_json.get("timestamp") or "1970-01-01T00:00:00Z",
            last_update=phase_json.get("timestamp") or "1970-01-01T00:00:00Z",
            task_spec=task_spec,
            exploration_report=exploration_report,
            file_set=file_set,
            plan=plan,
        )
    except Exception:
        # As a fallback, build a minimal viable state with defaults
        state = None

    return state, report

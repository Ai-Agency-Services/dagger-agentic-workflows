import asyncio
import json
from datetime import datetime
from types import SimpleNamespace

import pytest

from codebuff.orchestrator.models import OrchestrationState, TaskSpec, Phase, Status, Constitution, Spec, Task

# Legacy Plan/PlanStep tests removed - these models no longer exist in spec-kit workflow
# The spec-kit workflow uses Constitution → Spec → Task models instead

@pytest.mark.unit
def test_spec_kit_models_basic():
    """Test that spec-kit models can be instantiated."""
    constitution = Constitution(
        values=["Code quality", "Test coverage"],
        constraints=["Use existing patterns"],
        quality_gates=["All tests pass", "No linting errors"]
    )
    assert len(constitution.values) == 2
    assert len(constitution.quality_gates) == 2
    
    spec = Spec(
        objective="Build user profile feature",
        requirements=[],
        success_criteria=["Feature works", "Tests pass"],
        out_of_scope=["Admin features"]
    )
    assert spec.objective == "Build user profile feature"
    
    task = Task(
        id="TASK-001",
        description="Implement profile endpoint",
        acceptance_criteria=["Returns 200", "Validates input"],
        dependencies=[],
        estimated_complexity="simple",
        files_to_modify=["api/profile.py"]
    )
    assert task.id == "TASK-001"
    assert task.estimated_complexity == "simple"

"""Tests for spec-kit workflow functions."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from codebuff.orchestrator.models import (
    Constitution,
    Requirement,
    Spec,
    Task,
    TaskDependency,
    ValidationError,
)
from codebuff.orchestrator.speckit_workflow import (
    validate_constitution,
    validate_spec,
    validate_tasks,
    get_topological_order,
)


class TestConstitutionValidation:
    """Test constitution validation."""
    
    async def test_valid_constitution(self):
        """Valid constitution passes validation."""
        constitution = Constitution(
            values=["Maintainability", "Performance"],
            constraints=["No breaking changes"],
            quality_gates=["All tests pass", "Code coverage >80%"]
        )
        
        result = await validate_constitution(constitution)
        assert result is True
    
    async def test_invalid_constitution_missing_values(self):
        """Constitution with <2 values fails."""
        constitution = Constitution(
            values=["Maintainability"],  # Only 1
            constraints=["No breaking changes"],
            quality_gates=["All tests pass"]
        )
        
        result = await validate_constitution(constitution)
        assert result is False
    
    async def test_invalid_constitution_empty_strings(self):
        """Constitution with empty strings fails."""
        constitution = Constitution(
            values=["Maintainability", ""],  # Empty value
            constraints=["No breaking changes"],
            quality_gates=["All tests pass"]
        )
        
        result = await validate_constitution(constitution)
        assert result is False


class TestSpecValidation:
    """Test spec validation."""
    
    def create_valid_constitution(self) -> Constitution:
        """Helper to create valid constitution."""
        return Constitution(
            values=["Maintainability", "Performance"],
            constraints=["No breaking changes"],
            quality_gates=["All tests pass", "Performance <100ms"]
        )
    
    async def test_valid_spec(self):
        """Valid spec passes validation."""
        constitution = self.create_valid_constitution()
        spec = Spec(
            objective="Add user authentication feature",
            requirements=[
                Requirement(
                    id="REQ-001",
                    description="User can login with email",
                    acceptance_criteria=[
                        "Email validation works",
                        "Password is hashed",
                        "Login returns JWT token"
                    ],
                    priority="must"
                )
            ],
            success_criteria=["All tests pass", "Performance is <100ms"],
            out_of_scope=["Social login", "2FA"]
        )
        
        valid, issues = await validate_spec(spec, constitution)
        assert valid is True
        assert len(issues) == 0
    
    async def test_spec_missing_objective(self):
        """Spec without objective fails."""
        constitution = self.create_valid_constitution()
        spec = Spec(
            objective="",  # Empty
            requirements=[],
            success_criteria=[],
            out_of_scope=[]
        )
        
        valid, issues = await validate_spec(spec, constitution)
        assert valid is False
        assert any("objective" in issue.lower() for issue in issues)
    
    async def test_spec_duplicate_requirement_ids(self):
        """Spec with duplicate requirement IDs fails."""
        constitution = self.create_valid_constitution()
        spec = Spec(
            objective="Add feature",
            requirements=[
                Requirement(
                    id="REQ-001",
                    description="First requirement",
                    acceptance_criteria=["Criterion 1", "Criterion 2"],
                    priority="must"
                ),
                Requirement(
                    id="REQ-001",  # Duplicate!
                    description="Second requirement",
                    acceptance_criteria=["Criterion 3"],
                    priority="should"
                )
            ],
            success_criteria=["Tests pass"],
            out_of_scope=["Advanced features"]
        )
        
        valid, issues = await validate_spec(spec, constitution)
        assert valid is False
        assert any("duplicate" in issue.lower() for issue in issues)
    
    async def test_spec_vague_acceptance_criteria(self):
        """Spec with vague acceptance criteria fails."""
        constitution = self.create_valid_constitution()
        spec = Spec(
            objective="Add feature",
            requirements=[
                Requirement(
                    id="REQ-001",
                    description="User can login",
                    acceptance_criteria=["works"],  # Too vague!
                    priority="must"
                )
            ],
            success_criteria=["Tests pass"],
            out_of_scope=["Social login"]
        )
        
        valid, issues = await validate_spec(spec, constitution)
        assert valid is False
        assert any("vague" in issue.lower() or "too vague" in issue.lower() for issue in issues)


class TestTaskValidation:
    """Test task validation."""
    
    def create_valid_spec(self) -> Spec:
        """Helper to create valid spec."""
        return Spec(
            objective="Add authentication",
            requirements=[
                Requirement(
                    id="REQ-001",
                    description="User login",
                    acceptance_criteria=["Works correctly"],
                    priority="must"
                )
            ],
            success_criteria=["Tests pass"],
            out_of_scope=["Social login"]
        )
    
    async def test_valid_tasks(self):
        """Valid tasks pass validation."""
        spec = self.create_valid_spec()
        tasks = [
            Task(
                id="TASK-001",
                description="Implement login endpoint",
                acceptance_criteria=["Returns 200 on success", "Returns 401 on bad credentials"],
                dependencies=[],
                estimated_complexity="moderate",
                test_requirements=["tests/test_auth.py"],
                files_to_modify=["src/auth/routes.py"]
            )
        ]
        
        valid, issues = await validate_tasks(tasks, spec)
        assert valid is True
        assert len(issues) == 0
    
    async def test_tasks_circular_dependency(self):
        """Tasks with circular dependencies fail."""
        spec = self.create_valid_spec()
        tasks = [
            Task(
                id="TASK-001",
                description="Task 1",
                acceptance_criteria=["Done"],
                dependencies=[
                    TaskDependency(task_id="TASK-002", dependency_type="blocks")
                ],
                estimated_complexity="simple",
                files_to_modify=["file1.py"]
            ),
            Task(
                id="TASK-002",
                description="Task 2",
                acceptance_criteria=["Done"],
                dependencies=[
                    TaskDependency(task_id="TASK-001", dependency_type="blocks")  # Circular!
                ],
                estimated_complexity="simple",
                files_to_modify=["file2.py"]
            )
        ]
        
        valid, issues = await validate_tasks(tasks, spec)
        assert valid is False
        assert any("circular" in issue.lower() for issue in issues)
    
    async def test_tasks_invalid_dependency(self):
        """Task depending on non-existent task fails."""
        spec = self.create_valid_spec()
        tasks = [
            Task(
                id="TASK-001",
                description="Task 1",
                acceptance_criteria=["Done"],
                dependencies=[
                    TaskDependency(task_id="TASK-999", dependency_type="blocks")  # Doesn't exist!
                ],
                estimated_complexity="simple",
                files_to_modify=["file1.py"]
            )
        ]
        
        valid, issues = await validate_tasks(tasks, spec)
        assert valid is False
        assert any("non-existent" in issue.lower() for issue in issues)
    
    async def test_tasks_missing_acceptance_criteria(self):
        """Task without acceptance criteria fails."""
        spec = self.create_valid_spec()
        tasks = [
            Task(
                id="TASK-001",
                description="Task 1",
                acceptance_criteria=[],  # Empty!
                dependencies=[],
                estimated_complexity="simple",
                files_to_modify=["file1.py"]
            )
        ]
        
        valid, issues = await validate_tasks(tasks, spec)
        assert valid is False
        assert any("acceptance criteria" in issue.lower() for issue in issues)


class TestTopologicalOrder:
    """Test topological sorting of tasks."""
    
    def test_simple_linear_order(self):
        """Tasks with linear dependencies ordered correctly."""
        tasks = [
            Task(
                id="TASK-003",
                description="Task 3",
                acceptance_criteria=["Done"],
                dependencies=[
                    TaskDependency(task_id="TASK-002", dependency_type="blocks")
                ],
                estimated_complexity="simple",
                files_to_modify=["file3.py"]
            ),
            Task(
                id="TASK-001",
                description="Task 1",
                acceptance_criteria=["Done"],
                dependencies=[],
                estimated_complexity="simple",
                files_to_modify=["file1.py"]
            ),
            Task(
                id="TASK-002",
                description="Task 2",
                acceptance_criteria=["Done"],
                dependencies=[
                    TaskDependency(task_id="TASK-001", dependency_type="blocks")
                ],
                estimated_complexity="simple",
                files_to_modify=["file2.py"]
            ),
        ]
        
        ordered = get_topological_order(tasks)
        ordered_ids = [t.id for t in ordered]
        
        assert ordered_ids == ["TASK-001", "TASK-002", "TASK-003"]
    
    def test_parallel_tasks(self):
        """Independent tasks can be in any order."""
        tasks = [
            Task(
                id="TASK-001",
                description="Task 1",
                acceptance_criteria=["Done"],
                dependencies=[],
                estimated_complexity="simple",
                files_to_modify=["file1.py"]
            ),
            Task(
                id="TASK-002",
                description="Task 2",
                acceptance_criteria=["Done"],
                dependencies=[],
                estimated_complexity="simple",
                files_to_modify=["file2.py"]
            ),
        ]
        
        ordered = get_topological_order(tasks)
        
        # Both orderings are valid
        assert len(ordered) == 2
        assert set(t.id for t in ordered) == {"TASK-001", "TASK-002"}
    
    def test_complex_dag(self):
        """Complex dependency DAG ordered correctly."""
        #     TASK-001
        #     /      \\
        # TASK-002  TASK-003
        #     \\      /
        #     TASK-004
        
        tasks = [
            Task(
                id="TASK-004",
                description="Task 4",
                acceptance_criteria=["Done"],
                dependencies=[
                    TaskDependency(task_id="TASK-002", dependency_type="blocks"),
                    TaskDependency(task_id="TASK-003", dependency_type="blocks")
                ],
                estimated_complexity="simple",
                files_to_modify=["file4.py"]
            ),
            Task(
                id="TASK-002",
                description="Task 2",
                acceptance_criteria=["Done"],
                dependencies=[
                    TaskDependency(task_id="TASK-001", dependency_type="blocks")
                ],
                estimated_complexity="simple",
                files_to_modify=["file2.py"]
            ),
            Task(
                id="TASK-001",
                description="Task 1",
                acceptance_criteria=["Done"],
                dependencies=[],
                estimated_complexity="simple",
                files_to_modify=["file1.py"]
            ),
            Task(
                id="TASK-003",
                description="Task 3",
                acceptance_criteria=["Done"],
                dependencies=[
                    TaskDependency(task_id="TASK-001", dependency_type="blocks")
                ],
                estimated_complexity="simple",
                files_to_modify=["file3.py"]
            ),
        ]
        
        ordered = get_topological_order(tasks)
        ordered_ids = [t.id for t in ordered]
        
        # TASK-001 must be first
        assert ordered_ids[0] == "TASK-001"
        
        # TASK-004 must be last
        assert ordered_ids[-1] == "TASK-004"
        
        # TASK-002 and TASK-003 must be before TASK-004
        task_002_idx = ordered_ids.index("TASK-002")
        task_003_idx = ordered_ids.index("TASK-003")
        task_004_idx = ordered_ids.index("TASK-004")
        
        assert task_002_idx < task_004_idx
        assert task_003_idx < task_004_idx

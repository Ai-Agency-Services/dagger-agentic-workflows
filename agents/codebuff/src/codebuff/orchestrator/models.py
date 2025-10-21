"""Pydantic models for structured inter-agent communication."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic import BaseModel, Field, field_validator
from pydantic_ai.models.openai import OpenAIChatModel


class Phase(str, Enum):
    """Orchestration workflow phases."""
    INITIALIZATION = "initialization"
    EXPLORATION = "exploration"
    FILE_SELECTION = "file_selection"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    PULL_REQUEST = "pull_request"
    CONTEXT_PRUNING = "context_pruning"
    COMPLETE = "complete"
    FAILED = "failed"


class Status(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class ErrorKind(str, Enum):
    """Error classification for better handling."""
    TOOL_ERROR = "tool_error"
    VALIDATION_ERROR = "validation_error"
    MODEL_ERROR = "model_error"
    RESOURCE_ERROR = "resource_error"
    POLICY_ERROR = "policy_error"


class TaskSpec(BaseModel):
    """Input specification for orchestration."""
    id: str = Field(description="Unique task identifier")
    goal: str = Field(description="High-level description of what to accomplish")
    focus_area: Optional[str] = Field(default=None, description="Specific area to focus exploration")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Execution constraints")
    success_criteria: List[str] = Field(default_factory=list, description="Measurable success criteria")


class PathInfo(BaseModel):
    """Information about a file path."""
    path: str
    relevance_score: Optional[float] = None
    rationale: Optional[str] = None


class ExplorationReport(BaseModel):
    """Results from file exploration agent."""
    areas_explored: List[str]
    file_index: List[PathInfo]
    key_patterns: List[str] = Field(default_factory=list)
    architecture_notes: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class FileSet(BaseModel):
    """Selected files with rationale."""
    files: List[PathInfo]
    rationale: str
    total_files_considered: int
    confidence: float = Field(ge=0.0, le=1.0)


# Legacy models removed - use Spec-Kit models instead


class OrchestrationError(BaseModel):
    """Structured error information."""
    kind: ErrorKind
    message: str
    phase: Phase
    retry_count: int = 0
    recoverable: bool = True
    context: Dict[str, Any] = Field(default_factory=dict)


class PullRequestResult(BaseModel):
    """Results from pull request creation."""
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    branch_name: str
    commit_hash: Optional[str] = None
    status: str  # created, updated, failed
    message: str


# ============================================================================
# Spec-Kit Models (Constitution → Spec → Plan → Tasks methodology)
# ============================================================================

class Constitution(BaseModel):
    """Project constitution defining core values and constraints."""
    values: List[str] = Field(description="Core values guiding implementation (2-4 items)")
    constraints: List[str] = Field(description="Technical or business constraints (1-3 items)")
    quality_gates: List[str] = Field(description="Measurable quality gates (2-4 items)")


class Requirement(BaseModel):
    """Individual requirement from the spec."""
    id: str = Field(description="Unique ID (e.g., REQ-001)")
    description: str = Field(description="What needs to be built")
    acceptance_criteria: List[str] = Field(description="Testable conditions (2-4 items)")
    priority: Literal["must", "should", "could"] = Field(description="MoSCoW priority")


class Spec(BaseModel):
    """Detailed specification of what to build."""
    objective: str = Field(description="Clear 1-2 sentence goal")
    requirements: List[Requirement] = Field(description="Distinct requirements (3-10 items)")
    success_criteria: List[str] = Field(description="How we measure completion (2-5 items)")
    out_of_scope: List[str] = Field(description="What we're NOT doing (2-4 items)")


class TaskDependency(BaseModel):
    """Dependency between tasks."""
    task_id: str = Field(description="ID of the task this depends on")
    dependency_type: Literal["blocks", "requires"] = Field(
        description="'blocks' = must finish first, 'requires' = needs output from"
    )


class Task(BaseModel):
    """Individual implementation task."""
    id: str = Field(description="Unique ID (e.g., TASK-001)")
    description: str = Field(description="One-sentence summary")
    acceptance_criteria: List[str] = Field(description="Testable conditions (2-4 items)")
    dependencies: List[TaskDependency] = Field(default_factory=list, description="Task dependencies")
    estimated_complexity: Literal["simple", "moderate", "complex"] = Field(
        description="Complexity level"
    )
    test_requirements: List[str] = Field(default_factory=list, description="Test files to create/run")
    files_to_modify: List[str] = Field(description="File paths to modify")


class SpecKitPlan(BaseModel):
    """Complete spec-kit based plan."""
    constitution: Constitution
    spec: Spec
    tasks: List[Task]
    validation_status: Dict[str, bool] = Field(
        default_factory=dict,
        description="Track validation at each stage"
    )


# ============================================================================
# Error Handling for Spec-Kit Workflow
# ============================================================================

class OrchestrationException(Exception):
    """Base exception for orchestration errors."""
    pass


class ValidationError(OrchestrationException):
    """Raised when validation fails."""
    
    def __init__(self, message: str, issues: List[str]):
        super().__init__(message)
        self.issues = issues


class StateError(OrchestrationException):
    """Raised when state operations fail."""
    pass


class LLMGenerationError(OrchestrationException):
    """Raised when LLM generation fails after retries."""
    pass


class TaskExecutionError(OrchestrationException):
    """Raised when task execution fails."""
    
    def __init__(self, message: str, task_id: str = ""):
        super().__init__(message)
        self.task_id = task_id


class OrchestrationState(BaseModel):
    """Complete state of orchestration execution."""
    task_id: str
    current_phase: Phase
    status: Status
    start_time: datetime
    last_update: datetime
    retry_count: int = 0
    
    # Core phase artifacts (backward compatible)
    task_spec: Optional[TaskSpec] = None
    exploration_report: Optional[ExplorationReport] = None
    file_set: Optional[FileSet] = None
    pull_request_result: Optional[PullRequestResult] = None
    
    # Spec-Kit artifacts
    constitution: Optional[Constitution] = None
    spec: Optional[Spec] = None
    current_task: Optional[Task] = None
    completed_tasks: List[Task] = Field(default_factory=list)
    
    # Error tracking
    errors: List[OrchestrationError] = Field(default_factory=list)
    
    # Metrics
    total_tokens_used: int = 0
    total_requests: int = 0
    phase_durations: Dict[str, float] = Field(default_factory=dict)


@dataclass
class OrchestratorDependencies:
    """Dependencies for the orchestrator agent."""
    config: YAMLConfig
    config_file: dagger.File
    container: dagger.Container
    api_key: dagger.Secret
    github_token: Optional[dagger.Secret] = None

    # Optional model for sub-agents
    model: Optional[Any] = None

    # Lazy-loaded sub-agents (PydanticAI Agent instances)
    file_explorer_agent: Optional[Any] = None  # Agent type
    file_picker_agent: Optional[Any] = None
    implementation_agent: Optional[Any] = None
    reviewer_agent: Optional[Any] = None
    researcher_agent: Optional[Any] = None
    thinker_agent: Optional[Any] = None
    context_pruner_agent: Optional[Any] = None

    # Legacy sub-agent instances (deprecated, for backward compatibility)
    file_explorer: Optional[OpenAIChatModel] = None
    file_picker: Optional[OpenAIChatModel] = None
    researcher: Optional[OpenAIChatModel] = None
    thinker: Optional[OpenAIChatModel] = None
    reviewer: Optional[OpenAIChatModel] = None
    implementation: Optional[OpenAIChatModel] = None
    context_pruner: Optional[OpenAIChatModel] = None

    # Workflow state
    state: Optional[OrchestrationState] = None
    test_env_cfg_json: Optional[str] = None  # JSON from detect_test_env
    # Final command from get_test_command
    test_command: Optional[str] = None

    # Orchestration scratch
    current_task: Optional[TaskSpec] = None
    selected_files: list[str] = None
    exploration_results: Optional[str] = None
    
    def get_file_explorer(self) -> Any:
        """Lazy-load file explorer agent."""
        if self.file_explorer_agent is None:
            from ..file_explorer.agent import create_file_explorer_agent
            self.file_explorer_agent = create_file_explorer_agent(self.model)
        return self.file_explorer_agent
    
    def get_implementation(self) -> Any:
        """Lazy-load implementation agent."""
        if self.implementation_agent is None:
            from ..implementation.agent import create_implementation_agent
            self.implementation_agent = create_implementation_agent(self.model)
        return self.implementation_agent
    
    def get_reviewer(self) -> Any:
        """Lazy-load reviewer agent."""
        if self.reviewer_agent is None:
            from ..reviewer.agent import create_reviewer_agent
            self.reviewer_agent = create_reviewer_agent(self.model)
        return self.reviewer_agent


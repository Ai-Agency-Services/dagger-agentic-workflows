"""Pydantic models for structured inter-agent communication."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field
import dagger
from ais_dagger_agents_config import YAMLConfig


class Phase(str, Enum):
    """Orchestration workflow phases."""
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


class PlanStep(BaseModel):
    """Individual step in implementation plan."""
    id: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    risk_level: str = Field(default="low")  # low, medium, high
    estimated_effort: Optional[str] = None


class Plan(BaseModel):
    """Detailed implementation plan."""
    steps: List[PlanStep]
    risks: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    test_strategy: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    estimated_complexity: str = Field(default="medium")  # low, medium, high


class FileEdit(BaseModel):
    """Individual file modification."""
    path: str
    operation: str  # create, modify, delete
    content_preview: Optional[str] = None
    line_count_change: Optional[int] = None


class CommandExecution(BaseModel):
    """Command that was executed."""
    command: str
    exit_code: Optional[int] = None
    output_preview: Optional[str] = None


class ChangeSet(BaseModel):
    """All changes made during implementation."""
    edits: List[FileEdit]
    commands: List[CommandExecution]
    migration_notes: Optional[str] = None
    rollback_instructions: Optional[str] = None


class ReviewFinding(BaseModel):
    """Individual review finding."""
    category: str  # syntax, logic, style, security, performance
    severity: str  # info, warning, error, critical
    description: str
    file_path: Optional[str] = None
    suggestion: Optional[str] = None


class ReviewReport(BaseModel):
    """Results from code review agent."""
    findings: List[ReviewFinding]
    overall_status: Status
    tests_passed: Optional[bool] = None
    syntax_valid: Optional[bool] = None
    recommendations: List[str] = Field(default_factory=list)
    approval_status: str = Field(default="pending")  # approved, rejected, needs_changes


class ContextSummary(BaseModel):
    """Results from context pruning."""
    original_size: int
    pruned_size: int
    reduction_percent: float
    strategy_used: str
    token_estimate: int
    preserved_sections: List[str] = Field(default_factory=list)


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


class OrchestrationState(BaseModel):
    """Complete state of orchestration execution."""
    task_id: str
    current_phase: Phase
    status: Status
    start_time: datetime
    last_update: datetime
    retry_count: int = 0
    
    # Phase artifacts
    task_spec: Optional[TaskSpec] = None
    exploration_report: Optional[ExplorationReport] = None
    file_set: Optional[FileSet] = None
    plan: Optional[Plan] = None
    change_set: Optional[ChangeSet] = None
    review_report: Optional[ReviewReport] = None
    pull_request_result: Optional[PullRequestResult] = None
    context_summary: Optional[ContextSummary] = None
    
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
    container: dagger.Container
    codebuff_module: Any  # Reference to the Codebuff module instance
    api_key: dagger.Secret
    state: Optional[OrchestrationState] = None
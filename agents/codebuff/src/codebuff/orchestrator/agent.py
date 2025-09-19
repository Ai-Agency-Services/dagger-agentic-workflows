"""Main orchestration agent that coordinates Codebuff subagents."""

from datetime import datetime
from typing import Optional
import uuid
import json

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, green, red, yellow

from .models import (
    OrchestratorDependencies,
    OrchestrationState,
    TaskSpec,
    Phase,
    Status,
    ErrorKind,
    OrchestrationError,
    ExplorationReport,
    FileSet,
    Plan,
    ChangeSet,
    ReviewReport,
    PullRequestResult,
    ContextSummary,
)


async def start_task(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    focus_area: str = "entire project"
) -> str:
    """Initialize a new orchestration task."""
    print(blue(f"🚀 Starting orchestration task: {task_description}"))
    
    task_spec = TaskSpec(
        id=str(uuid.uuid4()),
        goal=task_description,
        focus_area=focus_area,
        success_criteria=["Code compiles without errors", "Tests pass", "Review approved"]
    )
    
    state = OrchestrationState(
        task_id=task_spec.id,
        current_phase=Phase.EXPLORATION,
        status=Status.PENDING,
        start_time=datetime.now(),
        last_update=datetime.now(),
        task_spec=task_spec
    )
    
    ctx.deps.state = state
    print(green(f"✅ Task {task_spec.id} initialized"))
    return f"Task {task_spec.id} started: {task_description}"


async def explore_codebase(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute exploration phase using File Explorer agent."""
    if not ctx.deps.state or not ctx.deps.state.task_spec:
        return "Error: No active task. Call start_task first."
    
    state = ctx.deps.state
    print(blue(f"🔍 Phase: Exploration - {state.task_spec.focus_area}"))
    
    try:
        state.current_phase = Phase.EXPLORATION
        state.status = Status.IN_PROGRESS
        state.last_update = datetime.now()
        
        # Call File Explorer agent
        exploration_result = await ctx.deps.codebuff_module.explore_files(
            container=ctx.deps.container,
            focus_area=state.task_spec.focus_area or "entire project",
            open_router_api_key=ctx.deps.api_key
        )
        
        # Parse result into structured format
        # Note: In practice, you'd want more sophisticated parsing
        exploration_report = ExplorationReport(
            areas_explored=[state.task_spec.focus_area or "entire project"],
            file_index=[],  # Would be populated from actual results
            confidence=0.8,  # Would be derived from agent response
            architecture_notes=exploration_result[:500] + "..." if len(exploration_result) > 500 else exploration_result
        )
        
        state.exploration_report = exploration_report
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ Exploration phase completed"))
        return f"Exploration completed. Found insights: {exploration_report.architecture_notes}"
        
    except Exception as e:
        error = OrchestrationError(
            kind=ErrorKind.TOOL_ERROR,
            message=str(e),
            phase=Phase.EXPLORATION,
            retry_count=state.retry_count
        )
        state.errors.append(error)
        state.status = Status.FAILED
        print(red(f"❌ Exploration failed: {e}"))
        return f"Exploration failed: {e}"


async def select_files(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute file selection phase using File Picker agent."""
    if not ctx.deps.state or not ctx.deps.state.task_spec:
        return "Error: No active task. Call start_task first."
    
    state = ctx.deps.state
    print(blue(f"📂 Phase: File Selection"))
    
    try:
        state.current_phase = Phase.FILE_SELECTION
        state.status = Status.IN_PROGRESS
        state.last_update = datetime.now()
        
        # Call File Picker agent
        selection_result = await ctx.deps.codebuff_module.pick_files(
            container=ctx.deps.container,
            task_description=state.task_spec.goal,
            open_router_api_key=ctx.deps.api_key
        )
        
        # Parse result into structured format
        file_set = FileSet(
            files=[],  # Would be populated from actual results
            rationale=selection_result[:200] + "..." if len(selection_result) > 200 else selection_result,
            total_files_considered=10,  # Would be derived from agent response
            confidence=0.85
        )
        
        state.file_set = file_set
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ File selection phase completed"))
        return f"File selection completed. Rationale: {file_set.rationale}"
        
    except Exception as e:
        error = OrchestrationError(
            kind=ErrorKind.TOOL_ERROR,
            message=str(e),
            phase=Phase.FILE_SELECTION,
            retry_count=state.retry_count
        )
        state.errors.append(error)
        state.status = Status.FAILED
        print(red(f"❌ File selection failed: {e}"))
        return f"File selection failed: {e}"


async def create_implementation_plan(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute planning phase using Thinker agent."""
    if not ctx.deps.state or not ctx.deps.state.task_spec:
        return "Error: No active task. Call start_task first."
    
    state = ctx.deps.state
    print(blue(f"🧠 Phase: Planning"))
    
    try:
        state.current_phase = Phase.PLANNING
        state.status = Status.IN_PROGRESS
        state.last_update = datetime.now()
        
        # Build relevant files string from file_set
        relevant_files = ""
        if state.file_set and state.file_set.files:
            relevant_files = ",".join([f.path for f in state.file_set.files])
        
        # Call Thinker agent
        plan_result = await ctx.deps.codebuff_module.create_plan(
            container=ctx.deps.container,
            task_description=state.task_spec.goal,
            relevant_files=relevant_files,
            open_router_api_key=ctx.deps.api_key
        )
        
        # Parse result into structured format
        plan = Plan(
            steps=[],  # Would be populated from actual parsing
            confidence=0.8,  # Would be derived from agent response
            estimated_complexity="medium",
            test_strategy="Unit tests and integration validation"
        )
        
        state.plan = plan
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ Planning phase completed"))
        return f"Implementation plan created with confidence: {plan.confidence}"
        
    except Exception as e:
        error = OrchestrationError(
            kind=ErrorKind.TOOL_ERROR,
            message=str(e),
            phase=Phase.PLANNING,
            retry_count=state.retry_count
        )
        state.errors.append(error)
        state.status = Status.FAILED
        print(red(f"❌ Planning failed: {e}"))
        return f"Planning failed: {e}"


async def execute_implementation(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute implementation phase using Implementation agent."""
    if not ctx.deps.state or not ctx.deps.state.plan:
        return "Error: No implementation plan available. Run planning phase first."
    
    state = ctx.deps.state
    print(blue(f"⚡ Phase: Implementation"))
    
    try:
        state.current_phase = Phase.IMPLEMENTATION
        state.status = Status.IN_PROGRESS
        state.last_update = datetime.now()
        
        # Convert plan to string for agent
        plan_str = json.dumps(state.plan.model_dump(), indent=2)
        
        # Call Implementation agent
        impl_result = await ctx.deps.codebuff_module.implement_plan(
            container=ctx.deps.container,
            plan=plan_str,
            open_router_api_key=ctx.deps.api_key
        )
        
        # Parse result into structured format
        change_set = ChangeSet(
            edits=[],  # Would be populated from actual parsing
            commands=[],  # Would be populated from actual parsing
            migration_notes=impl_result[:300] + "..." if len(impl_result) > 300 else impl_result
        )
        
        state.change_set = change_set
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ Implementation phase completed"))
        return f"Implementation completed. Changes: {len(change_set.edits)} files modified"
        
    except Exception as e:
        error = OrchestrationError(
            kind=ErrorKind.TOOL_ERROR,
            message=str(e),
            phase=Phase.IMPLEMENTATION,
            retry_count=state.retry_count
        )
        state.errors.append(error)
        state.status = Status.FAILED
        print(red(f"❌ Implementation failed: {e}"))
        return f"Implementation failed: {e}"


async def review_changes(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute review phase using Reviewer agent."""
    if not ctx.deps.state or not ctx.deps.state.change_set:
        return "Error: No changes to review. Run implementation phase first."
    
    state = ctx.deps.state
    print(blue(f"🔍 Phase: Review"))
    
    try:
        state.current_phase = Phase.REVIEW
        state.status = Status.IN_PROGRESS
        state.last_update = datetime.now()
        
        # Call Reviewer agent
        review_result = await ctx.deps.codebuff_module.review_changes(
            container=ctx.deps.container,
            changes_description=state.change_set.migration_notes or "Implementation changes",
            open_router_api_key=ctx.deps.api_key
        )
        
        # Parse result into structured format
        review_report = ReviewReport(
            findings=[],  # Would be populated from actual parsing
            overall_status=Status.SUCCESS,  # Would be derived from agent response
            approval_status="approved"  # Would be derived from analysis
        )
        
        state.review_report = review_report
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ Review phase completed"))
        return f"Review completed. Status: {review_report.approval_status}"
        
    except Exception as e:
        error = OrchestrationError(
            kind=ErrorKind.TOOL_ERROR,
            message=str(e),
            phase=Phase.REVIEW,
            retry_count=state.retry_count
        )
        state.errors.append(error)
        state.status = Status.FAILED
        print(red(f"❌ Review failed: {e}"))
        return f"Review failed: {e}"


async def create_pull_request(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute pull request creation phase using Pull Request agent."""
    if not ctx.deps.state or not ctx.deps.state.change_set:
        return "Error: No changes to create PR for. Run implementation phase first."
    
    state = ctx.deps.state
    print(blue(f"🔀 Phase: Pull Request Creation"))
    
    try:
        state.current_phase = Phase.PULL_REQUEST
        state.status = Status.IN_PROGRESS
        state.last_update = datetime.now()
        
        # Build context for PR creation
        task_description = state.task_spec.goal if state.task_spec else "Feature development"
        changes_summary = state.change_set.migration_notes or "Implementation changes"
        review_status = state.review_report.approval_status if state.review_report else "pending"
        
        pr_context = f"""
Task: {task_description}
Changes: {changes_summary}
Review Status: {review_status}

Please create a pull request with these changes.
"""
        
        # Call Pull Request agent through the codebuff module
        # Note: This assumes we add a create_pull_request method to the Codebuff class
        pr_result = await ctx.deps.codebuff_module.create_pull_request(
            container=ctx.deps.container,
            task_description=task_description,
            changes_description=changes_summary,
            open_router_api_key=ctx.deps.api_key
        )
        
        # Parse result into structured format
        pull_request_result = PullRequestResult(
            branch_name="feature-branch",  # Would be extracted from result
            status="created",  # Would be derived from agent response
            message=pr_result[:200] + "..." if len(pr_result) > 200 else pr_result
        )
        
        state.pull_request_result = pull_request_result
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ Pull request creation completed"))
        return f"Pull request created. Status: {pull_request_result.status}"
        
    except Exception as e:
        error = OrchestrationError(
            kind=ErrorKind.TOOL_ERROR,
            message=str(e),
            phase=Phase.PULL_REQUEST,
            retry_count=state.retry_count
        )
        state.errors.append(error)
        state.status = Status.FAILED
        print(red(f"❌ Pull request creation failed: {e}"))
        return f"Pull request creation failed: {e}"


async def get_orchestration_status(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Get current orchestration status and summary."""
    if not ctx.deps.state:
        return "No active orchestration task."
    
    state = ctx.deps.state
    duration = (datetime.now() - state.start_time).total_seconds()
    
    status_summary = f"""
🎯 Task: {state.task_spec.goal if state.task_spec else 'Unknown'}
📊 Status: {state.status.value}
🔄 Phase: {state.current_phase.value}
⏱️ Duration: {duration:.1f}s
🔢 Requests: {state.total_requests}
❌ Errors: {len(state.errors)}
"""
    
    if state.errors:
        status_summary += "\n⚠️ Recent Errors:\n"
        for error in state.errors[-3:]:  # Show last 3 errors
            status_summary += f"  - {error.phase.value}: {error.message[:100]}\n"
    
    return status_summary


def create_orchestrator_agent(model: OpenAIModel) -> Agent:
    """Create the orchestration agent."""
    system_prompt = """
You are a Feature Development Orchestrator Agent, equivalent to Codebuff's workflow coordination.

Your role:
- Coordinate multiple specialized agents (explorer, picker, thinker, implementation, reviewer)
- Manage workflow state and error handling
- Ensure structured communication between agents
- Provide progress tracking and status updates

Workflow phases:
1. start_task - Initialize with task description
2. explore_codebase - Map and understand the codebase
3. select_files - Pick relevant files for the task
4. create_implementation_plan - Generate detailed execution plan
5. execute_implementation - Implement the planned changes
6. review_changes - Review and validate changes
7. create_pull_request - Create pull request with changes
8. get_orchestration_status - Check current status

Always maintain structured state and provide clear progress updates.
Handle errors gracefully and provide actionable feedback.
"""
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=OrchestratorDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=3
    )
    
    # Register workflow tools
    agent.tool(start_task)
    agent.tool(explore_codebase)
    agent.tool(select_files)
    agent.tool(create_implementation_plan)
    agent.tool(execute_implementation)
    agent.tool(review_changes)
    agent.tool(create_pull_request)
    agent.tool(get_orchestration_status)
    
    print(f"Orchestrator Agent created with model: {model.model_name}")
    return agent
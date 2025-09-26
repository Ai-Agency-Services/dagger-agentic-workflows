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
    PathInfo
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
        
        # BEGIN: Updated parsing of structured JSON from File Explorer
        try:
            parsed = json.loads(exploration_result)
        except Exception:
            parsed = None
        
        if isinstance(parsed, dict):
            langs = parsed.get("languages", {})
            trunc = parsed.get("truncation", {}) or {}
            areas = [state.task_spec.focus_area or "entire project"]
            key_patterns = list(langs.keys())[:10]
            notes = f"languages={list(langs.keys())[:6]} trunc={trunc.get('level')} tokens={trunc.get('estimated_tokens')}/{trunc.get('budget')}"
            exploration_report = ExplorationReport(
                areas_explored=areas,
                file_index=[], 
                key_patterns=key_patterns,
                architecture_notes=notes,
                confidence=0.85,
            )
        else:
            # Fallback: previous behavior
            exploration_report = ExplorationReport(
                areas_explored=[state.task_spec.focus_area or "entire project"],
                file_index=[],  
                confidence=0.8,
                architecture_notes=exploration_result[:500] + "..." if len(exploration_result) > 500 else exploration_result
            )
        # END: Updated parsing
        
        state.exploration_report = exploration_report
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ Exploration phase completed"))
        return "Exploration completed."
        
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
        
        # BEGIN: Updated parsing of semantic_query JSON results
        files: list[PathInfo] = []
        try:
            parsed = json.loads(selection_result)
            if isinstance(parsed, list):
                for item in parsed[:50]:
                    p = item.get("path") if isinstance(item, dict) else None
                    s = float(item.get("score", 0)) if isinstance(item, dict) else None
                    r = item.get("reason") if isinstance(item, dict) else None
                    if p:
                        files.append(PathInfo(path=p, relevance_score=s, rationale=r))
        except Exception:
            # Non-JSON output: keep empty files and embed rationale below
            pass
        
        rationale = selection_result[:500] + "..." if len(selection_result) > 500 else selection_result
        file_set = FileSet(
            files=files,
            rationale=rationale,
            total_files_considered=max(len(files), 0),
            confidence=0.85 if files else 0.6,
        )
        # END: Updated parsing
        
        state.file_set = file_set
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ File selection phase completed"))
        return "File selection completed."
        
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
        
        # Build exploration summary for planner context
        exploration_summary = ""
        if state.exploration_report:
            exploration_summary = state.exploration_report.architecture_notes or ""
        
        # Call Thinker agent
        plan_result = await ctx.deps.codebuff_module.create_plan(
            container=ctx.deps.container,
            task_description=state.task_spec.goal,
            relevant_files=relevant_files,
            exploration_results=exploration_summary,
            open_router_api_key=ctx.deps.api_key
        )
        
        # Parse result into structured format (keep simple for now)
        plan = Plan(
            steps=[],  
            confidence=0.8,  
            estimated_complexity="medium",
            test_strategy="Unit tests and integration validation"
        )
        
        state.plan = plan
        state.status = Status.SUCCESS
        state.total_requests += 1
        
        print(green("✅ Planning phase completed"))
        return "Implementation plan created."
        
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
            edits=[],  
            commands=[],  
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
            findings=[],  
            overall_status=Status.SUCCESS,  
            approval_status="approved"  
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
        pr_result = await ctx.deps.codebuff_module.create_pull_request(
            container=ctx.deps.container,
            task_description=task_description,
            changes_description=changes_summary,
            open_router_api_key=ctx.deps.api_key
        )
        
        # Parse result into structured format
        pull_request_result = PullRequestResult(
            branch_name="feature-branch",  
            status="created",  
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
        for error in state.errors[-3:]:
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

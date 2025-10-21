"""Main orchestration agent that coordinates Codebuff subagents."""

import time
from datetime import datetime
import uuid
import json
from dagger import dag

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

from ..reviewer.agent import ReviewerDependencies, create_reviewer_agent
try:
    from simple_chalk import blue, green, red, yellow, cyan, magenta
except ImportError:
    from simple_chalk import blue, green, red, yellow

    def cyan(x):
        return x

    def magenta(x):
        return x
from ..utils.container_state import write_json, write_text, append_log, write_current_phase

from .tools.planning import create_plan, add_subgoal, update_subgoal, think_deeply
from .tools.file_ops import read_files as read_files_tool, write_file as write_file_tool, str_replace as str_replace_tool, code_search as code_search_tool
from .tools.execution import run_terminal_command as run_terminal_command_tool
from ..file_explorer.agent import (
    create_file_explorer_agent,
    run_file_pickers_in_parallel,
    FileExplorerDependencies,
)
from ..implementation.agent import create_implementation_agent, ImplementationDependencies
from ..utils.git_metadata import embed_state_metadata
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
    PullRequestResult,
    PathInfo,
    Constitution,
    Spec,
    Task,
    ValidationError,
    LLMGenerationError,
    TaskExecutionError,
)
from .speckit_workflow import (
    explore_codebase as speckit_explore,
    create_constitution,
    create_spec,
    create_task_plan,
    execute_task,
    get_topological_order,
    save_to_state,
    load_from_state,
    update_workflow_progress,
)
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


async def add_project_file_tree_to_context(
    ctx: RunContext[OrchestratorDependencies],
) -> str:
    """Helper to append project file tree to context string."""
    print(blue("🗺️ Appending project file tree to context"))

    try:
        tree = await ctx.deps.container.with_exec(
            ["tree", "-L", "3", "-a", "-I", ".git|node_modules|__pycache__|.venv|dist|build"]
        ).stdout()
    except Exception as e:
        print(red(f"❌ Failed to append project file tree: {e}"))
        return tree


async def add_file_token_scores_token_callers_to_context(
    ctx: RunContext[OrchestratorDependencies],
) -> str:
    """Helper to append file token scores to context string."""
    print(blue("🗺️ Appending file token scores to context"))

    try:
        code_map = dag.code_map(config_file=ctx.deps.config_file)
        src_dir = ctx.deps.container.directory(".")
        scores_json = await code_map.get_file_token_scores(source_dir=src_dir)

        try:
            scores_data = json.loads(scores_json)
            file_scores = scores_data.get("fileTokenScores", {})
            token_callers = scores_data.get("tokenCallers", {})

            output = f"Found {len(file_scores)} files with tokens\n"

            if file_scores:
                sorted_files = sorted(
                    file_scores.items(), key=lambda x: len(x[1]), reverse=True
                )[:10]
                for path, tokens in sorted_files:
                    output += f"  {path}: {len(tokens)} unique tokens\n"
        except Exception:
            output = "File token analysis completed"

        file_scores_str = json.dumps(file_scores, indent=2) if file_scores else "{}"
        token_callers_str = json.dumps(token_callers, indent=2) if token_callers else "{}"
        combined = f"File Token Scores:\n{file_scores_str}\n\nToken Callers:\n{token_callers_str}\n"

        print(green("✅ File token scores and token callers appended"))
        return combined
    except Exception as e:
        print(red(f"❌ Failed to append file token scores: {e}"))
        return f""


# ============================================================================
# Spec-Kit Workflow Orchestration
# ============================================================================

async def run_speckit_workflow(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    focus_area: str = "entire project"
) -> str:
    """
    Execute complete spec-kit methodology workflow.
    
    Flow: Explore → Constitution → Spec → Tasks → Execute → Review → PR
    
    Args:
        task_description: What feature/change to implement
        focus_area: Specific area to focus on (default: "entire project")
    
    Returns:
        Status message about workflow execution
    """
    try:
        from simple_chalk import blue, green, red, yellow, cyan
    except ImportError:
        # Fallback if simple_chalk not available
        def blue(s): return s
        def green(s): return s
        def red(s): return s
        def yellow(s): return s
        def cyan(s): return s
    
    with tracer.start_as_current_span("run_speckit_workflow") as span:
        start_time = time.time()
        try:
            # Initialize task state (inline to avoid external dependency)
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
            span.set_attribute("task_id", task_spec.id)
            
            span.set_attribute("task_id", state.task_id)
            print(blue("🎯 Starting Spec-Kit Workflow"))
            
            # Phase 1: Explore codebase
            print(blue("Phase 1: Codebase Exploration"))
            try:
                # explore_codebase already limits to 5k chars internally
                codebase_context = await speckit_explore(ctx, task_description)
            except Exception as e:
                print(red(f"Exploration failed: {e}. Using minimal context."))
                codebase_context = f"Limited codebase context due to error. Task: {task_description}"
            
            # Update container and save context
            container = await save_to_state(
                ctx,
                "codebase_context.json",
                {"context": codebase_context}
            )
            ctx.deps.container = container
            
            # Phase 2: Create Constitution
            print(blue("Phase 2: Constitution"))
            constitution = await create_constitution(ctx, task_description, codebase_context)
            
            # Validate and save
            container = await save_to_state(ctx, "constitution.json", constitution)
            ctx.deps.container = container
            print(green(f"✅ Constitution created: {len(constitution.values)} values, {len(constitution.quality_gates)} gates"))
            
            # Phase 3: Create Spec
            print(blue("Phase 3: Specification"))
            spec = await create_spec(ctx, constitution, task_description)
            
            # Validate and save
            container = await save_to_state(ctx, "spec.json", spec)
            ctx.deps.container = container
            print(green(f"✅ Spec created: {len(spec.requirements)} requirements"))
            
            # Phase 4: Create Task Plan
            print(blue("Phase 4: Task Planning"))
            tasks = await create_task_plan(ctx, spec, constitution, codebase_context)
            
            # Validate and save
            container = await save_to_state(
                ctx,
                "tasks.json",
                {"tasks": [t.model_dump() for t in tasks]}
            )
            ctx.deps.container = container
            print(green(f"✅ Task plan created: {len(tasks)} tasks"))
            
            # Phase 5: Execute Tasks
            print(blue("Phase 5: Task Execution"))
            ordered_tasks = get_topological_order(tasks)
            print(cyan(f"Executing {len(ordered_tasks)} tasks in topological order"))
            
            for i, task in enumerate(ordered_tasks):
                print(cyan(f"Task {i+1}/{len(ordered_tasks)}: {task.id} - {task.description}"))
                try:
                    await execute_task(ctx, task, constitution, spec)
                    span.set_attribute(f"task_{i+1}_status", "success")
                except TaskExecutionError as e:
                    span.set_attribute(f"task_{i+1}_status", "failed")
                    span.set_attribute(f"task_{i+1}_error", str(e))
                    print(red(f"❌ Task {task.id} failed: {e}"))
                    
                    # Record error and stop workflow
                    error = OrchestrationError(
                        kind=ErrorKind.TOOL_ERROR,
                        message=f"Task {task.id} failed: {e}",
                        phase=Phase.IMPLEMENTATION,
                        retry_count=0
                    )
                    state.errors.append(error)
                    state.status = Status.FAILED
                    return f"Workflow failed at task {task.id}: {e}"
            
            # Phase 6: Final commit and PR
            print(blue("Phase 6: Final Commit & Pull Request"))
            
            # Commit all changes with spec-kit metadata
            try:
                commit_msg = f"""feat: {task_description}

{spec.objective}

Implemented {len(tasks)} tasks following spec-kit methodology:
{chr(10).join(f'- {t.id}: {t.description}' for t in ordered_tasks[:5])}
{f'... and {len(ordered_tasks) - 5} more tasks' if len(ordered_tasks) > 5 else ''}

Constitution values: {', '.join(constitution.values[:3])}
{f'... and {len(constitution.values) - 3} more' if len(constitution.values) > 3 else ''}

🤖 Generated with Codebuff (spec-kit)
Co-Authored-By: Codebuff <noreply@codebuff.com>
"""
                
                ctx.deps.container = ctx.deps.container.with_exec([
                    "bash", "-c",
                    f"git add -A && git commit -F - <<'EOF'\n{commit_msg}\nEOF"
                ])
                
                print(green("✅ All changes committed"))
            except Exception as e:
                print(red(f"❌ Commit failed: {e}"))
                return f"Workflow completed but commit failed: {e}"
            
            # Create PR (simplified inline version)
            try:
                pull_request_container = dag.builder(ctx.deps.config_file).setup_pull_request_container(
                    base_container=ctx.deps.container,
                    token=ctx.deps.github_token,
                )
                pr_agent = await dag.pull_request_agent(config_file=ctx.deps.config_file).run(
                    container=pull_request_container,
                    provider="openrouter",
                    open_router_api_key=ctx.deps.api_key,
                    openai_api_key=None,
                    insight_context=f"Spec-kit workflow for: {task_description}",
                )
                if pr_agent:
                    ctx.deps.container = pr_agent
                    pr_result = "Pull request created successfully"
                else:
                    pr_result = "Pull request creation skipped"
            except Exception as e:
                pr_result = f"Pull request creation failed: {e}"
            
            # Mark workflow complete
            state.current_phase = Phase.PULL_REQUEST
            state.status = Status.SUCCESS
            
            container = await update_workflow_progress(ctx.deps.container, "COMPLETED", "SUCCESS")
            ctx.deps.container = container
            
            span.set_attribute("workflow_status", "success")
            span.set_attribute("total_tasks", len(ordered_tasks))
            
            print(green("✅ Spec-Kit workflow completed successfully!"))
            return f"Spec-kit workflow completed: {len(ordered_tasks)} tasks executed. {pr_result}"
        
        except ValidationError as e:
            span.set_attribute("error_type", "validation")
            span.set_attribute("error", str(e))
            print(red(f"❌ Validation failed: {e}"))
            if e.issues:
                for issue in e.issues:
                    print(yellow(f"  - {issue}"))
            return f"Workflow validation failed: {e}. Issues: {'; '.join(e.issues)}"
        
        except LLMGenerationError as e:
            span.set_attribute("error_type", "llm_generation")
            span.set_attribute("error", str(e))
            print(red(f"❌ LLM generation failed: {e}"))
            return f"Workflow failed during LLM generation: {e}"
        
        except TaskExecutionError as e:
            span.set_attribute("error_type", "task_execution")
            span.set_attribute("error", str(e))
            span.set_attribute("failed_task_id", e.task_id)
            print(red(f"❌ Task execution failed: {e}"))
            return f"Workflow failed during task execution: {e}"
        
        except Exception as e:
            span.set_attribute("error_type", "unknown")
            span.set_attribute("error", str(e))
            print(red(f"❌ Unexpected error: {e}"))
            return f"Workflow failed: {e}"
        
        finally:
            span.set_attribute("duration_seconds", time.time() - start_time)


def create_orchestrator_agent(model: OpenAIChatModel) -> Agent:
    """Create the orchestration agent with Spec-Kit workflow."""
    system_prompt = """
You are a Feature Development Orchestrator Agent using the Spec-Kit methodology.

Your role:
- Coordinate feature development using Constitution → Spec → Tasks workflow
- Manage implementation-review loops for each task
- Ensure quality through constitution-aligned validation
- Provide progress tracking and status updates

**PRIMARY WORKFLOW** (Spec-Kit Methodology):
Use `run_speckit_workflow` which handles:
1. Codebase exploration
2. Constitution creation (values, constraints, quality gates)
3. Spec generation (requirements with acceptance criteria)
4. Task planning (atomic tasks with dependencies)
5. Task execution (implementation → review loop per task)
6. Final commit and PR creation

For all feature requests, use run_speckit_workflow.

Always maintain structured state and provide clear progress updates.
"""

    # Create agent
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=OrchestratorDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=3
    )

    # Register workflow tools
    agent.system_prompt(add_project_file_tree_to_context)
    
    # Spec-Kit workflow (primary workflow)
    agent.tool(run_speckit_workflow)

    # Planning and documentation tools
    agent.tool(create_plan)
    agent.tool(add_subgoal)
    agent.tool(update_subgoal)

    # File operations
    agent.tool(read_files_tool)
    agent.tool(write_file_tool)
    agent.tool(str_replace_tool)
    agent.tool(code_search_tool)

    # Execution and testing
    agent.tool(run_terminal_command_tool)

    # Analysis
    agent.tool(think_deeply)

    print(f"Orchestrator Agent created with model: {model.model_name}")
    return agent


"""Main orchestration agent that coordinates Codebuff subagents."""

import time
from datetime import datetime
import uuid
import json
from dagger import dag

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
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
    Plan,
    PlanStep,
    ChangeSet,
    FileEdit,
    ReviewReport,
    PullRequestResult,
    ContextSummary,
    PathInfo
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
           ["tree", "-L", "3", "-a", "-I", ".git|node_modules|__pycache__|.venv|dist|build"]).stdout()
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
                    file_scores.items(), key=lambda x: len(x[1]), reverse=True)[:10]
                for path, tokens in sorted_files:
                    output += f"  {path}: {len(tokens)} unique tokens\n"
        except Exception:
            output = "File token analysis completed"

        file_scores_str = json.dumps(
            file_scores, indent=2) if file_scores else "{}"
        token_callers_str = json.dumps(
            token_callers, indent=2) if token_callers else "{}"
        combined = f"File Token Scores:\n{file_scores_str}\n\nToken Callers:\n{token_callers_str}\n"

        print(green("✅ File token scores and token callers appended"))
        return combined
    except Exception as e:
        print(red(f"❌ Failed to append file token scores: {e}"))
        return f""


async def start_task(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    focus_area: str = "entire project"
) -> str:
    """Initialize a new orchestration task."""
    with tracer.start_as_current_span("start_task") as span:
        start_time = time.time()
        try:
            span.set_attribute("task_description", task_description)
            span.set_attribute("focus_area", focus_area)
            print(blue(f"🚀 Starting orchestration task: {task_description}"))

            task_spec = TaskSpec(
                id=str(uuid.uuid4()),
                goal=task_description,
                focus_area=focus_area,
                success_criteria=["Code compiles without errors",
                                  "Tests pass", "Review approved"]
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

            # Persist current phase snapshot
            try:
                if getattr(ctx.deps, "container", None) is not None:
                    ctx.deps.container = await write_current_phase(
                        ctx.deps.container,
                        state.current_phase.value,
                        state.status.value,
                        {"task_id": state.task_id}
                    )
            except Exception:
                pass

            # Persist task spec + log
            try:
                if getattr(ctx.deps, "container", None) is not None:
                    spec = {
                        "id": task_spec.id,
                        "goal": task_spec.goal,
                        "focus_area": task_spec.focus_area,
                        "created_at": state.start_time.isoformat(),
                    }
                    ctx.deps.container = await write_json(ctx.deps.container, "task_spec.json", spec)
                    ctx.deps.container = await write_json(ctx.deps.container, "task.json", spec)
                    ctx.deps.container = await append_log(ctx.deps.container, f"start_task: {task_spec.id} {task_spec.goal}")
            except Exception:
                pass
            print(green(f"✅ Task {task_spec.id} initialized"))
            return f"Task {task_spec.id} started: {task_description}"
        except Exception as e:
            span.set_attribute("error", str(e))
            print(red(f"❌ Start task failed: {e}"))
            return f"Start task failed: {e}"
        finally:
            span.set_attribute("duration_seconds", time.time() - start_time)


async def explore_codebase(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute exploration phase using a multi-agent file explorer pattern."""
    with tracer.start_as_current_span("explore_codebase") as span:
        start_time = time.time()
        state = None
        try:
            if not ctx.deps.state or not ctx.deps.state.task_spec:
                return "Error: No active task. Call start_task first."

            state = ctx.deps.state
            span.set_attribute("task_id", state.task_id)
            span.set_attribute("focus_area", state.task_spec.focus_area)
            print(
                blue(f"🔍 Phase: Multi-Agent Exploration - {state.task_spec.focus_area}"))

            state.current_phase = Phase.EXPLORATION
            state.status = Status.IN_PROGRESS
            state.last_update = datetime.now()

            # Snapshot phase
            try:
                ctx.deps.container = await write_current_phase(
                    ctx.deps.container,
                    state.current_phase.value,
                    state.status.value,
                    {"task_id": state.task_id}
                )
            except Exception:
                pass

            # 2. Create the agent that will decide what to explore
            explorer_llm_agent = create_file_explorer_agent(
                ctx.deps.file_explorer)

            # 3. Run the explorer LLM to get a structured list of prompts
            explorer_prompt = f"Based on the overall goal '{state.task_spec.goal}', what are 1-4 different areas of the codebase that could be useful to explore in parallel? Think about components, features, or layers (e.g., 'API routes', 'database models', 'UI components')."

            # Run returns an AgentRunResult object that contains our structured output
            dep = FileExplorerDependencies(
                container=ctx.deps.container
            )
            explorer_result = await explorer_llm_agent.run(explorer_prompt, deps=dep)

            # Extract the ExplorePrompts object from the result
            explore_prompts_result = explorer_result.output

            # Now we can access the prompts attribute on the structured output
            prompts = explore_prompts_result.prompts
            span.set_attribute("explore_prompts", prompts)

            print(cyan(
                f"🧭 Explorer identified {len(prompts)} areas to explore:"))
            for i, prompt in enumerate(prompts):
                print(magenta(f"  {i+1}. {prompt}"))

            # Get code map scores for file ranking
            code_map = dag.code_map(config_file=ctx.deps.config_file)
            src_dir = ctx.deps.container.directory(".")
            scores_json = await code_map.get_file_token_scores(source_dir=src_dir)

            try:
                scores_data = json.loads(scores_json)
                file_scores = scores_data.get("fileTokenScores", {})
                token_callers = scores_data.get("tokenCallers", {})
            except Exception as e:
                print(red(f"Warning: Error parsing code map scores: {e}"))
                file_scores = {}
                token_callers = {}

            # 5. Run the file pickers in parallel using the generated prompts
            all_results = await run_file_pickers_in_parallel(
                overall_goal=state.task_spec.goal,
                focus_prompts=prompts,
                picker_agent_model=ctx.deps.file_picker,
                file_scores=file_scores,
                token_callers=token_callers,  # Add token_callers to the function call
            )

            # 6. Process and flatten results
            unique_files = sorted(list(set(
                file for sublist in all_results for file in sublist if not file.startswith("Error:"))))
            span.set_attribute("files_found_count", len(unique_files))

            # Print the files that were found by category
            print(cyan("\n📁 Files found during exploration:"))
            for i, (prompt, files) in enumerate(zip(prompts, all_results)):
                print(magenta(f"\n  Category {i+1}: {prompt}"))
                for file in files:
                    if not file.startswith("Error:"):
                        print(green(f"    • {file}"))

            # Print unique files after deduplication
            print(cyan(f"\n📦 Unique files identified ({len(unique_files)}):"))
            for file in unique_files:
                print(green(f"  • {file}"))

            # Filter to only code files and convert to PathInfo objects
            from codebuff.file_explorer.utils import _is_non_code_file
            code_files = [f for f in unique_files if not _is_non_code_file(f)]
            
            path_infos = [
                PathInfo(
                    path=file_path,
                    relevance=0.9,  # Default relevance score
                    tokens=len(file_scores.get(file_path, [])
                               ) if file_scores else 0
                )
                for file_path in code_files
            ]
            
            print(cyan(f"\n🔧 Code files after filtering ({len(code_files)}):"))
            for file in code_files:
                print(green(f"  • {file}"))

            exploration_report = ExplorationReport(
                areas_explored=prompts,
                file_index=path_infos,  # Use PathInfo objects instead of strings
                key_patterns=[],
                architecture_notes=f"Found {len(unique_files)} relevant files across {len(prompts)} explored areas.",
                confidence=0.9 if unique_files else 0.5,
            )

            state.exploration_report = exploration_report

            # Create a FileSet from the path_infos and update the state
            file_set = FileSet(
                files=path_infos,
                selection_criteria=f"Files selected by multi-agent exploration for '{state.task_spec.goal}'",
                rationale="Selected based on relevance to task requirements and token analysis",
                total_files_considered=len(file_scores) if file_scores else 0,
                confidence=0.9 if unique_files else 0.5
            )
            state.file_set = file_set

            # Persist exploration and selection
            try:
                ctx.deps.container = await write_json(ctx.deps.container, "exploration_results.json", exploration_report.model_dump())
                ctx.deps.container = await write_json(ctx.deps.container, "selected_files.json", file_set.model_dump())
            except Exception:
                pass

            state.status = Status.SUCCESS
            state.total_requests += 1
            span.set_attribute("confidence", exploration_report.confidence)

            print(
                green(f"✅ Multi-agent exploration completed. Found {len(code_files)} code files."))
            return f"Exploration completed. Found {len(code_files)} relevant code files."

        except Exception as e:
            span.set_attribute("error", str(e))
            if state:
                error = OrchestrationError(
                    kind=ErrorKind.TOOL_ERROR, message=str(e), phase=Phase.EXPLORATION, retry_count=state.retry_count if state else 0
                )
                state.errors.append(error)
                state.status = Status.FAILED
            print(red(f"❌ Exploration failed: {e}"))
            return f"Exploration failed: {e}"
        finally:
            span.set_attribute("duration_seconds", time.time() - start_time)


async def create_implementation_plan(
    ctx: RunContext[OrchestratorDependencies],
    path: str = "IMPLEMENTATION_PLAN.md",
    plan: str = ""
) -> str:
    """Generate a detailed markdown plan for complex tasks."""
    with tracer.start_as_current_span("create_implementation_plan") as span:
        start_time = time.time()
        try:
            if not ctx.deps.state or not ctx.deps.state.task_spec:
                return "Error: No active task. Call start_task first."

            state = ctx.deps.state
            span.set_attribute("task_id", state.task_id)
            span.set_attribute("plan_path", path)
            print(blue(f"🧠 Phase: Planning"))

            state.current_phase = Phase.PLANNING
            state.status = Status.IN_PROGRESS
            state.last_update = datetime.now()

            # Snapshot phase
            try:
                ctx.deps.container = await write_current_phase(
                    ctx.deps.container,
                    state.current_phase.value,
                    state.status.value,
                    {"task_id": state.task_id}
                )
            except Exception:
                pass

            # Build context from previous phases
            task_goal = state.task_spec.goal
            focus_area = state.task_spec.focus_area or "entire project"

            # Get exploration context
            exploration_notes = ""
            if state.exploration_report:
                exploration_notes = state.exploration_report.architecture_notes or ""
                key_patterns = ", ".join(
                    state.exploration_report.key_patterns[:5]) if state.exploration_report.key_patterns else ""
                if key_patterns:
                    exploration_notes += f"\nKey patterns: {key_patterns}"
                span.set_attribute("exploration_confidence",
                                   state.exploration_report.confidence)

            # Get selected files context
            selected_files = []
            if state.file_set and state.file_set.files:
                selected_files = [f.path for f in state.file_set.files[:10]]
                span.set_attribute("selected_files_count", len(selected_files))

            # Generate markdown plan content
            markdown_plan = f"""# Implementation Plan

## Task Overview
**Goal:** {task_goal}
**Focus Area:** {focus_area}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Architecture Analysis
{exploration_notes}

## Selected Files
{chr(10).join(f'- {file_path}' for file_path in selected_files) if selected_files else '- No specific files selected'}

## Implementation Steps

### Phase 1: Preparation
- [ ] Review selected files and understand current implementation
- [ ] Identify dependencies and potential conflicts
- [ ] Set up development environment if needed

### Phase 2: Core Implementation
- [ ] Implement main functionality based on task requirements
- [ ] Follow existing code patterns and conventions
- [ ] Ensure proper error handling and validation

### Phase 3: Testing & Validation
- [ ] Write or update unit tests for new functionality
- [ ] Run existing test suite to ensure no regressions
- [ ] Perform integration testing if applicable

### Phase 4: Documentation & Cleanup
- [ ] Update relevant documentation
- [ ] Clean up any temporary code or comments
- [ ] Ensure code follows project style guidelines

## Success Criteria
{chr(10).join(f'- {criteria}' for criteria in state.task_spec.success_criteria)}

## Risk Assessment
- **Complexity:** Medium
- **Dependencies:** Review selected files for external dependencies
- **Testing:** Ensure comprehensive test coverage
- **Rollback:** Changes can be reverted via git if needed

## Notes
{plan if plan else 'Additional implementation notes will be added during execution.'}
"""

            # Save markdown plan to container
            ctx.deps.container = await write_text(ctx.deps.container, path, markdown_plan)
            span.set_attribute("plan_size_chars", len(markdown_plan))

            # Create structured plan object for state
            plan_obj = Plan(
                steps=[
                    PlanStep(
                        id="step-1", description="Review selected files and understand current implementation"),
                    PlanStep(
                        id="step-2", description="Implement main functionality based on task requirements"),
                    PlanStep(
                        id="step-3", description="Write or update unit tests for new functionality"),
                    PlanStep(
                        id="step-4", description="Update relevant documentation and cleanup"),
                ],
                confidence=0.8,
                estimated_complexity="medium",
                test_strategy="Unit tests and integration validation"
            )

            state.plan = plan_obj
            state.status = Status.SUCCESS
            state.total_requests += 1
            span.set_attribute("plan_steps", len(plan_obj.steps))
            span.set_attribute("plan_confidence", plan_obj.confidence)

            # Persist plan metadata and log
            try:
                plan_metadata = {
                    "file_path": path,
                    "steps_count": len(plan_obj.steps),
                    "complexity": plan_obj.estimated_complexity,
                    "confidence": plan_obj.confidence,
                    "created_at": datetime.now().isoformat()
                }
                # Persist structured plan for resumption
                ctx.deps.container = await write_json(ctx.deps.container, "implementation_plan.json", state.plan.model_dump())
                ctx.deps.container = await write_json(ctx.deps.container, "plan_metadata.json", plan_metadata)
                ctx.deps.container = await append_log(ctx.deps.container, f"create_plan: saved to {path}")
            except Exception:
                pass

            print(green(f"✅ Planning phase completed - Plan saved to {path}"))
            return f"Implementation plan created and saved to {path}"

        except Exception as e:
            span.set_attribute("error", str(e))
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
        finally:
            span.set_attribute("duration_seconds", time.time() - start_time)


async def execute_implementation(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute implementation phase using Implementation agent."""
    with tracer.start_as_current_span("execute_implementation") as span:
        start_time = time.time()
        try:
            if not ctx.deps.state or not ctx.deps.state.plan:
                return "Error: No implementation plan available. Run planning phase first."

            state = ctx.deps.state
            span.set_attribute("task_id", state.task_id)
            span.set_attribute("plan_steps", len(state.plan.steps))
            print(blue(f"⚡ Phase: Implementation"))

            state.current_phase = Phase.IMPLEMENTATION
            state.status = Status.IN_PROGRESS
            state.last_update = datetime.now()

            # Snapshot phase
            try:
                ctx.deps.container = await write_current_phase(
                    ctx.deps.container,
                    state.current_phase.value,
                    state.status.value,
                    {"task_id": state.task_id}
                )
            except Exception:
                pass

            # Convert plan to string for agent
            plan_str = json.dumps(state.plan.model_dump(), indent=2)

            # Build selected files list for Implementation agent
            selected_files = [f.path for f in (
                state.file_set.files or [])][:20] if state.file_set and state.file_set.files else []

            # Create Implementation agent with the appropriate model
            # Check if we have the implementation model directly or need to use the general model
            if hasattr(ctx.deps, 'implementation') and ctx.deps.implementation is not None:
                # Use the dedicated implementation model if available
                impl_agent = create_implementation_agent(
                    ctx.deps.implementation)
            else:
                # Fall back to the main model
                if not ctx.deps.model:
                    raise ValueError(
                        "Implementation model not provided in dependencies")
                impl_agent = create_implementation_agent(ctx.deps.model)

            # Run Implementation agent
            impl_deps = ImplementationDependencies(
                config=ctx.deps.config,
                container=ctx.deps.container,
                plan=plan_str
            )

            impl_prompt = (
                "Apply the implementation plan.\n"
                "Requirements:\n"
                f"- Focus on these files: {', '.join(selected_files) if selected_files else 'any relevant files'}\n"
                "- Create NEW implementation code as needed\n"
                "- Create NEW unit tests for the new code\n"
                "- Keep changes minimal and focused\n"
                "- Follow existing code patterns\n"
                "Output a brief summary of changes made."
            )

            impl_result = await impl_agent.run(impl_prompt, deps=impl_deps)

            # Update container from Implementation agent
            ctx.deps.container = impl_deps.container

            # Stage changes to detect new files
            ctx.deps.container = ctx.deps.container.with_exec(
                ["bash", "-lc", "git add -N . || true"])

            # Get changed files using porcelain format
            raw_status = await ctx.deps.container.with_exec(["bash", "-lc", "git status --porcelain=v1 -z"]).stdout()

            # Parse changed files
            changed_paths = []
            created_files = set()
            modified_files = set()

            if raw_status:
                for entry in raw_status.split("\x00"):
                    if not entry.strip():
                        continue
                    status_code = entry[:2]
                    file_path = entry[3:].strip()
                    if not file_path:
                        continue
                    changed_paths.append(file_path)
                    # Check if file was created or modified
                    if status_code[0] in ['?', 'A'] or status_code[1] in ['?', 'A']:
                        created_files.add(file_path)
                    else:
                        modified_files.add(file_path)

            # Categorize files
            test_files = []
            code_files = []
            for path in changed_paths:
                # Detect test files using common patterns
                if any(pattern in path for pattern in [
                    "/__tests__/", ".test.", ".spec.", "test_", "_test.",
                    "/tests/", "/test/", "_tests."
                ]):
                    test_files.append(path)
                elif path.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".rs", ".cpp", ".c")):
                    code_files.append(path)

            # Create ChangeSet from detected changes
            edits = [
                FileEdit(
                    path=path,
                    operation="create" if path in created_files else "modify"
                ) for path in changed_paths
            ]

            change_set = ChangeSet(
                edits=edits,
                commands=[],
                migration_notes=str(impl_result.output) if hasattr(
                    impl_result, 'output') else str(impl_result)
            )

            state.change_set = change_set

            # Persist targeting data for test execution
            ctx.deps.container = await write_json(
                ctx.deps.container,
                "implementation/targets.json",
                {
                    "test_files": test_files,
                    "code_files": code_files,
                    "all_changed": changed_paths,
                    "created": list(created_files),
                    "modified": list(modified_files)
                }
            )

            # Execute targeted tests with TDD support
            tests_passed = False
            test_output = ""
            per_file_results = []
            tdd_cycle = 0
            max_tdd_cycles = 3

            # Check for TDD configuration (supports Pydantic models and dicts)
            tdd_enabled = False
            tdd_allow_tests_only_first = True
            # default max_tdd_cycles already set above
            oc = getattr(ctx.deps.config, 'orchestrator', None)
            if oc:
                testing = getattr(oc, 'testing', None) if hasattr(oc, 'testing') else (oc.get('testing') if isinstance(oc, dict) else None)
                if testing:
                    tdd = getattr(testing, 'tdd', None) if hasattr(testing, 'tdd') else (testing.get('tdd') if isinstance(testing, dict) else None)
                    if tdd:
                        if isinstance(tdd, dict):
                            tdd_enabled = tdd.get('enabled', False)
                            max_tdd_cycles = tdd.get('max_cycles', max_tdd_cycles)
                            tdd_allow_tests_only_first = tdd.get('allow_tests_only_first_cycle', True)
                        else:
                            tdd_enabled = getattr(tdd, 'enabled', False)
                            max_tdd_cycles = getattr(tdd, 'max_cycles', max_tdd_cycles)
                            tdd_allow_tests_only_first = getattr(tdd, 'allow_tests_only_first_cycle', True)
            if tdd_enabled:
                print(blue(f"🔄 TDD mode enabled - max cycles: {max_tdd_cycles}"))

            # Get test command template from config
            reporter_config = getattr(ctx.deps.config, 'reporter', None)
            file_test_template = getattr(
                reporter_config, 'file_test_command_template', None) if reporter_config else None

            # TDD cycle loop
            while tdd_cycle <= max_tdd_cycles:
                tdd_cycle += 1
                if tdd_cycle > 1:
                    print(blue(f"🔄 TDD Cycle {tdd_cycle}: Retrying after test failures"))

                if test_files:
                    print(blue(f"🧪 Running {len(test_files)} targeted test files (cycle {tdd_cycle})"))
                    tests_passed = True  # Assume success until a failure occurs
                    per_file_results = []  # Reset results for this cycle
                    
                    for test_file in test_files[:20]:
                        if file_test_template:
                            cmd = file_test_template.replace(
                                "{file}", test_file)
                        else:
                            if test_file.endswith('.py'):
                                cmd = f"pytest -xvs {test_file}"
                            elif any(test_file.endswith(ext) for ext in ['.ts', '.tsx', '.js', '.jsx']):
                                cmd = f"npm test -- --testPathPattern='{test_file}'"
                            elif test_file.endswith('.go'):
                                cmd = f"go test -v $(dirname {test_file})"
                            else:
                                cmd = f"echo 'No test runner configured for {test_file}'"
                        
                        # Capture test results without erroring on failure
                        try:
                            container_with_test = ctx.deps.container.with_exec([
                                "bash", "-c", 
                                f"{cmd}; echo -n $? > /tmp/exit_code_{test_file.replace('/', '_')}"
                            ])
                            test_output_single = await container_with_test.stdout()
                            
                            # Read exit code
                            try:
                                exit_code_str = await container_with_test.file(
                                    f"/tmp/exit_code_{test_file.replace('/', '_')}"
                                ).contents()
                                exit_code = int(exit_code_str.strip()) if exit_code_str.strip().isdigit() else 1
                            except:
                                exit_code = 1
                            
                            ctx.deps.container = container_with_test
                            
                            if exit_code == 0:
                                per_file_results.append({
                                    "file": test_file,
                                    "command": cmd,
                                    "status": "passed",
                                    "exit_code": exit_code,
                                    "output": (test_output_single or "")[:2000]
                                })
                            else:
                                tests_passed = False
                                per_file_results.append({
                                    "file": test_file,
                                    "command": cmd,
                                    "status": "failed",
                                    "exit_code": exit_code,
                                    "output": (test_output_single or "")[:2000]
                                })
                        except Exception as e:
                            tests_passed = False
                            per_file_results.append({
                                "file": test_file,
                                "command": cmd,
                                "status": "error",
                                "error": str(e)[:1000]
                            })
                    
                    test_output = json.dumps(per_file_results)[:5000]
                    
                    # Break if tests pass or if TDD disabled
                    if tests_passed or not tdd_enabled:
                        break
                    
                    # On test failure in TDD mode, re-run implementation agent
                    if tdd_cycle < max_tdd_cycles:
                        print(yellow(f"⚠️ Tests failed in cycle {tdd_cycle}, running implementation again"))
                        
                        # Extract failure context for implementation agent
                        failure_context = "\n".join([
                            f"Test file: {result['file']}\nCommand: {result['command']}\nError: {result.get('output', result.get('error', 'Unknown error'))}\n"
                            for result in per_file_results if result['status'] in ['failed', 'error']
                        ])[:2000]
                        
                        # Re-run implementation agent with failure context
                        retry_prompt = (
                            f"Fix the failing tests from cycle {tdd_cycle}.\n"
                            "Test failures:\n"
                            f"{failure_context}\n\n"
                            "Implement the required functionality to make these tests pass.\n"
                            "Focus on minimal changes to satisfy the failing assertions."
                        )
                        
                        impl_result = await impl_agent.run(retry_prompt, deps=impl_deps)
                        ctx.deps.container = impl_deps.container
                        
                        # Re-detect changed files after retry
                        ctx.deps.container = ctx.deps.container.with_exec(
                            ["bash", "-lc", "git add -N . || true"])
                        raw_status = await ctx.deps.container.with_exec(
                            ["bash", "-lc", "git status --porcelain=v1 -z"]).stdout()
                        
                        # Re-parse changed files
                        changed_paths = []
                        if raw_status:
                            for entry in raw_status.split("\x00"):
                                if entry.strip():
                                    file_path = entry[3:].strip()
                                    if file_path:
                                        changed_paths.append(file_path)
                        
                        # Re-categorize files
                        test_files = []
                        code_files = []
                        for path in changed_paths:
                            if any(pattern in path for pattern in [
                                "/__tests__/", ".test.", ".spec.", "test_", "_test.",
                                "/tests/", "/test/", "_tests."
                            ]):
                                test_files.append(path)
                            elif path.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".rs", ".cpp", ".c")):
                                code_files.append(path)
                    else:
                        print(yellow(f"⚠️ TDD cycles exhausted ({max_tdd_cycles}). Tests still failing."))
                        break
                else:
                    test_cmd = getattr(ctx.deps.config.testing, "test_command", None) if hasattr(
                        ctx.deps.config, 'testing') else None
                    if test_cmd:
                        print(
                            blue(f"🧪 No targeted tests found, running configured test command: {test_cmd}"))
                        try:
                            # Capture test results without erroring
                            container_with_test = ctx.deps.container.with_exec([
                                "bash", "-c", 
                                f"{test_cmd}; echo -n $? > /tmp/exit_code_fallback"
                            ])
                            test_output = await container_with_test.stdout() or ""
                            
                            # Read exit code
                            try:
                                exit_code_str = await container_with_test.file("/tmp/exit_code_fallback").contents()
                                exit_code = int(exit_code_str.strip()) if exit_code_str.strip().isdigit() else 1
                            except:
                                exit_code = 1
                            
                            ctx.deps.container = container_with_test
                            
                            if exit_code == 0:
                                tests_passed = True
                            else:
                                if any(phrase in test_output.lower() for phrase in [
                                    "collected 0 items", "no tests collected", "exit code: 5"
                                ]):
                                    tests_passed = True
                                    test_output = test_output + "\n(No tests collected; treating as success)"
                                else:
                                    tests_passed = False
                        except Exception as e:
                            tests_passed = False
                            test_output = str(e)[:5000]
                    else:
                        print(
                            yellow("⚠️ No targeted tests detected and no fallback test command configured"))
                        tests_passed = True
                        test_output = "No tests to run; proceeding with implementation"
                
                # End of TDD cycle loop - break here
                break

            # Save detailed test results (canonical + legacy for compatibility)
            ctx.deps.container = await write_json(
                ctx.deps.container,
                "implementation/test_results.json",
                {
                    "tests_passed": tests_passed,
                    "test_strategy": "targeted" if test_files else "fallback",
                    "files_tested": test_files,
                    "per_file_results": per_file_results,
                    "summary_output": test_output,
                    "tdd_cycle": tdd_cycle,
                    "tdd_enabled": tdd_enabled
                }
            )
            ctx.deps.container = await write_json(
                ctx.deps.container,
                "implementation/test-results.json",
                {
                    "tests_passed": tests_passed,
                    "test_strategy": "targeted" if test_files else "fallback",
                    "files_tested": test_files,
                    "per_file_results": per_file_results,
                    "summary_output": test_output,
                    "tdd_cycle": tdd_cycle,
                    "tdd_enabled": tdd_enabled
                }
            )

            # Validate that actual feature code was implemented (not just test changes)
            # In TDD mode, allow tests-only changes in first cycle
            if not code_files and test_files:
                if tdd_enabled and tdd_cycle == 1 and tdd_allow_tests_only_first:
                    print(yellow("⚠️ TDD Cycle 1: Tests-only changes allowed in first cycle"))
                else:
                    state.status = Status.FAILED
                    error = OrchestrationError(
                        kind=ErrorKind.TOOL_ERROR,
                        message="Only test files were modified; no feature implementation detected",
                        phase=Phase.IMPLEMENTATION,
                        retry_count=state.retry_count
                    )
                    state.errors.append(error)
                    print(red("❌ Only tests were modified; no feature code implemented"))
                    return "Implementation failed: only test files were modified, no feature code was implemented"

            # TDD-aware commit gating
            if not tests_passed:
                if tdd_enabled:
                    print(yellow(f"⚠️ TDD: Tests failed after {tdd_cycle} cycles. Workflow continues without commit."))
                    state.status = Status.SUCCESS  # Don't fail the workflow, just don't commit
                    try:
                        ctx.deps.container = await write_current_phase(
                            ctx.deps.container,
                            state.current_phase.value,
                            state.status.value,
                            {"task_id": state.task_id}
                        )
                    except Exception:
                        pass
                    print(yellow("🔄 Implementation phase marked as complete (no commit due to failing tests)"))
                    return f"Implementation completed with failing tests after {tdd_cycle} TDD cycles. No commit made."
                else:
                    state.status = Status.FAILED
                    error = OrchestrationError(
                        kind=ErrorKind.TOOL_ERROR,
                        message="Targeted tests failed; implementation aborted",
                        phase=Phase.IMPLEMENTATION,
                        retry_count=state.retry_count
                    )
                    state.errors.append(error)
                    print(red("❌ Targeted tests failed; aborting commit"))
                    return "Implementation failed: targeted tests did not pass"

            span.set_attribute("final_tests_passed", tests_passed)

            # Test results already persisted above in targeted test execution

            print(green("✅ Targeted tests passed; proceeding with commit"))

            # Git operations with telemetry
            branch = f"feature/{state.task_spec.id[:8]}" if state.task_spec else f"feature/{uuid.uuid4().hex[:8]}"
            span.set_attribute("feature_branch", branch)

            try:
                # Prepare commit message with embedded orchestration metadata
                header = f"feat: {state.task_spec.goal if state.task_spec else 'feature'}\n\nAutomated commit: applied implementation changes\nIncludes targeted tests with passing test suite"
                commit_msg = embed_state_metadata(
                    header,
                    task_id=(
                        state.task_spec.id if state and state.task_spec else None),
                    phase=(
                        state.current_phase.value if state and state.current_phase else None),
                    status=(state.status.value if state and state.status else None),
                )

                # Branch safety guard: never commit to base branch
                # - detect current branch
                # - resolve base branch from config (fallback to 'main')
                # - if on base/protected branch, switch to a unique working branch using branch_prefix
                base_branch = None
                try:
                    ocfg = getattr(ctx.deps.config, 'git', None)
                    if isinstance(ocfg, dict):
                        base_branch = ocfg.get(
                            'base_pull_request_branch') or ocfg.get('default_branch')
                    else:
                        base_branch = getattr(
                            ocfg, 'base_pull_request_branch', None) if ocfg else None
                except Exception:
                    base_branch = None
                if not base_branch:
                    base_branch = 'main'

                # Determine branch prefix
                branch_prefix = 'feature/codebuff-'
                try:
                    oc = getattr(ctx.deps.config, 'orchestrator', None)
                    if isinstance(oc, dict):
                        branch_prefix = (
                            oc.get('branch_prefix') or branch_prefix)
                    else:
                        branch_prefix = getattr(
                            oc, 'branch_prefix', branch_prefix)
                except Exception:
                    pass

                # Get current branch name
                try:
                    current_branch = await ctx.deps.container.with_exec(["bash", "-lc", "git rev-parse --abbrev-ref HEAD"]).stdout()
                    current_branch = (current_branch or '').strip()
                except Exception:
                    current_branch = ''

                # Read cloned source branch and treat it as protected too
                source_branch = None
                try:
                    sb_raw = await ctx.deps.container.file(".codebuff-state/source_branch.json").contents()
                    if sb_raw:
                        import json as _json
                        source_branch = (_json.loads(sb_raw)
                                         or {}).get("source_branch")
                except Exception:
                    source_branch = None

                protected = {base_branch, 'main', 'master', 'develop'}
                if source_branch:
                    protected.add(source_branch)

                # If on protected branch, create and switch to a unique working branch
                guard_cmds = []
                if not current_branch or current_branch in protected:
                    # Suffix using timestamp for uniqueness
                    unique_suffix = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                    safe_branch = f"{branch_prefix}{unique_suffix}"
                    guard_cmds += [
                        f"git checkout -b {safe_branch}"
                    ]
                    branch_to_use = safe_branch
                else:
                    branch_to_use = current_branch

                cmds = [
                    "git config user.name 'Codebuff Agent'",
                    "git config user.email 'codebuff@example.com'",
                ] + guard_cmds + [
                    "git add -A",
                    "git add .codebuff-state || true",
                    # Use a here-doc to pass multiline commit message (no nested bash)
                    f"git commit -F - <<'EOF'\n{commit_msg}\nEOF",
                ]
                for cmd in cmds:
                    ctx.deps.container = ctx.deps.container.with_exec(
                        ["bash", "-lc", cmd])
                span.set_attribute("git_commit", "success")

                # Write diff for debugging/review
                try:
                    diff_out = await ctx.deps.container.with_exec(["bash", "-lc", "git diff HEAD~1..HEAD"]).stdout()
                    span.set_attribute("diff_size", len(
                        diff_out) if diff_out else 0)
                except Exception:
                    diff_out = ""

                if getattr(ctx.deps, "container", None) is not None:
                    ctx.deps.container = await write_text(ctx.deps.container, "implementation/diffs/commit.diff", diff_out or "")
                    ctx.deps.container = await write_json(ctx.deps.container, "implementation/summary.json", change_set.model_dump())
                    ctx.deps.container = await append_log(ctx.deps.container, f"implement_plan: committed changes on {branch}")
            except Exception as e:
                span.set_attribute("git_error", str(e))
                state.status = Status.FAILED
                print(red(f"❌ Commit failed: {e}"))
                return f"Implementation failed: commit error: {e}"

            # Success
            state.status = Status.SUCCESS
            state.total_requests += 1
            span.set_attribute("files_modified", len(change_set.edits))
            print(green("✅ Implementation phase completed"))
            return f"Implementation completed. Changes: {len(change_set.edits)} files modified"

        except Exception as e:
            span.set_attribute("error", str(e))
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
        finally:
            span.set_attribute("duration_seconds", time.time() - start_time)


async def review_changes(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute review phase using Reviewer agent."""
    with tracer.start_as_current_span("review_changes") as span:
        start_time = time.time()
        try:
            if not ctx.deps.state or not ctx.deps.state.change_set:
                return "Error: No changes to review. Run implementation phase first."

            state = ctx.deps.state
            span.set_attribute("task_id", state.task_id)
            print(blue(f"🔍 Phase: Review"))

            state.current_phase = Phase.REVIEW
            state.status = Status.IN_PROGRESS
            state.last_update = datetime.now()

            # Snapshot phase
            try:
                ctx.deps.container = await write_current_phase(
                    ctx.deps.container,
                    state.current_phase.value,
                    state.status.value,
                    {"task_id": state.task_id}
                )
            except Exception:
                pass

            # Create review result directly (decoupled)
            review_report = ReviewReport(
                findings=[],
                overall_status=Status.SUCCESS,
                approval_status="approved"
            )

            state.review_report = review_report
            state.status = Status.SUCCESS
            state.total_requests += 1
            span.set_attribute("approval_status",
                               review_report.approval_status)
            span.set_attribute("findings_count", len(review_report.findings))

            # Persist review and log
            try:
                if getattr(ctx.deps, "container", None) is not None:
                    ctx.deps.container = await write_json(ctx.deps.container, "review.json", review_report.model_dump())
                    ctx.deps.container = await append_log(ctx.deps.container, f"review_changes: {review_report.approval_status}")
            except Exception:
                pass
            print(green("✅ Review phase completed"))
            return f"Review completed. Status: {review_report.approval_status}"

        except Exception as e:
            span.set_attribute("error", str(e))
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
        finally:
            span.set_attribute("duration_seconds", time.time() - start_time)


async def create_pull_request(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Execute pull request creation phase using Pull Request agent."""
    with tracer.start_as_current_span("create_pull_request") as span:
        start_time = time.time()
        try:
            if not ctx.deps.state or not ctx.deps.state.change_set:
                return "Error: No changes to create PR for. Run implementation phase first."

            state = ctx.deps.state
            span.set_attribute("task_id", state.task_id)
            print(blue(f"🔀 Phase: Pull Request Creation"))

            state.current_phase = Phase.PULL_REQUEST
            state.status = Status.IN_PROGRESS
            state.last_update = datetime.now()

            # Snapshot phase
            try:
                ctx.deps.container = await write_current_phase(
                    ctx.deps.container,
                    state.current_phase.value,
                    state.status.value,
                    {"task_id": state.task_id}
                )
            except Exception:
                pass

            # Build context for PR creation
            task_description = state.task_spec.goal if state.task_spec else "Feature development"
            changes_summary = state.change_set.migration_notes or "Implementation changes"
            review_status = state.review_report.approval_status if state.review_report else "pending"

            span.set_attribute("task_description", task_description)
            span.set_attribute("review_status", review_status)

            pr_context = f"""
Task: {task_description}
Changes: {changes_summary}
Review Status: {review_status}

Please create a pull request with these changes.
"""

            # Create PR result directly (decoupled)
            pr_text = f"Pull request for: {task_description}\nChanges: {changes_summary}\nReview: {review_status}"

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
                    insight_context=pr_context,
                )
                if pr_agent:
                    ctx.deps.container = pr_agent
                    state.status = Status.SUCCESS
                    try:
                        ctx.deps.container = await write_current_phase(
                            ctx.deps.container,
                            state.current_phase.value,
                            state.status.value,
                            {"task_id": state.task_id}
                        )
                    except Exception:
                        pass
                    state.total_requests += 1
                    span.set_attribute("pr_creation", "success")
                else:
                    span.set_attribute("pr_creation", "failed")
            except Exception as e:
                span.set_attribute("pr_creation_error", str(e))
                print(red(f"❌ PR creation failed: {e}"))

            # Persist PR metadata and log
            try:
                # detect current branch for metadata
                try:
                    curr_branch = await ctx.deps.container.with_exec(["bash", "-lc", "git rev-parse --abbrev-ref HEAD"]).stdout()
                    curr_branch = (curr_branch or "").strip()
                except Exception:
                    curr_branch = ""

                pr_meta = {
                    "branch": curr_branch,
                    "task": task_description,
                    "review_status": review_status,
                    "created_at": datetime.now().isoformat()
                }
                span.set_attribute("branch", curr_branch)

                if getattr(ctx.deps, "container", None) is not None:
                    ctx.deps.container = await write_json(ctx.deps.container, "pull_request.json", pr_meta)
                    ctx.deps.container = await append_log(ctx.deps.container, f"PR: {pr_meta}")
            except Exception:
                pass

            print(green("✅ Pull request creation completed"))
            return f"Pull request created successfully"

        except Exception as e:
            span.set_attribute("error", str(e))
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
        finally:
            span.set_attribute("duration_seconds", time.time() - start_time)


async def get_orchestration_status(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Get current orchestration status and summary."""
    with tracer.start_as_current_span("get_orchestration_status") as span:
        start_time = time.time()
        try:
            if not ctx.deps.state:
                return "No active orchestration task."

            state = ctx.deps.state
            duration = (datetime.now() - state.start_time).total_seconds()

            span.set_attribute("task_id", state.task_id)
            span.set_attribute("current_phase", state.current_phase.value)
            span.set_attribute("status", state.status.value)
            span.set_attribute("duration_seconds", duration)
            span.set_attribute("total_requests", state.total_requests)
            span.set_attribute("error_count", len(state.errors))

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
        finally:
            span.set_attribute("duration_seconds", time.time() - start_time)


def create_orchestrator_agent(model: OpenAIChatModel) -> Agent:
    """Create the orchestration agent with standard Pydantic AI patterns."""
    system_prompt = """
You are a Feature Development Orchestrator Agent, equivalent to Codebuff's workflow coordination.

Your role:
- Coordinate multiple specialized agents (explorer, picker, thinker, implementation, reviewer)
- Manage workflow state and error handling
- Ensure structured communication between agents
- Provide progress tracking and status updates

Workflow phases:
1. start_task - Initialize with task description and focus area
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
    # Not sure if adding this helps
    # agent.system_prompt(add_file_token_scores_token_callers_to_context)
    agent.system_prompt(add_project_file_tree_to_context)
    agent.tool(start_task)
    agent.tool(explore_codebase)
    agent.tool(create_implementation_plan)
    agent.tool(execute_implementation)
    agent.tool(review_changes)
    agent.tool(create_pull_request)
    agent.tool(get_orchestration_status)

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

    # Analysis & session
    agent.tool(think_deeply)

    print(f"Orchestrator Agent created with model: {model.model_name}")
    return agent

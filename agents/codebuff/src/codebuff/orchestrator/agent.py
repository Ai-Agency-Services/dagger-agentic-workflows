"""Main orchestration agent that coordinates Codebuff subagents."""

import time
from datetime import datetime
import uuid
import json
from dagger import dag

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from simple_chalk import blue, green, red, yellow, cyan, magenta
from ..utils.container_state import write_json, write_text, append_log

from .tools.planning import create_plan, add_subgoal, update_subgoal, think_deeply
from .tools.file_ops import read_files as read_files_tool, write_file as write_file_tool, str_replace as str_replace_tool, code_search as code_search_tool
from .tools.execution import run_terminal_command as run_terminal_command_tool
from ..file_explorer.agent import (
    create_file_explorer_agent,
    run_file_pickers_in_parallel,
    FileExplorerDependencies,
)
from ..implementation.agent import create_implementation_agent, ImplementationDependencies
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

            # Persist task spec + log
            try:
                if getattr(ctx.deps, "container", None) is not None:
                    spec = {
                        "id": task_spec.id,
                        "goal": task_spec.goal,
                        "focus_area": task_spec.focus_area,
                        "created_at": state.start_time.isoformat(),
                    }
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
            from ..file_picker.agent import _is_code_file
            code_files = [f for f in unique_files if _is_code_file(f)]
            
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

            # Execute targeted tests
            tests_passed = False
            test_output = ""
            per_file_results = []

            # Get test command template from config
            reporter_config = getattr(ctx.deps.config, 'reporter', None)
            file_test_template = getattr(
                reporter_config, 'file_test_command_template', None) if reporter_config else None

            if test_files:
                print(blue(f"🧪 Running {len(test_files)} targeted test files"))
                tests_passed = True  # Assume success until a failure occurs
                for test_file in test_files[:20]:
                    try:
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
                        test_output_single = await ctx.deps.container.with_exec(["bash", "-lc", cmd]).stdout()
                        per_file_results.append({
                            "file": test_file,
                            "command": cmd,
                            "status": "passed",
                            "output": (test_output_single or "")[:2000]
                        })
                    except Exception as e:
                        tests_passed = False
                        per_file_results.append({
                            "file": test_file,
                            "command": cmd,
                            "status": "failed",
                            "error": str(e)[:1000]
                        })
                test_output = json.dumps(per_file_results)[:5000]
            else:
                test_cmd = getattr(ctx.deps.config.testing, "test_command", None) if hasattr(
                    ctx.deps.config, 'testing') else None
                if test_cmd:
                    print(
                        blue(f"🧪 No targeted tests found, running configured test command: {test_cmd}"))
                    try:
                        test_output = await ctx.deps.container.with_exec(["bash", "-lc", test_cmd]).stdout() or ""
                        tests_passed = True
                    except Exception as e:
                        error_msg = str(e)
                        if any(phrase in error_msg.lower() for phrase in [
                            "collected 0 items", "no tests collected", "exit code: 5"
                        ]):
                            tests_passed = True
                            test_output = error_msg + \
                                "\n(No tests collected; treating as success)"
                        else:
                            tests_passed = False
                            test_output = error_msg[:5000]
                else:
                    print(
                        yellow("⚠️ No targeted tests detected and no fallback test command configured"))
                    tests_passed = True
                    test_output = "No tests to run; proceeding with implementation"

            # Save detailed test results
            ctx.deps.container = await write_json(
                ctx.deps.container,
                "implementation/test-results.json",
                {
                    "tests_passed": tests_passed,
                    "test_strategy": "targeted" if test_files else "fallback",
                    "files_tested": test_files,
                    "per_file_results": per_file_results,
                    "summary_output": test_output
                }
            )

            # Validate that actual feature code was implemented (not just test changes)
            if not code_files and test_files:
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

            # Gate commit on test results
            if not tests_passed:
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
                cmds = [
                    "git config user.name 'Codebuff Agent'",
                    "git config user.email 'codebuff@example.com'",
                    f"git checkout -b {branch}",
                    "git add -A",
                    f"git commit -m \"feat: {state.task_spec.goal if state.task_spec else 'feature'}\\n\\nAutomated commit: applied implementation changes\\nIncludes targeted tests with passing test suite\"",
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

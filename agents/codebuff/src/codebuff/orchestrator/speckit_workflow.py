"""Spec-kit methodology workflow functions.

Implements Constitution → Spec → Tasks methodology for feature development.
"""

import json
import logging
import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Tuple, Type, TypeVar, TYPE_CHECKING

import dagger
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

# Context size limits to prevent overflow
MAX_EXPLORATION_CHARS = 5000
MAX_CONTEXT_CHARS = 8000
MAX_SAVED_CONTEXT_CHARS = 10000

if TYPE_CHECKING:
    from .agent import update_progress

from .models import (
    Constitution,
    LLMGenerationError,
    OrchestratorDependencies,
    Requirement,
    Spec,
    StateError,
    Task,
    TaskDependency,
    TaskExecutionError,
    ValidationError,
)

T = TypeVar('T', bound=BaseModel)

# ============================================================================
# Validation Functions
# ============================================================================

async def validate_constitution(constitution: Constitution) -> bool:
    """Ensure constitution is complete and actionable."""
    return (
        len(constitution.values) >= 2 and
        len(constitution.constraints) >= 1 and
        len(constitution.quality_gates) >= 1 and
        all(len(v.strip()) > 0 for v in constitution.values) and
        all(len(c.strip()) > 0 for c in constitution.constraints) and
        all(len(q.strip()) > 0 for q in constitution.quality_gates)
    )


async def validate_spec(
    spec: Spec,
    constitution: Constitution
) -> Tuple[bool, List[str]]:
    """Ensure spec aligns with constitution and is complete."""
    issues = []
    
    if not spec.objective or len(spec.objective.strip()) == 0:
        issues.append("Missing or empty objective")
    
    if len(spec.requirements) == 0:
        issues.append("No requirements defined")
    
    # Check for duplicate requirement IDs
    req_ids = [r.id for r in spec.requirements]
    if len(req_ids) != len(set(req_ids)):
        duplicates = [id for id in req_ids if req_ids.count(id) > 1]
        issues.append(f"Duplicate requirement IDs: {', '.join(set(duplicates))}")
    
    for req in spec.requirements:
        if not req.acceptance_criteria or len(req.acceptance_criteria) == 0:
            issues.append(f"Requirement {req.id} has no acceptance criteria")
        
        # Check acceptance criteria quality
        for i, ac in enumerate(req.acceptance_criteria):
            if len(ac.strip()) < 10:  # Too vague
                issues.append(
                    f"Requirement {req.id} acceptance criterion {i+1} is too vague: '{ac}'"
                )
    
    if len(spec.success_criteria) == 0:
        issues.append("No success criteria defined")
    
    # Check alignment: success criteria should relate to quality gates
    success_lower = ' '.join(spec.success_criteria).lower()
    gates_lower = ' '.join(constitution.quality_gates).lower()
    
    # Look for keyword overlap
    success_words = set(success_lower.split())
    gates_words = set(gates_lower.split())
    common_words = success_words & gates_words
    
    if len(common_words) < 2:  # Weak alignment
        issues.append(
            "Success criteria may not align with constitution quality gates. "
            f"Quality gates: {constitution.quality_gates}. Success criteria: {spec.success_criteria}"
        )
    
    return len(issues) == 0, issues


async def validate_tasks(
    tasks: List[Task],
    spec: Spec
) -> Tuple[bool, List[str]]:
    """Ensure tasks cover all spec requirements and form valid DAG."""
    issues = []
    
    if len(tasks) == 0:
        issues.append("No tasks defined")
        return False, issues
    
    # Check for duplicate task IDs
    task_ids = [t.id for t in tasks]
    if len(task_ids) != len(set(task_ids)):
        duplicates = [id for id in task_ids if task_ids.count(id) > 1]
        issues.append(f"Duplicate task IDs: {', '.join(set(duplicates))}")
    
    # Build dependency graph and check for cycles using topological sort
    graph = defaultdict(list)
    in_degree = {task.id: 0 for task in tasks}
    
    for task in tasks:
        for dep in task.dependencies:
            if dep.task_id not in in_degree:
                issues.append(
                    f"Task {task.id} depends on non-existent task {dep.task_id}"
                )
                continue
            graph[dep.task_id].append(task.id)
            in_degree[task.id] += 1
    
    # Topological sort to detect cycles
    queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
    sorted_tasks = []
    
    while queue:
        current = queue.popleft()
        sorted_tasks.append(current)
        
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(sorted_tasks) != len(tasks):
        # Circular dependency detected
        remaining = set(in_degree.keys()) - set(sorted_tasks)
        issues.append(f"Circular dependency detected involving tasks: {', '.join(remaining)}")
    
    # Check that all requirements are covered
    must_reqs = [r for r in spec.requirements if r.priority == "must"]
    if len(tasks) < len(must_reqs):
        issues.append(
            f"Only {len(tasks)} tasks for {len(must_reqs)} must-have requirements - may be insufficient"
        )
    
    # Check task completeness
    for task in tasks:
        if not task.acceptance_criteria:
            issues.append(f"Task {task.id} has no acceptance criteria")
        
        if not task.files_to_modify:
            issues.append(f"Task {task.id} has no files to modify")
    
    return len(issues) == 0, issues


# ============================================================================
# Spec-Kit Workflow Functions
# ============================================================================

async def explore_codebase(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str
) -> str:
    """
    Explore codebase to gather context for constitution.
    
    Returns concise summary limiting context size.
    """
    # Simple, focused exploration without heavy web scraping
    explorer_prompt = f"""
    Briefly explore the codebase to understand patterns for: {task_description}
    
    Focus on:
    1. Key file locations and structure
    2. Testing setup (if any)
    3. Relevant patterns
    
    Keep response under 500 words.
    """
    
    try:
        # Use file-explorer agent with timeout and size limits
        explorer = ctx.deps.get_file_explorer()
        
        # Run with strict limits to prevent context overflow
        result = await explorer.run(
            explorer_prompt,
            deps=ctx.deps
        )
        
        output = result.output if hasattr(result, 'output') else str(result)
        
        # Truncate if too long (safety check)
        if len(output) > MAX_EXPLORATION_CHARS:
            logging.warning(f"Explorer output truncated from {len(output)} to {MAX_EXPLORATION_CHARS} chars")
            output = output[:MAX_EXPLORATION_CHARS] + "\n... (truncated for brevity)"
        
        return output
    except Exception as e:
        logging.exception(f"Exploration failed: {e}")
        # Return minimal fallback instead of failing
        return f"Codebase exploration limited due to error. Task: {task_description}"


async def create_constitution(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    codebase_context: str
) -> Constitution:
    """
    Phase 1: Generate project constitution.
    Defines core values, constraints, and quality gates.
    """
    # Truncate context if needed to prevent overflow
    if len(codebase_context) > MAX_CONTEXT_CHARS:
        logging.warning(f"Truncating codebase context from {len(codebase_context)} to {MAX_CONTEXT_CHARS} chars")
        codebase_context = codebase_context[:MAX_CONTEXT_CHARS] + "\n... (truncated)"
    
    # Get LLM model - prefer cheaper model for planning
    model_name = (
        ctx.deps.config.orchestrator.speckit.planning_model
        if hasattr(ctx.deps.config.orchestrator, 'speckit') and 
           hasattr(ctx.deps.config.orchestrator.speckit, 'planning_model')
        else str(ctx.deps.model.model_name) if ctx.deps.model else 'openai:gpt-4o-mini'
    )
    
    # Create agent with structured output
    agent = Agent[
        OrchestratorDependencies,
        Constitution
    ](
        model=model_name,
        deps_type=OrchestratorDependencies,
        output_type=Constitution,
        retries=2
    )
    
    prompt = f"""
Create a Constitution for this feature request:

**Feature**: {task_description}

**Codebase Context**:
{codebase_context}

The Constitution must define:

1. **Core Values** (2-4 values): What matters most for this feature?
   - Examples: "Maintainability", "Performance", "User Privacy", "Backward Compatibility"
   - Focus on what will guide implementation decisions

2. **Constraints** (1-3 constraints): What must we avoid or respect?
   - Examples: "No breaking API changes", "Must work offline", "Zero external dependencies"
   - Think about technical and business limitations

3. **Quality Gates** (2-4 gates): How do we know we succeeded?
   - Examples: "All tests pass", "Code coverage >80%", "Performance <100ms", "Passes accessibility audit"
   - Must be measurable/verifiable

Be specific to THIS feature, not generic. Use the codebase context to inform your choices.
    """
    
    try:
        result = await agent.run(prompt, deps=ctx.deps)
        constitution = result.output
        
        # Validate
        if not await validate_constitution(constitution):
            raise ValidationError(
                "Generated constitution failed validation",
                ["Constitution does not meet minimum requirements"]
            )
        
        return constitution
    except Exception as e:
        logging.error(f"Constitution generation failed: {e}")
        raise LLMGenerationError(f"Failed to generate constitution: {e}")


async def create_spec(
    ctx: RunContext[OrchestratorDependencies],
    constitution: Constitution,
    task_description: str
) -> Spec:
    """
    Phase 2: Generate detailed specification.
    Must align with constitution.
    """
    # Truncate task description if needed
    if len(task_description) > MAX_CONTEXT_CHARS:
        logging.warning(f"Truncating task description from {len(task_description)} to {MAX_CONTEXT_CHARS} chars")
        task_description = task_description[:MAX_CONTEXT_CHARS] + "\n... (truncated)"
    
    model_name = (
        ctx.deps.config.orchestrator.speckit.planning_model
        if hasattr(ctx.deps.config.orchestrator, 'speckit') and 
           hasattr(ctx.deps.config.orchestrator.speckit, 'planning_model')
        else str(ctx.deps.model.model_name) if ctx.deps.model else 'openai:gpt-4o-mini'
    )
    
    agent = Agent[
        OrchestratorDependencies,
        Spec
    ](
        model=model_name,
        deps_type=OrchestratorDependencies,
        output_type=Spec,
        retries=2
    )
    
    prompt = f"""
Create a detailed Specification aligned with this Constitution:

**Constitution**:
Values: {', '.join(constitution.values)}
Constraints: {', '.join(constitution.constraints)}
Quality Gates: {', '.join(constitution.quality_gates)}

**Feature Request**:
{task_description}

Generate a Spec with:

1. **Objective** (1-2 sentences): Clear goal of this feature

2. **Requirements** (3-10 requirements):
   - ID format: REQ-001, REQ-002, etc.
   - Description: What needs to be built
   - Acceptance Criteria: 2-4 testable conditions per requirement
   - Priority: must/should/could (use MoSCoW)
   
   Example:
   {{
     "id": "REQ-001",
     "description": "User can authenticate with email",
     "acceptance_criteria": [
       "Email validation follows RFC 5322",
       "Password hashed with bcrypt",
       "Login fails gracefully with clear error"
     ],
     "priority": "must"
   }}

3. **Success Criteria** (2-5 criteria): How we measure completion
   - Must align with Quality Gates from Constitution
   - Be specific and measurable

4. **Out of Scope** (2-4 items): What we're NOT doing
   - Prevents scope creep
   - Clarifies boundaries

Ensure every requirement upholds the Constitution's values and respects its constraints.
    """
    
    try:
        result = await agent.run(prompt, deps=ctx.deps)
        spec = result.output
        
        # Validate against constitution
        valid, issues = await validate_spec(spec, constitution)
        if not valid:
            raise ValidationError(
                f"Spec validation failed: {len(issues)} issue(s)",
                issues
            )
        
        return spec
    except ValidationError:
        raise
    except Exception as e:
        logging.error(f"Spec generation failed: {e}")
        raise LLMGenerationError(f"Failed to generate spec: {e}")


async def create_task_plan(
    ctx: RunContext[OrchestratorDependencies],
    spec: Spec,
    constitution: Constitution,
    codebase_context: str
) -> List[Task]:
    """
    Phase 3: Break spec into executable tasks.
    Must satisfy all spec requirements.
    """
    # Truncate context if needed
    if len(codebase_context) > MAX_CONTEXT_CHARS:
        logging.warning(f"Truncating codebase context from {len(codebase_context)} to {MAX_CONTEXT_CHARS} chars")
        codebase_context = codebase_context[:MAX_CONTEXT_CHARS] + "\n... (truncated)"
    
    model_name = (
        ctx.deps.config.orchestrator.speckit.planning_model
        if hasattr(ctx.deps.config.orchestrator, 'speckit') and 
           hasattr(ctx.deps.config.orchestrator.speckit, 'planning_model')
        else str(ctx.deps.model.model_name) if ctx.deps.model else 'openai:gpt-4o-mini'
    )
    
    agent = Agent[
        OrchestratorDependencies,
        List[Task]
    ](
        model=model_name,
        deps_type=OrchestratorDependencies,
        output_type=List[Task],
        retries=2
    )
    
    # Get max tasks from config
    max_tasks = 20
    if hasattr(ctx.deps.config.orchestrator, 'speckit'):
        if hasattr(ctx.deps.config.orchestrator.speckit, 'max_tasks_per_spec'):
            max_tasks = ctx.deps.config.orchestrator.speckit.max_tasks_per_spec
    
    prompt = f"""
Create an implementation task plan for this Specification:

**Objective**: {spec.objective}

**Requirements**:
{chr(10).join(f'{r.id}: {r.description}' for r in spec.requirements)}

**Constitution Constraints**:
{chr(10).join(f'- {c}' for c in constitution.constraints)}

**Codebase Context**:
{codebase_context}

Generate 3-{max_tasks} atomic tasks.

For each task:

1. **ID**: TASK-001, TASK-002, etc.

2. **Description**: One-sentence summary of what this task does

3. **Acceptance Criteria**: 2-4 testable conditions
   - Must be verifiable (e.g., "Function X returns Y when given Z")
   - Should map to requirement acceptance criteria

4. **Dependencies**: List other task IDs this depends on
   - Format: [{{"task_id": "TASK-001", "dependency_type": "blocks"}}]
   - Types: "blocks" (must finish first) or "requires" (needs output from)
   - Ensure NO circular dependencies

5. **Complexity**: simple/moderate/complex
   - Simple: <30 min, 1 file, obvious implementation
   - Moderate: 30-120 min, 2-3 files, some design needed
   - Complex: >2 hours, multiple files, architecture decisions

6. **Test Requirements**: What tests to write/run
   - Unit tests for new functions
   - Integration tests for workflows
   - Specify test file locations

7. **Files to Modify**: List of file paths
   - Be specific (full paths from repo root)

Ensure:
- Every requirement from spec is covered by at least one task
- Tasks form a valid dependency DAG (no cycles)
- Tasks can be executed in parallel where dependencies allow
- Each task is independently testable
    """
    
    try:
        result = await agent.run(prompt, deps=ctx.deps)
        tasks = result.output
        
        # Validate
        valid, issues = await validate_tasks(tasks, spec)
        if not valid:
            raise ValidationError(
                f"Task plan validation failed: {len(issues)} issue(s)",
                issues
            )
        
        return tasks
    except ValidationError:
        raise
    except Exception as e:
        logging.error(f"Task plan generation failed: {e}")
        raise LLMGenerationError(f"Failed to generate task plan: {e}")


# ============================================================================
# Task Execution
# ============================================================================

def get_topological_order(tasks: List[Task]) -> List[Task]:
    """Return tasks in topological order (respecting dependencies)."""
    graph = defaultdict(list)
    in_degree = {task.id: 0 for task in tasks}
    task_by_id = {task.id: task for task in tasks}
    
    for task in tasks:
        for dep in task.dependencies:
            dep_id = dep.task_id
            graph[dep_id].append(task.id)
            in_degree[task.id] += 1
    
    queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
    ordered_tasks = []
    
    while queue:
        current_id = queue.popleft()
        ordered_tasks.append(task_by_id[current_id])
        
        for neighbor_id in graph[current_id]:
            in_degree[neighbor_id] -= 1
            if in_degree[neighbor_id] == 0:
                queue.append(neighbor_id)
    
    return ordered_tasks


async def execute_task(
    ctx: RunContext[OrchestratorDependencies],
    task: Task,
    constitution: Constitution,
    spec: Spec
) -> None:
    """
    Execute a single task with implementation-review loop.
    
    Raises:
        TaskExecutionError: If task fails after max retries
    """
    max_iterations = 3
    
    # Log task start
    container = await append_to_log(ctx, f"Starting task {task.id}: {task.description}")
    ctx.deps.container = container
    
    for iteration in range(max_iterations):
        try:
            # Implementation phase
            impl_result = await execute_implementation_task(ctx, task, constitution, spec, iteration)
            
            # Review phase
            review_result = await execute_review_task(ctx, task, constitution)
            
            if review_result == "APPROVED":
                # Success!
                container = await append_to_log(
                    ctx,
                    f"Task {task.id} approved after {iteration + 1} iteration(s)"
                )
                ctx.deps.container = container
                
                # Run tests if specified
                if task.test_requirements:
                    await run_task_tests(ctx, task)
                
                logging.info(f"Task {task.id} completed successfully")
                return
            
            elif review_result.startswith("NEEDS_CHANGES:"):
                feedback = review_result.replace("NEEDS_CHANGES:", "").strip()
                container = await append_to_log(
                    ctx,
                    f"Task {task.id} iteration {iteration + 1}: needs changes - {feedback}"
                )
                ctx.deps.container = container
                
                if iteration == max_iterations - 1:
                    raise TaskExecutionError(
                        f"Task {task.id} failed to pass review after {max_iterations} iterations. "
                        f"Last feedback: {feedback}",
                        task.id
                    )
                
                # Continue to next iteration with feedback
                continue
            
            else:
                raise ValueError(f"Unexpected review result: {review_result}")
        
        except Exception as e:
            logging.error(f"Error executing task {task.id} on iteration {iteration + 1}: {e}")
            container = await append_to_log(ctx, f"Task {task.id} error: {str(e)}")
            ctx.deps.container = container
            
            if iteration == max_iterations - 1:
                raise TaskExecutionError(f"Task {task.id} failed: {e}", task.id)
            
            # Retry
            continue


async def execute_implementation_task(
    ctx: RunContext[OrchestratorDependencies],
    task: Task,
    constitution: Constitution,
    spec: Spec,
    iteration: int
) -> str:
    """
    Execute implementation phase using implementation agent.
    
    Returns:
        Result message from implementation agent
    """
    # Lazy-load implementation agent
    impl_agent = ctx.deps.get_implementation()
    
    # Create implementation dependencies
    from ..implementation.agent import ImplementationDependencies
    impl_deps = ImplementationDependencies(
        config=ctx.deps.config,
        container=ctx.deps.container,
        plan=""  # Task-based, no markdown plan needed
    )
    
    impl_prompt = f"""
Implement this task (iteration {iteration + 1}):

**Task ID**: {task.id}
**Description**: {task.description}

**Acceptance Criteria**:
{chr(10).join(f'- {c}' for c in task.acceptance_criteria)}

**Files to Modify**: {', '.join(task.files_to_modify)}

**Constitution**:
- Values: {', '.join(constitution.values)}
- Constraints: {', '.join(constitution.constraints)}

**Spec Context**: {spec.objective}

Make minimal, focused changes to accomplish only what's needed.
    """
    
    result = await impl_agent.run(impl_prompt, deps=impl_deps)
    
    # Update container from implementation
    ctx.deps.container = impl_deps.container
    
    return result.output


async def execute_review_task(
    ctx: RunContext[OrchestratorDependencies],
    task: Task,
    constitution: Constitution
) -> str:
    """
    Execute review phase using reviewer agent.
    
    Returns:
        "APPROVED" or "NEEDS_CHANGES: <feedback>"
    """
    # Lazy-load reviewer agent
    reviewer_agent = ctx.deps.get_reviewer()
    
    # Create reviewer dependencies
    from ..reviewer.agent import ReviewerDependencies
    reviewer_deps = ReviewerDependencies(
        container=ctx.deps.container,
        config=ctx.deps.config,
        read_file=lambda path: ctx.deps.container.file(path).contents(),
        write_file=lambda path, content: ctx.deps.container.with_new_file(path, content),
        run_command=lambda cmd: ctx.deps.container.with_exec(cmd)
    )
    
    review_prompt = f"""
Review the implementation of task {task.id}:

**Task Description**: {task.description}

**Acceptance Criteria**:
{chr(10).join(f'- {c}' for c in task.acceptance_criteria)}

**Constitution Quality Gates**:
{chr(10).join(f'- {q}' for q in constitution.quality_gates)}

Check:
1. Does the implementation meet all acceptance criteria?
2. Does it uphold the constitution's values?
3. Are there any code quality issues?
4. Are tests adequate (if applicable)?

Respond with:
- "APPROVED" if all criteria met
- "NEEDS_CHANGES: <specific feedback>" if issues found

Be specific and actionable in feedback.
    """
    
    result = await reviewer_agent.run(review_prompt, deps=reviewer_deps)
    
    # Update container from reviewer
    ctx.deps.container = reviewer_deps.container
    
    return result.output.strip()


async def run_task_tests(
    ctx: RunContext[OrchestratorDependencies],
    task: Task
) -> None:
    """
    Run tests specified in task requirements.
    
    Raises:
        TaskExecutionError: If tests fail
    """
    for test_file in task.test_requirements:
        logging.info(f"Running tests: {test_file}")
        
        # Determine test command based on file extension
        if test_file.endswith('.py'):
            cmd = ["bash", "-c", f"pytest {test_file} -v"]
        elif test_file.endswith(('.js', '.ts')):
            cmd = ["bash", "-c", f"npm test {test_file}"]
        else:
            logging.warning(f"Unknown test file type: {test_file} - skipping")
            continue
        
        try:
            container_with_test = ctx.deps.container.with_exec(cmd)
            result = await container_with_test.stdout()
            ctx.deps.container = container_with_test
            logging.info(f"Tests passed: {test_file}")
        except Exception as e:
            raise TaskExecutionError(f"Tests failed for {test_file}: {e}", task.id)


# ============================================================================
# State Persistence (Dagger-safe with immutable containers)
# ============================================================================

async def save_to_state(
    ctx: RunContext[OrchestratorDependencies],
    filename: str,
    data: BaseModel | Dict[str, Any]
) -> dagger.Container:
    """Save data to .codebuff-state directory.
    
    Returns new container with updated state.
    Caller must update ctx.deps.container with returned value.
    """
    container = ctx.deps.container
    
    try:
        json_data = (
            data.model_dump_json(indent=2) if isinstance(data, BaseModel)
            else json.dumps(data, indent=2)
        )
        
        # Return NEW container (immutable pattern)
        new_container = container.with_new_file(
            f".codebuff-state/{filename}",
            json_data
        )
        
        logging.info(f"Saved state to .codebuff-state/{filename}")
        return new_container
    except Exception as e:
        logging.error(f"Failed to save state to {filename}: {e}")
        raise StateError(f"State persistence failed for {filename}: {e}")


async def load_from_state(
    ctx: RunContext[OrchestratorDependencies],
    filename: str,
    model_class: Type[T] | None = None
) -> T | Dict | None:
    """Load data from .codebuff-state directory.
    
    Returns None if file doesn't exist.
    Raises ValueError if file exists but is corrupted.
    """
    container = ctx.deps.container
    
    try:
        file = container.file(f".codebuff-state/{filename}")
        content = await file.contents()
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupted JSON in {filename}: {e}")
        
        if model_class:
            try:
                return model_class.model_validate(data)
            except Exception as e:
                raise ValueError(f"Invalid data in {filename} for {model_class.__name__}: {e}")
        
        return data
    except Exception as e:
        if "no such file" in str(e).lower() or "not found" in str(e).lower():
            logging.debug(f"State file {filename} not found")
            return None
        logging.error(f"Failed to load state from {filename}: {e}")
        raise


async def append_to_log(
    ctx: RunContext[OrchestratorDependencies],
    message: str
) -> dagger.Container:
    """Append message to task_log.jsonl.
    
    Returns new container with updated log.
    """
    
    container = ctx.deps.container
    log_entry = {
        "timestamp": time.time(),
        "message": message
    }
    
    try:
        # Try to read existing log
        file = container.file(".codebuff-state/task_log.jsonl")
        existing = await file.contents()
    except:
        existing = ""
    
    new_log = existing + json.dumps(log_entry) + "\n"
    
    new_container = container.with_new_file(
        ".codebuff-state/task_log.jsonl",
        new_log
    )
    
    return new_container


async def update_workflow_progress(
    container: dagger.Container,
    phase: str,
    status: str
) -> dagger.Container:
    """Update progress.json for external monitoring.
    
    Returns new container with updated progress.
    """
    
    progress = {
        "phase": phase,
        "status": status,
        "timestamp": time.time()
    }
    
    new_container = container.with_new_file(
        ".codebuff-state/progress.json",
        json.dumps(progress, indent=2)
    )
    
    return new_container




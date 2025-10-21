# Spec-Kit Complete Replacement Plan

## Overview
Replace the current Codebuff planning and implementation workflow with spec-kit's proven methodology (Constitution → Spec → Plan → Tasks). This is a complete replacement, not a hybrid approach.

## Phase 0: Setup Agent Infrastructure

### 0.1 Update OrchestratorDependencies
**File:** `agents/codebuff/src/codebuff/orchestrator/models.py`

Add agent fields to OrchestratorDependencies:
```python
from typing import Optional
from pydantic_ai import Agent

@dataclass
class OrchestratorDependencies:
    container: dagger.Container
    config: dict
    llm_model: str
    
    # Lazy-loaded sub-agents (initialized on first use)
    file_explorer_agent: Optional[Agent] = None
    file_picker_agent: Optional[Agent] = None
    implementation_agent: Optional[Agent] = None
    reviewer_agent: Optional[Agent] = None
    
    def get_file_explorer(self) -> Agent:
        """Lazy-load file explorer agent."""
        if self.file_explorer_agent is None:
            from codebuff.file_explorer.agent import create_file_explorer_agent
            self.file_explorer_agent = create_file_explorer_agent()
        return self.file_explorer_agent
    
    def get_file_picker(self) -> Agent:
        """Lazy-load file picker agent."""
        if self.file_picker_agent is None:
            from codebuff.file_picker.agent import create_file_picker_agent
            self.file_picker_agent = create_file_picker_agent()
        return self.file_picker_agent
    
    def get_implementation(self) -> Agent:
        """Lazy-load implementation agent."""
        if self.implementation_agent is None:
            from codebuff.implementation.agent import create_implementation_agent
            self.implementation_agent = create_implementation_agent()
        return self.implementation_agent
    
    def get_reviewer(self) -> Agent:
        """Lazy-load reviewer agent."""
        if self.reviewer_agent is None:
            from codebuff.reviewer.agent import create_reviewer_agent
            self.reviewer_agent = create_reviewer_agent()
        return self.reviewer_agent
```

## Phase 1: Core Spec-Kit Integration

### 1.1 Update Dependencies
- Add spec-kit as a dependency to `agents/codebuff/pyproject.toml`
- Version: Use latest stable release
- Run `uv add spec-kit` in the codebuff agent directory

### 1.2 Create Spec-Kit Models
**File:** `agents/codebuff/src/codebuff/orchestrator/models.py`

Add new Pydantic models mirroring spec-kit's structure:

```python
class Constitution(BaseModel):
    """Project constitution defining core values and constraints."""
    values: list[str]
    constraints: list[str]
    quality_gates: list[str]

class Requirement(BaseModel):
    """Individual requirement from the spec."""
    id: str
    description: str
    acceptance_criteria: list[str]
    priority: Literal["must", "should", "could"]

class Spec(BaseModel):
    """Detailed specification of what to build."""
    objective: str
    requirements: list[Requirement]
    success_criteria: list[str]
    out_of_scope: list[str]

class TaskDependency(BaseModel):
    """Dependency between tasks."""
    task_id: str
    dependency_type: Literal["blocks", "requires"]

class Task(BaseModel):
    """Individual implementation task."""
    id: str
    description: str
    acceptance_criteria: list[str]
    dependencies: list[TaskDependency]
    estimated_complexity: Literal["simple", "moderate", "complex"]
    test_requirements: list[str]
    files_to_modify: list[str]

class SpecKitPlan(BaseModel):
    """Complete spec-kit based plan."""
    constitution: Constitution
    spec: Spec
    tasks: list[Task]
    validation_status: dict[str, bool]  # Track validation at each stage
```

### 1.3 Remove Legacy Models
From `agents/codebuff/src/codebuff/orchestrator/models.py`, **remove**:
- `PlanStep` dataclass
- `Plan` dataclass with `_coerce_steps` method
- Any references to `plan.md` format

## Phase 2: Implement Spec-Kit Workflow Functions

### 2.1 Constitution Phase
**File:** `agents/codebuff/src/codebuff/orchestrator/agent.py`

Create new function:
```python
async def explore_codebase(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str
) -> str:
    """
    Explore codebase to gather context for constitution.
    """
    # Spawn file-explorer agent to understand codebase
    from pydantic_ai import Agent
    
    explorer_prompt = f"""
    Explore the codebase to understand:
    1. Existing code patterns and conventions
    2. Testing practices
    3. Architecture decisions
    4. Related code to: {task_description}
    """
    
    # Use file-explorer agent
    result = await ctx.deps.file_explorer_agent.run(
        explorer_prompt,
        deps=ctx.deps
    )
    
    return result.output

async def create_constitution(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    codebase_context: str
) -> Constitution:
    """
    Phase 1: Generate project constitution.
    Defines core values, constraints, and quality gates.
    """
    from pydantic_ai import Agent
    from pydantic_ai.models.openai import OpenAIModel
    
    # Get LLM model - prefer cheaper model for planning
    model_name = (
        ctx.deps.config.get('orchestrator', {})
        .get('speckit', {})
        .get('planning_model', ctx.deps.llm_model)
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
            raise ValueError("Generated constitution failed validation")
        
        return constitution
    except Exception as e:
        # Log error and retry with more guidance
        logging.error(f"Constitution generation failed: {e}")
        raise ValueError(f"Failed to generate constitution: {e}")
```

### 2.2 Spec Phase
**File:** `agents/codebuff/src/codebuff/orchestrator/agent.py`

Create new function:
```python
async def create_spec(
    ctx: RunContext[OrchestratorDependencies],
    constitution: Constitution,
    task_description: str
) -> Spec:
    """
    Phase 2: Generate detailed specification.
    Must align with constitution.
    """
    agent = Agent[
        OrchestratorDependencies,
        Spec
    ](
        ctx.deps.llm_model,
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
       {
         "id": "REQ-001",
         "description": "User can authenticate with email",
         "acceptance_criteria": [
           "Email validation follows RFC 5322",
           "Password hashed with bcrypt",
           "Login fails gracefully with clear error"
         ],
         "priority": "must"
       }
    
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
            raise ValueError(f"Spec validation failed: {', '.join(issues)}")
        
        return spec
    except Exception as e:
        logging.error(f"Spec generation failed: {e}")
        raise ValueError(f"Failed to generate spec: {e}")
```

### 2.3 Plan Phase
**File:** `agents/codebuff/src/codebuff/orchestrator/agent.py`

Create new function:
```python
async def create_task_plan(
    ctx: RunContext[OrchestratorDependencies],
    spec: Spec,
    constitution: Constitution,
    codebase_context: str
) -> list[Task]:
    """
    Phase 3: Break spec into executable tasks.
    Must satisfy all spec requirements.
    """
    agent = Agent[
        OrchestratorDependencies,
        list[Task]
    ](
        ctx.deps.llm_model,
        output_type=list[Task],
        retries=2
    )
    
    # First, spawn file-picker to identify relevant files
    file_picker_prompt = f"""
    Find files relevant to implementing:
    {spec.objective}
    
    Requirements:
    {chr(10).join(f'- {r.description}' for r in spec.requirements)}
    """
    
    file_picker_result = await ctx.deps.file_picker_agent.run(
        file_picker_prompt,
        deps=ctx.deps
    )
    relevant_files = file_picker_result.output
    
    prompt = f"""
    Create an implementation task plan for this Specification:
    
    **Objective**: {spec.objective}
    
    **Requirements**:
    {chr(10).join(f'{r.id}: {r.description}' for r in spec.requirements)}
    
    **Constitution Constraints**:
    {chr(10).join(f'- {c}' for c in constitution.constraints)}
    
    **Relevant Files** (from codebase analysis):
    {relevant_files}
    
    Generate 3-{ctx.deps.config.get('orchestrator', {}).get('speckit', {}).get('max_tasks_per_spec', 20)} atomic tasks.
    
    For each task:
    
    1. **ID**: TASK-001, TASK-002, etc.
    
    2. **Description**: One-sentence summary of what this task does
    
    3. **Acceptance Criteria**: 2-4 testable conditions
       - Must be verifiable (e.g., "Function X returns Y when given Z")
       - Should map to requirement acceptance criteria
    
    4. **Dependencies**: List other task IDs this depends on
       - Format: [{"task_id": "TASK-001", "dependency_type": "blocks"}]
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
       - Use the relevant files identified above
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
            raise ValueError(f"Task plan validation failed: {', '.join(issues)}")
        
        return tasks
    except Exception as e:
        logging.error(f"Task plan generation failed: {e}")
        raise ValueError(f"Failed to generate task plan: {e}")
```

### 2.4 Validation Functions
**File:** `agents/codebuff/src/codebuff/orchestrator/agent.py`

Add comprehensive validation at each stage:
```python
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
) -> tuple[bool, list[str]]:
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
                issues.append(f"Requirement {req.id} acceptance criterion {i+1} is too vague: '{ac}'")
    
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
    tasks: list[Task],
    spec: Spec
) -> tuple[bool, list[str]]:
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
    from collections import defaultdict, deque
    
    graph = defaultdict(list)
    in_degree = {task.id: 0 for task in tasks}
    
    for task in tasks:
        for dep in task.dependencies:
            if dep["task_id"] not in in_degree:
                issues.append(f"Task {task.id} depends on non-existent task {dep['task_id']}")
                continue
            graph[dep["task_id"]].append(task.id)
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
    req_ids_in_spec = {req.id for req in spec.requirements if req.priority == "must"}
    # This is simplified - in real impl, would need to map tasks to requirements
    # For now, just check that we have enough tasks
    if len(tasks) < len([r for r in spec.requirements if r.priority == "must"]):
        issues.append(
            f"Only {len(tasks)} tasks for {len([r for r in spec.requirements if r.priority == 'must'])} "
            "must-have requirements - may be insufficient"
        )
    
    # Check task complexity
    for task in tasks:
        if not task.acceptance_criteria:
            issues.append(f"Task {task.id} has no acceptance criteria")
        
        if not task.files_to_modify:
            issues.append(f"Task {task.id} has no files to modify")
    
    return len(issues) == 0, issues
```

## Phase 3: Update Orchestrator Main Workflow

### 3.1 Replace `orchestrate_feature_development`
**File:** `agents/codebuff/src/codebuff/orchestrator/agent.py`

**Remove** the current implementation entirely.

**Replace with:**
```python
import logging

async def orchestrate_feature_development(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str
) -> str:
    """
    Main orchestration using spec-kit methodology.
    
    Flow:
    1. Explore codebase
    2. Create Constitution
    3. Create Spec (validate against Constitution)
    4. Create Tasks (validate against Spec)
    5. Execute Tasks (with review loop)
    6. Create PR
    
    Raises:
        ValidationError: If any phase validation fails
        TaskExecutionError: If task execution fails
        StateError: If state persistence fails
    """
    
    try:
        # Step 1: Explore codebase
        logging.info("Phase 1: Exploring codebase")
        container = await update_progress(ctx, "exploration", "in_progress")
        ctx.deps.container = container
        
        exploration_report = await explore_codebase(ctx, task_description)
        
        container = await update_progress(ctx, "exploration", "complete")
        ctx.deps.container = container
        
        # Step 2: Constitution
        logging.info("Phase 2: Creating constitution")
        container = await update_progress(ctx, "constitution", "in_progress")
        ctx.deps.container = container
        
        constitution = await create_constitution(ctx, task_description, exploration_report)
        
        if not await validate_constitution(constitution):
            raise ValidationError(
                "Constitution validation failed",
                ["Constitution does not meet minimum requirements"]
            )
        
        # Save constitution (get new container)
        container = await save_to_state(ctx, "constitution.json", constitution)
        ctx.deps.container = container
        
        container = await update_progress(ctx, "constitution", "complete")
        ctx.deps.container = container
        
        logging.info(f"Constitution created: {len(constitution.values)} values, {len(constitution.constraints)} constraints")
        
        # Step 3: Spec
        logging.info("Phase 3: Creating specification")
        container = await update_progress(ctx, "spec", "in_progress")
        ctx.deps.container = container
        
        spec = await create_spec(ctx, constitution, task_description)
        
        valid, issues = await validate_spec(spec, constitution)
        if not valid:
            raise ValidationError(
                f"Spec validation failed: {len(issues)} issue(s)",
                issues
            )
        
        container = await save_to_state(ctx, "spec.json", spec)
        ctx.deps.container = container
        
        container = await update_progress(ctx, "spec", "complete")
        ctx.deps.container = container
        
        logging.info(f"Spec created: {len(spec.requirements)} requirements")
        
        # Step 4: Tasks
        logging.info("Phase 4: Creating task plan")
        container = await update_progress(ctx, "tasks", "in_progress")
        ctx.deps.container = container
        
        tasks = await create_task_plan(ctx, spec, constitution, exploration_report)
        
        valid, issues = await validate_tasks(tasks, spec)
        if not valid:
            raise ValidationError(
                f"Task plan validation failed: {len(issues)} issue(s)",
                issues
            )
        
        container = await save_to_state(ctx, "tasks.json", {"tasks": [t.model_dump() for t in tasks]})
        ctx.deps.container = container
        
        container = await update_progress(ctx, "tasks", "complete")
        ctx.deps.container = container
        
        logging.info(f"Task plan created: {len(tasks)} tasks")
        
        # Step 5: Execute tasks in topological order
        logging.info("Phase 5: Executing tasks")
        container = await update_progress(ctx, "execution", "in_progress")
        ctx.deps.container = container
        
        # Get topological order (assumes validate_tasks already checked for cycles)
        task_order = get_topological_order(tasks)
        
        for i, task in enumerate(task_order):
            logging.info(f"Executing task {i+1}/{len(task_order)}: {task.id}")
            
            try:
                await execute_task(ctx, task, constitution, spec)
            except TaskExecutionError as e:
                logging.error(f"Task {task.id} failed: {e}")
                
                # Decide: abort or continue?
                enforce_validation = (
                    ctx.deps.config.get('orchestrator', {})
                    .get('speckit', {})
                    .get('enforce_validation', True)
                )
                
                if enforce_validation:
                    raise  # Abort workflow
                else:
                    logging.warning(f"Skipping failed task {task.id}, continuing with remaining tasks")
                    container = await append_to_log(ctx, f"SKIPPED task {task.id} due to failure")
                    ctx.deps.container = container
                    continue
        
        container = await update_progress(ctx, "execution", "complete")
        ctx.deps.container = container
        
        # Step 6: Create PR
        logging.info("Phase 6: Creating pull request")
        container = await update_progress(ctx, "pr_creation", "in_progress")
        ctx.deps.container = container
        
        pr_result = await create_pull_request_with_speckit_context(ctx, constitution, spec, tasks)
        
        container = await update_progress(ctx, "pr_creation", "complete")
        ctx.deps.container = container
        
        logging.info("Orchestration completed successfully")
        return pr_result
    
    except ValidationError as e:
        logging.error(f"Validation failed: {e}")
        logging.error(f"Issues: {e.issues}")
        
        # Save error state
        container = await update_progress(ctx, "validation_error", "failed")
        ctx.deps.container = container
        
        raise
    
    except TaskExecutionError as e:
        logging.error(f"Task execution failed: {e}")
        
        # Save error state
        container = await update_progress(ctx, "execution_error", "failed")
        ctx.deps.container = container
        
        raise
    
    except Exception as e:
        logging.error(f"Orchestration failed with unexpected error: {e}")
        
        # Save error state
        container = await update_progress(ctx, "unknown_error", "failed")
        ctx.deps.container = container
        
        raise OrchestrationError(f"Orchestration failed: {e}")

def get_topological_order(tasks: list[Task]) -> list[Task]:
    """Return tasks in topological order (respecting dependencies)."""
    from collections import defaultdict, deque
    
    graph = defaultdict(list)
    in_degree = {task.id: 0 for task in tasks}
    task_by_id = {task.id: task for task in tasks}
    
    for task in tasks:
        for dep in task.dependencies:
            dep_id = dep["task_id"]
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

async def create_pull_request_with_speckit_context(
    ctx: RunContext[OrchestratorDependencies],
    constitution: Constitution,
    spec: Spec,
    tasks: list[Task]
) -> str:
    """
    Create PR with spec-kit context in description.
    """
    pr_description = f"""
## Spec-Kit Implementation Summary

### Constitution
**Values**: {', '.join(constitution.values)}
**Constraints**: {', '.join(constitution.constraints)}
**Quality Gates**: {', '.join(constitution.quality_gates)}

### Specification
**Objective**: {spec.objective}

**Requirements** ({len(spec.requirements)}):
{chr(10).join(f'- {r.id}: {r.description}' for r in spec.requirements)}

**Success Criteria**:
{chr(10).join(f'- {c}' for c in spec.success_criteria)}

### Implementation
**Tasks Completed**: {len(tasks)}
{chr(10).join(f'- {t.id}: {t.description}' for t in tasks)}

---
*Generated using spec-kit methodology*
    """
    
    # Use existing PR creation logic with enhanced description
    # This would call the actual PR creation agent
    # For now, return the description
    return pr_description
```

### 3.2 Task Execution with Review Loop
**File:** `agents/codebuff/src/codebuff/orchestrator/agent.py`

Add:
```python
import logging
from typing import Literal

class TaskExecutionError(Exception):
    """Raised when task execution fails after retries."""
    pass

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
            impl_result = await execute_implementation(ctx, task, constitution, spec, iteration)
            
            # Review phase
            review_result = await execute_review(ctx, task, constitution)
            
            if review_result == "APPROVED":
                # Success!
                container = await append_to_log(ctx, f"Task {task.id} approved after {iteration + 1} iteration(s)")
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
                        f"Last feedback: {feedback}"
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
                raise TaskExecutionError(f"Task {task.id} failed: {e}")
            
            # Retry
            continue

async def execute_implementation(
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
    impl_agent = ctx.deps.get_implementation()
    
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
    
    result = await impl_agent.run(impl_prompt, deps=ctx.deps)
    return result.output

async def execute_review(
    ctx: RunContext[OrchestratorDependencies],
    task: Task,
    constitution: Constitution
) -> str:
    """
    Execute review phase using reviewer agent.
    
    Returns:
        "APPROVED" or "NEEDS_CHANGES: <feedback>"
    """
    reviewer_agent = ctx.deps.get_reviewer()
    
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
    
    result = await reviewer_agent.run(review_prompt, deps=ctx.deps)
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
            cmd = f"pytest {test_file} -v"
        elif test_file.endswith(('.js', '.ts')):
            cmd = f"npm test {test_file}"
        else:
            logging.warning(f"Unknown test file type: {test_file} - skipping")
            continue
        
        # Run test (use orchestrator's run_command tool if available)
        # This is simplified - in real impl, would use proper test execution
        try:
            # Execute test command
            result = await ctx.deps.container.with_exec(cmd.split()).stdout()
            logging.info(f"Tests passed: {test_file}")
        except Exception as e:
            raise TaskExecutionError(f"Tests failed for {test_file}: {e}")
```

## Phase 4: Update State Management

### 4.1 New State Structure
**Directory:** `.codebuff-state/`

**Remove:**
- `plan.md`
- `implementation_plan.json` (if exists)

**Add:**
- `constitution.json` - Stores Constitution
- `spec.json` - Stores Spec
- `tasks.json` - Stores task list
- `task_log.jsonl` - JSONL log of task execution
- `validation_history.json` - Track validation results

### 4.2 State Persistence Functions
**File:** `agents/codebuff/src/codebuff/orchestrator/agent.py`

**CRITICAL**: Dagger containers are immutable. State persistence must return new containers.

```python
import json
import logging
from typing import TypeVar, Type

T = TypeVar('T', bound=BaseModel)

async def save_to_state(
    ctx: RunContext[OrchestratorDependencies],
    filename: str,
    data: BaseModel | dict
) -> dagger.Container:
    """Save data to .codebuff-state directory.
    
    Returns new container with updated state.
    Caller must update ctx.deps.container with returned value.
    """
    container = ctx.deps.container
    
    try:
        json_data = data.model_dump_json(indent=2) if isinstance(data, BaseModel) else json.dumps(data, indent=2)
        
        # Return NEW container (immutable pattern)
        new_container = container.with_new_file(
            f".codebuff-state/{filename}",
            json_data
        )
        
        logging.info(f"Saved state to .codebuff-state/{filename}")
        return new_container
    except Exception as e:
        logging.error(f"Failed to save state to {filename}: {e}")
        raise ValueError(f"State persistence failed for {filename}: {e}")

async def load_from_state(
    ctx: RunContext[OrchestratorDependencies],
    filename: str,
    model_class: Type[T] | None = None
) -> T | dict | None:
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
    except FileNotFoundError:
        logging.debug(f"State file {filename} not found")
        return None
    except Exception as e:
        logging.error(f"Failed to load state from {filename}: {e}")
        raise

async def append_to_log(
    ctx: RunContext[OrchestratorDependencies],
    message: str
) -> dagger.Container:
    """Append message to task_log.jsonl.
    
    Returns new container with updated log.
    """
    import time
    
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

async def update_progress(
    ctx: RunContext[OrchestratorDependencies],
    phase: str,
    status: str
) -> dagger.Container:
    """Update progress.json for external monitoring.
    
    Returns new container with updated progress.
    """
    import time
    
    container = ctx.deps.container
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
```

## Phase 5: Migration & Backward Compatibility

### 5.1 State Migration Function
**File:** `agents/codebuff/src/codebuff/orchestrator/agent.py`

```python
import logging

async def migrate_old_state(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str
) -> tuple[bool, str]:
    """
    Migrate from old plan.md format to spec-kit format.
    
    Returns:
        (success, message): Tuple of migration result and descriptive message
    """
    container = ctx.deps.container
    
    # Check if old plan.md exists
    try:
        old_plan_file = container.file(".codebuff-state/plan.md")
        old_plan_content = await old_plan_file.contents()
    except FileNotFoundError:
        return False, "No old plan.md found - nothing to migrate"
    except Exception as e:
        logging.error(f"Failed to read old plan.md: {e}")
        return False, f"Failed to read old plan.md: {e}"
    
    logging.info("Found old plan.md - starting migration")
    
    # Parse old plan.md using LLM
    try:
        constitution = await convert_plan_to_constitution(ctx, old_plan_content, task_description)
        spec = await convert_plan_to_spec(ctx, old_plan_content, task_description, constitution)
        tasks = await convert_plan_to_tasks(ctx, old_plan_content, spec)
    except Exception as e:
        logging.error(f"Migration conversion failed: {e}")
        return False, f"Failed to convert plan.md: {e}. You may need to start fresh."
    
    # Validate migrated data
    if not await validate_constitution(constitution):
        return False, "Migrated constitution failed validation - please start fresh"
    
    valid, issues = await validate_spec(spec, constitution)
    if not valid:
        logging.warning(f"Migrated spec has issues: {issues}")
        # Continue anyway - best effort
    
    valid, issues = await validate_tasks(tasks, spec)
    if not valid:
        logging.warning(f"Migrated tasks have issues: {issues}")
        # Continue anyway - best effort
    
    # Save in new format (update container each time)
    try:
        container = await save_to_state(ctx, "constitution.json", constitution)
        ctx.deps.container = container
        
        container = await save_to_state(ctx, "spec.json", spec)
        ctx.deps.container = container
        
        container = await save_to_state(ctx, "tasks.json", {"tasks": [t.model_dump() for t in tasks]})
        ctx.deps.container = container
        
        # Backup old plan.md
        container = container.with_exec(["mv", ".codebuff-state/plan.md", ".codebuff-state/plan.md.old"])
        ctx.deps.container = container
        
        logging.info("Migration completed successfully")
        return True, "Successfully migrated old plan.md to spec-kit format. Old file backed up as plan.md.old"
    except Exception as e:
        logging.error(f"Failed to save migrated state: {e}")
        return False, f"Migration failed during save: {e}"

async def convert_plan_to_constitution(
    ctx: RunContext[OrchestratorDependencies],
    plan_content: str,
    task_description: str
) -> Constitution:
    """Convert old plan.md to Constitution using LLM."""
    from pydantic_ai import Agent
    
    agent = Agent[
        OrchestratorDependencies,
        Constitution
    ](
        model=ctx.deps.llm_model,
        deps_type=OrchestratorDependencies,
        output_type=Constitution,
        retries=2
    )
    
    prompt = f"""
    Convert this old implementation plan to a Constitution:
    
    **Original Task**: {task_description}
    
    **Old Plan**:
    {plan_content}
    
    Extract or infer:
    1. **Values** (2-4): What matters most based on the plan's approach?
    2. **Constraints** (1-3): What limitations or requirements are implied?
    3. **Quality Gates** (2-4): How would we know this plan succeeded?
    
    Be specific to THIS plan, not generic.
    """
    
    result = await agent.run(prompt, deps=ctx.deps)
    return result.output

async def convert_plan_to_spec(
    ctx: RunContext[OrchestratorDependencies],
    plan_content: str,
    task_description: str,
    constitution: Constitution
) -> Spec:
    """Convert old plan.md to Spec using LLM."""
    from pydantic_ai import Agent
    
    agent = Agent[
        OrchestratorDependencies,
        Spec
    ](
        model=ctx.deps.llm_model,
        deps_type=OrchestratorDependencies,
        output_type=Spec,
        retries=2
    )
    
    prompt = f"""
    Convert this old implementation plan to a Spec:
    
    **Original Task**: {task_description}
    
    **Old Plan**:
    {plan_content}
    
    **Constitution**:
    Values: {constitution.values}
    Constraints: {constitution.constraints}
    
    Generate:
    1. **Objective**: Clear 1-2 sentence goal
    2. **Requirements**: Extract distinct requirements from plan steps
       - Give each an ID (REQ-001, REQ-002, etc.)
       - Add acceptance criteria (2-4 per requirement)
       - Set priority (must/should/could)
    3. **Success Criteria**: How we know it's complete
    4. **Out of Scope**: What's NOT included
    """
    
    result = await agent.run(prompt, deps=ctx.deps)
    return result.output

async def convert_plan_to_tasks(
    ctx: RunContext[OrchestratorDependencies],
    plan_content: str,
    spec: Spec
) -> list[Task]:
    """Convert old plan.md to Task list using LLM."""
    from pydantic_ai import Agent
    
    agent = Agent[
        OrchestratorDependencies,
        list[Task]
    ](
        model=ctx.deps.llm_model,
        deps_type=OrchestratorDependencies,
        output_type=list[Task],
        retries=2
    )
    
    prompt = f"""
    Convert this old implementation plan to atomic Tasks:
    
    **Old Plan**:
    {plan_content}
    
    **Spec Requirements**:
    {chr(10).join(f'{r.id}: {r.description}' for r in spec.requirements)}
    
    Break plan into:
    - Task ID (TASK-001, TASK-002, etc.)
    - Description (one sentence)
    - Acceptance criteria (2-4 testable conditions)
    - Dependencies (if any)
    - Complexity (simple/moderate/complex)
    - Test requirements
    - Files to modify (estimate based on plan)
    
    Ensure NO circular dependencies.
    """
    
    result = await agent.run(prompt, deps=ctx.deps)
    return result.output
```

### 5.2 Update `resume_workflow`
**File:** `agents/codebuff/src/codebuff/main.py`

Modify to check for and migrate old state:
```python
async def resume_workflow(...) -> str:
    # ... existing setup ...
    
    # Check for old state and migrate
    migrated = await migrate_old_state(ctx)
    if migrated:
        log_message = "Migrated old plan.md to spec-kit format"
    
    # Load spec-kit state
    constitution = await load_from_state(ctx, "constitution.json", Constitution)
    spec = await load_from_state(ctx, "spec.json", Spec)
    tasks_data = await load_from_state(ctx, "tasks.json")
    
    # Resume from last incomplete task
    # ...
```

## Phase 5.3: Error Handling Hierarchy
**File:** `agents/codebuff/src/codebuff/orchestrator/models.py`

Add custom exceptions:
```python
class OrchestrationError(Exception):
    """Base exception for orchestration errors."""
    pass

class ValidationError(OrchestrationError):
    """Raised when validation fails."""
    
    def __init__(self, message: str, issues: list[str]):
        super().__init__(message)
        self.issues = issues

class StateError(OrchestrationError):
    """Raised when state operations fail."""
    pass

class LLMGenerationError(OrchestrationError):
    """Raised when LLM generation fails after retries."""
    pass

class TaskExecutionError(OrchestrationError):
    """Raised when task execution fails."""
    
    def __init__(self, message: str, task_id: str):
        super().__init__(message)
        self.task_id = task_id

class MigrationError(OrchestrationError):
    """Raised when state migration fails."""
    pass
```

## Phase 6: Update Configuration

### 6.1 Remove Legacy Config
**File:** `shared/dagger-agents-config/src/ais_dagger_agents_config/models.py`

**Remove** from `OrchestratorConfig`:
- Any references to old planning system

**Add** to `OrchestratorConfig`:
```python
class SpecKitConfig(BaseModel):
    """Configuration for spec-kit methodology."""
    enforce_validation: bool = True  # Fail if validation fails
    allow_spec_refinement: bool = True  # Allow user to refine spec
    max_tasks_per_spec: int = 20  # Maximum tasks in a plan
    require_test_coverage: bool = True  # Require tests for each task

class OrchestratorConfig(BaseModel):
    # ... existing fields ...
    speckit: SpecKitConfig = Field(default_factory=SpecKitConfig)
```

## Phase 7: Update Tools

### 7.1 Remove `create_plan` Tool
**File:** `agents/codebuff/src/codebuff/orchestrator/tools/planning.py`

**Remove** the `create_plan` function entirely. It's replaced by the spec-kit workflow.

### 7.2 Add Spec-Kit Tools
**File:** `agents/codebuff/src/codebuff/orchestrator/tools/speckit.py` (new file)

```python
from pydantic_ai import RunContext
from ..models import OrchestratorDependencies, Constitution, Spec, Task

@orchestrator.tool
async def refine_constitution(
    ctx: RunContext[OrchestratorDependencies],
    feedback: str
) -> Constitution:
    """Refine constitution based on user feedback."""
    # Load current constitution
    # Apply refinements
    # Re-validate
    # Save updated version
    pass

@orchestrator.tool
async def refine_spec(
    ctx: RunContext[OrchestratorDependencies],
    feedback: str
) -> Spec:
    """Refine spec based on user feedback."""
    # Load current spec
    # Apply refinements
    # Re-validate against constitution
    # Save updated version
    pass

@orchestrator.tool
async def add_task(
    ctx: RunContext[OrchestratorDependencies],
    task: Task
) -> None:
    """Add a new task to the plan."""
    # Load current tasks
    # Validate new task
    # Check dependencies
    # Add to task list
    # Save updated tasks
    pass
```

## Phase 8: Update Tests

### 8.1 Remove Old Plan Tests
**File:** `agents/codebuff/tests/test_plan_models.py`

**Remove** all tests related to `Plan` and `PlanStep`.

### 8.2 Add Spec-Kit Tests
**File:** `agents/codebuff/tests/test_speckit_models.py` (new file)

```python
import pytest
from codebuff.orchestrator.models import Constitution, Spec, Requirement, Task

def test_constitution_validation():
    """Constitution must have minimum required fields."""
    const = Constitution(
        values=["Maintainability", "Performance"],
        constraints=["No breaking changes"],
        quality_gates=["All tests pass"]
    )
    assert len(const.values) >= 2

def test_requirement_has_acceptance_criteria():
    """Every requirement must have acceptance criteria."""
    req = Requirement(
        id="REQ-001",
        description="User can log in",
        acceptance_criteria=["Login form validates email", "Password is hashed"],
        priority="must"
    )
    assert len(req.acceptance_criteria) > 0

def test_task_dependencies():
    """Tasks can have dependencies."""
    # Test dependency graph validation
    # Test no circular dependencies
    pass
```

### 8.3 Add Integration Tests
**File:** `agents/codebuff/tests/test_speckit_workflow.py` (new file)

```python
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from codebuff.orchestrator.agent import (
    create_constitution,
    create_spec,
    create_task_plan,
    validate_constitution,
    validate_spec,
    validate_tasks,
    execute_task_with_review,
    migrate_old_state
)
from codebuff.orchestrator.models import (
    Constitution,
    Spec,
    Requirement,
    Task,
    OrchestratorDependencies
)

@pytest.fixture
def mock_deps(mock_dagger_container):
    """Create mock orchestrator dependencies."""
    deps = OrchestratorDependencies(
        container=mock_dagger_container,
        config={
            'orchestrator': {
                'speckit': {
                    'max_tasks_per_spec': 20,
                    'enforce_validation': True
                }
            }
        },
        llm_model='openai:gpt-4o-mini',
        # Mock agents
        file_explorer_agent=AsyncMock(),
        file_picker_agent=AsyncMock(),
        implementation_agent=AsyncMock(),
        reviewer_agent=AsyncMock()
    )
    return deps

@pytest.mark.integration
async def test_full_speckit_workflow(mock_deps):
    """Test complete spec-kit workflow."""
    task_desc = "Add user authentication"
    
    # Mock LLM responses for each phase
    mock_deps.file_explorer_agent.run = AsyncMock(
        return_value=MagicMock(output="Codebase uses Flask, has auth module")
    )
    
    # Mock constitution generation
    constitution = Constitution(
        values=["Security", "Simplicity"],
        constraints=["No third-party auth services"],
        quality_gates=["All tests pass", "Security audit passes"]
    )
    
    # Validate constitution
    assert await validate_constitution(constitution)
    
    # Mock spec generation
    spec = Spec(
        objective="Implement user authentication system",
        requirements=[
            Requirement(
                id="REQ-001",
                description="Users can register with email/password",
                acceptance_criteria=[
                    "Email validation works",
                    "Password hashed with bcrypt"
                ],
                priority="must"
            )
        ],
        success_criteria=["Users can log in", "Tests pass"],
        out_of_scope=["OAuth", "2FA"]
    )
    
    # Validate spec
    valid, issues = await validate_spec(spec, constitution)
    assert valid, f"Spec validation failed: {issues}"
    
    # Mock task generation
    tasks = [
        Task(
            id="TASK-001",
            description="Create User model",
            acceptance_criteria=["Model has email and password fields"],
            dependencies=[],
            estimated_complexity="simple",
            test_requirements=["tests/test_user.py"],
            files_to_modify=["models/user.py"]
        )
    ]
    
    # Validate tasks
    valid, issues = await validate_tasks(tasks, spec)
    assert valid, f"Task validation failed: {issues}"
    
    # Verify state would be saved (check container operations)
    assert mock_deps.container is not None

@pytest.mark.integration
async def test_spec_validation_catches_issues():
    """Spec validation should catch incomplete specs."""
    constitution = Constitution(
        values=["Quality"],
        constraints=["No breaking changes"],
        quality_gates=["Tests pass"]
    )
    
    # Spec with missing acceptance criteria
    incomplete_spec = Spec(
        objective="Build feature",
        requirements=[
            Requirement(
                id="REQ-001",
                description="Something",
                acceptance_criteria=[],  # Empty!
                priority="must"
            )
        ],
        success_criteria=["Done"],
        out_of_scope=[]
    )
    
    valid, issues = await validate_spec(incomplete_spec, constitution)
    assert not valid
    assert any("acceptance criteria" in issue.lower() for issue in issues)

@pytest.mark.integration
async def test_task_circular_dependency_detection():
    """Tasks with circular dependencies should fail validation."""
    spec = Spec(
        objective="Test",
        requirements=[Requirement(id="REQ-001", description="Test", acceptance_criteria=["Done"], priority="must")],
        success_criteria=["Done"],
        out_of_scope=[]
    )
    
    # Create circular dependency: A -> B -> C -> A
    tasks = [
        Task(
            id="TASK-A",
            description="Task A",
            acceptance_criteria=["Done"],
            dependencies=[{"task_id": "TASK-C", "dependency_type": "blocks"}],
            estimated_complexity="simple",
            test_requirements=[],
            files_to_modify=[]
        ),
        Task(
            id="TASK-B",
            description="Task B",
            acceptance_criteria=["Done"],
            dependencies=[{"task_id": "TASK-A", "dependency_type": "blocks"}],
            estimated_complexity="simple",
            test_requirements=[],
            files_to_modify=[]
        ),
        Task(
            id="TASK-C",
            description="Task C",
            acceptance_criteria=["Done"],
            dependencies=[{"task_id": "TASK-B", "dependency_type": "blocks"}],
            estimated_complexity="simple",
            test_requirements=[],
            files_to_modify=[]
        )
    ]
    
    valid, issues = await validate_tasks(tasks, spec)
    assert not valid
    assert any("circular" in issue.lower() for issue in issues)

@pytest.mark.integration
async def test_migration_from_old_plan(mock_deps):
    """Test migration from old plan.md format."""
    old_plan_content = """
# Implementation Plan

1. Create user model with email and password fields
2. Add password hashing with bcrypt
3. Create login endpoint
4. Write tests
    """
    
    # Mock container with old plan.md
    mock_deps.container.file = MagicMock(
        return_value=MagicMock(
            contents=AsyncMock(return_value=old_plan_content)
        )
    )
    
    task_desc = "Add user authentication"
    
    # Mock LLM conversion responses
    # ... setup mocks for convert_plan_to_* functions ...
    
    success, message = await migrate_old_state(mock_deps, task_desc)
    
    assert success
    assert "migrated" in message.lower()
    # Verify new state files were created
    # ...

@pytest.mark.integration
async def test_review_loop_with_iterations(mock_deps):
    """Test implementation-review loop with multiple iterations."""
    constitution = Constitution(
        values=["Code quality"],
        constraints=["No global variables"],
        quality_gates=["Linter passes"]
    )
    
    spec = Spec(
        objective="Test",
        requirements=[Requirement(id="REQ-001", description="Test", acceptance_criteria=["Works"], priority="must")],
        success_criteria=["Done"],
        out_of_scope=[]
    )
    
    task = Task(
        id="TASK-001",
        description="Write function",
        acceptance_criteria=["Function exists", "Function tested"],
        dependencies=[],
        estimated_complexity="simple",
        test_requirements=["tests/test_func.py"],
        files_to_modify=["src/func.py"]
    )
    
    # Mock implementation agent
    mock_deps.implementation_agent.run = AsyncMock(
        return_value=MagicMock(output="Implemented")
    )
    
    # Mock reviewer: reject first, approve second
    review_responses = [
        MagicMock(output="NEEDS_CHANGES: Missing docstring"),
        MagicMock(output="APPROVED")
    ]
    mock_deps.reviewer_agent.run = AsyncMock(
        side_effect=review_responses
    )
    
    # Execute task with review loop
    await execute_task_with_review(mock_deps, task, constitution, spec)
    
    # Verify implementation ran twice (once + one retry)
    assert mock_deps.implementation_agent.run.call_count == 2
    # Verify reviewer ran twice
    assert mock_deps.reviewer_agent.run.call_count == 2
```

## Phase 9: Documentation

### 9.1 Update Knowledge Files
**File:** `agents/codebuff/knowledge.md`

Add section:
```markdown
## Spec-Kit Methodology

Codebuff uses the spec-kit methodology for feature development:

1. **Constitution**: Define core values, constraints, and quality gates
2. **Spec**: Detailed requirements with acceptance criteria
3. **Plan**: Break spec into atomic, testable tasks
4. **Execute**: Implement tasks, validate against constitution

### State Files

- `.codebuff-state/constitution.json` - Project values and constraints
- `.codebuff-state/spec.json` - Detailed specification
- `.codebuff-state/tasks.json` - Task breakdown
- `.codebuff-state/task_log.jsonl` - Execution log

### Migration

Old `plan.md` files are automatically migrated to spec-kit format on first resume.
```

### 9.2 Update README
**File:** `agents/codebuff/README.md`

Update workflow description to reflect spec-kit methodology.

## Phase 10: Cleanup

### 10.1 Remove Dead Code
- Remove all references to old `Plan` model
- Remove `create_plan` tool
- Remove `create_implementation_plan` function
- Clean up imports

### 10.2 Update Type Hints
- Update all function signatures that referenced `Plan`
- Update return types to use new models

## Implementation Order

### Recommended Sequence (Minimize Breaking Changes)

1. **Phase 0**: Update OrchestratorDependencies for lazy-loaded agents (non-breaking)
2. **Phase 1**: Add spec-kit models to `models.py` alongside existing models (non-breaking)
3. **Phase 2**: Implement spec-kit workflow functions in new file `orchestrator/speckit_workflow.py` (isolated, non-breaking)
4. **Phase 4**: Add state persistence helpers (non-breaking utilities)
5. **Phase 5**: Add migration functions (safe, doesn't break existing code)
6. **Phase 10**: Add error handling classes (non-breaking)
7. **Phase 6**: Update configuration with SpecKitConfig (non-breaking addition)
8. **Phase 7**: Add spec-kit tools to new file (non-breaking)
9. **Phase 8**: Add comprehensive tests for all new code (verify before breaking changes)
10. **Phase 3**: **BREAKING** - Replace `orchestrate_feature_development` with spec-kit workflow
11. **Phase 11**: **BREAKING** - Remove old Plan models, create_plan tool, and related code
12. **Phase 9**: Update documentation to reflect changes

### Key Checkpoints

**After Phase 8 (Before Breaking Changes)**:
- [ ] All new models tested
- [ ] All workflow functions tested
- [ ] Migration tested on sample old states
- [ ] Validation functions verified
- [ ] Review loop tested
- [ ] Run full test suite: `make test-codebuff`

**After Phase 11 (After Breaking Changes)**:
- [ ] All references to old Plan removed
- [ ] No import errors
- [ ] Test suite still passes
- [ ] Manual test of full workflow

### Parallel Development Strategy

**Can work in parallel:**
- Phases 0-8 (all setup, no conflicts)
- Documentation updates (Phase 9)

**Must be sequential:**
- Phase 10 (breaking changes) requires Phases 0-9 complete
- Phase 11 (cleanup) requires Phase 10 complete

## Success Criteria

### Functional Requirements
- [ ] Constitution generation produces valid output with 2+ values, 1+ constraints, 1+ quality gates
- [ ] Spec generation produces requirements with IDs, descriptions, acceptance criteria, priorities
- [ ] Task generation produces valid dependency DAG (no cycles)
- [ ] All spec requirements covered by at least one task
- [ ] Task execution follows topological order
- [ ] Review loop: implementation → reviewer → approval/iteration (max 3 iterations)
- [ ] Review loop terminates on approval or max iterations
- [ ] Old plan.md migrates successfully to constitution.json + spec.json + tasks.json
- [ ] Resume workflow detects current phase from state files
- [ ] Resume workflow resumes from last incomplete task

### Error Handling
- [ ] Invalid JSON in state files handled gracefully
- [ ] Missing required state files raise clear errors
- [ ] LLM generation failures trigger retry with better prompts
- [ ] Circular task dependencies detected and rejected
- [ ] Validation failures include actionable error messages
- [ ] State corruption triggers recovery from backups (if available)

### User Experience
- [ ] Progress logged at each phase transition
- [ ] Task execution logged to task_log.jsonl
- [ ] Migration status clearly communicated to user
- [ ] Validation errors formatted for readability
- [ ] PR description includes constitution, spec, tasks summary

### Testing
- [ ] All new models tested (unit tests)
- [ ] All validation functions tested (unit tests)
- [ ] Full workflow tested end-to-end (integration test)
- [ ] Migration tested with various old plan.md formats
- [ ] Review loop tested with multiple iterations
- [ ] Error recovery tested
- [ ] Circular dependency detection tested
- [ ] All tests pass with >80% coverage of new code

### Code Quality
- [ ] Zero references to old `Plan` or `PlanStep` models
- [ ] No unused imports
- [ ] Type hints correct throughout
- [ ] Follows existing code patterns (PydanticAI, Dagger)
- [ ] Docstrings on all public functions
- [ ] Error messages include context and suggested fixes

## Rollout Strategy

1. **Development**: Implement on feature branch
2. **Testing**: Test migration on sample repos
3. **Alpha**: Release to small group with migration notice
4. **Beta**: Wider release with monitoring
5. **GA**: Full release with migration guide

## Additional Implementation Details

### User Feedback Integration Points

The plan supports optional user review at each major phase:

1. **After Constitution**: User can review and refine values/constraints
2. **After Spec**: User can review and refine requirements
3. **After Task Plan**: User can review and modify task breakdown

Configuration in `orchestrator.feedback`:
```yaml
orchestrator:
  feedback:
    enabled: true
    phase: "spec"  # constitution | spec | planning | none
```

When feedback is enabled:
- Workflow stops at configured phase
- Creates draft PR with current state
- User can:
  - Approve: `@orchestrator approve`
  - Modify: `@orchestrator modify <changes>`
  - Add files: `@orchestrator add_files <paths>`
- `continue_workflow` resumes after approval

### Tools for Spec-Kit Refinement

Add to `orchestrator/tools/speckit.py`:

```python
@orchestrator.tool
async def view_constitution(ctx: RunContext[OrchestratorDependencies]) -> str:
    """View the current constitution."""
    const = await load_from_state(ctx, "constitution.json", Constitution)
    if const:
        return const.model_dump_json(indent=2)
    return "No constitution found"

@orchestrator.tool
async def view_spec(ctx: RunContext[OrchestratorDependencies]) -> str:
    """View the current spec."""
    spec = await load_from_state(ctx, "spec.json", Spec)
    if spec:
        return spec.model_dump_json(indent=2)
    return "No spec found"

@orchestrator.tool
async def view_tasks(ctx: RunContext[OrchestratorDependencies]) -> str:
    """View the current task plan."""
    tasks_data = await load_from_state(ctx, "tasks.json")
    if tasks_data:
        return json.dumps(tasks_data, indent=2)
    return "No tasks found"
```

### Performance Considerations

**LLM Calls Per Workflow:**
- Exploration: 1 call (file-explorer agent)
- Constitution: 1-2 calls (generation + optional retry)
- Spec: 1-2 calls
- Task Plan: 2-3 calls (file-picker + generation + validation)
- Per-task: 2-6 calls (implementation + review iterations)

**Estimated Time:**
- Constitution + Spec + Tasks: 30-60 seconds
- Per task execution: 15-90 seconds depending on complexity
- Total for 5-task feature: 2-8 minutes

**Cost Optimization:**
- Use cheaper models (gpt-4o-mini) for constitution/spec generation
- Use more capable model (gpt-4o) for task execution
- Configure in YAML:
  ```yaml
  orchestrator:
    llm_model: "openai:gpt-4o"
    speckit:
      planning_model: "openai:gpt-4o-mini"
  ```

**Progress Indicators:**
- Log to console at each phase transition
- Update progress.json for external monitoring
- Append to task_log.jsonl for audit trail

### Rollback Strategy

If spec-kit workflow fails mid-execution:

1. **State preserved**: All .codebuff-state/*.json files remain
2. **Manual resume**: User can inspect state and resume
3. **Rollback to old workflow**: Not supported - migration is one-way
4. **Recovery**: User can:
   - Edit state files manually
   - Delete .codebuff-state/ and restart from scratch
   - Use migration feedback to improve prompts

### Notes

- **No backward compatibility flag** - clean replacement, simpler codebase
- **Migration happens automatically** on first resume with old state
- **Old state files preserved** as `.old` backup for auditing
- **Clear errors on migration failure** with logs of what went wrong
- **Documentation emphasizes benefits**: Better structure, clearer validation, easier resume
- **Spec-kit is a methodology**, not a package - we implement its patterns, not import code
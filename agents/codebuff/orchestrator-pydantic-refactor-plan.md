Title: Refactor Orchestrator Agent Using PydanticAI Native Patterns

Objective
- Refactor agents/codebuff orchestrator to follow PydanticAI's native patterns
- Use Agent class with proper dependencies, tools, and instructions
- Leverage PydanticAI's built-in features: toolsets, retries, streaming, multi-agent coordination

1) PydanticAI Agent Structure (Native Pattern)
- **Agent Definition**:
```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

orchestrator_agent = Agent(
    model='openai:gpt-4o',
    deps_type=OrchestratorDependencies,
    instructions="""
    You are an Orchestrator Agent that coordinates feature development workflows.
    
    Your role:
    - Break down tasks into manageable phases
    - Coordinate specialized agents for exploration, planning, implementation
    - Maintain state and ensure proper progression
    - Validate tests pass before creating PRs
    
    Available tools let you:
    - Initialize tasks and analyze requirements
    - Explore codebases and select relevant files  
    - Create implementation plans and execute changes
    - Review code and create pull requests
    
    Always persist state after each phase and ensure tests pass before committing.
    """,
    retries=2
)
```

2) Dependencies (PydanticAI Pattern)
- **Structured Dependencies** using `deps_type`:
```python
from dataclasses import dataclass
from typing import Optional
import dagger
from ais_dagger_agents_config import YAMLConfig

@dataclass
class OrchestratorDependencies:
    # Core resources
    config: YAMLConfig
    container: dagger.Container
    config_file: dagger.File
    model: Any  # LLM model for sub-agents
    
    # Sub-agent instances (lazy-loaded)
    file_explorer: Optional[Any] = None
    file_picker: Optional[Any] = None
    researcher: Optional[Any] = None
    thinker: Optional[Any] = None
    reviewer: Optional[Any] = None
    implementation: Optional[Any] = None
    context_pruner: Optional[Any] = None
    
    # Workflow state
    state: Optional[OrchestrationState] = None
    test_command: Optional[str] = None
    current_task: Optional[TaskSpec] = None
    selected_files: list[str] = field(default_factory=list)
    exploration_results: Optional[str] = None
    
    # State management helpers
    def update_container(self, new_container: dagger.Container):
        self.container = new_container
    
    def get_sub_agent(self, agent_type: str) -> Any:
        """Get or create sub-agent instance."""
        if agent_type == "file_explorer" and self.file_explorer is None:
            self.file_explorer = create_file_explorer_agent(self.model, self)
        elif agent_type == "file_picker" and self.file_picker is None:
            self.file_picker = create_file_picker_agent(self.model, self)
        elif agent_type == "researcher" and self.researcher is None:
            self.researcher = create_researcher_agent(self.model)
        elif agent_type == "thinker" and self.thinker is None:
            self.thinker = create_thinker_agent(self.model)
        elif agent_type == "reviewer" and self.reviewer is None:
            self.reviewer = create_reviewer_agent(self.model)
        elif agent_type == "implementation" and self.implementation is None:
            self.implementation = create_implementation_agent(self.model, self)
        elif agent_type == "context_pruner" and self.context_pruner is None:
            self.context_pruner = create_context_pruner_agent()
        
        return getattr(self, agent_type)
```

3) Tool Registration (Complete Set - PydanticAI @tool Pattern)
- **All Available Tools**:
```python
# Planning and Documentation Tools
@orchestrator_agent.tool
async def create_plan(
    ctx: RunContext[OrchestratorDependencies],
    path: str,
    plan: str
) -> str:
    """Generate detailed markdown plans for complex tasks."""
    # Implementation

@orchestrator_agent.tool
async def add_subgoal(
    ctx: RunContext[OrchestratorDependencies],
    id: str,
    objective: str,
    status: str
) -> str:
    """Track progress on complex multi-step tasks."""
    # Implementation

@orchestrator_agent.tool
async def update_subgoal(
    ctx: RunContext[OrchestratorDependencies],
    id: str,
    status: str = None,
    log: str = None
) -> str:
    """Update subgoal status and log progress."""
    # Implementation

# File Operations Tools  
@orchestrator_agent.tool
async def read_files(
    ctx: RunContext[OrchestratorDependencies],
    paths: list[str]
) -> str:
    """Read multiple files from the codebase."""
    # Implementation

@orchestrator_agent.tool
async def write_file(
    ctx: RunContext[OrchestratorDependencies],
    path: str,
    instructions: str,
    content: str
) -> str:
    """Create or edit files using edit snippets."""
    # Implementation with state persistence

@orchestrator_agent.tool
async def str_replace(
    ctx: RunContext[OrchestratorDependencies],
    path: str,
    replacements: list[dict]
) -> str:
    """Make precise string replacements in existing files."""
    # Implementation

@orchestrator_agent.tool
async def code_search(
    ctx: RunContext[OrchestratorDependencies],
    pattern: str,
    flags: str = None,
    cwd: str = None,
    max_results: int = 30
) -> str:
    """Search for patterns across the codebase using ripgrep."""
    # Implementation

# Execution and Testing Tools
@orchestrator_agent.tool
async def run_terminal_command(
    ctx: RunContext[OrchestratorDependencies],
    command: str,
    process_type: str = "SYNC",
    cwd: str = None,
    timeout_seconds: int = 30
) -> str:
    """Execute CLI commands (SYNC or BACKGROUND)."""
    # Implementation with test gating

@orchestrator_agent.tool
async def browser_logs(
    ctx: RunContext[OrchestratorDependencies],
    type: str,
    url: str,
    wait_until: str = "load"
) -> str:
    """Navigate to URLs and capture console logs/errors for web apps."""
    # Implementation

# Agent Coordination Tools
@orchestrator_agent.tool
async def spawn_agents(
    ctx: RunContext[OrchestratorDependencies],
    agents: list[dict]
) -> str:
    """Spawn multiple agents in parallel for complex tasks."""
    # Implementation using PydanticAI agent-as-tool pattern

@orchestrator_agent.tool
async def spawn_agent_inline(
    ctx: RunContext[OrchestratorDependencies],
    agent_type: str,
    prompt: str = None,
    params: dict = None
) -> str:
    """Spawn a single agent within current message history."""
    # Implementation

@orchestrator_agent.tool
async def lookup_agent_info(
    ctx: RunContext[OrchestratorDependencies],
    agent_type: str = None
) -> str:
    """Get information about available agent types."""
    # Return info about all available sub-agents

# Sub-Agent Coordination Tools (Specific Agents)
@orchestrator_agent.tool
async def run_file_explorer(
    ctx: RunContext[OrchestratorDependencies],
    focus_area: str,
    with_tokens: bool = True
) -> str:
    """Run file explorer agent to analyze codebase structure."""
    # Delegate to codebuff/file-explorer@0.0.2

@orchestrator_agent.tool
async def run_file_picker(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    max_files: int = 10
) -> str:
    """Run file picker agent to find relevant files for task."""
    # Delegate to codebuff/file-picker@0.0.2

@orchestrator_agent.tool
async def run_researcher(
    ctx: RunContext[OrchestratorDependencies],
    research_query: str
) -> str:
    """Run researcher agent for web search and documentation."""
    # Delegate to codebuff/researcher@0.0.2

@orchestrator_agent.tool
async def run_thinker(
    ctx: RunContext[OrchestratorDependencies],
    problem_description: str
) -> str:
    """Run thinker agent for deep problem analysis."""
    # Delegate to codebuff/thinker@0.0.2

@orchestrator_agent.tool
async def run_reviewer(
    ctx: RunContext[OrchestratorDependencies],
    review_focus: str
) -> str:
    """Run reviewer agent to validate code changes."""
    # Delegate to codebuff/reviewer@0.0.2

@orchestrator_agent.tool
async def run_implementation(
    ctx: RunContext[OrchestratorDependencies],
    task_spec: dict,
    selected_files: list[str]
) -> str:
    """Run implementation agent to execute code changes."""
    # Create and coordinate implementation agent

@orchestrator_agent.tool
async def run_context_pruner(
    ctx: RunContext[OrchestratorDependencies],
    max_context_length: int = 50000
) -> str:
    """Run context pruner to manage conversation length."""
    # Delegate to codebuff/context-pruner@0.0.2

# Analysis Tools
@orchestrator_agent.tool
async def think_deeply(
    ctx: RunContext[OrchestratorDependencies],
    thought: str
) -> str:
    """Perform detailed step-by-step analysis for complex problems."""
    # Implementation

# Session Management
@orchestrator_agent.tool
async def end_turn(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    """Signal completion and hand control back to user."""
    # Implementation - should trigger workflow completion
```

4) Toolset Organization (PydanticAI Toolset Pattern)
- **Group Related Tools**:
```python
from pydantic_ai import Toolset

# Planning and Documentation Toolset
planning_toolset = Toolset()
planning_toolset.tool(create_plan)
planning_toolset.tool(add_subgoal)
planning_toolset.tool(update_subgoal)
planning_toolset.tool(think_deeply)

# File Operations Toolset
file_ops_toolset = Toolset()
file_ops_toolset.tool(read_files)
file_ops_toolset.tool(write_file)
file_ops_toolset.tool(str_replace)
file_ops_toolset.tool(code_search)

# Execution Toolset
execution_toolset = Toolset()
execution_toolset.tool(run_terminal_command)
execution_toolset.tool(browser_logs)

# Agent Coordination Toolset
agent_coordination_toolset = Toolset()
agent_coordination_toolset.tool(spawn_agents)
agent_coordination_toolset.tool(spawn_agent_inline)
agent_coordination_toolset.tool(lookup_agent_info)

# Sub-Agent Coordination Toolset
sub_agent_toolset = Toolset()
sub_agent_toolset.tool(run_file_explorer)
sub_agent_toolset.tool(run_file_picker)
sub_agent_toolset.tool(run_researcher)
sub_agent_toolset.tool(run_thinker)
sub_agent_toolset.tool(run_reviewer)
sub_agent_toolset.tool(run_implementation)
sub_agent_toolset.tool(run_context_pruner)

# Session Management Toolset
session_toolset = Toolset()
session_toolset.tool(end_turn)

# Register all toolsets with agent
orchestrator_agent = Agent(
    model='openai:gpt-4o',
    deps_type=OrchestratorDependencies,
    instructions=ORCHESTRATOR_INSTRUCTIONS,
    toolsets=[
        planning_toolset,
        file_ops_toolset, 
        execution_toolset,
        agent_coordination_toolset,
        sub_agent_toolset,
        session_toolset
    ],
    retries=2
)
```

5) Multi-Agent Coordination (Complete Sub-Agent Integration)
- **All Available Sub-Agents**:
```python
# Available Sub-Agents for Orchestration:
# - codebuff/file-explorer@0.0.2: Comprehensive codebase exploration
# - codebuff/file-picker@0.0.2: Find relevant files for specific tasks  
# - codebuff/researcher@0.0.2: Web search and documentation research
# - codebuff/thinker@0.0.2: Deep thinking on specific problems
# - codebuff/reviewer@0.0.2: Code review and feedback
# - codebuff/context-pruner@0.0.2: Context management for long conversations
# - Implementation Agent: Code implementation with test validation

@orchestrator_agent.tool
async def run_file_explorer(
    ctx: RunContext[OrchestratorDependencies],
    focus_area: str,
    with_tokens: bool = True
) -> str:
    """Run file explorer agent to analyze codebase structure."""
    agent = ctx.deps.get_sub_agent("file_explorer")
    
    explorer_deps = FileExplorerDependencies(
        container=ctx.deps.container,
        config=ctx.deps.config,
        config_file=ctx.deps.config_file,
        focus_area=focus_area,
        with_tokens=with_tokens
    )
    
    result = await agent.run(
        f"Explore the codebase focusing on: {focus_area}",
        deps=explorer_deps
    )
    
    # Update container and save exploration results
    ctx.deps.update_container(explorer_deps.container)
    ctx.deps.exploration_results = result.output
    
    return result.output

@orchestrator_agent.tool
async def run_file_picker(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    max_files: int = 10
) -> str:
    """Run file picker agent to find relevant files for task."""
    agent = ctx.deps.get_sub_agent("file_picker")
    
    picker_deps = FilePickerDependencies(
        container=ctx.deps.container,
        config=ctx.deps.config,
        config_file=ctx.deps.config_file,
        query=task_description,
        top=max_files
    )
    
    result = await agent.run(
        f"Find files relevant to: {task_description}",
        deps=picker_deps
    )
    
    # Parse and store selected files
    try:
        files_data = json.loads(result.output)
        ctx.deps.selected_files = [f["path"] for f in files_data if "path" in f]
    except Exception:
        pass
    
    ctx.deps.update_container(picker_deps.container)
    return result.output

@orchestrator_agent.tool
async def run_implementation(
    ctx: RunContext[OrchestratorDependencies],
    task_spec: dict,
    selected_files: list[str]
) -> str:
    """Run implementation agent to execute code changes with test validation."""
    agent = ctx.deps.get_sub_agent("implementation")
    
    impl_deps = ImplementationDependencies(
        container=ctx.deps.container,
        config=ctx.deps.config,
        config_file=ctx.deps.config_file,
        task_spec=TaskSpec(**task_spec),
        selected_files=selected_files,
        test_command=ctx.deps.test_command
    )
    
    result = await agent.run(
        "Implement the planned changes with test validation",
        deps=impl_deps
    )
    
    # Update container with implementation results
    ctx.deps.update_container(impl_deps.container)
    
    return result.output
```

6) State Management (Container + JSON Pattern)
- **Persist State in Container**:
```python
from ..utils.container_state import write_json, append_log

@orchestrator_agent.tool
async def start_task(
    ctx: RunContext[OrchestratorDependencies],
    task_description: str,
    focus_area: str
) -> str:
    # Create task state
    task_spec = TaskSpec(
        id=str(uuid.uuid4()),
        goal=task_description,
        focus_area=focus_area
    )
    
    # Update orchestration state
    ctx.deps.state = OrchestrationState(
        task_id=task_spec.id,
        current_phase=Phase.EXPLORATION,
        status=Status.IN_PROGRESS,
        start_time=datetime.now(UTC),
        last_update=datetime.now(UTC),
        task_spec=task_spec
    )
    
    # Persist to container
    ctx.deps.container = await write_json(
        ctx.deps.container, 
        "task.json", 
        task_spec.model_dump()
    )
    ctx.deps.container = await append_log(
        ctx.deps.container,
        f"start_task: {task_spec.id} {task_description}"
    )
    
    return f"Task {task_spec.id} initialized: {task_description}"
```

7) Error Handling and Retries (PydanticAI Built-in)
- **Use Agent's Built-in Retry Mechanism**:
```python
orchestrator_agent = Agent(
    model='openai:gpt-4o',
    deps_type=OrchestratorDependencies,
    instructions=INSTRUCTIONS,
    retries=3  # Built-in retry for failed tool calls
)
```

- **Tool-level Error Handling**:
```python
@orchestrator_agent.tool
async def implement_plan(
    ctx: RunContext[OrchestratorDependencies]
) -> str:
    try:
        # Implementation logic
        result = await execute_implementation(ctx)
        
        # Test execution with proper error handling
        test_result = await run_tests(ctx)
        if not test_result.success:
            return f"Implementation failed: tests did not pass - {test_result.output}"
        
        return f"Implementation successful: {len(result.changes)} files modified"
        
    except Exception as e:
        # Log error and return structured response
        await append_log(ctx.deps.container, f"implement_plan ERROR: {str(e)}")
        return f"Implementation failed: {str(e)}"
```

8) Agent Factory (PydanticAI Pattern)
- **Factory for Agent Creation**:
```python
def create_orchestrator_agent(model: str | OpenAIModel) -> Agent:
    """Factory function to create orchestrator agent."""
    if isinstance(model, str):
        model = OpenAIModel(model)
    
    return Agent(
        model=model,
        deps_type=OrchestratorDependencies,
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        retries=2
    )
```

9) Streaming and Iteration (PydanticAI iter() Pattern)
- **For Real-time Workflow Updates**:
```python
async def run_orchestration_stream(
    agent: Agent,
    prompt: str,
    deps: OrchestratorDependencies
):
    """Stream orchestration progress in real-time."""
    async with agent.iter(prompt, deps=deps) as it:
        async for step in it:
            if step.is_tool_call:
                print(f"🔧 Running tool: {step.tool_name}")
            elif step.is_model_response:
                print(f"🤖 Agent: {step.content}")
            elif step.is_tool_result:
                print(f"✅ Tool result: {step.tool_result}")
        
        return it.final_result()
```

10) File Structure (PydanticAI Native)
```
agents/codebuff/src/codebuff/orchestrator/
├── __init__.py           # Export create_orchestrator_agent
├── agent.py             # Agent definition and factory
├── dependencies.py      # OrchestratorDependencies dataclass
├── tools/
│   ├── __init__.py
│   ├── planning.py     # create_plan, add_subgoal, update_subgoal, think_deeply
│   ├── file_ops.py     # read_files, write_file, str_replace, code_search
│   ├── execution.py    # run_terminal_command, browser_logs
│   ├── agents.py       # spawn_agents, spawn_agent_inline, lookup_agent_info
│   ├── sub_agents.py   # run_file_explorer, run_file_picker, run_researcher, etc.
│   └── session.py      # end_turn
├── toolsets.py         # Organized toolsets (planning, file_ops, execution, agents, etc.)
├── models.py           # Keep existing state models
└── instructions.py     # System instructions/prompts
```

11) Migration Strategy
1. Create new agent.py with PydanticAI Agent() instantiation
2. Convert existing tool functions to @agent.tool decorated functions
3. Update dependencies to use dataclass pattern with update_container helper
4. Organize tools into logical toolsets (exploration, implementation, review)
5. Add streaming support for real-time progress updates
6. Update main.py to use new agent factory
7. Test that all functionality works with new structure
8. Remove old agent implementation

12) Integration with Existing Code
- **Keep Current Container State Pattern**: Continue using write_json/append_log for .codebuff-state
- **Maintain Test Gating**: Keep test execution and commit gating in implement_plan tool
- **Preserve Multi-Agent Calls**: Use agent-as-tool pattern for file_explorer, file_picker, etc.
- **Keep Dagger Integration**: All tools continue to work with Dagger containers/files

13) Benefits of PydanticAI Approach
- **Built-in Retry Logic**: Automatic handling of failed tool calls
- **Type Safety**: Automatic schema generation from type hints
- **Streaming Support**: Real-time progress updates via iter()
- **Cleaner Tool Organization**: @tool decorator vs manual registration
- **Better Error Handling**: Structured exception management
- **Multi-Agent Coordination**: Native support for agent-as-tool patterns

14) Testing Updates
- Update tests to work with Agent() instances instead of manual tool calls
- Test toolsets individually
- Add tests for streaming functionality
- Verify error handling and retry mechanisms

15) Documentation
- Update orchestrator knowledge.md with PydanticAI patterns
- Document toolset organization and agent coordination
- Add examples of streaming orchestration
- Document dependencies injection pattern

from dataclasses import dataclass
from typing import Dict, List

import anyio
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path

import dagger
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext
try:
    from simple_chalk import blue, green, yellow, red, cyan, magenta
except ImportError:
    from simple_chalk import blue, green, yellow, red
    def cyan(x):
        return x
    def magenta(x):
        return x

from ..file_explorer.utils import find_files, _extract_keywords_from_prompt


class ExplorePrompts(BaseModel):
    """A model to hold a list of exploration prompts for the file picker agents."""
    prompts: List[str] = Field(
        ..., description="A list of 1 to 4 concise prompts for exploring different areas of the codebase in parallel.")


@dataclass
class FileExplorerDependencies:
    """Dependencies for the File Explorer agent."""
    container: dagger.Container


async def add_project_file_tree_to_context(
    ctx: RunContext[FileExplorerDependencies],
) -> str:
    """Helper to append project file tree to context string."""
    print(blue("🗺️ Appending project file tree to context"))

    try:
        # Add timeout protection
        with anyio.move_on_after(30):  # 30-second timeout for tree command
            tree = await ctx.deps.container.with_exec(
                ["tree", "-L", "3", "-a", "-I", ".git|node_modules|__pycache__|.venv|dist|build"]).stdout()
            return tree
    except Exception as e:
        print(red(f"❌ Failed to append project file tree: {e}"))
        return "Error retrieving file tree. Continuing without it."


async def _run_single_picker(
    prompt_text: str,
    prompt_index: int,
    model,
    file_scores: Dict[str, Dict[str, float]],  # Enhanced format only
    token_callers: Dict[str, Dict[str, List[Dict]]] = None,
    task_goal: str = None
) -> List[str]:
    """Run a single file picker agent with fallback mechanism."""
    try:
        # Create a named wrapper function for find_files that uses file_scores and token callers
        async def find_files_with_scores(prompt: str) -> List[str]:
            """Wrapper for find_files that uses the provided file scores and token callers."""
            return await find_files(prompt, file_scores, token_callers, task_goal)

        # Set proper name for Pydantic AI tool registration
        find_files_with_scores.__name__ = "find_files_with_scores"

        # Create a temporary agent with the wrapper function
        temp_picker_agent = Agent(
            model=model,
            system_prompt="You are an expert at finding relevant files in a codebase for a given task. Analyze the user's request and return the most relevant file paths as a JSON list of strings.",
            output_type=List[str],
            tools=[find_files_with_scores],
            retries=0,  # Set to 0 to ensure only one attempt
            end_strategy="early"
        )

        # Run the agent - single attempt, no usage limits
        print(f"Running picker {prompt_index+1} for: {prompt_text[:50]}...")
        result = await temp_picker_agent.run(prompt_text)

        # Handle the result based on its type
        if isinstance(result, list):
            print(f"Picker {prompt_index+1} found {len(result)} files")
            return result

        # For AgentRunResult objects with output attribute
        if hasattr(result, 'output'):
            output = result.output
            print(f"Picker {prompt_index+1} found {len(output)} files")
            return output

        print(
            f"Picker {prompt_index+1} returned unexpected result type: {type(result)}")
        return []

    except Exception as e:
        print(f"Error in file picker {prompt_index+1}: {e}")
        import traceback
        print(traceback.format_exc())

        # Get files using direct keyword matching as fallback
        try:
            print(
                f"Using fallback keyword matching for picker {prompt_index+1}")
            # Extract keywords directly from prompt
            keywords = _extract_keywords_from_prompt(prompt_text, task_goal)

            # Do simple keyword matching on file paths
            matched_files = []

            for file_path, token_scores in file_scores.items():
                # Skip non-code files
                if "." not in file_path or any(part in file_path for part in [".git", "node_modules", "__pycache__"]):
                    continue

                # Simple matching
                score = 0
                for keyword in keywords:
                    if keyword.lower() in file_path.lower():
                        score += 1

                if score > 0:
                    matched_files.append((file_path, score))

            # Get top 10 matches
            result_files = [f for f, _ in sorted(
                matched_files, key=lambda x: x[1], reverse=True)[:10]]
            if result_files:
                print(
                    f"Fallback found {len(result_files)} files for picker {prompt_index+1}")
                return result_files

        except Exception as fallback_err:
            print(
                f"Fallback also failed for picker {prompt_index+1}: {fallback_err}")

        return [f"Error: Could not complete file search for area {prompt_index+1}"]


async def run_file_pickers_in_parallel(
    overall_goal: str,
    focus_prompts: List[str],
    picker_agent_model: str,
    file_scores: Dict[str, Dict[str, float]],  # Enhanced format only
    token_callers: Dict[str, Dict[str, List[Dict]]] = None
) -> List[List[str]]:
    """
    Spawns multiple file picker agents in parallel to explore different parts of the codebase.
    Uses anyio.TaskGroup for proper concurrent execution.
    """
    print(f"Starting parallel file exploration for goal: '{overall_goal}'")

    # Using a dictionary to store results keyed by index
    results_dict: Dict[int, List[str]] = {}

    # Limit to a reasonable number of prompts
    # Maximum 4 prompts for performance reasons
    focus_prompts = focus_prompts[:4]

    # Create a TaskGroup to run pickers in parallel
    async with anyio.create_task_group() as tg:
        async def run_picker(idx, prompt):
            try:
                # Include overall_goal context in each prompt for better results
                picker_prompt = f'Based on the overall goal "{overall_goal}", find files related to this specific area: {prompt}'

                # Use timeout for individual pickers to prevent hanging
                with anyio.move_on_after(120):  # 2-minute timeout per picker
                    result = await _run_single_picker(
                        picker_prompt,
                        idx,
                        picker_agent_model,
                        file_scores,
                        token_callers,
                        overall_goal
                    )
                    results_dict[idx] = result
            except Exception as e:
                print(f"Error running picker {idx+1}: {e}")
                results_dict[idx] = [f"Error: {str(e)}"]

        # Start all pickers in parallel with small delay to avoid rate limits
        for i, focus_prompt in enumerate(focus_prompts):
            tg.start_soon(run_picker, i, focus_prompt)
            if i < len(focus_prompts) - 1:
                await anyio.sleep(0.5)  # Small delay between starts

    # Convert dict to ordered list of results
    ordered_results = []
    for i in range(len(focus_prompts)):
        ordered_results.append(results_dict.get(
            i, [f"Error: No result for prompt {i+1}"]))

    return ordered_results


def create_file_explorer_agent(model) -> Agent:
    """
    Creates a file explorer agent that orchestrates multiple file pickers.
    """
    agent = Agent(
        model=model,
        system_prompt=(
            "You are a file explorer agent for a software project. "
            "Your job is to determine 1-4 distinct areas of the codebase to explore "
            "based on a high-level goal. Return these areas as a list of prompts. "
            "Each prompt should focus on a different aspect of the goal, "
            "covering important functional areas without overlap."
        ),
        output_type=ExplorePrompts,
        instrument=True,
    )
    agent.system_prompt(add_project_file_tree_to_context)
    return agent

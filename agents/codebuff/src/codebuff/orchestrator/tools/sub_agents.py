import json
from typing import List, Optional, Dict

import anyio
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class ExplorePrompts(BaseModel):
    """A model to hold a list of exploration prompts for the file picker agents."""
    prompts: List[str] = Field(
        ..., description="A list of 1 to 4 concise prompts for exploring different areas of the codebase in parallel.")


class FilePickerDependencies(BaseModel):
    """Dependencies for the File Picker agent."""
    pass


async def find_files(
    prompt: str,
    file_scores: dict,
    token_callers: dict = None,
    task_goal: str = None,  # Add task_goal parameter with default for backward compatibility
) -> List[str]:
    """
    Finds relevant files in the codebase based on a prompt using file token scores and token callers.
    """
    print(f"Finding files for prompt: '{prompt}'")
    try:
        if not file_scores:
            print("Warning: No file scores provided, returning empty list")
            return []

        # Extract keywords from the prompt and task goal for filtering
        keywords = _extract_keywords_from_prompt(prompt, task_goal)
        print(f"Using keywords for search: {keywords}")

        # Handle different file_scores data structure formats
        scored_files = []

        # Check if file_scores is a dictionary as expected
        if isinstance(file_scores, dict):
            # Standard structure: {file_path: [tokens]}
            for file_path, tokens in file_scores.items():
                # Skip non-code files
                if _is_non_code_file(file_path):
                    continue

                # Calculate relevance score
                score = _calculate_token_relevance(
                    tokens, keywords, file_path, token_callers)
                if score > 0:
                    scored_files.append((file_path, score))

        # Handle case where file_scores is a list (unexpected but handle gracefully)
        elif isinstance(file_scores, list):
            # Fall back to searching file paths for keywords
            for file_path in file_scores:
                if _is_non_code_file(file_path):
                    continue

                # Simple path-based scoring
                score = 0
                for keyword in keywords:
                    if keyword.lower() in file_path.lower():
                        score += 3.0

                if score > 0:
                    scored_files.append((file_path, score))

        # If we don't have results yet, try to get all files from git
        if not scored_files:
            print(
                "No files matched from provided scores, falling back to keyword search in paths")
            # This would need container access, but you mentioned we don't need that dependency
            # Instead, use whatever files we have available
            return []

        # Sort by relevance score
        sorted_files = [file for file, _ in sorted(
            scored_files, key=lambda x: x[1], reverse=True)]

        # Return top results (maximum 20)
        result_files = sorted_files[:20]
        print(f"Found {len(result_files)} relevant files")
        return result_files

    except Exception as e:
        print(f"Error finding files: {e}")
        import traceback
        print(traceback.format_exc())
        return [f"Error: Unexpected error finding files: {str(e)}"]


def _calculate_token_relevance(
    tokens: List[str],
    keywords: List[str],
    file_path: str,
    token_callers: Dict = None
) -> float:
    """
    Calculate relevance score based on token matches with keywords and caller relationships.
    Handles different data structure formats safely.
    """
    score = 0.0

    # Handle different token formats
    if not tokens:
        tokens = []
    elif isinstance(tokens, str):
        tokens = [tokens]  # Convert single token to list

    # Path-based scoring
    for keyword in keywords:
        if keyword.lower() in file_path.lower():
            score += 3.0

    # Token-based scoring
    if isinstance(tokens, list):  # Ensure tokens is a list
        lower_tokens = [t.lower() for t in tokens if isinstance(t, str)]
        lower_keywords = [k.lower() for k in keywords]

        for keyword in lower_keywords:
            for token in lower_tokens:
                if keyword == token:
                    score += 5.0
                elif keyword in token:
                    score += 2.0
                elif len(token) > 3 and token in keyword:
                    score += 1.0

    # Token caller relationship scoring - with safe handling
    if token_callers and isinstance(token_callers, dict):
        try:
            # Look for files that call important tokens related to keywords
            caller_bonus = 0.0
            for token in tokens:
                if not isinstance(token, str):
                    continue

                # Check if this token is called by other files
                if token in token_callers:
                    callers = token_callers[token]

                    # Skip if callers is not a dictionary
                    if not isinstance(callers, dict):
                        continue

                    # If this token is related to keywords, increase score based on caller count
                    for keyword in lower_keywords:
                        if (keyword in token.lower() or
                            token.lower() in keyword or
                            any(keyword in caller_token.lower() for caller_token in callers.keys()
                                if isinstance(caller_token, str))):

                            # Add score based on the number of callers (capped)
                            caller_count = sum(len(files) for files in callers.values()
                                               if isinstance(files, list))
                            caller_bonus += min(caller_count * 0.5, 5.0)

                            # Add extra points if called by multiple different files
                            unique_caller_files = set()
                            for file_list in callers.values():
                                if isinstance(file_list, list):
                                    unique_caller_files.update(file_list)

                            caller_bonus += min(len(unique_caller_files)
                                                * 0.8, 8.0)

            score += caller_bonus
        except Exception as e:
            print(f"Warning: Error processing token callers: {e}")

    return score


def _extract_keywords_from_prompt(prompt: str, task_goal: str = None) -> List[str]:
    """
    Extract relevant keywords from the prompt and task goal for file filtering.
    
    Args:
        prompt: The specific search prompt
        task_goal: The overall task goal to extract domain keywords from
    
    Returns:
        List of relevant keywords for file matching
    """
    stop_words = {'and', 'or', 'the', 'for', 'in', 'on', 'with', 'that',
                  'this', 'to', 'a', 'an', 'be', 'is', 'are', 'was', 'were',
                  'from', 'as', 'at', 'by', 'of'}

    # Combine text sources for keyword extraction
    text_sources = [prompt.lower()]
    if task_goal:
        text_sources.append(task_goal.lower())

    # Extract all potential keywords
    all_words = []
    for text in text_sources:
        words = text.replace(',', ' ').replace(
            '.', ' ').replace(':', ' ').replace(';', ' ').split()
        all_words.extend(words)

    # Filter words: keep words longer than 2 characters that aren't stop words
    keywords = [word for word in all_words if len(
        word) > 2 and word not in stop_words]

    # Count word frequency to identify important domain terms
    word_counts = {}
    for word in keywords:
        word_counts[word] = word_counts.get(word, 0) + 1

    # Sort by frequency to prioritize repeated keywords
    sorted_keywords = sorted(
        word_counts.items(), key=lambda x: x[1], reverse=True)

    # Take the top keywords, with more weight given to task_goal keywords
    selected_keywords = [word for word, _ in sorted_keywords[:30]]

    # Ensure we don't have too many keywords (which could dilute relevance)
    return selected_keywords[:20]


def _is_non_code_file(file_path: str) -> bool:
    """Determines if a file is likely not a code file."""
    non_code_extensions = {
        '.md', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
        '.json', '.lock', '.yml', '.yaml', '.toml', '.license'
    }
    excluded_patterns = {'.git', 'node_modules',
                         '.venv', 'dist', 'build', '__pycache__'}

    file_ext = '.' + file_path.split('.')[-1] if '.' in file_path else ''

    return (
        file_ext.lower() in non_code_extensions or
        any(pattern in file_path for pattern in excluded_patterns)
    )


def create_file_picker_agent(model) -> Agent:
    """
    Creates an agent that is an expert at finding relevant files in a codebase.
    """
    return Agent(
        model=model,
        system_prompt="You are an expert at finding relevant files in a codebase for a given task. Analyze the user's request and return the most relevant file paths as a JSON list of strings.",
        output_type=List[str],
        instrument=True,
    )


async def _run_single_picker(
    prompt_text: str,
    prompt_index: int,
    model,
    file_scores: Dict[str, List[str]],
    token_callers: Dict[str, Dict[str, List[str]]] = None,
    task_goal: str = None  # Add task_goal parameter
) -> List[str]:
    """Run a single file picker agent with proper error handling."""
    try:
        # Create a named wrapper function for find_files that uses file_scores and token_callers
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
        )

        # Run the agent with timeout protection
        with anyio.move_on_after(300):  # 5-minute timeout
            print(
                f"Running picker {prompt_index+1} for: {prompt_text[:50]}...")
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
        return [f"Error: {str(e)}"]


async def run_file_pickers_in_parallel(
    overall_goal: str,
    focus_prompts: List[str],
    picker_agent: Agent,
    file_scores: Dict[str, List[str]],
    token_callers: Dict[str, Dict[str, List[str]]] = None
) -> List[List[str]]:
    """
    Spawns multiple file picker agents in parallel to explore different parts of the codebase.
    Uses file token scores and token callers for improved file relevance scoring.
    """
    print(f"Starting parallel file exploration for goal: '{overall_goal}'")

    # Using a dictionary to store results keyed by index
    results_dict: Dict[int, List[str]] = {}

    # Run each picker in its own protected context to prevent TaskGroup exceptions
    for i, focus_prompt in enumerate(focus_prompts):
        try:
            picker_prompt = f'Based on the overall goal "{overall_goal}", find files related to this specific area: {focus_prompt}'

            # Run the picker directly without TaskGroup to avoid exception propagation
            result = await _run_single_picker(
                picker_prompt,
                i,
                picker_agent.model,
                file_scores,
                token_callers,
                overall_goal  # Pass the overall goal to extract domain-specific keywords
            )
            results_dict[i] = result
        except Exception as e:
            print(f"Error running picker {i+1}: {e}")
            import traceback
            print(traceback.format_exc())
            results_dict[i] = [f"Error: {str(e)}"]

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
    return Agent(
        model=model,
        system_prompt="You are a file explorer agent. Your job is to determine 1-4 distinct areas of a codebase to explore based on a high-level goal. Return these areas as a list of prompts.",
        output_type=ExplorePrompts,
        instrument=True,
    )

from dataclasses import dataclass
from typing import List

import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, green, yellow


@dataclass
class FilePickerDependencies:
    config: YAMLConfig
    container: dagger.Container
    task_description: str


async def search_relevant_files(
    ctx: RunContext[FilePickerDependencies],
    search_terms: str
) -> str:
    """Search for files relevant to the task."""
    print(blue(f"🔍 Searching for files related to: {search_terms}"))
    
    try:
        # Search file names
        name_search = await ctx.deps.container.with_exec([
            "bash", "-c", f"find . -type f -iname '*{search_terms}*' | head -15"
        ]).stdout()
        
        # Search file contents
        content_search = await ctx.deps.container.with_exec([
            "bash", "-c", f"grep -r -l '{search_terms}' --include='*.py' --include='*.js' --include='*.ts' --include='*.java' --include='*.go' --include='*.rs' . 2>/dev/null | head -10"
        ]).stdout()
        
        result = f"""File Search Results for '{search_terms}':

Files with matching names:
{name_search if name_search.strip() else 'No matches found'}

Files with matching content:
{content_search if content_search.strip() else 'No matches found'}"""
        
        print(green("✅ File search completed"))
        return result
        
    except Exception as e:
        error_msg = f"Error searching files: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


async def analyze_file_relevance(
    ctx: RunContext[FilePickerDependencies],
    file_pattern: str = "*"
) -> str:
    """Analyze files to determine relevance to the task."""
    print(blue(f"📊 Analyzing file relevance for: {ctx.deps.task_description}"))
    
    try:
        # Get recently modified files
        recent_files = await ctx.deps.container.with_exec([
            "bash", "-c", "find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.java' -o -name '*.go' \) -exec ls -lt {} + | head -10"
        ]).stdout()
        
        # Get file sizes and types
        file_types = await ctx.deps.container.with_exec([
            "bash", "-c", "find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' \) | head -20 | xargs file"
        ]).stdout()
        
        result = f"""File Relevance Analysis:

Task: {ctx.deps.task_description}

Recently modified files:
{recent_files}

File types found:
{file_types}"""
        
        print(green("✅ Relevance analysis completed"))
        return result
        
    except Exception as e:
        error_msg = f"Error analyzing relevance: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


def create_file_picker_agent(model: OpenAIModel) -> Agent:
    """Create the File Picker agent."""
    system_prompt = """
You are a File Picker Agent, equivalent to Codebuff's file selection capabilities.

Your role:
- Identify the most relevant files for a given coding task
- Filter out irrelevant files to focus attention
- Prioritize files based on relevance to the task
- Provide a curated list of files to work with

Your tools:
1. search_relevant_files - Search for files by name and content
2. analyze_file_relevance - Analyze files for task relevance

Always provide:
- A focused list of the most relevant files
- Explanation of why each file is relevant
- Priority ordering of files to examine
- Suggestions for files that might be missing but needed
"""
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=FilePickerDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=3
    )
    
    agent.tool(search_relevant_files)
    agent.tool(analyze_file_relevance)
    
    print(f"File Picker Agent created with model: {model.model_name}")
    return agent
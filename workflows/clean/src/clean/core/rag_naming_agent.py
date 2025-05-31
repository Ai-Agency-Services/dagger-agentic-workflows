import re
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import dagger
from clean.models.config import YAMLConfig
from clean.template import get_rag_naming_agent_template
from clean.utils.code_parser import parse_code_file
from clean.utils.embeddings import generate_embeddings
from pydantic_ai import Agent, RunContext
from pydantic_ai.direct import model_request_sync
from pydantic_ai.messages import ModelRequest
from pydantic_ai.models.openai import OpenAIModel
from supabase import Client, create_client


@dataclass
class CodeEmbedding:
    """A code snippet with its embedding and metadata."""
    content: str
    embedding: List[float]
    filepath: str
    start_line: int
    end_line: int
    language: str
    context: Optional[str] = None
    symbols: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RagNamingAgentDependencies:
    config: YAMLConfig
    container: dagger.Container
    supabase_url: str
    supabase_key: dagger.Secret
    openai_api_key: Optional[dagger.Secret] = None
    embedding_collection: str = "code_embeddings"
    results_limit: int = 5
    similarity_threshold: float = 0.80


@dataclass
class RenameCandidate:
    """A candidate for variable/function renaming."""
    symbol_name: str
    suggested_name: str
    filepath: str
    line_number: int
    symbol_type: str  # 'variable', 'function', 'class', etc.
    reason: str
    context: str  # The code surrounding the symbol for context


async def query_similar_code(
    ctx: RunContext[RagNamingAgentDependencies],
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Query the Supabase vector store for similar code snippets based on the query.
    """
    try:
        # Create Supabase client
        supabase: Client = create_client(
            ctx.deps.supabase_url,
            await ctx.deps.supabase_key.plaintext()
        )

        # Ensure limit is a positive integer
        if not isinstance(limit, int) or limit <= 0:
            print(f"Warning: Invalid limit ({limit}), using default of 5")
            limit = 5

        # Validate similarity threshold
        similarity_threshold = ctx.deps.similarity_threshold
        if not isinstance(similarity_threshold, (int, float)) or similarity_threshold <= 0:
            print(
                f"Warning: Invalid similarity threshold ({similarity_threshold}), using default of 0.7")
            similarity_threshold = 0.7

        # Check for API key
        if not ctx.deps.openai_api_key:
            print("Warning: OpenAI API key is missing")
            return []

        # Generate embedding for the query
        query_embedding = await generate_embeddings(
            text=query,
            openai_api_key=ctx.deps.openai_api_key,
        )

        if not query_embedding:
            print("Warning: Failed to generate embedding for query")
            return []

        # Query the vector database
        response = supabase.table('code_embeddings') \
            .select("content, filepath, start_line, end_line, language, context, symbols") \
            .rpc("match_code_embeddings", {
                "query_embedding": query_embedding,
                "match_threshold": similarity_threshold,
                "match_limit": limit
            }) \
            .execute()

        return response.data if response and hasattr(response, 'data') else []
    except Exception as e:
        print(f"Error querying Supabase: {e}")
        traceback.print_exc()
        return []


async def scan_code_for_naming_issues(
    ctx: RunContext[RagNamingAgentDependencies],
    code_content: str,
    filepath: str
) -> List[Dict[str, Any]]:
    """
    Analyze code content to identify potential naming issues.
    """
    try:
        # Parse the code to extract symbols
        code_file = parse_code_file(code_content, filepath)

        if not code_file or not hasattr(code_file, 'symbols') or not code_file.symbols:
            print(f"Warning: No symbols found in {filepath}")
            return []

        # Query for naming best practices related to the code's symbols
        issues = []

        for symbol in code_file.symbols:
            # Ensure symbol has required attributes
            if not hasattr(symbol, 'name') or not hasattr(symbol, 'type') or not hasattr(symbol, 'line_number'):
                print(f"Warning: Symbol missing required attributes")
                continue

            # Ensure line_number is an integer
            if symbol.line_number is None:
                symbol.line_number = 0

            # Query similar code with better naming conventions
            similar_codes = await query_similar_code(
                ctx,
                f"best naming practices for {symbol.name} as a {symbol.type} in {code_file.language}",
                limit=3
            )

            if similar_codes:
                issues.append({
                    "symbol_name": symbol.name,
                    "symbol_type": symbol.type,
                    "line_number": int(symbol.line_number) if hasattr(symbol, 'line_number') else 0,
                    "similar_examples": similar_codes,
                    "context": code_file.get_context_around_line(
                        int(symbol.line_number) if hasattr(
                            symbol, 'line_number') else 0,
                        5
                    )
                })

        return issues
    except Exception as e:
        print(f"Error scanning code: {e}")
        traceback.print_exc()
        return []


async def suggest_better_names(
    ctx: RunContext[RagNamingAgentDependencies],
    issues: List[Dict[str, Any]]
) -> List[RenameCandidate]:
    """Generate suggested names for symbols with naming issues."""
    candidates = []

    try:
        # Validate input
        if not issues:
            print("No issues to process")
            return []

        print(f"DEBUG: Processing {len(issues)} issues")
        for idx, issue in enumerate(issues):
            print(f"DEBUG: Issue {idx+1} structure: {list(issue.keys())}")
            print(
                f"DEBUG: line_number type: {type(issue.get('line_number'))}, value: {issue.get('line_number')}")

        for issue in issues:
            try:
                # Validate required fields
                symbol_name = issue.get("symbol_name")
                symbol_type = issue.get("symbol_type")
                line_number = issue.get("line_number", 0)
                context = issue.get("context", "")

                if not symbol_name or not symbol_type:
                    print(
                        f"Skipping issue with missing required fields: {issue}")
                    continue

                # Ensure line_number is an integer
                try:
                    line_number = int(line_number)
                except (TypeError, ValueError):
                    print(
                        f"Warning: Invalid line_number - {line_number}, using 0")
                    line_number = 0

                # Create context from similar examples safely
                similar_examples = issue.get("similar_examples", [])
                if not similar_examples:
                    similar_examples = []

                context_examples = "\n".join([
                    f"Example {i+1}: {ex.get('content', '')}"
                    for i, ex in enumerate(similar_examples)
                ])

                # Format reasoning for the LLM
                reasoning = f"""
                Symbol: {symbol_name}
                Type: {symbol_type}
                Current context:
                {context}

                Similar examples with better naming:
                {context_examples}
                
                Based on the above information, suggest a better name for this symbol that follows best practices.
                Return just the new name without explanation.
                """

                # Use Pydantic AI's model_request_sync for LLM interaction
                try:
                    # Only attempt to use the LLM if we have all the required configuration
                    provider = getattr(ctx.deps.config.llm, 'provider', None)
                    model_name = getattr(
                        ctx.deps.config.llm, 'model_name', None)

                    if provider and model_name:
                        # Use model_request_sync for name suggestion
                        model_response = model_request_sync(
                            f'{provider}:{model_name}',
                            [ModelRequest.user_text_prompt(reasoning)]
                        )

                        # Extract the suggested name
                        if model_response and hasattr(model_response, 'parts') and model_response.parts:
                            suggested_name = model_response.parts[0].content.strip(
                            )

                            # Validate the suggested name
                            if not suggested_name or len(suggested_name) > 50 or ' ' in suggested_name:
                                # Fallback to rule-based name generation
                                suggested_name = generate_better_name(
                                    symbol_name, symbol_type)
                        else:
                            # Fallback if no valid response
                            suggested_name = generate_better_name(
                                symbol_name, symbol_type)
                    else:
                        # Fallback if provider or model_name is missing
                        suggested_name = generate_better_name(
                            symbol_name, symbol_type)
                except Exception as model_error:
                    print(
                        f"Error using LLM for name suggestion: {model_error}")
                    traceback.print_exc()
                    # Fallback to rule-based name suggestion
                    suggested_name = generate_better_name(
                        symbol_name, symbol_type)

                # Safe file path extraction
                filepath = ""
                if similar_examples and len(similar_examples) > 0:
                    filepath = similar_examples[0].get("filepath", "")

                # Create RenameCandidate
                candidates.append(RenameCandidate(
                    symbol_name=symbol_name,
                    suggested_name=suggested_name,
                    filepath=filepath,
                    line_number=line_number,
                    symbol_type=symbol_type,
                    reason=f"Based on analysis of similar code patterns.",
                    context=context
                ))
            except Exception as inner_e:
                print(f"Error processing issue: {inner_e}")
                traceback.print_exc()

        return candidates
    except Exception as e:
        print(f"Error suggesting better name: {e}")
        traceback.print_exc()
        return []  # Return empty list on error


# Simple function to generate better names based on symbol type
def generate_better_name(name: str, symbol_type: str) -> str:
    """
    Generate a better name based on the symbol type.
    This is a placeholder for the LLM-based generation.
    #TODO: Replace with actual LLM call or more sophisticated logic.
    """
    if not name:
        return "unnamed"

    if symbol_type == "variable":
        if name.startswith("_") or name.startswith("tmp"):
            return f"processed{name.title().replace('_', '')}"
        return f"descriptive{name.title().replace('_', '')}"

    elif symbol_type == "function" or symbol_type == "method":
        if not name.startswith(("get", "set", "is", "has", "do", "process")):
            return f"process{name.title().replace('_', '')}"
        return name

    elif symbol_type == "class":
        # Ensure class names are PascalCase
        return ''.join(word.title() for word in re.split(r'[_\s]+', name))

    elif symbol_type == "constant":
        # Ensure constants are UPPER_SNAKE_CASE
        return name.upper()

    # Default improvement
    return f"better{name.title().replace('_', '')}"


def create_rag_naming_agent(pydantic_ai_model: OpenAIModel) -> Agent:
    """
    Create an agent for finding code that needs better naming through RAG.
    """
    if pydantic_ai_model is None:
        raise ValueError("AI model cannot be None")

    base_system_prompt = get_rag_naming_agent_template()

    agent = Agent(
        model=pydantic_ai_model,
        system_prompt=base_system_prompt,
        deps_type=RagNamingAgentDependencies,
        instrument=True,
        end_strategy="exhaustive",
        output_type=List[RenameCandidate]
    )

    # Register tools
    agent.tool(scan_code_for_naming_issues)
    agent.tool(query_similar_code)
    agent.tool(suggest_better_names)

    return agent

from dataclasses import dataclass, field
from pydantic_ai.direct import model_request_sync
from pydantic_ai.messages import ModelRequest
from typing import Any, Dict, List, Optional
import re

import dagger
from clean.template import get_rag_naming_agent_template
from clean.utils.code_parser import CodeFile, parse_code_file
from clean.utils.embeddings import generate_embeddings
from clean.models.config import YAMLConfig
from pydantic_ai import Agent, RunContext
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


# Make a synchronous request to the model


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

        # Generate embedding for the query
        query_embedding = await generate_embeddings(query)

        # Query the vector database
        response = supabase.table(ctx.deps.embedding_collection) \
            .select("content, filepath, start_line, end_line, language, context, symbols") \
            .rpc("match_code_embeddings", {
                "query_embedding": query_embedding,
                "match_threshold": ctx.deps.similarity_threshold,
                "match_limit": limit
            }) \
            .execute()

        return response.data
    except Exception as e:
        print(f"Error querying Supabase: {e}")
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

        # Query for naming best practices related to the code's symbols
        issues = []

        for symbol in code_file.symbols:
            # Query similar code with better naming conventions
            similar_codes = await query_similar_code(
                ctx.deps,
                f"best naming practices for {symbol.name} as a {symbol.type} in {code_file.language}",
                limit=3
            )

            if similar_codes:
                issues.append({
                    "symbol_name": symbol.name,
                    "symbol_type": symbol.type,
                    "line_number": symbol.line_number,
                    "similar_examples": similar_codes,
                    "context": code_file.get_context_around_line(symbol.line_number, 5)
                })

        return issues
    except Exception as e:
        print(f"Error scanning code: {e}")
        return []


async def suggest_better_names(
    ctx: RunContext[RagNamingAgentDependencies],
    issues: List[Dict[str, Any]]
) -> List[RenameCandidate]:
    """Generate suggested names for symbols with naming issues."""
    candidates = []

    for issue in issues:
        # Create context from similar examples
        context_examples = "\n".join([
            f"Example {i+1}: {ex['content']}"
            for i, ex in enumerate(issue.get("similar_examples", []))
        ])

        # Format reasoning for the LLM
        reasoning = f"""
            Symbol: {issue['symbol_name']}
            Type: {issue['symbol_type']}
            Current context:
            {issue['context']}

            Similar examples with better naming:
            {context_examples}

            Based on the above information, suggest a better name for this symbol that follows best practices.
            The name should be clear, descriptive, and follow standard conventions for {issue['symbol_type']} names.
            Return just the new name without explanation.
        """

        try:
            # Use the LLM to generate a better name
            # This is the proper way to use reasoning with Pydantic AI
            response = model_request_sync(
                f'{ctx.deps.config.llm.provider}:{ctx.deps.config.llm.model_name}',
                [ModelRequest.user_text_prompt(
                    f'{reasoning}',)]
            )

            # Extract the actual suggested name from the response
            if response and hasattr(response, 'parts') and response.parts and len(response.parts) > 0:
                suggested_name = response.parts[0].content.strip()

                # If the response looks too complex (multiple words or sentences), simplify
                if len(suggested_name.split()) > 3 or len(suggested_name) > 50:
                    # Fall back to simple logic
                    suggested_name = generate_better_name(
                        issue['symbol_name'], issue['symbol_type'])
            else:
                # Fallback if we couldn't get a valid response
                suggested_name = generate_better_name(
                    issue['symbol_name'], issue['symbol_type'])

            suggestion = {
                "symbol_name": issue["symbol_name"],
                "suggested_name": suggested_name,
                "filepath": issue["similar_examples"][0]["filepath"] if issue["similar_examples"] else "",
                "line_number": issue["line_number"],
                "symbol_type": issue["symbol_type"],
                "reason": f"Based on analysis of similar code patterns and best practices for {issue['symbol_type']}.",
                "context": issue["context"]
            }

            candidates.append(RenameCandidate(**suggestion))
        except Exception as e:
            print(
                f"Error suggesting better name for {issue['symbol_name']}: {e}")
            # Fallback suggestion if LLM fails
            candidates.append(RenameCandidate(
                symbol_name=issue["symbol_name"],
                suggested_name=generate_better_name(
                    issue['symbol_name'], issue['symbol_type']),
                filepath=issue["similar_examples"][0]["filepath"] if issue["similar_examples"] else "",
                line_number=issue["line_number"],
                symbol_type=issue["symbol_type"],
                reason=f"Fallback suggestion due to error in name generation: {str(e)[:100]}",
                context=issue["context"]
            ))

    return candidates


# Simple function to generate better names based on symbol type
def generate_better_name(name: str, symbol_type: str) -> str:
    """
    Generate a better name based on the symbol type.
    This is a placeholder for the LLM-based generation.
    """
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


def create_rag_naming_agent(pydantic_ai_model: Agent) -> Agent:
    """
    Create an agent for finding code that needs better naming through RAG.
    """
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
    agent.tool(query_similar_code)
    agent.tool(scan_code_for_naming_issues)
    agent.tool(suggest_better_names)

    return agent

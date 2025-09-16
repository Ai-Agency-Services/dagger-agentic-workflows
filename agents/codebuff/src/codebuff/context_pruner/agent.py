from dataclasses import dataclass
from typing import Dict, List

import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import blue, green, yellow


@dataclass
class ContextPrunerDependencies:
    config: YAMLConfig
    container: dagger.Container
    context_data: str
    max_tokens: int = 4000


async def analyze_context_size(
    ctx: RunContext[ContextPrunerDependencies]
) -> str:
    """Analyze the current context size and identify pruning opportunities."""
    print(blue("📏 Analyzing context size"))
    
    try:
        context = ctx.deps.context_data
        context_length = len(context)
        estimated_tokens = context_length // 4  # Rough estimate: 4 chars per token
        
        # Analyze context structure
        lines = context.split('\n')
        sections = []
        current_section = None
        
        for line in lines:
            if line.startswith('=== ') or line.startswith('## ') or line.startswith('# '):
                if current_section:
                    sections.append(current_section)
                current_section = {'title': line, 'lines': [], 'size': 0}
            elif current_section:
                current_section['lines'].append(line)
                current_section['size'] += len(line) + 1  # +1 for newline
        
        if current_section:
            sections.append(current_section)
        
        # Identify large sections
        large_sections = [s for s in sections if s['size'] > 1000]
        
        result = f"""Context Size Analysis:

Total characters: {context_length:,}
Estimated tokens: {estimated_tokens:,}
Target max tokens: {ctx.deps.max_tokens:,}
Pruning needed: {'Yes' if estimated_tokens > ctx.deps.max_tokens else 'No'}
Overage: {max(0, estimated_tokens - ctx.deps.max_tokens):,} tokens

Context structure:
- Total sections found: {len(sections)}
- Large sections (>1000 chars): {len(large_sections)}

Top sections by size:"""
        
        # Sort sections by size and show top ones
        sections.sort(key=lambda x: x['size'], reverse=True)
        for i, section in enumerate(sections[:5]):
            result += f"\n{i+1}. {section['title'][:60]}... ({section['size']:,} chars, {len(section['lines'])} lines)"
        
        print(green("✅ Context analysis completed"))
        return result
        
    except Exception as e:
        error_msg = f"Error analyzing context: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


async def prune_context(
    ctx: RunContext[ContextPrunerDependencies],
    strategy: str = "smart"
) -> str:
    """Prune context to fit within token limits."""
    print(blue(f"✂️ Pruning context using {strategy} strategy"))
    
    try:
        context = ctx.deps.context_data
        max_chars = ctx.deps.max_tokens * 4  # Rough conversion
        
        if len(context) <= max_chars:
            return "Context is already within limits - no pruning needed"
        
        pruned_context = ""
        
        if strategy == "smart":
            # Smart pruning: preserve important sections
            lines = context.split('\n')
            important_keywords = ['error', 'important', 'critical', 'summary', 'result', 'warning', 'todo', 'fixme']
            
            # Keep important lines, headers, and short lines
            for line in lines:
                line_lower = line.lower()
                is_important = (
                    any(keyword in line_lower for keyword in important_keywords) or
                    line.startswith(('===', '##', '#', '- ', '* ')) or
                    len(line.strip()) < 80 or  # Keep short lines
                    line.strip().endswith(':')  # Keep labels
                )
                
                if is_important:
                    pruned_context += line + '\n'
                    
                if len(pruned_context) > max_chars:
                    pruned_context = pruned_context[:max_chars] + "\n[...context truncated...]\n"
                    break
        
        elif strategy == "truncate":
            # Simple truncation
            pruned_context = context[:max_chars] + "\n[...truncated...]\n"
        
        elif strategy == "summarize":
            # Keep first and last parts
            quarter_size = max_chars // 4
            pruned_context = (
                context[:quarter_size] + 
                "\n\n[... middle content pruned for brevity ...]\n\n" + 
                context[-quarter_size:]
            )
        
        elif strategy == "sections":
            # Keep only section headers and first few lines of each
            lines = context.split('\n')
            in_section = False
            lines_in_section = 0
            
            for line in lines:
                if line.startswith(('===', '##', '#')):
                    in_section = True
                    lines_in_section = 0
                    pruned_context += line + '\n'
                elif in_section and lines_in_section < 3:
                    pruned_context += line + '\n'
                    lines_in_section += 1
                elif in_section and lines_in_section == 3:
                    pruned_context += "[...section content pruned...]\n\n"
                    in_section = False
                
                if len(pruned_context) > max_chars:
                    break
        
        original_size = len(context)
        pruned_size = len(pruned_context)
        reduction_percent = ((original_size - pruned_size) / original_size) * 100
        
        result = f"""Context Pruning Results:

Strategy: {strategy}
Original size: {original_size:,} characters
Pruned size: {pruned_size:,} characters
Reduction: {reduction_percent:.1f}%
Target achieved: {'Yes' if pruned_size <= max_chars else 'No'}

--- PRUNED CONTEXT ---
{pruned_context}
--- END PRUNED CONTEXT ---"""
        
        print(green(f"✅ Context pruned by {reduction_percent:.1f}%"))
        return result
        
    except Exception as e:
        error_msg = f"Error pruning context: {e}"
        print(yellow(f"⚠️ {error_msg}"))
        return error_msg


def create_context_pruner_agent(model: OpenAIModel) -> Agent:
    """Create the Context Pruner agent."""
    system_prompt = """
You are a Context Pruner Agent, equivalent to Codebuff's context management capabilities.

Your role:
- Analyze context size and identify what can be safely removed
- Prune context to fit within token limits while preserving essential information
- Use intelligent strategies to maintain context quality
- Ensure important information is retained

Your tools:
1. analyze_context_size - Analyze current context and identify pruning opportunities
2. prune_context - Actually prune the context using various strategies

Pruning strategies available:
- smart: Preserve important sections, headers, and keywords
- truncate: Simple truncation from the end
- summarize: Keep beginning and end, summarize middle
- sections: Keep section headers and first few lines of each

Always prioritize keeping:
- Error messages and critical information
- Headers and section markers
- Summary information
- Recent results
- Important keywords (error, warning, critical, etc.)

Provide clear analysis of what was removed and what was preserved.
"""
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=ContextPrunerDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=2
    )
    
    agent.tool(analyze_context_size)
    agent.tool(prune_context)
    
    print(f"Context Pruner Agent created with model: {model.model_name}")
    return agent
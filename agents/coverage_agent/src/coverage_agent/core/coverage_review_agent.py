from dataclasses import dataclass
from typing import TYPE_CHECKING

import dagger
from coverage_agent.models.code_module import CodeModule
from coverage_agent.models.coverage_review import CoverageReview
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.template import get_review_agent_template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

# Conditional import for Reporter type hint if it's complex
if TYPE_CHECKING:
    from dagger.client.gen import \
        Reporter  # Or your custom Reporter class path


@dataclass
class ReviewAgentDependencies:
    initial_container: dagger.Container
    container: dagger.Container
    report: CoverageReport
    reporter: 'Reporter'
    code_module: CodeModule


async def add_coverage_reports_prompt(ctx: RunContext[ReviewAgentDependencies]) -> str:
    """ System Prompt: Get the coverage reports content. """
    try:
        coverage_report_html = await ctx.deps.reporter.get_coverage_html(
            html_report_path=ctx.deps.report.coverage_report_path,
            test_container=ctx.deps.container)

        initial_coverage_report_html = await ctx.deps.reporter.get_coverage_html(
            html_report_path=ctx.deps.report.coverage_report_path,
            test_container=ctx.deps.initial_container)

        return f"""
                    \n ------- \n
                    <initial_coverage_report> \n
                    {initial_coverage_report_html}
                    </initial_coverage_report> \n   
                    \n ------- \n

                    \n ------- \n
                    <coverage_report_html> \n
                    {coverage_report_html}
                    </coverage_report_html> \n
                    \n ------- \n
                """
    except Exception as e:
        print(f"Error in add_coverage_report_prompt: {e}")
        return "\n ------- \n <coverage_report_html>Error retrieving coverage report.</coverage_report_html> \n ------- \n"


def create_coverage_review_agent(pydantic_ai_model: OpenAIModel) -> Agent:
    """
    Create and configure a pydantic_ai.Agent instance for code review and test generation.

    Args:
        pydantic_ai_model: An instance of pydantic_ai.models.OpenAIModel
                           configured with the desired provider and API key.

    Returns:
        A configured pydantic_ai.Agent instance.
    """

    base_system_prompt = get_review_agent_template()

    agent = Agent(
        model=pydantic_ai_model,
        output_type=CoverageReview,
        system_prompt=base_system_prompt,
        deps_type=ReviewAgentDependencies,
        instrument=True,
        end_strategy="exhaustive",
        retries=5,
        result_retries=5
    )

    # agent.tool(run_tests_tool)

    print(
        f"CoverAI Review Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Export necessary components
__all__ = ["create_code_review_agent", "ReviewAgentDependencies"]

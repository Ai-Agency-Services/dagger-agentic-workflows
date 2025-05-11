from dataclasses import dataclass
from typing import TYPE_CHECKING

import dagger
from coverage_agent.models.code_module import CodeModule
from coverage_agent.models.config import YAMLConfig
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.models.coverage_review import CoverageReview
from coverage_agent.template import get_review_agent_template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import yellow

# Conditional import for Reporter type hint if it's complex
if TYPE_CHECKING:
    from dagger.client.gen import \
        Reporter  # Or your custom Reporter class path


@dataclass
class ReviewAgentDependencies:
    config: YAMLConfig
    container: dagger.Container
    report: CoverageReport
    reporter: 'Reporter'
    code_module: CodeModule


async def add_test_results_prompt(ctx: RunContext[ReviewAgentDependencies]) -> str:
    """ System Prompt: Get the test results content. """
    try:
        test_command = ctx.deps.config.reporter.command
        result_container = await ctx.deps.container.with_exec(["bash", "-c", f"{test_command}; echo -n $? > /exit_code"])
        test_results = await result_container.file(
            f"{ctx.deps.config.reporter.output_path}"
        ).contents()

        error = await ctx.deps.reporter.parse_test_results(test_results)
        if error:
            # Store the error for the next iteration's system prompt (self-correction)
            print(yellow(f"Test Run Failed: {error}"))
            return f"Test Run Failed: {error}"
        else:
            # Tests passed, clear any previous error
            if ctx.deps.code_module:
                ctx.deps.code_module.error = None
            return "Test Run Succeeded."
    except Exception as e:
        import traceback
        print(f"Error in add_test_results_prompt: {e}")
        print(traceback.format_exc())
        return "\n ------- \n <test_results>Error retrieving test results.</test_results> \n ------- \n"


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

    agent.system_prompt(add_test_results_prompt)

    print(
        f"CoverAI Review Agent created with model: {pydantic_ai_model.model_name}")
    return agent


# Export necessary components
__all__ = ["create_coverage_review_agent", "ReviewAgentDependencies"]

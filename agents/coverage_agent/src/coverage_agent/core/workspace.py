from dataclasses import dataclass
from dagger.client.gen import Reporter

import dagger
from coverage_agent.models.code_module import CodeModule
from coverage_agent.models.coverage_report import CoverageReport
from coverage_agent.template import get_system_template
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


@dataclass
class Dependencies:
    ctr: dagger.Container
    reporter: Reporter
    coverage_html: str


unit_test_agent = Agent(
    'openai:gpt-4o',
    output_type=CodeModule,
    system_prompt=get_system_template(
        coverage_html="",
        directories="",
        current_directory="",
    )
)


@unit_test_agent.system_prompt
async def add_coverage_html(ctx: RunContext[Dependencies]) -> str:
    code_under_test = await ctx.deps.reporter.get_coverage_html(html_report_path=ctx.deps.report.coverage_report_path, test_container=ctx.deps.ctr)
    return f"""
                \n ------- \n
                <code_under_test> \n
                {code_under_test}
                </code_under_test> \n
                \n ------- \n
            """


@unit_test_agent.system_prompt
async def add_code_under_test(ctx: RunContext[Dependencies]) -> str:
    code_under_test = await ctx.deps.reporter.get_code_under_test(ctx.deps.coverage_html)
    return f"""
                \n ------- \n
                <code_under_test> \n
                {code_under_test}
                </code_under_test> \n
                \n ------- \n
            """


# @unit_test_agent.tool
# async def customer_balance(
#     ctx: RunContext[Dependencies], include_pending: bool
# ) -> float:
#     """Returns the customer's current account balance."""
#     return await ctx.deps.db.customer_balance(
#         id=ctx.deps.customer_id,
#         include_pending=include_pending,
#     )


# @unit_test_agent.tool
# async def read_file(ctx: RunContext[Dependencies], path: str) -> str:
#     """Read the contents of a file in the workspace.
#     Args:
#         path: The path to the file to read.
#     """
#     return await ctx.ctr.file(path).contents()


# @function_tool
# def write_file(wrapper: RunContextWrapper[Workspace], path: str, contents: str) -> str:
#     """Write a file to the workspace.
#     Args:
#         path: The path to the file to read.
#         contents: The contents to write to the file.
#     """
#     wrapper.context.ctr = wrapper.context.ctr.with_new_file(path, contents)
#     return f"{path} contents written."


# @function_tool
# async def build(wrapper: RunContextWrapper[Workspace]) -> str:
#     """Attempt to build the workspace.
#     """
#     return await wrapper.context.ctr.with_exec(["go", "build", "./..."]).stdout()


# async def main():
#     deps = SupportDependencies(customer_id=123, db=DatabaseConn())
#     result = await unit_test_agent.run('What is my balance?', deps=deps)
#     print(result.output)
#     """
#     support_advice='Hello John, your current account balance, including pending transactions, is $123.45.' block_card=False risk=1
#     """

#     result = await unit_test_agent.run('I just lost my card!', deps=deps)
#     print(result.output)
#     """

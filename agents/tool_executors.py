from context.app_context import ApplicationContext

from services.sql_service import run_sql_workflow
from memory.memory_service import get_memory_context

from tools.email_tool import email_tool


async def execute_sql_tool(
    tool_args: dict,
    app_context: ApplicationContext
):
    """
    Execute the SQL tool using application-provided
    runtime dependencies.
    """

    question = tool_args["question"]

    with open("schema.txt", "r") as f:
        schema = f.read()


    memory_context = await get_memory_context(
        app_context.current_user["sub"]
    )

    result = await run_sql_workflow(
        question,
        schema,
        memory_context,
        app_context.db_pool
    )

    return result

async def execute_email_tool(
    tool_args: dict,
    app_context: ApplicationContext
):

    raise RuntimeError("Test email service failure")

"""async def execute_email_tool(
    tool_args: dict,
    app_context: ApplicationContext
):
    """
    Execute the email tool.

    Currently this is a mock email implementation.
    """

    result = await email_tool.ainvoke({
        "recipient": tool_args["recipient"],
        "subject": tool_args["subject"],
        "body": tool_args["body"]
    })

    return result"""
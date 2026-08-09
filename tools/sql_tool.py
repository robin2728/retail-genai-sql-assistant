from services.sql_service import run_sql_workflow
from langchain_core.tools import tool
from memory.memory_service import *

def load_schema():

    with open("schema.txt", "r") as f:
        return f.read()


from langchain_core.tools import tool


@tool
async def sql_tool(
    question: str
):
    """
    Use this tool when the user asks questions that require
    retrieving, aggregating, filtering, or analyzing retail
    database data.

    Examples:
    - Total sales this month
    - Revenue by category
    - Top customers
    - Number of orders yesterday
    """

    return {
        "question": question
    }
from langchain_openai import ChatOpenAI
from tools.sql_tool import sql_tool
import os
from dotenv import load_dotenv
load_dotenv()
value = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

llm_with_tools = llm.bind_tools([
    sql_tool
])

from langchain_core.messages import HumanMessage

async def ask_agent(question: str):

    response = await llm_with_tools.ainvoke([
        HumanMessage(content=question)
    ])

    print("Content:", response.content)

    print("Tool Calls:", response.tool_calls)
    tool_call = response.tool_calls[0]

    print(tool_call)
    print(tool_call["name"])

    print(tool_call["args"])

    return response


import asyncio

if __name__ == "__main__":

    asyncio.run(
        ask_agent(
            "Country with the highest revenue"
        )
    )
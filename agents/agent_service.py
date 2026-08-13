from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)

from context.app_context import ApplicationContext

from agents.tool_registry import (
    get_llm_tools,
    get_tool_executor,
)


# ============================================================
# LLM
# ============================================================

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


# ============================================================
# Bind tools dynamically from Tool Registry
# ============================================================

llm_with_tools = llm.bind_tools(
    get_llm_tools()
)


# ============================================================
# Generic Tool Execution
# ============================================================

async def execute_tool(
    tool_name: str,
    tool_args: dict,
    app_context: ApplicationContext
):
    """
    Generic runtime tool executor.

    The LLM provides:
        tool_name
        tool_args

    The application provides:
        app_context

    The Tool Registry determines which
    Python executor should actually run.
    """

    # --------------------------------------------------------
    # Find the executor for this tool
    # --------------------------------------------------------

    executor = get_tool_executor(tool_name)


    # --------------------------------------------------------
    # Execute the tool
    # --------------------------------------------------------

    return await executor(
        tool_args,
        app_context
    )


# ============================================================
# Agent
# ============================================================

async def ask_agent(
    question: str,
    app_context: ApplicationContext
):

    # --------------------------------------------------------
    # Retrieve previous conversation
    # --------------------------------------------------------

    from memory.memory_service import get_memory_context

    memory_context = await get_memory_context(
        app_context.current_user["sub"]
    )


    # --------------------------------------------------------
    # Initial conversation
    # --------------------------------------------------------

    messages = [
        HumanMessage(
            content=f"""
                    Previous conversation:
                    {memory_context}

                    Current user question:
                    {question}"""
        )
    ]


    # ========================================================
    # Agent Loop
    # ========================================================

    while True:

        # ----------------------------------------------------
        # Ask LLM what to do
        # ----------------------------------------------------

        response = await llm_with_tools.ainvoke(
            messages
        )


        # ----------------------------------------------------
        # Debugging
        # ----------------------------------------------------

        print("\n========== LLM RESPONSE ==========")
        print("Content:", response.content)
        print("Tool Calls:", response.tool_calls)


        # ----------------------------------------------------
        # No tool required
        # ----------------------------------------------------

        if not response.tool_calls:

            print("\n========== FINAL ANSWER ==========")
            print(response.content)

            return response


        # ----------------------------------------------------
        # Add LLM response to conversation
        # ----------------------------------------------------

        messages.append(response)


        # ----------------------------------------------------
        # Execute each requested tool
        # ----------------------------------------------------

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]


            print("\n========== TOOL CALL ==========")
            print("Tool:", tool_name)
            print("Arguments:", tool_args)


            # ------------------------------------------------
            # Execute through Tool Registry
            # ------------------------------------------------

            tool_result = await execute_tool(
                tool_name=tool_name,
                tool_args=tool_args,
                app_context=app_context
            )


            print("\n========== TOOL RESULT ==========")
            print(tool_result)


            # ------------------------------------------------
            # Give result back to LLM
            # ------------------------------------------------

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call_id
                )
            )
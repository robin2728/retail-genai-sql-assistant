from tools.sql_tool import sql_tool
from tools.email_tool import email_tool

from agents.tool_executors import (
    execute_sql_tool,
    execute_email_tool,
)


TOOL_REGISTRY = {
    "sql_tool": {
        "tool": sql_tool,
        "executor": execute_sql_tool,
    },

    "email_tool": {
        "tool": email_tool,
        "executor": execute_email_tool,
    },
}

def get_llm_tools():
    return [
        config["tool"]
        for config in TOOL_REGISTRY.values()
    ]


def get_tool_executor(tool_name: str):
    config = TOOL_REGISTRY.get(tool_name)

    if config is None:
        raise ValueError(
            f"No tool registered: {tool_name}"
        )

    return config["executor"]
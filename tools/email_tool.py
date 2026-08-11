from langchain_core.tools import tool


@tool
async def email_tool(
    recipient: str,
    subject: str,
    body: str
):
    """
    Use this tool when the user explicitly asks
    to send information by email.
    """

    return {
        "recipient": recipient,
        "subject": subject,
        "body": body
    }
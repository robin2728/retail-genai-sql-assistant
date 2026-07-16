from memory.conversation_memory import (
    get_conversation,
    get_summary,
    format_conversation
)

async def get_memory_context(
    user_id: str
) -> str:

    summary = await get_summary(user_id)

    conversation = await get_conversation(user_id)

    recent_messages = format_conversation(
        conversation
    )

    memory_context = ""

    if summary:

        memory_context += (
            "Conversation Summary:\n"
            f"{summary}\n\n"
        )

    memory_context += (
        "Recent Conversation:\n"
        f"{recent_messages}"
    )

    return memory_context
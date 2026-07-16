from memory.conversation_memory import (
    get_conversation,
    format_conversation
)


# ==========================================
# MEMORY SERVICE
# ==========================================

async def get_formatted_conversation(
    user_id: str
) -> str:
    """
    Loads the user's conversation from Redis
    and returns a formatted conversation
    ready to be sent to the LLM.
    """

    conversation = await get_conversation(user_id)

    return format_conversation(conversation)
import json

from cache.redis_client import redis_client

from utils.logger import log_event


# ==========================================
# GET COMPLETE CONVERSATION
# ==========================================

async def get_conversation(user_id: str):

    """
    Reads the user's conversation history
    from Redis.

    Returns:
        list[dict]
    """

    key = f"chat:{user_id}"

    conversation = await redis_client.get(key)

    if conversation:

        return json.loads(conversation)

    return []


# ==========================================
# SAVE COMPLETE CONVERSATION
# ==========================================

async def save_conversation(
    user_id: str,
    conversation: list
):

    """
    Saves the complete conversation
    back into Redis.
    """

    key = f"chat:{user_id}"

    await redis_client.set(

        key,

        json.dumps(conversation),

        ex=86400

    )

    log_event(

        event="conversation_saved",

        user=user_id,

        messages=len(conversation)

    )


# ==========================================
# APPEND NEW MESSAGE
# ==========================================

async def append_message(

    user_id: str,

    role: str,

    content: str

):

    """
    Adds a new message
    to the conversation history.
    """

    conversation = await get_conversation(

        user_id

    )

    conversation.append(

        {

            "role": role,

            "content": content

        }

    )

    await save_conversation(

        user_id,

        conversation

    )

# ==========================================
# FORMAT CONVERSATION FOR LLM
# ==========================================

def format_conversation(
    conversation: list,
    max_messages: int = 10
) -> str:
    """
    Converts conversation history into
    a readable text format for the LLM.

    Example:

    User: Hi
    Assistant: Hello
    User: What is revenue?
    """

    if not conversation:
        return "This is the beginning of the conversation."
    
    conversation = conversation[-max_messages:]

    formatted_conversation = ""

    for message in conversation:

        role = message.get(
            "role",
            "Unknown"
        ).capitalize()

        content = message.get(
            "content",
            ""
        )

        formatted_conversation += (
            f"{role}: {content}\n"
        )

    return formatted_conversation



# ==========================================
# GET CONVERSATION SUMMARY
# ==========================================

async def get_summary(
    user_id: str
) -> str:

    key = f"summary:{user_id}"

    summary = await redis_client.get(key)

    if summary:

        return summary

    return ""


# ==========================================
# SAVE CONVERSATION SUMMARY
# ==========================================

async def save_summary(
    user_id: str,
    summary: str
):

    key = f"summary:{user_id}"

    await redis_client.set(
        key,
        summary,
        ex=86400
    )

    log_event(
        event="summary_saved",
        user=user_id
    )


# ==========================================
# TRIM CONVERSATION
# ==========================================

async def trim_conversation(
    user_id: str,
    keep_last: int = 10
):

    conversation = await get_conversation(user_id)

    conversation = conversation[-keep_last:]

    await save_conversation(
        user_id,
        conversation
    )

    log_event(
        event="conversation_trimmed",
        user=user_id,
        remaining_messages=len(conversation)
    )
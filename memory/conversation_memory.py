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
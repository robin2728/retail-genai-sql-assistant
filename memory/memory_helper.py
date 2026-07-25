from memory.conversation_memory import (
    append_message,
    get_conversation,
    get_summary,
    save_summary,
    trim_conversation
)

from services.summary_service import generate_summary

SUMMARY_THRESHOLD = 30
RECENT_MESSAGES = 10


async def update_memory(
    user_id: str,
    question: str,
    answer: str
):
    """
    Updates conversation memory.

    Steps:
    1. Save user message
    2. Save assistant response
    3. Check if conversation exceeds threshold
    4. Summarize older messages
    5. Save updated summary
    6. Trim conversation
    """

    # =====================================
    # SAVE USER MESSAGE
    # =====================================

    await append_message(
        user_id,
        "user",
        question
    )

    # =====================================
    # SAVE ASSISTANT MESSAGE
    # =====================================

    await append_message(
        user_id,
        "assistant",
        answer
    )

    # =====================================
    # LOAD CONVERSATION
    # =====================================

    conversation = await get_conversation(
        user_id
    )

    # =====================================
    # CHECK SUMMARY THRESHOLD
    # =====================================

    if len(conversation) < SUMMARY_THRESHOLD:
        return

    # =====================================
    # SUMMARIZE OLD MESSAGES
    # =====================================

    old_conversation = conversation[:-RECENT_MESSAGES]

    new_summary = await generate_summary(
        old_conversation
    )

    # =====================================
    # LOAD EXISTING SUMMARY
    # =====================================

    existing_summary = await get_summary(
        user_id
    )

    if existing_summary:

        final_summary = (
            existing_summary
            + "\n\n"
            + new_summary
        )

    else:

        final_summary = new_summary

    # =====================================
    # SAVE SUMMARY
    # =====================================

    await save_summary(
        user_id,
        final_summary
    )

    # =====================================
    # TRIM CONVERSATION
    # =====================================

    await trim_conversation(
        user_id,
        keep_last=RECENT_MESSAGES
    )
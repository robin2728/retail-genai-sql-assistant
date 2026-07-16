from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from memory.conversation_memory import (
    format_conversation
)

llm_summary = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

prompt = ChatPromptTemplate.from_template(
    """
You are an expert AI conversation summarizer.

Summarize the following conversation.

Rules:

- Keep only important information.
- Remove greetings and small talk.
- Preserve user preferences.
- Preserve important business context.
- Preserve important technical discussions.
- Keep the summary under 200 words.
- Return ONLY the summary.

Conversation:

{conversation}
"""
)

chain = prompt | llm_summary | StrOutputParser()

async def generate_summary(conversation: list) -> str:

    conversation_text = format_conversation(
        conversation
    )

    summary = await chain.ainvoke(
        {
            "conversation": conversation_text
        }
    )

    return summary.strip()
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm_chat = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5
)

prompt = ChatPromptTemplate.from_template(
"""
You are a friendly AI Assistant.

Use the previous conversation if it helps answer the question.

Conversation:

{conversation}

Current Question:

{question}

Provide a helpful response.
"""
)

chain = prompt | llm_chat | StrOutputParser()

async def generate_chat_response(
    question: str,
    conversation: str):
    response = await chain.ainvoke(
    {
        "conversation": conversation,
        "question": question
    })
    return response.strip()
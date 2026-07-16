from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from memory.conversation_memory import (
    format_conversation
)

llm_insight = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5
)

prompt = ChatPromptTemplate.from_template(
    """
        You are an expert Retail Data Analyst.

        Conversation History:

        {conversation}

        Current User Question:

        {question}

        SQL Result:

        {result}

        Generate a clear business insight.
    """
)

chain = prompt | llm_insight | StrOutputParser()

async def generate_insight(question,result,conversation):

    return await chain.ainvoke({
        "conversation": conversation,
        "question": question,
        "result": result
    })
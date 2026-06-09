from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm_insight = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5
)

prompt = ChatPromptTemplate.from_template(
    """
    Generate business insights.

    Question:
    {question}

    Answer:
    {answer}
    """
)

chain = prompt | llm_insight | StrOutputParser()

async def generate_insight(
    question,
    answer
):

    return await chain.ainvoke({
        "question": question,
        "answer": answer
    })
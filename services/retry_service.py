from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm_retry = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

prompt = ChatPromptTemplate.from_template(
    """
    Fix SQL query based on error.

    Return ONLY corrected SQL.

    Schema:
    {schema}

    Question:
    {question}

    Old SQL:
    {old_sql}

    Error:
    {error}
    """
)

chain = prompt | llm_retry | StrOutputParser()

async def retry_sql(
    schema,
    question,
    old_sql,
    error
):

    return await chain.ainvoke({
        "schema": schema,
        "question": question,
        "old_sql": old_sql,
        "error": error
    })
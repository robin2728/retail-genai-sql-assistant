from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm_sql = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a Retail Data Analyst.

        Return ONLY SQL query.

        Rules:
        - PostgreSQL syntax only
        - No SELECT *
        - Use only schema columns
        - No hallucination
        - Return ONLY the SQL query.
        - Do not include markdown.
        - Do not include explanations.
        - Do not wrap the query in ```sql blocks.
        - Use double quotes for table and column names

        Schema:
        {schema}
        """
    ),
    ("human", "{question}")
])

chain = prompt | llm_sql | StrOutputParser()

async def generate_sql(question: str, schema: str):

    output = await chain.ainvoke({
        "schema": schema,
        "question": question
    })

    return output.strip()
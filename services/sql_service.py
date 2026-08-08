from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from memory.conversation_memory import format_conversation

from db.database import execute_sql
from validators.sql_validator import validate_sql
from services.retry_service import retry_sql
from services.insight_service import generate_insight
from models.schemas import SQLWorkflowResult


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
            - Use double quotes for table and column names.

            Database Schema:
            {schema}

            Previous Conversation:
            {conversation}
            """
                ),
                (
                    "human",
                    """Current User Question:{question}""")
])

chain = prompt | llm_sql | StrOutputParser()

async def generate_sql(question: str, schema: str, memory_context):


    output = await chain.ainvoke({
        "schema": schema,
        "conversation": memory_context,
        "question": question})

    return output.strip()


async def execute_database_query(
    sql_query: str,
    db_pool
):

    result = await execute_sql(
    sql_query,
    db_pool
)

    return result
    

async def run_sql_workflow(
    question,
    schema,
    memory_context,
    db_pool
):
    """
    Complete SQL execution pipeline.

    This function will eventually:
    1. Generate SQL
    2. Validate SQL
    3. Execute query
    4. Retry if needed
    5. Generate insights
    6. Return DatabaseResponse
    """

    sql_query = await generate_sql(
    question,
    schema,
    memory_context)

    if not validate_sql(sql_query):
        raise Exception("Unsafe SQL generated")

    try:

        result = await execute_database_query(sql_query,db_pool)

    except Exception as e:

        corrected_sql = await retry_sql(
            schema,
            question,
            sql_query,
            str(e)
        )

        if not validate_sql(corrected_sql):
            raise Exception("Unsafe retry SQL")

        result = await execute_database_query(
            corrected_sql,
            db_pool)

        sql_query = corrected_sql

    insight = await generate_insight(
        question,
        str(result),
        memory_context)
    
    return SQLWorkflowResult(
        sql=sql_query,
        result=result,
        insight=insight
    )

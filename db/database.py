import asyncpg
from config import DB_CONFIG

pool = None

async def create_db_pool():

    global pool

    pool = await asyncpg.create_pool(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
        min_size=5,
        max_size=20
    )

async def execute_sql(sql_query: str):

    async with pool.acquire() as connection:

        rows = await connection.fetch(sql_query)

        return [dict(row) for row in rows]
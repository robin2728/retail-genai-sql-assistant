from fastapi import APIRouter, HTTPException
import time

from models.schemas import (
    QuestionRequest,
    AskResponse
)

from services.sql_service import generate_sql
from services.retry_service import retry_sql
from services.insight_service import generate_insight

from validators.sql_validator import validate_sql

from db.database import execute_sql

from cache.cache_service import (
    generate_cache_key,
    get_cache,
    set_cache
)

from cache.rate_limiter import (
    check_rate_limit
)

from utils.logger import logger

router = APIRouter()

def load_schema():

    with open("schema.txt", "r") as f:
        return f.read()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: QuestionRequest):

    total_start = time.time()

    allowed = await check_rate_limit(
        request.user_id
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    schema = load_schema()

    sql_query = await generate_sql(
        request.question,
        schema
    )
    logger.info(f"Generated SQL: {sql_query}")
    if not validate_sql(sql_query):
        raise HTTPException(
            status_code=400,
            detail="Unsafe SQL generated"
        )

    cache_key = generate_cache_key(sql_query)

    cached = await get_cache(cache_key)

    if cached:

        logger.info("Cache HIT")

        return cached

    logger.info("Cache MISS")

    result = None

    try:

        result = await execute_sql(sql_query)

    except Exception as e:
        logger.error(f"SQL Execution Error: {e}")
        corrected_sql = await retry_sql(
            schema,
            request.question,
            sql_query,
            str(e)
        )

        if not validate_sql(corrected_sql):
            raise HTTPException(
                status_code=400,
                detail="Unsafe retry SQL"
            )

        result = await execute_sql(corrected_sql)

        sql_query = corrected_sql

    insight = await generate_insight(
        request.question,
        str(result)
    )

    response = AskResponse(
        question=request.question,
        sql_generated=sql_query,
        insight=insight,
        data=result
    )

    await set_cache(
        cache_key,
        response.model_dump()
    )

    total_time = time.time() - total_start

    logger.info(
        f"Total Request Time: {total_time:.4f}s"
    )

    return response
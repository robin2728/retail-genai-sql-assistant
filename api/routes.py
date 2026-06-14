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


@router.get("/")
async def home():
    return {
        "status": "healthy",
        "application": "Retail GenAI SQL Assistant"
    }


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: QuestionRequest):

    request_start = time.perf_counter()

    # =====================================
    # RATE LIMIT TIMING
    # =====================================

    rate_start = time.perf_counter()

    allowed = await check_rate_limit(
        request.user_id
    )

    rate_time = (
        time.perf_counter() - rate_start
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    # =====================================
    # SCHEMA LOAD TIMING
    # =====================================

    schema_start = time.perf_counter()

    schema = load_schema()

    schema_time = (
        time.perf_counter() - schema_start
    )

    # =====================================
    # SQL GENERATION TIMING
    # =====================================

    sql_start = time.perf_counter()

    sql_query = await generate_sql(
        request.question,
        schema
    )

    sql_time = (
        time.perf_counter() - sql_start
    )

    logger.info(
        f"Generated SQL: {sql_query}"
    )

    if not validate_sql(sql_query):
        raise HTTPException(
            status_code=400,
            detail="Unsafe SQL generated"
        )

    # =====================================
    # CACHE LOOKUP TIMING
    # =====================================

    cache_key = generate_cache_key(sql_query)

    cache_start = time.perf_counter()

    cached = await get_cache(cache_key)

    cache_lookup_time = (
        time.perf_counter() - cache_start
    )

    if cached:

        total_time = (
            time.perf_counter() - request_start
        )

        logger.info(
            f"""
==============================
CACHE HIT
==============================

Question:
{request.question}

Rate Limit Time : {rate_time:.4f}s
Schema Time     : {schema_time:.4f}s
SQL Time        : {sql_time:.4f}s
Cache Lookup    : {cache_lookup_time:.4f}s

TOTAL TIME      : {total_time:.4f}s

==============================
"""
        )

        return cached

    logger.info("Cache MISS")

    # =====================================
    # DATABASE TIMING
    # =====================================

    db_time = 0
    retry_time = 0

    try:

        db_start = time.perf_counter()

        result = await execute_sql(
            sql_query
        )

        db_time = (
            time.perf_counter() - db_start
        )

    except Exception as e:

        logger.error(
            f"SQL Execution Error: {e}"
        )

        # ============================
        # RETRY TIMING
        # ============================

        retry_start = time.perf_counter()

        corrected_sql = await retry_sql(
            schema,
            request.question,
            sql_query,
            str(e)
        )

        retry_time = (
            time.perf_counter() - retry_start
        )

        if not validate_sql(corrected_sql):
            raise HTTPException(
                status_code=400,
                detail="Unsafe retry SQL"
            )

        db_start = time.perf_counter()

        result = await execute_sql(
            corrected_sql
        )

        db_time += (
            time.perf_counter() - db_start
        )

        sql_query = corrected_sql

    # =====================================
    # INSIGHT GENERATION TIMING
    # =====================================

    insight_start = time.perf_counter()

    insight = await generate_insight(
        request.question,
        str(result)
    )

    insight_time = (
        time.perf_counter() - insight_start
    )

    # =====================================
    # RESPONSE BUILD
    # =====================================

    response = AskResponse(
        question=request.question,
        sql_generated=sql_query,
        insight=insight,
        data=result
    )

    # =====================================
    # CACHE SAVE TIMING
    # =====================================

    cache_save_start = time.perf_counter()

    await set_cache(
        cache_key,
        response.model_dump()
    )

    cache_save_time = (
        time.perf_counter() - cache_save_start
    )

    # =====================================
    # TOTAL REQUEST TIME
    # =====================================

    total_time = (
        time.perf_counter() - request_start
    )

    logger.info(
        f"""
==============================
LATENCY BREAKDOWN
==============================

Question:
{request.question}

Rate Limit Time : {rate_time:.4f}s
Schema Time     : {schema_time:.4f}s
SQL Time        : {sql_time:.4f}s
Cache Lookup    : {cache_lookup_time:.4f}s
DB Time         : {db_time:.4f}s
Retry Time      : {retry_time:.4f}s
Insight Time    : {insight_time:.4f}s
Cache Save Time : {cache_save_time:.4f}s

TOTAL TIME      : {total_time:.4f}s

==============================
"""
    )

    return response
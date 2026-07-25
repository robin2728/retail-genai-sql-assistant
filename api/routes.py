from fastapi import APIRouter, HTTPException
import time
from fastapi import Depends
from auth.auth_dependency import authenticate_user
from typing import Union
from models.schemas import *


from services.summary_service import (
    generate_summary
)

from services.router_service import *
from services.chat_service import *

from memory.conversation_memory import *
from memory.memory_service import *
from memory.memory_helper import update_memory

from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_handler import create_access_token

from models.schemas import TokenResponse

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

from utils.logger import logger, log_event

router = APIRouter()
# =====================================
# TEMPORARY USER (Learning Purpose)
# =====================================

HARDCODED_USER = {
    "username": "robin",
    "password": "password123"
}

# =====================================
# MEMORY CONFIGURATION
# =====================================

SUMMARY_THRESHOLD = 30
RECENT_MESSAGES = 10

def load_schema():

    with open("schema.txt", "r") as f:
        return f.read()


@router.get("/")
async def home():
    return {
        "status": "healthy",
        "application": "Retail GenAI SQL Assistant"
    }


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    # =====================================
    # VERIFY USERNAME & PASSWORD
    # =====================================

    if (
        form_data.username != HARDCODED_USER["username"]
        or
        form_data.password != HARDCODED_USER["password"]
    ):

        log_event(
            event="login_failed",
            username=form_data.username
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # =====================================
    # CREATE JWT TOKEN
    # =====================================

    access_token = create_access_token(
        data={
            "sub": form_data.username
        }
    )

    log_event(
        event="login_success",
        username=form_data.username
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/classify")
async def classify(request: QuestionRequest):

    intent = await classify_intent(
        request.question
    )

    return {
        "intent": intent
    }

@router.get("/generate-summary")
async def generate_summary_test():

    conversation = await get_conversation(
        "robin"
    )

    summary = await generate_summary(
        conversation
    )

    return {
        "summary": summary
    }



@router.post(
    "/ask",
    response_model=Union[
        DatabaseResponse,
        ChatResponse,
        ErrorResponse
    ]
)
async def ask_question(request: QuestionRequest,user=Depends(authenticate_user)):

    request_start = time.perf_counter()

    # =====================================
    # RATE LIMIT TIMING
    # =====================================

    rate_start = time.perf_counter()

    allowed = await check_rate_limit(
        user["sub"]
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
    # LOAD MEMORY
    # =====================================

    memory_context = await get_memory_context(
        user["sub"]
    )


    # =====================================
    # CLASSIFY USER INTENT
    # =====================================

    intent = await classify_intent(
        request.question
    )

    log_event(
        event="intent_classified",
        question=request.question,
        intent=intent
    )

        # ==================================================
    # CHAT / GENERAL PATH
    # ==================================================

    if intent in ["GENERAL", "CONVERSATION"]:

        response = await generate_chat_response(
            request.question,
            memory_context
        )
        await update_memory(
            user["sub"],
            request.question,
            response
        )
  

        return ChatResponse(
                response_type="chat",
                question=request.question,
                answer=response)


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
        schema,
        memory_context)

    sql_time = (
        time.perf_counter() - sql_start
    )

    log_event(
        event="sql_generated",
        question=request.question,
        sql=sql_query,
        sql_generation_time=round(sql_time, 4))

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

        log_event(
            event="cache_hit",
            question=request.question,
            rate_limit_time=round(rate_time, 4),
            schema_load_time=round(schema_time, 4),
            sql_generation_time=round(sql_time, 4),
            cache_lookup_time=round(cache_lookup_time, 4),
            total_time=round(total_time, 4)
        )

        return DatabaseResponse(**cached)

    log_event(
        event="cache_miss",
        question=request.question)

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

        log_event(
            event="sql_execution_error",
            question=request.question,
            error=str(e))

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
        str(result),
        memory_context
    )

    insight_time = (
        time.perf_counter() - insight_start
    )

    # =====================================
    # RESPONSE BUILD
    # =====================================

    response = DatabaseResponse(
        response_type="database",
        question=request.question,
        sql_generated=sql_query,
        insight=insight,
        data=result)

        # =====================================
    # SAVE CONVERSATION MEMORY
    # =====================================

    await update_memory(
        user["sub"],
        request.question,
        insight
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

    log_event(
        event="request_completed",
        question=request.question,
        rate_limit_time=round(rate_time, 4),
        schema_load_time=round(schema_time, 4),
        sql_generation_time=round(sql_time, 4),
        cache_lookup_time=round(cache_lookup_time, 4),
        db_execution_time=round(db_time, 4),
        retry_time=round(retry_time, 4),
        insight_generation_time=round(insight_time, 4),
        cache_save_time=round(cache_save_time, 4),
        total_time=round(total_time, 4))

    return response
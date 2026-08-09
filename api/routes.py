from fastapi import APIRouter, HTTPException , Request
import time
from fastapi import Depends
from auth.auth_dependency import authenticate_user
from typing import Union
from models.schemas import *
from agents.agent_service import ask_agent
from context.context_builder import ContextBuilder


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

from services.sql_service import run_sql_workflow


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



@router.post("/ask")
async def ask_question(
    request: QuestionRequest,
    http_request: Request,
    user=Depends(authenticate_user)):

    # =====================================
    # 1. Build Application Context
    # =====================================

    app_context = ContextBuilder.build_application_context(
        http_request.app,
        user
    )


    # =====================================
    # 2. Send question to Agent
    # =====================================

    response = await ask_agent(
        request.question,
        app_context
    )


    # =====================================
    # 3. Return Agent response
    # =====================================

    return {
        "question": request.question,
        "answer": response.content
    }
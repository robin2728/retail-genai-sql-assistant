from typing import List, Any, Literal
from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

class DatabaseResponse(BaseModel):
    response_type: Literal["database"]
    question: str
    sql_generated: str
    data: list
    insight: str

class ChatResponse(BaseModel):
    response_type: Literal["chat"]
    question: str
    answer: str

class ErrorResponse(BaseModel):
    response_type: Literal["error"]
    message: str

class LoginRequest(BaseModel):

    username: str

    password: str


class TokenResponse(BaseModel):

    access_token: str

    token_type: str


class SQLWorkflowResult(BaseModel):
    sql: str
    result: Any
    insight: str
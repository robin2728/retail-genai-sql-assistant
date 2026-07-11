from pydantic import BaseModel
from typing import List, Any

class QuestionRequest(BaseModel):
    user_id: str
    question: str

class AskResponse(BaseModel):
    question: str
    sql_generated: str
    insight: str
    data: List[Any]

class LoginRequest(BaseModel):

    username: str

    password: str


class TokenResponse(BaseModel):

    access_token: str

    token_type: str
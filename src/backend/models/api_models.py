from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

class UserData(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserRequest(BaseModel):
    chat_id: Optional[str] = None
    request: str

class ModelResponse(BaseModel):
    user_id: int
    chat_id: str
    response: str
    streamed_response: Optional[bool] = False
    is_last: Optional[bool] = False

class ChatMessage(BaseModel):   # convert chat history object to JSON for fronted request
    role: Literal["ai", "human"]
    content: str
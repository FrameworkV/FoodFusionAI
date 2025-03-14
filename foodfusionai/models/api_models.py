from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

class UserData(BaseModel):
    username: str
    password: str
    email: EmailStr

class UpdateUserData(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None

class UserRequest(BaseModel):
    chat_id: Optional[str] = None
    model: Literal["g-01-base", "g-01-reasoning"]
    request: str

class ModelResponse(BaseModel):
    user_id: int
    chat_id: str
    model: Literal["g-01-base", "g-01-reasoning"]
    response: str
    streamed_response: Optional[bool] = False
    is_last: Optional[bool] = False

class ChatMessage(BaseModel):   # convert chat history object to JSON for fronted request
    role: Literal["ai", "human"]
    content: str
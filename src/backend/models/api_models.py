from typing import Optional
from pydantic import BaseModel, EmailStr

class UserData(BaseModel):
    username: str
    password: str
    email: EmailStr

class ModelResponse(BaseModel):
    user_id: int
    chat_id: str
    response: str
    is_last: Optional[bool] = False
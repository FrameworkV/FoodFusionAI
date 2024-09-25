from pydantic import BaseModel
from typing import Optional

class UserModel(BaseModel):
    user_id: Optional[int] = None
    username: str
    password: str

class UserRequestModel(BaseModel):
    request_id: int
    request: str
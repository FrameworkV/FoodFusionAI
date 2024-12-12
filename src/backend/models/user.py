from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class User(SQLModel, table=True):
    id: Optional[int] = Field(index=True, default=None, primary_key=True)  # automatically assign user id
    username: str = Field(index=True, unique=True)
    password: str
    email: EmailStr = Field(index=True, unique=True)
    reset_code: Optional[int] = Field(default=None)
    reset_code_expiration: Optional[datetime] = Field(default=None)
    is_verified: bool = Field(default=False)
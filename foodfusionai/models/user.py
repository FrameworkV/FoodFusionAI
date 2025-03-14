from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class User(SQLModel, table=True):
    id: Optional[int] = Field(index=True, default=None, primary_key=True)  # automatically assign user id
    username: str = Field(index=True, unique=True, max_length=50)
    password: str = Field(max_length=255)
    email: EmailStr = Field(unique=True, max_length=255)
    subscription_type: str = Field(max_length=30)
    reset_code: Optional[int] = Field(default=None)
    reset_code_expiration: Optional[datetime] = Field(default=None)
    is_verified: bool = Field(default=False)
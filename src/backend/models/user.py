from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

class User(SQLModel, table=True):  # User for the database table
    id: Optional[int] = Field(index=True, default=None, primary_key=True)  # automatically assign user id
    username: str = Field(index=True, unique=True)
    password: str
    email: EmailStr = Field(index=True, unique=True)
    is_verified: bool = False

    groceries: List["Item"] = Relationship(back_populates="user")


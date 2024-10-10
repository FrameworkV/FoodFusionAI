from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

class Roles(str, Enum):
    user = "user"
    admin = "admin"

class User(SQLModel, table=True):  # User for the database table
    id: Optional[int] = Field(default=None, primary_key=True)  # automatically assign user id
    username: str = Field(index=True, unique=True)
    hashed_password: str
    email: EmailStr
    is_verified: bool = False

    groceries: List["Grocery"] = Relationship(back_populates="user")


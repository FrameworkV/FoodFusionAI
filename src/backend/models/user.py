from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class Roles(str, Enum):
    user = "user"
    admin = "admin"


class BaseUser(SQLModel):
    role: Roles


class DBUser(SQLModel, table=True):  # User for the database table
    id: Optional[int] = Field(default=None, primary_key=True)  # automatically assign user id
    username: str = Field(index=True, unique=True)
    hashed_password: str

    groceries: List["Grocery"] = Relationship(back_populates="user")


class User(BaseUser):  # User from the API input
    password: str

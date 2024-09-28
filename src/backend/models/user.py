from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field

class Roles(str, Enum):
    user = "user"
    admin = "admin"

class BaseUser(SQLModel):
    username: str = Field(index=True, unique=True)
    role: Roles

class DBUser(BaseUser, table=True):     # User for the database table 
    id: Optional[int] = Field(default=None, primary_key=True)   # automatically assign user id
    hashed_password: str

class User(BaseUser):       # User from the API input
    password: str
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Grocery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Grocery name

    # Foreign key to link the grocery to the user
    user_id: Optional[int] = Field(default=None, foreign_key="dbuser.id")

    # Many-to-One relationship: many groceries belong to one user
    user: "DBUser" = Relationship(back_populates="groceries")

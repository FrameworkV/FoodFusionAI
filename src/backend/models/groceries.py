from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    quantity: int
    weight: Optional[float]
    category: Optional[str]
    expiration_date: Optional[str]

    # Foreign key to link the grocery to the user
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Many-to-One relationship: many groceries belong to one user
    user: "User" = Relationship(back_populates="groceries")

class ShoppingList(SQLModel, table=True):
    id: Optional[int] = Field(index=True, default=None, primary_key=True)
    content: str
    recipe: str

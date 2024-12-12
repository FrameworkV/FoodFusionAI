from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field

class Category(str, Enum):
    Fruits = "Fruits"
    Vegetables = "Vegetables"
    Dairy = "Dairy"
    Meat = "Meat"
    Fish = "Fish"
    Bakery = "Bakery"
    Beverages = "Beverages"
    Snacks = "Snacks"
    Frozen = "Frozen"
    Canned = "Canned"
    Condiments = "Condiments"
    Spices = "Spices"
    Grains = "Grains"
    Pasta = "Pasta"
    Breakfast = "Breakfast"

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)   # auto generated
    name: str
    quantity: int
    weight_in_gram: Optional[float]
    category: Optional[Category]
    expiration_date: Optional[str]  # string to ensure easier llm processing, format should be YYYY-MM-DD
    user_id: int = Field(foreign_key="user.id")

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(index=True, default=None, primary_key=True)
    content: str
    user_id: int = Field(foreign_key="user.id")

class ShoppingList(SQLModel, table=True):
    id: Optional[int] = Field(index=True, default=None, primary_key=True)
    content: str
    user_id: int = Field(foreign_key="user.id")
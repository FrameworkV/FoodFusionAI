from enum import Enum
from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

class Category(Enum):
    FRUITS = "Fruits"
    VEGETABLES = "Vegetables"
    DAIRY = "Dairy"
    MEAT = "Meat"
    FISH = "Fish"
    BAKERY = "Bakery"
    BEVERAGES = "Beverages"
    SNACKS = "Snacks"
    FROZEN = "Frozen"
    CANNED_GOODS = "Canned Goods"
    CONDIMENTS = "Condiments"
    SPICES = "Spices"
    GRAINS = "Grains"
    PASTA = "Pasta"
    BREAKFAST = "Breakfast"
    CLEANING_SUPPLIES = "Cleaning Supplies"
    PERSONAL_CARE = "Personal Care"

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    quantity: int
    weight_in_gram: Optional[float]
    category: Optional[Category]
    expiration_date: Optional[str]  # string to ensure easier llm processing, format should be YYYY-MM-DD

    # Foreign key to link the grocery to the user
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Many-to-One relationship: many groceries belong to one user
    user: "User" = Relationship(back_populates="groceries")

class ShoppingList(SQLModel, table=True):
    id: Optional[int] = Field(index=True, default=None, primary_key=True)
    content: str
    recipe: str

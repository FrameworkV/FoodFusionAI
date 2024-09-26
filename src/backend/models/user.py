import sqlite3
from typing import List
from backend.models.groceries import Groceries

class User:
    def __init__(self, name: str, groceries: List[Groceries]):
        self.name = name
        self.groceries = groceries

    def get_name(self) -> str:
        return self.name
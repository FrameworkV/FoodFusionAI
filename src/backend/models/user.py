from typing import List
from src.backend.models.groceries import Groceries
class User:
    def __init__(self, name: str, groceries: List[Groceries]):
        self.name = name
        self.groceries = groceries

    def get_name(self) -> str:
        return self.name
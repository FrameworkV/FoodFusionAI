from sqlmodel import Session, SQLModel, create_engine
from typing import Generator
import os
from backend.models.groceries import Grocery
from backend.models.user import User

path = os.path.dirname(os.path.abspath(__file__))
SQLITE_URL = f"sqlite:///{path}/users.db"
engine = create_engine(SQLITE_URL, echo=True)


def get_session() -> Generator:
    """
    Create session to interact with the database
    """
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


create_db_and_tables()

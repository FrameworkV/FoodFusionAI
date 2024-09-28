from sqlmodel import Session, SQLModel, create_engine
from typing import Generator

SQLITE_URL = "sqlite:///src/backend/database/users.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False}, echo=True)

def get_session() -> Generator:
    """
    Create session to interact with the database
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

create_db_and_tables()
from sqlmodel import Session, SQLModel, create_engine
from langchain_community.utilities import SQLDatabase
from typing import Generator
import os
from backend.utils import config
# import all tables to create them
from backend.models.user import User
from backend.models.groceries import Item, ShoppingList
# --------------------------------

# Dev
if config['app']['status'] == "dev":
    path = os.path.dirname(os.path.abspath(__file__))
    url = f"sqlite:///{path}/users.db"
    engine = create_engine(url, echo=config['database']['echo'])
# Prod
else:
    # if used locally: download ODBC Driver 17 for SQL Server, add ip address to firewall rules on Azure
    server = config['database']['sql_database']['server']
    database = config['database']['sql_database']['database_name']
    username = config['database']['sql_database']['username']
    password = os.getenv("AZURE_SQL_DATABASE_PASSWORD")

    url = f"mssql+pyodbc://{username}:{password}@{server}.database.windows.net/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    engine = create_engine(url, echo=False)

SQLModel.metadata.create_all(engine)    # create all provided tables (if not already existent)
db = SQLDatabase.from_uri(url)          # langchain class for RAG in /llm

def get_session() -> Generator:
    """
    Create session to interact with the database
    """
    with Session(engine) as session:
        yield session
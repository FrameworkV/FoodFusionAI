from sqlmodel import Session, SQLModel, create_engine
from langchain_community.utilities import SQLDatabase
from typing import Generator
import os
from foodfusionai.utils import project_config
from foodfusionai.CONFIG import get_config
config = get_config()
# import all tables to create them
from foodfusionai.models.user import User
from foodfusionai.models.groceries import Item, ShoppingList, Recipe
# --------------------------------

# Dev
if project_config['app']['status'] == "dev":
    path = os.path.dirname(os.path.abspath(__file__))
    url = f"sqlite:///{path}/users.db"
    engine = create_engine(url, echo=project_config['database']['echo'])
# Prod
else:
    # if used locally: download ODBC Driver 17 for SQL Server, add ip address to firewall rules on Azure
    server = project_config['database']['sql_database']['server']
    database = project_config['database']['sql_database']['database_name']
    username = project_config['database']['sql_database']['username']
    password = config.azure_sql_database_password

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
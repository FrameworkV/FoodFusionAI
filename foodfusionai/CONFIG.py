from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from foodfusionai.utils import project_config

class Config(BaseSettings):
    jwt_secret_key: str
    email: str
    email_password: str
    google_api_key: str
    langchain_api_key: str
    azure_sql_database_password: str
    azure_cosmosdb_access_key: str
    redis_host: str
    redis_port: int
    redis_password: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()

AUTH_ENDPOINT = f"{project_config['api']['version']}/users/auth/login"
SUBSCRIPTION_TYPES = [  # default should be at index 0
    "standard",
    "premium"
]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.logs.loggers import create_logger
from backend.utils import config

from backend.routers.users import user_router
from backend.routers.requests import requests_router

api_logger = create_logger("api", config['logging']['api'])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"]
)

app.include_router(user_router)
app.include_router(requests_router)

@app.get("/")
async def read_root():
    return {
        "API version": config['api']['version'],
        "description": config['api']['description']
    }

if __name__ == "__main__":
    if config['app']['status'] == "dev":
        uvicorn.run(app, host=config['api']['local']['host'], port=config['api']['local']['port'])
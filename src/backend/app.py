# # allows import from different folder
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
load_dotenv(override=True)
from backend.utils import config
from backend.routers.users import user_router
from backend.routers.storage import storage_router
from backend.routers.llm import llm_router

app = FastAPI(title=config['app']['title'], version=config['api']['version'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"]
)

app.include_router(user_router)
app.include_router(storage_router)
app.include_router(llm_router)

@app.get("/")
async def read_root():
    return {
        "API version": config['api']['version'],
        "description": config['api']['description']
    }

if __name__ == "__main__":
    if config['app']['status'] == "dev":
        uvicorn.run(app, host=config['api']['local']['host'], port=config['api']['local']['port'])
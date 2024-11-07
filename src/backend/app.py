from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
load_dotenv(override=True)
import sys
sys.path.insert(0, '/Users/paul/paul_data/projects_cs/FoodFusionAI')
sys.path.insert(0, '/Users/paul/paul_data/projects_cs/FoodFusionAI/src')
print(sys.path)
from backend.utils import config
from backend.routers.users import user_router
from backend.routers.storage import storage_router
from backend.routers.llm import llm_router
from backend.routers.auth import auth_router


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

app.include_router(auth_router)

@app.get("/")
async def read_root():
    return {
        "API version": config['api']['version'],
        "description": config['api']['description']
    }

if __name__ == "__main__":
    if config['app']['status'] == "dev":
        uvicorn.run(app, host=config['api']['local']['host'], port=config['api']['local']['port'])
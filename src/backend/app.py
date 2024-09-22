from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utils import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"]
)

@app.get("/")
async def read_root():
    return {"message": "placeholder"}

if __name__ == "__main__":
    uvicorn.run(app, host=config['app']['local']['host'], port=config['app']['local']['port'])
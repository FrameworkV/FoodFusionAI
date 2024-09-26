from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from database.database import DatabaseHelper
import uvicorn
import bcrypt
from typing import Dict
from utils import config
from api_models.models import UserModel, UserRequestModel
from models.user import User
from database.database import DatabaseHelper

dh = DatabaseHelper.instance()

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
    return {
        "API version": config['api']['version'],
        "description": config['api']['description']
    }

@app.post("/create_user")
async def create_user(user: UserModel) -> Dict[str, str]:
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        dh.add_user(user.username, hashed_password)

        return {"message": f"User {user.username} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")

async def authenticate_user(user: UserModel) -> User:
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username or password missing")
    
    try:
        user_object = dh.get_user(user.username)

        if not user_object:
            raise HTTPException(status_code=404, detail="User not found")  
        
        if not dh.valid_password(user.username, user.password):                            
            raise HTTPException(status_code=403, detail="Invalid password")
        
        return user_object
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error authenticating user: {e}")
    
@app.post("/dummy_request")
async def dummy_request(user_request: UserRequestModel, user: User = Depends(authenticate_user)) -> Dict[str, str]:
    return {"message": user_request.request}

if __name__ == "__main__":
    if config['app']['status'] == "dev":
        uvicorn.run(app, host=config['api']['local']['host'], port=config['api']['local']['port'])
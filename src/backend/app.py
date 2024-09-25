from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import bcrypt
from typing import Dict
from utils import config
from api_models.models import UserModel, UserRequestModel
from database.components.user import User
from database.user import add_user, get_user, valid_password

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
        add_user(user.username, hashed_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")

    return {
        "message": f"User {user.username} created successfully",
    }

async def authenticate_user(user: UserModel) -> User:
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username or password missing")
    
    user = get_user(user.username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")  
    
    if not valid_password(user.username, user.password):                            
        raise HTTPException(status_code=403, detail="Invalid password")
    
    return user

@app.post("/dummy_request")
async def dummy_request(user_request: UserRequestModel, user: User = Depends(authenticate_user)) -> Dict[str, str]:
    return {"message": user_request.request}

if __name__ == "__main__":
    if config['app']['status'] == "dev":
        uvicorn.run(app, host=config['api']['local']['host'], port=config['api']['local']['port'])
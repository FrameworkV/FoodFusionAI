from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
import bcrypt
from typing import Dict
import logging
from backend.models.user import User
from backend.api_models.models import UserModel
from backend.database.database import DatabaseHelper

api_logger = logging.getLogger("api")

user_router = APIRouter()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")      # get login token from login endpoint

dh = DatabaseHelper.instance()

@user_router.post("/create_user")
async def create_user(user: UserModel) -> Dict[str, str]:
    api_logger.info(f"Attempt to create user: {user.username}")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        dh.add_user(user.username, hashed_password)
        api_logger.info(f"User {user.username} created successfully")

        return {"message": f"User {user.username} created successfully"}
    except Exception as e:
        api_logger.error(f"Error creating user: {user.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {user.username}, Exception: {e}")

@user_router.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    try:
        api_logger.info(f"Login attempt for username: {data.username}")
        user = dh.get_user(data.username)

        if not user:
            api_logger.warning(f"Login attempt failed: User {data.username} not found")
            raise HTTPException(status_code=404, detail=f"User {data.username} not found")

        if not dh.valid_password(data.username, data.password):
            api_logger.warning(f"Login attempt failed: Invalid password for user {data.username}")
            raise HTTPException(status_code=403, detail=f"Invalid password for user {data.username}")
        
        access_token = jwt.encode({"user": data.username}, key="secret")

        api_logger.info(f"User {data.username} logged in successfully")

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        api_logger.error(f"Error logging in user: {data.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging in user: {data.username}, Exception: {e}")

async def get_user(token: str = Depends(oauth2_schema)) -> User:
    try:
        username = jwt.decode(token, key="secret")["user"]      # dictionary with the username

        return dh.get_user(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {e}")
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict
from backend.logs.logger_config import logger
from sqlmodel import Session
from backend.models.user import User
from backend.database import database_setup, crud, auth
from backend.api_models.models import UserModel

user_router = APIRouter()

@user_router.post("/create_user")
async def create_user(user: User, db: Session = Depends(database_setup.get_session)) -> Dict[str, str]:
    logger.info(f"Attempt to create user: {user.username}")

    try:
        crud.create_user(db, user)
        logger.info(f"User {user.username} created successfully")

        return {"message": f"User {user.username} created successfully"}
    except Exception as e:
        logger.error(f"Error creating user {user.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user {user.username}, Exception: {e}")

@user_router.post("/login")
async def login(db: Session = Depends(database_setup.get_session), data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    try:
        logger.info(f"Login attempt for username: {data.username}")
        db_user = crud.get_user(db, data.username)

        if not db_user:
            logger.warning(f"User {data.username} not found")
            raise HTTPException(status_code=404, detail=f"User {data.username} not found")

        if not auth.valid_password(data.password, db_user.hashed_password):
            logger.warning(f"Invalid password for user {data.username}")
            raise HTTPException(status_code=401, detail=f"Invalid password for user {data.username}")

        access_token = auth.create_access_token(db_user)

        logger.info(f"User {data.username} logged in successfully")

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error logging in user {data.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging in user {data.username}, Exception: {e}")

async def get_user(db: Session = Depends(database_setup.get_session), token: str = Depends(auth.oauth2_schema)) -> User:
    """
    Another dependency injection of the oauth2_schema dependency injection to get access to the user's data
    """
    try:
        username = auth.decode_access_token(token)["sub"]
        print(username)

        return crud.get_user(db, username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {e}")
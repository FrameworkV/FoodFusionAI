from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from typing import Dict
from backend.logs.logger_config import logger
from sqlmodel import Session
from backend.models.user import User
from backend.database import database_setup, crud, auth
from backend.verification_mail import registration_confirmation, send_mail

user_router = APIRouter(tags=["Users"])

@user_router.post("/users/create_user")
async def create_user(user: User, db: Session = Depends(database_setup.get_session)) -> Dict[str, str]:
    logger.info(f"Attempt to create user: {user.username}")

    try:
        crud.create_user(db, user)
        logger.info(f"User {user.username} created successfully")

        token = auth.create_access_token(user)
        logger.info(f"Attempt to send verification email to user {user.username}")
        send_mail(user.email, user.username, token)
        logger.info(f"Verification email successfully sent to user {user.username}")

        return {"message": f"User {user.username} created successfully"}
    except Exception as e:
        logger.warning(f"Error creating user {user.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user {user.username}, Exception: {e}")

@user_router.post("/users/login")
async def login(db: Session = Depends(database_setup.get_session), data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    try:
        logger.info(f"Login attempt for user: {data.username}")
        user = crud.get_user(db, data.username)

        if not user:
            logger.warning(f"User {data.username} not found")
            raise HTTPException(status_code=404, detail=f"User {data.username} not found")

        if not auth.valid_password(data.password, user.password):
            logger.warning(f"Invalid password for user {data.username}")
            raise HTTPException(status_code=401, detail=f"Invalid password for user {data.username}")

        access_token = auth.create_access_token(user)

        logger.info(f"User {data.username} logged in successfully")

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.warning(f"Error logging in user {data.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging in user {data.username}, Exception: {e}")

@user_router.get("/users/verify/{token}", response_class=HTMLResponse)
async def verify_user(token: str, db: Session = Depends(database_setup.get_session)) -> HTMLResponse:
    logger.info(f"Attempt to verify user with token {token} via email")

    try:
        username = auth.decode_access_token(token)["sub"]

        logger.info(f"User {username} found")

        user = crud.get_user(db, username)
        user.is_verified = True
        db.commit()
        db.refresh(user)

        logger.info(f"User {username} verified successfully")

        return registration_confirmation(username)
    except Exception as e:
        logger.warning(f"Error verifying user {username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error verifying user {username}, Exception: {e}")

async def _get_user(db: Session = Depends(database_setup.get_session), token: str = Depends(auth.oauth2_schema)) -> User:
    """
    Another dependency injection of the oauth2_schema dependency injection to get access to the user's data
    """
    logger.info(f"Attempt to get user from token: {token}")

    try:
        username = auth.decode_access_token(token)["sub"]

        logger.info(f"User {username} found")

        return crud.get_user(db, username)
    except Exception as e:
        logger.warning(f"Error getting user, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user: {e}")

@user_router.put("/users/update_user")
async def update_user(updated_user: User, db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"Attempt to update user: {user.username}")

    try:
        crud.update_user(db, user, updated_user)
        logger.info(f"User {user.username} updated successfully")

        return {"message": f"User {user.username} updated successfully"}
    except Exception as e:
        logger.warning(f"Error updating user {user.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating user {user.username}, Exception: {e}")
    
@user_router.delete("/users/delete_user")
async def delete_user(db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"Attempt to delete user: {user.username}")

    try:
        crud.delete_user(db, user)
        logger.info(f"User {user.username} deleted successfully")

        return {"message": f"User {user.username} deleted successfully"}
    except Exception as e:
        logger.warning(f"Error deleting user {user.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting user {user.username}, Exception: {e}")
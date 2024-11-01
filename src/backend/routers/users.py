from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from typing import Dict
from pydantic import EmailStr
from backend.logs.logger_config import logger
from sqlmodel import Session, select
from backend.models.user import User
from backend.models.api_models import UserData
from backend.database import database_setup, crud, auth
from backend.send_mail import registration_confirmation, send_verification_mail, send_password_reset_mail

user_router = APIRouter(tags=["Users"])

@user_router.post("/users/create_user")
async def create_user(user: UserData, db: Session = Depends(database_setup.get_session)) -> Dict[str, str]:
    logger.info(f"Attempt to create user: {user.username}")

    db_user = User(username=user.username, password=user.password, email=user.email)

    try:
        crud.create_user(db, db_user)

        token = auth.create_access_token(db_user)
        logger.info(f"Attempt to send verification email to user {user.username}")
        send_verification_mail(user.email, user.username, token)
        logger.info(f"Verification email successfully sent to user {user.username}")
        logger.info(f"User {user.username} created successfully")

        return {"message": f"User {user.username} created successfully"}
    except Exception as e:
        logger.warning(f"Error creating user {user.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user {user.username}, Exception: {e}")

@user_router.post("/users/login")
async def login(db: Session = Depends(database_setup.get_session), data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    logger.info(f"Login attempt for user: {data.username}")

    try:
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

@user_router.post("/users/resend_verification_email")
async def resend_verification_email(user: UserData) -> Dict[str, str]:
    logger.info(f"Attempt to resend verification email to user {user.email}")

    try:
        db_user = User(username=user.username, password=user.password, email=user.email)    # user of type User because of the required JWT claims parameters
        token = auth.create_access_token(db_user)
        send_verification_mail(user.email, user.username, token)

        logger.info(f"Verification email successfully resent to user {user.username}")

        return {"msg": f"Verification email successfully resent to user {user.username}"}
    except Exception as e:
        logger.warning(f"Error resending verification email to user {user.username}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error resending verification email to user {user.username}, Exception: {e}")

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
        logger.warning(f"Error verifying user with token {token}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error verifying user with token {token}, Exception: {e}")

@user_router.post("/users/forgot_password")
async def forgot_password(email: EmailStr, db: Session = Depends(database_setup.get_session)) -> Dict[str, str]:
    logger.info(f"Attempt to send email with reset code to {email}")

    try:
        statement = select(User).where(User.email == email)
        user = db.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User with email {email} not found")

        reset_code = auth.create_reset_code()

        user.reset_code = reset_code

        user.reset_code_expiration = (datetime.now() + timedelta(minutes=5)).replace(tzinfo=None)
        db.commit()

        send_password_reset_mail(email, reset_code)

        logger.info(f"Email with a reset code has successfully been sent to {email}")

        return {"msg": f"Email with a reset code has successfully been sent to {email}"}
    except Exception as e:
        logger.warning(f"Error sending reset email to {email}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending reset email to {email}, Exception: {e}")

@user_router.post("/users/reset_password")
async def reset_password(email: EmailStr, reset_code: int, new_password: str, db: Session = Depends(database_setup.get_session)) -> Dict[str, str]:
    logger.info(f"Attempt to reset password for user with email {email}")

    try:
        statement = select(User).where(User.email == email)
        user = db.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User with email {email} not found")

        if user.reset_code != reset_code:
            raise HTTPException(status_code=404, detail=f"Invalid code for user with email {email}")

        if datetime.now().replace(tzinfo=None) > user.reset_code_expiration:
            raise HTTPException(status_code=400, detail=f"The code for user with email {email} has expired")

        new_password_hashed = auth.create_password_hash(new_password)
        user.password = new_password_hashed
        user.reset_code = None                 # delete the code
        user.reset_code_expiration = None
        db.commit()

        logger.info(f"Password has been reset successfully for user with email {email}")

        return {"msg": f"Password has been reset successfully for user with email {email}"}
    except Exception as e:
        logger.warning(f"Error resetting password for user with {email}, Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting password for user with {email}, Exception: {e}")

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
async def update_user(updated_user: UserData, db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"Attempt to update user: {user.username}")

    try:
        updated_db_user = User(username=user.username, password=user.password, email=user.email)

        crud.update_user(db, user, updated_db_user)
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
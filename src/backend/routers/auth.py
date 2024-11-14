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
from src.backend.database.auth import check_active, create_access_token, create_refresh_token
from backend.database.crud import get_user

auth_router = APIRouter(tags=["Auth"])

#TODO
@auth_router.get("/auth/get_expiration_date", dependencies=[Depends(auth.check_active)])
async def get_expiration_date(token: str = Depends(auth.oauth2_schema)):
    return {"expiration date" : check_active(token).get("exp")}

#TODO: Dependency to get the refresh token from headers
async def get_refresh_token():

    return

#TODO: Endpoint to actually refresh the access token
@auth_router.post("/auth/refresh_access_token")
async def refresh_access_token(db: Session = Depends(database_setup.get_session)):
    user = crud.get_user(db, "jakob")
    return create_refresh_token(user)


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
from src.backend.database.auth import check_active

auth_router = APIRouter(tags=["Auth"])

#TODO
@auth_router.get("/auth/checkExpirationDate", dependencies=[Depends(auth.check_active)])
async def checkExpirationDate(token: str = Depends(auth.oauth2_schema)):
    return {"token payload" : check_active(token)}

#TODO: Endpoint to refresh the access token
#@app.post("/refresh")
async def refresh_access_token():
    return
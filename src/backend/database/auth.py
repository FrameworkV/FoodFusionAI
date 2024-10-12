import bcrypt
from typing import Dict, Any
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from backend.models.user import User

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

# automate log in for secured endpoints
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/users/login")  # url equal to the path of the login endpoint

def create_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def valid_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user: User, expires: timedelta = timedelta(minutes=15)) -> str:
    claims = {
        "sub": user.username,
        "email": user.email,
        "active": user.is_verified,
        "exp": datetime.now(timezone.utc) + expires
    }

    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = decode_access_token(token)

        return payload
    except Exception as e:
        raise Exception(f"Wrong token: {e}")

def check_active(token: str = Depends(oauth2_schema)) -> Dict[str, Any]:
    payload = verify_token(token)
    active = payload["active"]

    if not active:
        raise HTTPException(status_code=401, detail="Activate your account first")
    else:
        return payload
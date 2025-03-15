import random
import bcrypt
from typing import Dict, Any
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt
from datetime import timedelta
from foodfusionai.models.user import User
from foodfusionai.CONFIG import get_config, AUTH_ENDPOINT
config = get_config()

SECRET_KEY = config.jwt_secret_key
ALGORITHM = "HS256"

oauth2_schema = OAuth2PasswordBearer(tokenUrl=AUTH_ENDPOINT)

def create_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def valid_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user: User, expires: timedelta = timedelta(minutes=15)) -> str:
    claims = {
        "sub": user.username,
        "email": user.email,
        "subscription_type": user.subscription_type,
        "active": user.is_verified
    }

    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)

def create_reset_code() -> int:
    return random.randint(100000, 999999)

def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = decode_access_token(token)

        return payload
    except Exception as e:
        raise Exception(f"Error with token: {e}")

def check_active(token: str = Depends(oauth2_schema)) -> Dict[str, Any]:
    payload = verify_token(token)
    active = payload["active"]

    if not active:
        raise HTTPException(status_code=401, detail="Activate your account first")
    else:
        return payload
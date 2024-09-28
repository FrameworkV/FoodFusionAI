import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from backend.models.user import DBUser

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

# automate log in for secured endpoints
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")  # url equal to the path of the login endpoint

def create_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def valid_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user: DBUser, expires: timedelta = timedelta(minutes=15)):
    claims = {
        "sub": user.username,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + expires
    }

    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
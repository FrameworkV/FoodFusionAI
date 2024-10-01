from fastapi import APIRouter, Depends
from typing import Dict
from backend.logs.logger_config import logger
from backend.api_models.models import UserRequestModel
from backend.models.user import User
from backend.routers.users import get_user

requests_router = APIRouter()

@requests_router.post("/dummy_request")
async def dummy_request(user_request: UserRequestModel, user: User = Depends(get_user)) -> Dict[str, str]:
    logger.info(f"User {user.username} made a request: {user_request.request}")
    
    return {"message": user_request.request, "user": user.username}
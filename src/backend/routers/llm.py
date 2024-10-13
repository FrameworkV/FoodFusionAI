from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlmodel import Session
from typing import Dict, List
from backend.logs.logger_config import logger
from backend.database import database_setup, crud, auth
from backend.models.llm_requests import DummyRequest
from backend.models.user import User
from backend.routers.users import _get_user

llm_router = APIRouter(tags=["LLM Requests"])

@llm_router.post("/llm/dummy_request", dependencies=[Depends(auth.check_active)])
async def dummy_request(user_request: DummyRequest, user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"User {user.username} made a request: {user_request.request}")
    
    return {"message": user_request.request, "user": user.username}
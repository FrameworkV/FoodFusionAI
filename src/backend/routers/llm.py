from fastapi import APIRouter, Depends
from typing import Dict, Union
from sse_starlette import EventSourceResponse
from sse_starlette.sse import EventSourceResponse
from backend.logs.logger_config import logger
from backend.database import auth
from backend.models.api_models import ModelResponse
from backend.models.llm_requests import DummyRequest
from backend.models.user import User
from backend.routers.users import _get_user
from backend.routers.response_stream import stream_formatter
from backend.llm.chat_history.chat_history import ChatHistory
from backend.llm.recipe import recipe

llm_router = APIRouter(tags=["LLM Requests"])

@llm_router.post("/llm/create_recipe", dependencies=[Depends(auth.check_active)])
async def create_recipe(user_request: DummyRequest, user: User = Depends(_get_user)) -> ModelResponse:
    logger.info(f"User {user.username} requested a recipe: {user_request.request}")

    chat_id="0"
    chat_history = ChatHistory(chat_id=chat_id) # todo als dependency injection (inklusive chat id weil frontend festlegt ob neuer chat oder nicht?)

    chat_history.add_to_chat_history(message=user_request.request, role="user")

    response_stream = recipe(user_request.request).stream(
        {
            "preferences": ["glutenfrei", "vegan"],
            "chat_history": chat_history.messages
        }
    )

    stream = True

    if stream:
        return EventSourceResponse(stream_formatter(user.id, chat_id, response_stream, stream=True))
    else:
        return await anext(stream_formatter(user.id, chat_id, response_stream, stream=False))
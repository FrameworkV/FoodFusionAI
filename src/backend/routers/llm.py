from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from backend.logs.logger_config import logger
from backend.database import auth
from backend.models.api_models import ModelResponse, UserRequest, ChatMessage
from backend.models.user import User
from backend.routers.users import _get_user
from backend.routers.response_stream import stream_formatter
from backend.llm.chat_history.chat_history import ChatHistory
from backend.llm.recipe import recipe

llm_router = APIRouter(tags=["LLM Requests"])

# get a list of all created chats
@llm_router.get("/llm/get_chats")
async def get_chats(user: User = Depends(_get_user)) -> List[Dict[str, str]]:
    logger.info(f"Attempt to retrieve all chats for user {user.username}")
    try:
        chat_titles = ChatHistory(user_id=user.id).get_chat_titles()

        logger.info(f"Successfully retrieved all chats for user {user.username}")

        return chat_titles

    except Exception as e:
        logger.warning(f"Error retrieving all chats for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving all chats for user {user.username}: {e}")

# get chat messages for a specific chat
@llm_router.get("/llm/get_chat/{chat_id}")
async def get_chat(chat_id: str, user: User = Depends(_get_user)) -> List[ChatMessage]:
    logger.info(f"Attempt to retrieve chat with id {chat_id} for user {user.username}")

    try:
        chat_history = ChatHistory(user_id=user.id, chat_id=chat_id).get_messages()

        logger.info(f"Successfully retrieved chat with id {chat_id} for user {user.username}")

        return chat_history

    except Exception as e:
        logger.warning(f"Error retrieving chat with id {chat_id} for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chat with id {chat_id} for user {user.username}: {e}")

@llm_router.delete("/llm/delete_chat/{chat_id}")
async def delete_chat(chat_id: str, user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"Attempt to delete chat with id {chat_id} for user {user.username}")

    try:
        ChatHistory(user_id=user.id, chat_id=chat_id).delete_chat()

        logger.info(f"Successfully deleted chat with id {chat_id} for user {user.username}")

        return {"message": f"Successfully deleted chat with id {chat_id} for user {user.username}"}
    except Exception as e:
        logger.warning(f"Error deleting chat with id {chat_id} for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting chat with id {chat_id} for user {user.username}: {e}")

@llm_router.post("/llm/create_recipe", dependencies=[Depends(auth.check_active)])
async def create_recipe(user_request: UserRequest, user: User = Depends(_get_user)) -> ModelResponse:
    logger.info(f"User {user.username} requested a recipe: {user_request.request}")

    try:
        chat_history = ChatHistory(user_id=user.id, chat_id=user_request.chat_id)

        chat_history.add_message(message=user_request.request, role="human")
        response_stream = recipe(user_request.request).stream(
            {
                "preferences": ["glutenfrei", "vegan"], # todo preferences in user table
                "chat_history": chat_history.get_messages(formatted=True)
            }
        )

        stream = False

        logger.info(f"User {user.username} successfully received a recipe response")

        if stream:
            return EventSourceResponse(stream_formatter(user.id, user_request.chat_id, response_stream, stream=True))
        else:
            return await anext(stream_formatter(user.id, user_request.chat_id, response_stream, stream=False))
    except Exception as e:
        logger.warning(f"Error generating recipe for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recipe for user {user.username}: {e}")
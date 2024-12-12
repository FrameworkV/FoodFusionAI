import uuid
from typing import List, Dict, Union
from langchain.schema import BaseMessage
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlmodel import Session
from backend.database import crud, database_setup
from backend.logs.logger_config import logger
from backend.database import auth
from backend.models.api_models import ModelResponse, UserRequest
from backend.models.user import User
from backend.models.groceries import ShoppingList
from backend.routers.users import _get_user
from backend.routers.response_stream import stream_formatter
from backend.llm.chat_history.chat_history import ChatHistory
from backend.llm.model_generations import recipe, shopping_list, react_agent

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
async def get_chat(chat_id: str, user: User = Depends(_get_user)) -> Union[List[Dict[str, str]], List[BaseMessage]]:
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

@llm_router.post("/llm/model_request", dependencies=[Depends(auth.check_active)])
async def model_request(user_request: UserRequest, user: User = Depends(_get_user)) -> ModelResponse:
    logger.info(f"User {user.username} made a request: {user_request.request}")

    try:
        chat_id = user_request.chat_id

        if not chat_id:  # first message: generate new id
            chat_id = str(uuid.uuid4())

        chat_history = ChatHistory(user_id=user.id, chat_id=chat_id)
        chat_history.add_message(message=user_request.request, role="human")

        model_handler = {
            "g-01-base": lambda: recipe(user_request.request).stream(
                {
                    "preferences": ["glutenfrei", "vegan"],  # todo preferences in user table
                    "chat_history": chat_history.get_messages(formatted=True)
                }
            ),
            "g-01-reasoning": lambda: react_agent(user.id, chat_history).invoke({"input": user_request.request})["output"]
        }

        handler = model_handler.get(user_request.model)
        response = handler()

        logger.info(f"User {user.username} successfully made a request")

        if user_request.model == "g-01-base":
            return EventSourceResponse(stream_formatter(user.id, chat_id, user_request.model, response))
        else:
            return await anext(stream_formatter(user.id, chat_id, user_request.model, response))
    except Exception as e:
        logger.warning(f"Error generating a response for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating a response for user {user.username}: {e}")

@llm_router.post("/llm/generate_shopping_list", dependencies=[Depends(auth.check_active)])
async def generate_shopping_list(recipe_id: int, db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"User {user.username} requested a shopping list for a recipe")

    try:
        recipe = crud.get_recipe(db, recipe_id)
        stock = crud.get_user_stock(db, user.id)

        response = shopping_list().invoke(
            {
                "recipe": recipe,
                "user_stock": stock
            }
        )

        new_shopping_list = ShoppingList(content=response, user_id=user.id)
        crud.create_shopping_list(db, new_shopping_list)

        logger.info(f"User {user.username} successfully received a shopping list")

        return {"message": f"Successfully generated a shopping list for user {user.username}"}
    except Exception as e:
        logger.warning(f"Error generating a shopping list for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating a shopping list for user {user.username}: {e}")
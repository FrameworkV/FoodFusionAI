from typing import Iterable, AsyncGenerator
from langchain_core.messages import BaseMessage
from backend.models.api_models import ModelResponse
from backend.llm.chat_history.chat_history import ChatHistory

async def stream_formatter(user_id: int, chat_id: str, response_stream: Iterable[BaseMessage], stream: bool = False) -> AsyncGenerator[ModelResponse, None]:
    response = ""

    if stream:
        for chunk in response_stream:
            response += chunk.content
            response_chunk = ModelResponse(
                user_id=user_id,
                chat_id=chat_id,
                response=chunk.content
            )

            yield response_chunk

        yield ModelResponse(    # indicate end of stream
            user_id=user_id,
            id=chat_id,
            response="",
            is_last=True
        )
    else:
        for chunk in response_stream:
            response += chunk.content

        yield ModelResponse(
            user_id=user_id,
            id=chat_id,
            response=response
        )

    ChatHistory(chat_id).add_to_chat_history(message=response, role="model")
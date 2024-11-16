from typing import Iterable, AsyncGenerator
from langchain_core.messages import BaseMessage
from backend.models.api_models import ModelResponse
from backend.llm.chat_history.chat_history import ChatHistory

async def stream_formatter(user_id: int, chat_id: str, response_stream: Iterable[BaseMessage], stream: bool = False) -> AsyncGenerator[ModelResponse, None]:
    response = ""

    if stream:
        for chunk in response_stream:
            response += chunk
            response_chunk = ModelResponse(
                user_id=user_id,
                chat_id=chat_id,
                response=chunk,
                streamed_response=True
            )

            yield response_chunk

        yield ModelResponse(    # indicate end of stream
            user_id=user_id,
            chat_id=chat_id,
            response="",
            streamed_response=True,
            is_last=True
        )

        ChatHistory(user_id=user_id, chat_id=chat_id).add_message(message=response, role="ai")
    else:
        for chunk in response_stream:
            response += chunk

        ChatHistory(user_id=user_id, chat_id=chat_id).add_message(message=response, role="ai")  # no stream --> one element --> code after yield unreachable

        yield ModelResponse(
            user_id=user_id,
            chat_id=chat_id,
            response=response,
            is_last=True
        )
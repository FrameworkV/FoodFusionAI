from typing import Union, Iterable, AsyncGenerator
from langchain_core.messages import BaseMessage
from foodfusionai.models.api_models import ModelResponse
from foodfusionai.llm.chat_history.chat_history import ChatHistory

async def stream_formatter(user_id: int, chat_id: str, model: str, response_stream: Union[Iterable[BaseMessage], str]) -> AsyncGenerator[ModelResponse, None]:
    if model == "g-01-base":
        response = ""

        for chunk in response_stream:
            response += chunk
            response_chunk = ModelResponse(
                user_id=user_id,
                chat_id=chat_id,
                model=model,
                response=chunk,
                streamed_response=True
            )

            yield response_chunk

        yield ModelResponse(    # indicate end of stream
            user_id=user_id,
            chat_id=chat_id,
            model=model,
            response="",
            streamed_response=True,
            is_last=True
        )

        ChatHistory(user_id=user_id, chat_id=chat_id).add_message(message=response, role="ai")
    else:
        ChatHistory(user_id=user_id, chat_id=chat_id).add_message(message=response_stream, role="ai")

        yield ModelResponse(
            user_id=user_id,
            chat_id=chat_id,
            model=model,
            response=response_stream,
            is_last=True
        )
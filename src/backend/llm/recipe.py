from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables import RunnableSerializable
from backend.llm.prompts import recipe_system_prompt
from backend.utils import model

def recipe(request: str) ->  RunnableSerializable[dict, BaseMessage]:
    messages = [
        ("system", recipe_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", request)
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    chain = prompt | model | StrOutputParser()

    return chain

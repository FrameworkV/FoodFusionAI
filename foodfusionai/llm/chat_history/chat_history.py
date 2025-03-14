import time
from typing import List, Dict, Union
from azure.cosmos import CosmosClient
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from foodfusionai.CONFIG import get_config
config = get_config()

credential = config.azure_cosmosdb_access_key

client = CosmosClient(url="https://foodfusionai.documents.azure.com:443/", credential=credential)

database = client.get_database_client("Chats")
container = database.get_container_client("ChatsContainer")

class ChatHistory:
    def __init__(self, user_id: int, chat_id: str = None):
        self.user_id = str(user_id)
        self.chat_id = chat_id

    @staticmethod
    def _formatter(messages: List[Dict]) -> List[BaseMessage]:
        formatted_messages = []

        for message in messages:
            if message["role"] == "human":
                formatted_messages.append(HumanMessage(content=message["message"]))
            else:
                formatted_messages.append(AIMessage(content=message["message"]))

        return formatted_messages

    def add_message(self, message: str, role: str) -> None:
        message_id = f"{self.chat_id}-{time.time()}"

        item = {
            "id": message_id,               # id defined by CosmosDB
            "user_id": str(self.user_id),   # partition key
            "chat_id": self.chat_id,
            "message": message,
            "role": role,
        }

        container.upsert_item(item)

    def get_messages(self, formatted=False) -> Union[List[Dict[str, str]], List[BaseMessage]]:
        query = f"SELECT c.id, c.role, c.message FROM ChatsContainer c WHERE c.user_id = @user_id AND c.chat_id = @chat_id"

        messages = container.query_items(
            query=query,
            parameters=[
                dict(
                    name="@user_id",
                    value=self.user_id,
                ),
                dict(
                    name="@chat_id",
                    value=self.chat_id,
                )
            ]
        )

        items = [message for message in messages]

        if formatted:
            items = self._formatter(items)

        return items

    def get_chat_titles(self) -> List[Dict[str, str]]:
        chat_titles = []

        # TODO inefficiency --> store in SQL database?
        get_chat_ids_query = f"SELECT DISTINCT c.chat_id FROM ChatsContainer c WHERE c.user_id = @user_id"

        chat_ids = container.query_items(  # [{chat_id: ...}]
            query=get_chat_ids_query,
            parameters=[
                dict(
                    name="@user_id",
                    value=self.user_id,
                )
            ]
        )

        for chat_id_dict in chat_ids:
            chat_id = chat_id_dict["chat_id"]
            query = f"SELECT c.message FROM ChatsContainer c WHERE c.user_id = @user_id AND c.chat_id = @chat_id"

            messages = container.query_items(
                query=query,
                parameters=[
                    dict(
                        name="@user_id",
                        value=self.user_id,
                    ),
                    dict(
                        name="@chat_id",
                        value=chat_id,
                    )
                ]
            )

            first_message = next(messages, None)

            if first_message:
                chat_titles.append({"chat_id": chat_id, "title": f"{first_message['message'][:15]}..."})

        return chat_titles

    def delete_chat(self) -> None:
        messages = self.get_messages()

        for message in messages:
            container.delete_item(
                item=message["id"],
                partition_key=self.user_id
            )
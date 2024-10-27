from typing import List, Dict
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
import boto3
from backend.llm.chat_history.setup import table_name
from backend.models.api_models import ChatMessage

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)

class ChatHistory(DynamoDBChatMessageHistory):
    """
    Call this with the user_id generated chat_id
    Extract the chat history with .messages
    """
    def __init__(self, user_id: int, chat_id: str = None):
        super().__init__(table_name=table_name, session_id=chat_id, key={"UserId": user_id, "SessionId": chat_id})
        self.chat_id = chat_id
        self.user_id = user_id
        self.history = DynamoDBChatMessageHistory(table_name=table_name, session_id=self.chat_id, key={"UserId": user_id, "SessionId": chat_id})

    def add_to_chat_history(self, message: str, role: str) -> None:
        if role == "human":
            self.history.add_user_message(message)

        if role == "ai":
            self.history.add_ai_message(message)

    def get_messages(self) -> List[ChatMessage]:
        """
        Retrieve the messages of a chat
        """
        # query only looks for matching entries, scan searches the whole table
        response = self.table.query(
            KeyConditionExpression="#uid = :uid AND #sid = :sid",
            ExpressionAttributeNames={  # placeholders
                "#uid": "UserId",
                "#sid": "SessionId"
            },
            ExpressionAttributeValues={ # placeholders
                ":uid": self.user_id,
                ":sid": self.session_id
            }
        )

        if not response.get("Items"):
            return []

        columns = response["Items"][0]    # response["Items"] example:  [{'UserId': Decimal('2'), 'SessionId': 'string', 'History': [{'type': 'human', 'data': {'additional_kwargs': {}, 'name': None, 'response_metadata': {}, 'id': None, 'type': 'human', 'content': 'string', 'example': False}}]}]
        messages = columns["History"]

        chat_history = []

        for message in messages:
            role = message["type"]
            content = message["data"]["content"]

            chat_history.append(
                ChatMessage(role=role, content=content)
            )

        return chat_history

    def _get_all_chat_ids(self) -> List[str]:
        session_ids = []

        response = table.query(
            KeyConditionExpression="#uid = :uid",
            ExpressionAttributeNames={
                "#uid": "UserId"
            },
            ExpressionAttributeValues={
                ":uid": self.user_id
            },
            ProjectionExpression="SessionId"
        )

        # add SessionIds from first response
        session_ids.extend([item["SessionId"] for item in response.get("Items", [])])

        # handle pagination if necessary (only 1MB per request in DynamoDB)
        while "LastEvaluatedKey" in response:
            response = table.query(
                KeyConditionExpression="#uid = :uid",
                ExpressionAttributeNames={
                    "#uid": "UserId"
                },
                ExpressionAttributeValues={
                    ":uid": self.user_id
                },
                ProjectionExpression="SessionId",
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )

            session_ids.extend([item["SessionId"] for item in response.get("Items", [])])

        return session_ids

    def get_chat_titles(self) -> List[Dict[str, str]]:
        """
        Get the titles of all chats of the user
        """
        chat_titles = []
        chat_ids = self._get_all_chat_ids()

        for chat_id in chat_ids:
            title = ChatHistory(user_id=self.user_id, chat_id=chat_id).messages[0].content[:15] + "..."  # title is first 15 characters of the user message

            chat_titles.append(
                {"chat_id": chat_id, "title": title}
            )

        return chat_titles

    def delete_history(self) -> None:
        """
        Deletes all messages for the current chat_id from the DynamoDB table.
        """
        response = table.query(
            KeyConditionExpression="#uid = :uid AND #sid = :sid",
            ExpressionAttributeNames={
                "#uid": "UserId",
                "#sid": "SessionId"
            },
            ExpressionAttributeValues={
                ":uid": self.user_id,
                ":sid": self.chat_id
            }
        )

        table.delete_item(
            Key={
                'UserId': self.user_id,
                'SessionId': self.chat_id
            }
        )
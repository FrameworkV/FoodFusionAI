from langchain_community.chat_message_histories import DynamoDBChatMessageHistory

class ChatHistory(DynamoDBChatMessageHistory):
    """
    Call this with the generated chat_id
    Extract the chat history with .messages
    """
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.table_name = "SessionTable"
        super().__init__(table_name=self.table_name, session_id=self.chat_id)
        self.history = DynamoDBChatMessageHistory(table_name=self.table_name, session_id=self.chat_id)

    def add_to_chat_history(self, message: str, role: str) -> None:
        valid_role = ["user", "model"]

        if role not in valid_role:
            raise ValueError(f"Invalid role, choose from: {valid_role}")

        if role == "user":
            self.history.add_user_message(message)

        if role == "model":
            self.history.add_ai_message(message)
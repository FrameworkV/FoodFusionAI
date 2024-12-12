from typing import Dict, Any
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables import RunnableSerializable
from backend.llm.prompts import recipe_system_prompt, shopping_list_prompt
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import Tool
from backend.llm.rag import graph
from backend.utils import llm
from backend.llm.chat_history.chat_history import ChatHistory
from backend.database.database_setup import db

def recipe(request: str) ->  RunnableSerializable[dict, BaseMessage]:
    messages = [
        ("system", recipe_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", request)
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    chain = prompt | llm | StrOutputParser()

    return chain

def shopping_list() ->  RunnableSerializable[dict, BaseMessage]:
    prompt = ChatPromptTemplate.from_template(shopping_list_prompt)

    chain = prompt | llm | StrOutputParser()

    return chain

def react_agent(user_id: int, chat_history: ChatHistory):
    def get_current_day_and_time(*args, **kwargs) -> Dict[str, datetime.time]:
        """
        Returns the current day and time in a structured format.

        The function retrieves the current system date and time,
        formats it into a human-readable string, and returns both
        the day and time components.

        Returns:
            dict: A dictionary containing the current day and time.

        Example:
            >>> get_current_day_and_time()
            {'day': '2024-11-29', 'time': '14:35:22'}
        """
        now = datetime.now()

        return {
            "day": now.strftime("%Y-%m-%d"),  # format: YYYY-MM-DD
            "time": now.strftime("%H:%M:%S")  # format: HH:MM:SS
        }

    def get_user_groceries(request: str) -> Dict[str, Any]:
        """
        Takes a query in natural languange, transforms it to an SQL query and executes it on the groceries table.

        Args:
            request (str): A semantic query asked by the user.

        Returns:
            dict: A dict with the sql_query, the table_structure and the result as a list of tuples.
        """
        state = {"user_id": user_id, "question": request}
        result = graph.invoke(state, stream_mode="updates")     # example: graph.invoke({"user_id": 1, "tables": ["item"], "question": "How much milk do I have?"}, stream_mode="updates")

        # [{'write_query': {'query': '...'}}, {'execute_query': {'query': '...', 'result': '[(...,)]'}}]
        sql_query =  result[-1].get("execute_query").get("query")
        table_structure =  db.get_table_info(["item"])
        result = result[-1].get("execute_query").get("result")

        return {"sql_query": sql_query, "table_structure": table_structure, "result": result}

    tools = [
        Tool(
            name="Day and time",
            func=get_current_day_and_time,
            description="Useful for when you need to know the current day and time.",
        ),
        Tool(
            name="GroceriesStock",
            func=get_user_groceries,
            description="Useful for when you need to know what and how many groceries the user has. Needs semantic search query",
        ),
    ]

    # ReAct agent prompt
    prompt = hub.pull("hwchase17/structured-chat-agent")

    # ConversationBufferMemory stores the conversation history in RAM
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, k=10)    # return_messages: return list, k: keep last k messages in memory

    # add messages to memory
    for message in chat_history.get_messages(formatted=True):
        memory.chat_memory.add_message(message)

    agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,  # handle any parsing errors gracefully

    )

    return agent_executor
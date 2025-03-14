from typing import Annotated, List, Dict
from langchain.prompts import PromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langgraph.graph import START, StateGraph
from pydantic import BaseModel
from typing_extensions import TypedDict
import codecs
from foodfusionai.utils import llm
from foodfusionai.llm.prompts import sql_query_prompt
from foodfusionai.database.database_setup import db

class State(TypedDict): # equivalent to dict at runtime --> allows to initialise subset of keys
    user_id: int
    question: str
    query: str
    result: str
    answer: str

class QueryOutput(BaseModel):
    """Generated SQL query"""  # class description and param description important to LLM
    query: Annotated[str, ..., "Syntactically valid SQL query."]

def write_query(state: State) -> Dict[str, str]:
    """
    Generate SQL query to fetch information
    """
    prompt = PromptTemplate.from_template(sql_query_prompt).format(
        user_id=state["user_id"],
        dialect=db.dialect,
        table_info=db.get_table_info(["item"]),
        input=state["question"]
    )

    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)

    result.query = codecs.decode(result.query.replace('\\', ''), 'unicode_escape')  # remove "\" as gemini adds them as special characters (example: \\'water\\'): causes SQL error

    return {"query": result.query}

def execute_query(state: State) -> Dict[str, str]:
    """
    Execute SQL query
    """
    execute_query_tool = QuerySQLDataBaseTool(db=db)

    return {"query": state["query"], "result": execute_query_tool.invoke(state["query"])}

graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()
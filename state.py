from langgraph.graph import StateGraph
from typing import TypedDict

class State(TypedDict):

    repo_url: str
    start_date: str
    end_date: str
    
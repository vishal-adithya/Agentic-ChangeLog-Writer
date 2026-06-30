from langgraph.graph import StateGraph,START,END
from typing import TypedDict


from nodes.fetch_commits import fetch_commits
class State(TypedDict):

    repo_url: str
    start_date: str
    end_date: str
    git_author: str
    git_repo: str

if __name__ == "__main__":
    graph_builder = StateGraph(State)
    graph_builder.add_node(fetch_commits,"Fetch Commit")

    graph_builder.add_edge(START,"Fetch Commit")
    graph_builder.add_edge("Fetch Commit",END)

    graph = graph_builder.compile()
    graph.invoke("https://github.com/vishal-adithya/changelog-test-repo")

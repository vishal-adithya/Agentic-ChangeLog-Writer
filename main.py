from nodes.fetch_commits import fetch_commits,git_info
from langgraph.graph import StateGraph,START,END

from state import State
from nodes.fetch_commits import fetch_commits,git_info

if __name__ == "__main__":
    graph_builder = StateGraph(State)
    graph_builder.add_node("fetch_comit",fetch_commits)

    graph_builder.add_edge(START,"fetch_comit")
    graph_builder.add_edge("fetch_comit",END)

    graph = graph_builder.compile()
    result = graph.invoke("https://github.com/vishal-adithya/changelog-test-repo")
    print(result)
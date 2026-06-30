from typing import TypedDict


class State(TypedDict):

    repo_url: str
    start_date: str
    end_date: str
    git_author: str
    git_repo: str



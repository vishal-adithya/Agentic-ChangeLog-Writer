from state import State
import os
from datetime import datetime
from github import Github,GithubException
import re

def git_info(state: State) -> State:
    pattern = r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$"

    matches = re.search(pattern,state["repo_url"])

    if matches:
        git_author = matches.group(1)
        git_repo = matches.group(2)

        return {"git_author":git_author,"git_repo":git_repo}

    else:
        print("Enter a valid Github URL!")

    
def fetch_commits(state:State) -> dict:

    try:
        github_token = os.getenv["GITHUB_TOKEN"]
        gh = Github(github_token)
        print(github_token)

        start = datetime.strptime(state["start_date"],"%Y-%m-%d")
        end = datetime.strptime(state["end_date"],"%Y-%m-%d")
        
        repo = gh.get_repo(state["repo_url"])
        raw_commits = repo.get_commits(
            since=start,
            until=end
        )

        commits = []
        for commit in raw_commits:
            commits.append(
                {
                    "sha": commit.sha[:7],
                    "author": commit.commit.author.name,
                    "message": commit.commit.message,
                    "date":commit.commit.author.date.strftime("%Y-%m-%d"),
                    "url": commit.html_url
                }
            )

    except GithubException as e:
        if e.status == 404:
            return {"error": f"Repo not found: {state["repo_url"]}. Check the URL."}
        if e.status == 401:
            return {"error": "GitHub token is invalid or expired."}
        return {"error": f"GitHub API error {e.status}: {e.data.get('message', '')}"}

    if not commits:
        return {"error": f"No commits found between {state['since_date']} and {state['until_date']}."}

    return {"commits": commits, "error": None}



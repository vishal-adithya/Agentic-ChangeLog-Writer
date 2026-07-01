import os
from datetime import datetime
from github import Github,GithubException
import re
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()

from langchain_core.globals import set_debug
set_debug(True)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2)

@tool
def git_info(repo_url:str) -> dict:
    """
Use this tool whenever a GitHub repository URL is provided and the repository
owner and repository name need to be extracted for use with the GitHub API
or other repository-related tools.

Input:
    repo_url: A GitHub repository URL.
    
Supported URL formats:
        - https://github.com/owner/repository
        - https://github.com/owner/repository/
        - https://github.com/owner/repository.git

Output:
    A dictionary containing:
    - repo_owner: Repository owner (user or organization).
    - repo_repo: Repository name.

Returns an error dictionary if the URL is not a valid GitHub repository URL.
"""
    pattern = r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$"

    matches = re.search(pattern,repo_url)

    if matches:
        git_author = matches.group(1)
        git_repo = matches.group(2)

        return {"repo_owner":git_author,"repo_name":git_repo}

    else:
        return {"error": "Enter a valid git url"}

@tool   
def fetch_commits(start_date:str,end_date:str,repo_owner:str,repo_name:str) -> dict:
    """
Fetches all commits from a GitHub repository within a specified date range.

Use this tool when commit history is needed for tasks such as generating
changelogs, summarizing repository activity, reviewing code changes, or
analyzing development progress.

Args:
    start_date (str):
        The start of the date range (inclusive) in YYYY-MM-DD format.

    end_date (str):
        The end of the date range (inclusive) in YYYY-MM-DD format.

    repo_owner (str):
        The GitHub username or organization that owns the repository.

    repo_name (str):
        The name of the GitHub repository.

Returns:
    dict:
        On success:
        {
            "commits": [
                {
                    "sha": "<7-character commit SHA>",
                    "author": "<commit author>",
                    "message": "<commit message>",
                    "date": "<YYYY-MM-DD>",
                    "url": "<GitHub commit URL>"
                },
                ...
            ],
            "error": None
        }

        On failure:
        {
            "error": "<error description>"
        }

Possible errors:
    - Repository does not exist.
    - GitHub access token is invalid or missing.
    - No commits exist within the specified date range.
    - GitHub API returned an unexpected error.
"""
    try:
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            return {"error": "GitHub token not found. Set the GITHUB_TOKEN environment variable."}
        
        gh = Github(github_token)

        start = datetime.strptime(start_date,"%Y-%m-%d")
        end = datetime.strptime(end_date,"%Y-%m-%d")
        
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")
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
            return {"error": f"Repo not found: {repo_owner}/{repo_name}. Check the URL."}
        if e.status == 401:
            return {"error": "GitHub token is invalid or expired."}
        return {"error": f"GitHub API error {e.status}: {e.data.get('message', '')}"}

    if not commits:
        return {"error": f"No commits found between {start_date} and {end_date}."}

    return {"commits": commits, "error": None}


def create_agent_with_tools(question):
    tools = [git_info, fetch_commits]
    agent = create_agent(
        llm,
        tools=tools,
        system_prompt="""You are an expert GitHub Changelog Writer.

Your responsibility is to generate clear, accurate, and well-structured changelogs from a GitHub repository's commit history.

You have access to tools for:
1. Extracting the repository owner and repository name from a GitHub URL.
2. Fetching commits from a GitHub repository within a specified date range.

Guidelines:

- Carefully understand the user's request before deciding which tool to use.
- If the user provides a GitHub repository URL, first extract the repository owner and repository name using the appropriate tool.
- If the repository owner and name are already provided, do not call the extraction tool.
- Fetch commits only after the repository information and date range are available.
- Never fabricate commits or repository information.
- If a required piece of information is missing (repository or dates), ask the user for it instead of guessing.
- If a tool returns an error, explain the issue clearly and suggest how the user can resolve it.
- If no commits are found, inform the user politely.

When writing changelogs:

- Group related commits whenever appropriate.
- Merge duplicate or similar commit messages into concise summaries.
- Remove unnecessary implementation details unless they are important.
- Write in clear, professional Markdown.
- Prioritize user-facing changes over internal refactoring.
- Preserve important bug fixes, new features, documentation updates, performance improvements, security changes, and breaking changes.
- Highlight breaking changes in a dedicated section if any exist.

Preferred changelog structure:

# Changelog

## 🚀 Features
- ...

## 🐛 Bug Fixes
- ...

## ⚡ Improvements
- ...

## 📚 Documentation
- ...

## 🧹 Maintenance
- ...

## 💥 Breaking Changes
- ...

If a category has no changes, omit it.

Keep the changelog concise, readable, and suitable for publishing in release notes.""")
    result = agent.invoke({"messages":[{"role":"user","content":question}]})
    print("===================================================================================================")
    last_message = result["messages"][-1]

    if isinstance(last_message.content, list):
        print(last_message.content[0]["text"])
    else:
        print(last_message.content)

qn = "https://github.com/vishal-adithya/changelog-test-repo, from 2026-06-29 to 2026-07-02"


create_agent_with_tools(qn)
from datetime import datetime

import requests
from itsdangerous import base64_decode

from podcast_generator.fixtures import load_graphql_query
from podcast_generator.github_authorization import GithubAuthorization

# GitHub GraphQL API endpoint
GRAPHQL_API_URL = "https://api.github.com/graphql"


def get_repo_data(
    github_authorization: GithubAuthorization,
    owner: str,
    name: str,
    since: datetime,
    until: datetime,
) -> dict:
    # Headers for authentication
    headers = {
        "Authorization": github_authorization.get_authorization_header_value(),
    }

    # Load GraphQL query
    query = load_graphql_query("repository")

    readme_response = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/readme",
        headers=headers,
    )
    # FIXME: Use last commit prior to $until
    readme = (
        str(base64_decode(readme_response.json()["content"]))
        if readme_response.ok
        else None
    )

    relevant_range = f"{since.isoformat()}..{until.isoformat()}"

    # Variables for the query
    variables = {
        "owner": owner,
        "name": name,
        "since": since.isoformat(),
        "until": until.isoformat(),
        "openPullsQuery": f"repo:{owner}/{name} is:pr state:open updated:{relevant_range} sort:interactions",
        "mergedPullsQuery": f"repo:{owner}/{name} is:pr merged:{relevant_range} sort:interactions",
        "openIssuesQuery": f"repo:{owner}/{name} is:issue state:open updated:{relevant_range} sort:interactions",
        "closedIssuesQuery": f"repo:{owner}/{name} is:issue closed:{relevant_range} reason:completed sort:interactions",
        "discussionsQuery": f"repo:{owner}/{name} updated:{relevant_range} sort:interactions",
    }

    # Make the request
    response = requests.post(
        GRAPHQL_API_URL, json={"query": query, "variables": variables}, headers=headers
    )

    response.raise_for_status()

    raw_json = response.json()
    if "errors" in raw_json:
        raise ValueError(raw_json)
    data = response.json()["data"]
    repository_data = data["repository"]
    repository_data["releases"]["nodes"] = [
        node
        for node in repository_data["releases"]["nodes"]
        if datetime.fromisoformat(node["publishedAt"]) >= since
        and datetime.fromisoformat(node["publishedAt"]) <= until
    ]

    data["readme"] = readme

    default_branch = repository_data.get("defaultBranchRef")
    if default_branch is not None:
        commits = default_branch["target"]["history"]["nodes"]
        data["diff"] = get_diff(owner, name, headers, commits)

    data["startDate"] = since.isoformat()
    data["endDate"] = until.isoformat()

    return data


def get_diff(owner, name, headers, commits):
    if not commits:
        return {"files": []}

    if commits[-1]["parents"]["totalCount"] == 0:
        # FIXME: Properly handle this case (first commit). Should try to get file tree
        return {"files": []}

    first_commit_sha = commits[-1]["oid"]
    last_commit_sha = commits[0]["oid"]

    diff_response = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/compare/{first_commit_sha}^...{last_commit_sha}",
        headers=headers,
    )
    diff_response.raise_for_status()

    diff = diff_response.json()
    diff = {
        "files": [
            {
                "filename": file["filename"],
                "status": file["status"],
                "additions": file["additions"],
                "deletions": file["deletions"],
                "patch": file.get("patch"),
            }
            for file in diff["files"]
        ],
    }

    return diff

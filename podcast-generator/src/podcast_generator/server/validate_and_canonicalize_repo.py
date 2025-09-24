import requests

from podcast_generator.github_authorization import GithubAuthorization


def validate_and_canonicalize_repo(
    github_auth: GithubAuthorization, owner: str, name: str
):
    headers = {
        "Authorization": github_auth.get_authorization_header_value(),
    }

    response = requests.get(
        f"https://api.github.com/repos/{owner}/{name}",
        headers=headers,
        allow_redirects=True,
    )

    response.raise_for_status()

    data = response.json()

    return data["owner"]["login"], data["name"]

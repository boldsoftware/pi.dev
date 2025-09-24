import urllib.parse


def get_github_repo_id(owner, name):
    return urllib.parse.quote_plus(f"github.com/{owner}/{name}")

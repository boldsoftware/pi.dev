import os

from podcast_generator.github_authorization import GithubAuthorization


class GithubPersonalAuthorization(GithubAuthorization):
    def __init__(self):
        self.personal_token = os.environ.get("GITHUB_TOKEN")
        if not self.personal_token:
            raise OSError("Please set GITHUB_TOKEN environment variable.")

    def get_authorization_header_value(self):
        return f"Bearer {self.personal_token}"

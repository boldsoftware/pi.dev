import os
import time
from datetime import datetime

import jwt
import requests

from podcast_generator.github_authorization import GithubAuthorization


class GithubAppAuthorization(GithubAuthorization):
    def __init__(self):
        self.client_id = os.environ["GITHUB_APP_CLIENT_ID"]
        self.installation_id = os.environ["GITHUB_APP_INSTALLATION_ID"]
        self.private_key = os.environ["GITHUB_APP_PRIVATE_KEY"]

        self.installation_token = None
        self.installation_token_expiration = None

    def _create_jwt(self):
        now = int(time.time())
        payload = {
            "iat": now,
            "exp": now + (10 * 60),  # expires in 10 minutes
            "iss": self.client_id,
        }
        token = jwt.encode(payload, self.private_key, algorithm="RS256")
        return token

    def _request_installation_access_token(self):
        jwt_token = self._create_jwt()
        url = f"https://api.github.com/app/installations/{self.installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
        }
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["token"], data["expires_at"]

    def _get_valid_installation_token(self):
        # Check if we have a valid token
        if self.installation_token and self.installation_token_expiration:
            expiration_time = datetime.strptime(
                self.installation_token_expiration, "%Y-%m-%dT%H:%M:%SZ"
            ).timestamp()
            if time.time() < expiration_time:
                return self.installation_token

        # Token missing or expired, request a new one
        new_token, new_expires_at = self._request_installation_access_token()
        self.installation_token = new_token
        self.installation_token_expiration = new_expires_at
        return self.installation_token

    def get_authorization_header_value(self):
        token = self._get_valid_installation_token()
        return f"token {token}"

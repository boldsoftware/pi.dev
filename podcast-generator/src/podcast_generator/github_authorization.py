from abc import ABC, abstractmethod


class GithubAuthorization(ABC):
    @abstractmethod
    def get_authorization_header_value(self) -> str:
        pass

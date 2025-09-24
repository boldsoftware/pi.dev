from abc import ABC, abstractmethod
from pathlib import Path


class ArtifactLogger(ABC):
    @abstractmethod
    def log(self, name: str, content: str):
        pass

    @abstractmethod
    def log_multiple(self, artifacts: list[tuple[str, str]]):
        for name, content in artifacts:
            self.log(name, content)

    @abstractmethod
    def log_directory(self, name: str, directory: Path):
        pass

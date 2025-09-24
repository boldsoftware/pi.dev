from abc import ABC, abstractmethod


class LlmModel(ABC):
    @abstractmethod
    def run(self, prompt: str) -> str:
        pass

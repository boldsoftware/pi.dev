import enum

from podcast_generator.llm_models.model import LlmModel

import anthropic


# Enum of models (haiku and sonnet)
class ClaudeModel(enum.Enum):
    HAIKU = "claude-3-5-haiku-20241022"
    SONNET = "claude-3-5-sonnet-20241022"


class Claude(LlmModel):
    def __init__(
        self,
        model_name: ClaudeModel = ClaudeModel.SONNET,
        *,
        temperature: float | None = None,
    ):
        self.client = anthropic.Anthropic()
        self.temperature = (
            temperature if temperature is not None else anthropic.NOT_GIVEN
        )
        self.model_name = model_name.value

    def run(self, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=8192,
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ],
                }
            ],
        )

        content_block = message.content[0]
        if content_block.type == "text":
            return str(content_block.text)
        else:
            raise ValueError(f"Unexpected content type: {content_block.type}")

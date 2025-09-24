from openai import NOT_GIVEN, OpenAI
from podcast_generator.llm_models.model import LlmModel


class OpenAi(LlmModel):
    def __init__(self, *, temperature: float | None = None):
        self.client = OpenAI()
        self.temperature = temperature if temperature is not None else NOT_GIVEN

    def run(
        self,
        prompt: str,
    ) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o",
            temperature=self.temperature,
        )

        content = chat_completion.choices[0].message.content

        if content is not None:
            return content

        raise ValueError("Unexpected content type: None")

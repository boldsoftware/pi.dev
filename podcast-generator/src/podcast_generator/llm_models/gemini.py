import os

import google.generativeai as genai
from podcast_generator.llm_models.model import LlmModel


class Gemini(LlmModel):
    def __init__(self, *, use_grounding=False, temperature: float | None = None):
        self.use_grounding = use_grounding
        self.temperature = temperature
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def run(
        self,
        prompt: str,
    ) -> str:
        return self.model.generate_content(
            contents=prompt,
            tools="google_search_retrieval" if self.use_grounding else None,
            generation_config={
                "temperature": self.temperature,
            }
            if self.temperature is not None
            else None,
        ).text

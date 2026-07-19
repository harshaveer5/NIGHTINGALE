import os

from app.core.logging import logger
from app.services.llm.base_provider import BaseLLMProvider
from groq import Groq


class GroqProvider(BaseLLMProvider):

    def __init__(self):

        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def generate(self, prompt: str) -> str:

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )

            return response.choices[0].message.content

        except Exception:

            logger.exception("Groq provider failed")

            return "LLM unavailable."

    def health_check(self) -> bool:

        self.client.models.list()

        return True

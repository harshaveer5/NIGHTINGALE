import os

import ollama
from app.services.llm.base_provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):

    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "deepseek-r1:latest")

    def generate(self, prompt: str) -> str:

        try:

            response = ollama.chat(
                model=self.model, messages=[{"role": "user", "content": prompt}]
            )

            return response["message"]["content"]

        except Exception:

            return "LLM unavailable. " "Please ensure Ollama is running."

    def health_check(self) -> bool:

        ollama.list()

        return True

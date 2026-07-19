import os

from app.services.llm.groq_provider import GroqProvider
from app.services.llm.ollama_provider import OllamaProvider


def get_provider():

    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "groq":

        return GroqProvider()

    return OllamaProvider()

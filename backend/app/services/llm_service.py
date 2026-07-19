from app.core.logging import logger
from app.services.llm.provider_factory import get_provider


def generate_chat_answer(prompt: str, trace=None) -> str:
    """
    Generate a response using the configured LLM provider.
    """

    if trace:
        with trace.stage("LLM Provider Selection"):
            provider = get_provider()

        with trace.stage("LLM Inference", prompt_chars=len(prompt)):
            return provider.generate(prompt)

    provider = get_provider()

    logger.info(
        "Sending prompt to LLM", extra={"provider": provider.__class__.__name__}
    )

    logger.info("LLM response received")

    return provider.generate(prompt)

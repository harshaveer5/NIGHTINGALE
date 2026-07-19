from typing import List

from app.models.chat_message import ChatMessage


def build_conversation_context(messages: List[ChatMessage]) -> str:
    """
    Converts recent chat messages into a formatted
    conversation history for the prompt.
    """

    if not messages:
        return ""

    history = []

    for message in messages:

        role = "User" if message.role == "user" else "Assistant"

        history.append(f"{role}: {message.content}")

    return "\n".join(history)

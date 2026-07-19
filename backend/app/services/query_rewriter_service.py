import re

from app.core.logging import logger
from app.services.llm_service import generate_chat_answer

FOLLOW_UP_PATTERNS = [
    r"^what does that mean\??$",
    r"^what about.*",
    r"^and.*",
    r"^is that.*",
    r"^is it.*",
    r"^why\??$",
    r"^how so\??$",
    r"^tell me more.*",
    r"^explain that.*",
    r"^compare.*",
    r"^previous.*",
    r"^those.*",
    r"^these.*",
]


def needs_rewrite(question: str) -> bool:

    question = question.strip().lower()

    for pattern in FOLLOW_UP_PATTERNS:

        if re.match(pattern, question):
            return True

    return False


def rewrite_question(question: str, conversation_context: str) -> str:
    """
    Rewrites follow-up questions into
    standalone questions using recent
    conversation history.
    """

    if not conversation_context.strip():
        return question

    if not needs_rewrite(question):
        return question

    prompt = f"""
You are a query rewriting assistant.

Your task is ONLY to rewrite the latest user question
into a complete standalone question.

Rules:

Return ONLY the rewritten question.

Do not answer it.

Do not explain it.

Do not use markdown.

Do not say
"Here is the rewritten question."

Do not add notes.

Output exactly one sentence.

If no rewrite is necessary,
return the original question unchanged.
Conversation:

{conversation_context}

Latest Question:

{question}

Standalone Question:
"""

    rewritten = generate_chat_answer(prompt)

    logger.info(
        "Query rewritten | original=%s | rewritten=%s", question, rewritten.strip()
    )

    return rewritten.strip()

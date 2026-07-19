from typing import Dict, List, Optional

from app.models.chat_message import ChatMessage
from app.models.document import Document
from app.services.document_selector_service import get_display_document_type
from sqlalchemy.orm import Session

FOLLOW_UP_MARKERS = {
    "it",
    "that",
    "this",
    "these",
    "those",
    "there",
    "same",
    "previous",
    "last",
    "again",
    "continue",
}


def is_ambiguous_follow_up(question: str) -> bool:
    words = {word.strip(".,?!:;").lower() for word in question.split()}

    return len(words) <= 8 and bool(words & FOLLOW_UP_MARKERS)


def build_structured_memory(messages: List[ChatMessage], max_items: int = 6) -> Dict:
    """
    Keeps only durable conversational signals.
    Raw assistant answers are intentionally excluded so an earlier bad answer
    cannot be reinforced by replaying it into future prompts.
    """

    user_questions = [
        message.content.strip()
        for message in messages
        if message.role == "user" and message.content.strip()
    ]

    return {
        "recent_user_questions": user_questions[-max_items:],
        "turn_count": len(messages),
    }


def infer_active_document_id(
    messages: List[ChatMessage], documents: List[Document]
) -> Optional[int]:
    if not documents:
        return None

    document_terms = []

    for document in documents:
        filename = (document.filename or "").lower()
        document_terms.append((document.id, filename))

    for message in reversed(messages):
        if message.role != "user":
            continue

        content = message.content.lower()

        for document_id, filename in document_terms:
            if filename and filename in content:
                return document_id

    return documents[0].id


def build_conversation_state(
    db: Session,
    medical_record_id: int,
    user_id: int,
    messages: List[ChatMessage],
    intent: str,
) -> Dict:
    documents = (
        db.query(Document)
        .filter(
            Document.user_id == user_id, Document.medical_record_id == medical_record_id
        )
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    active_document_id = infer_active_document_id(
        messages=messages, documents=documents
    )

    active_document = next(
        (document for document in documents if document.id == active_document_id), None
    )

    return {
        "active_patient": medical_record_id,
        "active_document": active_document_id,
        "active_document_name": (active_document.filename if active_document else None),
        "active_report_type": (
            get_display_document_type(active_document) if active_document else None
        ),
        "active_entities": [],
        "last_intent": intent,
        "available_documents": [
            {
                "document_id": document.id,
                "filename": document.filename,
                "document_type": get_display_document_type(document),
                "report_date": document.report_date,
            }
            for document in documents[:10]
        ],
    }


def format_structured_section(title: str, data: Dict) -> str:
    lines = [title]

    for key, value in data.items():
        if value in (None, "", [], {}):
            continue

        lines.append(f"{key}: {value}")

    return "\n".join(lines)

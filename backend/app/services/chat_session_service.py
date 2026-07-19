from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from sqlalchemy.orm import Session


def create_session(db: Session, user_id: int, medical_record_id: int, title: str):

    session = ChatSession(
        user_id=user_id, medical_record_id=medical_record_id, title=title
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_session(db: Session, session_id: int, user_id: int):
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )


def validate_chat_session(
    db: Session, session_id: int, user_id: int, medical_record_id: int
):
    return (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.medical_record_id == medical_record_id,
        )
        .first()
    )


def save_message(db: Session, session_id: int, role: str, content: str):

    message = ChatMessage(session_id=session_id, role=role, content=content)

    db.add(message)
    db.commit()

    if role == "user":

        total_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .count()
        )

        if total_messages == 1:

            session = (
                db.query(ChatSession)
                .filter(ChatSession.id == session_id)
                .first()
            )

            if session and session.title == "New Conversation":
                session.title = content[:40]
                db.commit()

    return message


def get_recent_messages(db: Session, session_id: int, limit: int = 10):

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )

    messages.reverse()

    return messages


def get_user_sessions(db: Session, user_id: int):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


def delete_session(db: Session, session: ChatSession):
    db.delete(session)
    db.commit()

    return {"message": "Chat session deleted successfully."}

def get_or_create_latest_session(
    db: Session,
    user_id: int,
    medical_record_id: int,
):
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == user_id,
            ChatSession.medical_record_id == medical_record_id,
        )
        .order_by(ChatSession.created_at.desc())
        .first()
    )

    if session:
        return session

    session = ChatSession(
        user_id=user_id,
        medical_record_id=medical_record_id,
        title="New Conversation",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session

def get_session_messages(
    db: Session,
    session_id: int,
    user_id: int,
):
    session = get_session(
        db=db,
        session_id=session_id,
        user_id=user_id,
    )

    if session is None:
        return None

    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

def get_latest_session(
    db: Session,
    user_id: int,
    medical_record_id: int,
):
    return (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == user_id,
            ChatSession.medical_record_id == medical_record_id,
        )
        .order_by(ChatSession.created_at.desc())
        .first()
    )

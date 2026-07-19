from app.api.users import get_current_user
from app.db.dependencies import get_db
from app.models.user import Users

# from app.schemas.chat import (
#     CreateSessionRequest,
# )
from app.schemas.chat_session import (
    ChatSessionListResponse,
    ChatSessionResponse,
    CreateChatSessionRequest,
    ChatMessageResponse
)
from app.services.chat_session_service import (
    create_session,
    delete_session,
    get_session,
    get_user_sessions,
    get_session_messages
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sessions", tags=["Chat Sessions"])


@router.post(
    "/",
    response_model=ChatSessionResponse,
    status_code=201,
    summary="Create chat session",
    description="Creates a new AI conversation session for a medical record.",
    responses={
        201: {"description": "Chat session created successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Medical record not found"},
    },
)
def create_chat_session(
    request: CreateChatSessionRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):

    return create_session(
        db=db,
        user_id=current_user.id,
        medical_record_id=request.medical_record_id,
        title=request.title,
    )


@router.get(
    "/",
    response_model=list[ChatSessionListResponse],
    summary="List chat sessions",
    description="Returns all chat sessions for the authenticated user.",
)
def list_chat_sessions(
    db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)
):
    return get_user_sessions(db=db, user_id=current_user.id)


@router.get(
    "/{session_id}",
    response_model=ChatSessionResponse,
    summary="Get chat session",
    description="Returns a chat session and its metadata.",
    responses={
        200: {"description": "Chat session retrieved successfully"},
        404: {"description": "Chat session not found"},
    },
)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    session = get_session(db=db, session_id=session_id, user_id=current_user.id)

    if session is None:

        raise HTTPException(status_code=404, detail="Chat session not found.")

    return session


@router.delete(
    "/{session_id}",
    summary="Delete chat session",
    description="Deletes a chat session.",
    responses={
        200: {"description": "Chat session deleted successfully"},
        404: {"description": "Chat session not found"},
    },
)
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    session = get_session(db=db, session_id=session_id, user_id=current_user.id)

    if session is None:

        raise HTTPException(status_code=404, detail="Chat session not found.")

    return delete_session(db=db, session=session)

@router.get(
    "/{session_id}/messages",
    response_model=list[ChatMessageResponse],
    summary="Conversation history",
)
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return get_session_messages(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )


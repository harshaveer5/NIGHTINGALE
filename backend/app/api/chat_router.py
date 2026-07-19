from app.api.users import get_current_user
from app.db.dependencies import get_db
from app.models.user import Users
from app.schemas.chat import ChatRequest, ChatResponse 
from app.schemas.chat_session import ChatSessionResponse
from app.services.chat_service import ask_question
from app.services.chat_session_service import get_or_create_latest_session
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Chat with NIGHTINGALE",
    description=(
        "Interact with NIGHTINGALE to understand uploaded medical "
        "documents using patient-scoped Retrieval-Augmented "
        "Generation (RAG). Supports report summaries, document "
        "comparison, follow-up questions, and source citations."
    ),
    responses={
        200: {"description": "Response generated successfully"},
        400: {"description": "Invalid chat request"},
        401: {"description": "Authentication required"},
        404: {"description": "Requested document or medical record not found"},
        422: {"description": "Validation error"},
    },
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return ask_question(
        session_id=request.session_id,
        question=request.question,
        user_id=current_user.id,
        medical_record_id=request.medical_record_id,
        db=db,
    )

@router.get(
    "/latest/{medical_record_id}",
    response_model=ChatSessionResponse,
)
def latest_session(
    medical_record_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return get_or_create_latest_session(
        db=db,
        user_id=current_user.id,
        medical_record_id=medical_record_id,
    )
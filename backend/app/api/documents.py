from urllib.parse import quote

from app.api.users import get_current_user
from app.db.dependencies import get_db
from app.models.user import Users
from app.schemas.documents import DocumentResponse
from app.schemas.qdran import SearchRequest
from app.services.document_service import (
    delete_document,
    get_document,
    get_document_dashboard,
    get_document_media_type,
    get_document_text,
    get_user_documents,
    process_document_upload,
    resolve_document_file_path,
)
from app.services.embedding_service import embed_document
from app.services.retrival_service import retrieve_chunks
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=201,
    summary="Upload a medical document",
    description="Uploads a medical document, extracts its text, and stores its metadata.",
    responses={
        201: {"description": "Document uploaded successfully"},
        400: {"description": "Invalid upload request"},
        401: {"description": "Authentication required"},
        404: {"description": "Medical record not found"},
    },
)
def upload_document(
    medical_record_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return process_document_upload(
        db=db, file=file, medical_record_id=medical_record_id, user_id=current_user.id
    )


@router.get(
    "/",
    response_model=list[DocumentResponse],
    summary="List documents",
    description="Returns all documents belonging to the authenticated user. Optionally filter by medical record.",
    responses={
        200: {"description": "Documents retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
def list_documents(
    medical_record_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return get_user_documents(
        db=db, user_id=current_user.id, medical_record_id=medical_record_id
    )


@router.get(
    "/dashboard",
    summary="Document dashboard",
    description="Returns a dashboard summary of the user's uploaded medical documents.",
)
def get_document_dashboard_route(
    db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)
):
    return get_document_dashboard(db=db, user_id=current_user.id)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get a document",
    description="Returns metadata for a specific medical document.",
    responses={
        200: {"description": "Document retrieved successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Document not found"},
    },
)
def get_single_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return get_document(db=db, document_id=document_id, user_id=current_user.id)


@router.get(
    "/{document_id}/file",
    summary="Preview document",
    description="Streams the original uploaded document for inline viewing.",
)
def preview_document_file(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    document = get_document(db=db, document_id=document_id, user_id=current_user.id)
    file_path = resolve_document_file_path(document)
    encoded_filename = quote(document.filename)

    return FileResponse(
        path=str(file_path),
        media_type=get_document_media_type(document),
        headers={
            "Content-Disposition": (f"inline; filename*=UTF-8''{encoded_filename}")
        },
    )


@router.get(
    "/{document_id}/download",
    summary="Download document",
    description="Downloads the original uploaded medical document.",
)
def download_document_file(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    document = get_document(db=db, document_id=document_id, user_id=current_user.id)
    file_path = resolve_document_file_path(document)
    encoded_filename = quote(document.filename)

    return FileResponse(
        path=str(file_path),
        media_type=get_document_media_type(document),
        headers={
            "Content-Disposition": (f"attachment; filename*=UTF-8''{encoded_filename}")
        },
    )


@router.delete(
    "/{document_id}",
    summary="Delete a document",
    description="Deletes a medical document and its associated metadata.",
    responses={
        200: {"description": "Document deleted successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Document not found"},
    },
)
def delete_document_route(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    document = get_document(db=db, document_id=document_id, user_id=current_user.id)

    return delete_document(db=db, document=document)


@router.get(
    "/{document_id}/ocr",
    summary="Get OCR text",
    description="Returns the extracted OCR text for a medical document.",
)
def get_ocr_text(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    get_document(db=db, document_id=document_id, user_id=current_user.id)

    return get_document_text(db=db, document_id=document_id)


@router.post(
    "/{document_id}/embed",
    summary="Generate embeddings",
    description="Generates vector embeddings for a document's extracted text.",
)
def embed_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return embed_document(db=db, document_id=document_id, user_id=current_user.id)


@router.post(
    "/search",
    summary="Semantic document search",
    description="Searches document chunks using semantic vector similarity.",
)
def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return retrieve_chunks(
        query=request.query,
        user_id=current_user.id,
        medical_record_id=request.medical_record_id,
        db=db,
    )

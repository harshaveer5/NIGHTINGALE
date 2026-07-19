import mimetypes
import os
import shutil
import uuid
from pathlib import Path

from app.core.logging import logger
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_text import DocumentText
from app.models.medical_record import MedicalRecord
from app.services.chunking_service import chunk_text
from app.services.metadata_service import extract_metadata
from app.services.ocr_service import extract_text_from_image
from app.services.pdf_service import extract_text_from_pdf
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads"


def validate_medical_record(db: Session, medical_record_id: int, user_id: int):
    medical_record = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == medical_record_id, MedicalRecord.user_id == user_id)
        .first()
    )

    if not medical_record:
        raise HTTPException(status_code=404, detail="Patient not found")

    return medical_record


def save_uploaded_file(file: UploadFile):
    allowed_types = [".pdf", ".png", ".jpg", ".jpeg"]

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    UPLOAD_DIR.mkdir(exist_ok=True)

    unique_filename = f"{uuid.uuid4()}-{file.filename}"

    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return (file_extension, unique_filename, str(file_path))


def extract_document_text(file_extension: str, file_path: str):
    if file_extension == ".pdf":
        extracted_text = extract_text_from_pdf(file_path)
    else:
        ocr_result = extract_text_from_image(file_path)

        extracted_text = ocr_result["text"]

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted.")

    return extracted_text


def create_document(
    db: Session,
    user_id: int,
    medical_record_id: int,
    filename: str,
    stored_filename: str,
    file_type: str,
    file_path: str,
):
    document = Document(
        user_id=user_id,
        medical_record_id=medical_record_id,
        filename=filename,
        stored_filename=stored_filename,
        file_type=file_type,
        file_path=file_path,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def save_document_text(db: Session, document_id: int, extracted_text: str):
    document_text = DocumentText(document_id=document_id, extracted_text=extracted_text)

    db.add(document_text)
    db.commit()

    return document_text


def create_chunks(db: Session, document_id: int, extracted_text: str):
    chunks = chunk_text(extracted_text)

    for index, chunk in enumerate(chunks):

        document_chunk = DocumentChunk(
            document_id=document_id, chunk_index=index, chunk_text=chunk
        )

        db.add(document_chunk)

    db.commit()

    return chunks


def process_document_upload(
    db: Session, file: UploadFile, medical_record_id: int, user_id: int
):

    logger.info(
        "Document upload started",
        extra={
            "user_id": user_id,
            "patient_id": medical_record_id,
            "document_name": file.filename,
        },
    )
    validate_medical_record(db, medical_record_id, user_id)

    file_extension, unique_filename, file_path = save_uploaded_file(file)

    extracted_text = extract_document_text(file_extension, file_path)

    logger.info("Text extraction completed", extra={"characters": len(extracted_text)})

    metadata = extract_metadata(extracted_text)

    document = create_document(
        db=db,
        user_id=user_id,
        medical_record_id=medical_record_id,
        filename=file.filename,
        stored_filename=unique_filename,
        file_type=file_extension,
        file_path=file_path,
    )

    logger.info(
        "Document stored",
        extra={"document_id": document.id, "document_name": document.filename},
    )

    logger.info("Document upload completed", extra={"document_id": document.id})

    document.document_type = metadata["document_type"]
    document.report_date = metadata["report_date"]

    db.commit()
    db.refresh(document)

    save_document_text(db=db, document_id=document.id, extracted_text=extracted_text)

    chunks = create_chunks(
        db=db, document_id=document.id, extracted_text=extracted_text
    )

    logger.info(
        "Chunking completed",
        extra={"document_id": document.id, "chunk_count": len(chunks)},
    )

    return document


def get_document(db: Session, document_id: int, user_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return document


def get_user_documents(db: Session, user_id: int, medical_record_id: int | None = None):
    query = db.query(Document).filter(Document.user_id == user_id)

    if medical_record_id is not None:
        query = query.filter(Document.medical_record_id == medical_record_id)

    return query.order_by(Document.uploaded_at.desc()).all()


def resolve_document_file_path(document: Document) -> Path:
    file_path = Path(document.file_path or "")

    if not file_path.is_absolute():
        file_path = BACKEND_DIR / file_path

    resolved_path = file_path.resolve()
    resolved_upload_dir = UPLOAD_DIR.resolve()

    if resolved_upload_dir not in resolved_path.parents:
        raise HTTPException(status_code=403, detail="Document file path is not allowed")

    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")

    return resolved_path


def get_document_media_type(document: Document) -> str:
    media_type, _ = mimetypes.guess_type(document.filename)

    if media_type:
        return media_type

    if document.file_type == ".pdf":
        return "application/pdf"

    if document.file_type in [".jpg", ".jpeg"]:
        return "image/jpeg"

    if document.file_type == ".png":
        return "image/png"

    return "application/octet-stream"


def get_document_dashboard(db: Session, user_id: int):
    documents = (
        db.query(Document)
        .options(joinedload(Document.medical_record))
        .filter(Document.user_id == user_id)
        .all()
    )

    response = []

    for document in documents:

        response.append(
            {
                "document_id": document.id,
                "filename": document.filename,
                "file_type": document.file_type,
                "document_type": document.document_type,
                "report_date": document.report_date,
                "uploaded_at": document.uploaded_at,
                "patient": {
                    "medical_record_id": document.medical_record.id,
                    "patient_name": document.medical_record.patient_name,
                    "age": document.medical_record.age,
                    "gender": document.medical_record.gender,
                },
            }
        )

    return response


def delete_document(db: Session, document: Document):
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}


def get_document_text(db: Session, document_id: int):
    text = (
        db.query(DocumentText).filter(DocumentText.document_id == document_id).first()
    )

    if not text:
        return {"extracted_text": ""}

    return {"extracted_text": text.extracted_text}

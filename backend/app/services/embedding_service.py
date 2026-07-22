from app.core.logging import logger
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.qdrant_service import upload_chunk_embedding
from fastapi import HTTPException
from sqlalchemy.orm import Session

_model = None


_model = None


def get_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model...")

        _model = SentenceTransformer("all-MiniLM-L6-v2")

        logger.info("Embedding model loaded.")

    return _model



def generate_embedding(text: str):
    return get_model().encode(text).tolist()


def embed_document(db: Session, document_id: int, user_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    chunks = (
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
    )

    embedded_count = 0

    logger.info("Embedding generation started", extra={"document_id": document.id})

    for chunk in chunks:

        vector = generate_embedding(chunk.chunk_text)

        upload_chunk_embedding(
            chunk_id=chunk.id,
            vector=vector,
            user_id=user_id,
            medical_record_id=document.medical_record_id,
            document_id=document.id,
            chunk_index=chunk.chunk_index,
        )

        embedded_count += 1

        logger.info(
            "Embedding upload completed",
            extra={"document_id": document.id, "chunks": embedded_count},
        )

    return {
        "message": "Embeddings uploaded successfully",
        "chunks_embedded": embedded_count,
    }

from app.services.retrival_service import retrieve_chunks
from sqlalchemy.orm import Session


def run(
    query: str,
    user_id: int,
    medical_record_id: int,
    db: Session,
    document_ids: list[int] | None = None,
    limit: int = 10,
    trace=None,
):
    chunks = retrieve_chunks(
        query=query,
        user_id=user_id,
        medical_record_id=medical_record_id,
        db=db,
        document_ids=document_ids,
        limit=limit,
        trace=trace,
    )

    return chunks

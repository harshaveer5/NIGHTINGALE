from contextlib import contextmanager

from app.core.logging import logger
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding
from app.services.qdrant_service import search_chunks
from sqlalchemy.orm import Session

MIN_RETRIEVAL_SCORE = 0.15


@contextmanager
def _null_stage():
    yield


def retrieve_chunks(
    query: str,
    user_id: int,
    medical_record_id: int,
    db: Session,
    document_ids: list[int] | None = None,
    limit: int = 10,
    trace=None,
):

    if trace:
        with trace.stage("Embedding Generation"):
            query_vector = generate_embedding(query)
    else:
        query_vector = generate_embedding(query)

    if trace:
        with trace.stage(
            "Semantic Retrieval", document_filter=bool(document_ids), limit=limit
        ):
            results = search_chunks(
                query_vector=query_vector,
                user_id=user_id,
                medical_record_id=medical_record_id,
                document_ids=document_ids,
                limit=limit,
            )
    else:
        results = search_chunks(
            query_vector=query_vector,
            user_id=user_id,
            medical_record_id=medical_record_id,
            document_ids=document_ids,
            limit=limit,
        )

    if trace:
        with trace.stage("Retrieval Score Filter", result_count=len(results.points)):
            valid_points = [
                point for point in results.points if point.score >= MIN_RETRIEVAL_SCORE
            ]
    else:
        valid_points = [
            point for point in results.points if point.score >= MIN_RETRIEVAL_SCORE
        ]

    if not valid_points:
        return []

    chunk_ids = [point.id for point in valid_points]

    if trace:
        with trace.stage(
            "Metadata Filtering",
            chunk_id_count=len(chunk_ids),
            document_filter=bool(document_ids),
        ):
            db_query = (
                db.query(DocumentChunk, Document)
                .join(Document, Document.id == DocumentChunk.document_id)
                .filter(DocumentChunk.id.in_(chunk_ids))
            )

            if document_ids:
                db_query = db_query.filter(DocumentChunk.document_id.in_(document_ids))

            db_results = db_query.all()
    else:
        db_query = (
            db.query(DocumentChunk, Document)
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(DocumentChunk.id.in_(chunk_ids))
        )

        if document_ids:
            db_query = db_query.filter(DocumentChunk.document_id.in_(document_ids))

        db_results = db_query.all()

    chunk_lookup = {chunk.id: (chunk, document) for chunk, document in db_results}

    retrieved_chunks = []

    seen_chunk_ids = set()

    with (
        trace.stage(
            "Duplicate Removal",
            valid_point_count=len(valid_points),
            db_result_count=len(db_results),
        )
        if trace
        else _null_stage()
    ):
        for point in valid_points:

            result = chunk_lookup.get(point.id)

            if result is None:
                continue

            chunk, document = result

            if chunk.id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk.id)

            retrieved_chunks.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "filename": document.filename,
                    "chunk_index": chunk.chunk_index,
                    "score": float(point.score),
                    "chunk_text": chunk.chunk_text,
                }
            )

    logger.info(
        "Semantic retrieval completed",
        extra={"query": query, "retrieved_chunks": len(retrieved_chunks)},
    )

    return retrieved_chunks

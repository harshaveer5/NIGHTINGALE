import os

from app.core.logging import logger
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

# for serachinge service
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

load_dotenv()


client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))


def create_medical_collection():

    client.create_collection(
        collection_name="medical_chunks",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )


def upload_chunk_embedding(
    chunk_id: int,
    vector: list,
    user_id: int,
    document_id: int,
    chunk_index: int,
    medical_record_id: int,
):
    client.upsert(
        collection_name="medical_chunks",
        points=[
            PointStruct(
                id=chunk_id,
                vector=vector,
                payload={
                    "user_id": user_id,
                    "document_id": document_id,
                    "medical_record_id": medical_record_id,
                    # "document_type": document.document_type,
                    "chunk_index": chunk_index,
                },
            )
        ],
    )


def get_collection_info():
    return client.get_collection(collection_name="medical_chunks")


def search_chunks(
    query_vector: list,
    user_id: int,
    medical_record_id: int,
    limit: int = 10,
    document_ids: list[int] | None = None,
):
    base_filters = [
        FieldCondition(key="user_id", match=MatchValue(value=user_id)),
        FieldCondition(
            key="medical_record_id", match=MatchValue(value=medical_record_id)
        ),
    ]

    filters = list(base_filters)

    if document_ids:
        filters.append(
            FieldCondition(key="document_id", match=MatchValue(value=document_ids[0]))
        )

    try:
        results = client.query_points(
            collection_name="medical_chunks",
            query=query_vector,
            limit=limit,
            query_filter=Filter(must=filters),
        )
    except UnexpectedResponse as exc:
        if not (
            document_ids and "Index required" in str(exc) and "document_id" in str(exc)
        ):
            raise

        results = client.query_points(
            collection_name="medical_chunks",
            query=query_vector,
            limit=limit,
            query_filter=Filter(must=base_filters),
        )

    return results


def create_payload_indexes():
    indexed_fields = [
        "user_id",
        "medical_record_id",
        "document_id",
    ]

    for field_name in indexed_fields:
        try:
            client.create_payload_index(
                collection_name="medical_chunks",
                field_name=field_name,
                field_schema=PayloadSchemaType.INTEGER,
            )
        except UnexpectedResponse as exc:
            if "already exists" not in str(exc).lower():
                raise

    logger.info("Qdrant payload indexes ensured | fields=%s", indexed_fields)

from app.core.logging import logger
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from sqlalchemy.orm import Session

REPORT_TYPE_HINTS = {
    "CBC": [
        "cbc",
        "complete blood count",
        "blood count",
        "hemoglobin",
        "haemoglobin",
        "platelet",
        "wbc",
        "rbc",
        "ferritin",
        "iron",
    ],
    "LIPID_PROFILE": [
        "lipid",
        "cholesterol",
        "ldl",
        "hdl",
        "triglyceride",
    ],
    "DIABETES_MONITORING": [
        "diabetes",
        "glucose",
        "hba1c",
        "blood sugar",
        "microalbumin",
    ],
    "PRESCRIPTION": [
        "medicine",
        "medication",
        "prescription",
        "tablet",
        "dose",
        "dosage",
    ],
    "KFT": [
        "kidney",
        "renal",
        "creatinine",
        "egfr",
        "urea",
    ],
    "LFT": [
        "liver",
        "bilirubin",
        "sgpt",
        "sgot",
        "alt",
        "ast",
    ],
    "THYROID": [
        "thyroid",
        "tsh",
        "t3",
        "t4",
    ],
    "XRAY": [
        "xray",
        "x-ray",
        "radiology",
        "chest",
        "knee",
    ],
}

DOCUMENT_TYPE_PRIORITY = [
    "PRESCRIPTION",
    "LIPID_PROFILE",
    "DIABETES_MONITORING",
    "CBC",
    "KFT",
    "LFT",
    "THYROID",
    "XRAY",
]


def infer_report_type_from_question(question: str) -> str | None:
    question_lower = question.lower()

    for report_type, hints in REPORT_TYPE_HINTS.items():
        if any(hint in question_lower for hint in hints):
            return report_type

    return None


def infer_report_type_from_document(document: Document) -> str | None:
    searchable_text = " ".join(
        [
            document.filename or "",
            document.document_type or "",
        ]
    ).lower()

    for report_type in DOCUMENT_TYPE_PRIORITY:
        hints = REPORT_TYPE_HINTS[report_type]

        if any(hint in searchable_text for hint in hints):
            return report_type

    return None


def get_display_document_type(document: Document) -> str | None:
    return infer_report_type_from_document(document) or document.document_type


def _document_matches_report_type(document: Document, report_type: str | None) -> bool:
    if not report_type:
        return True

    filename = (document.filename or "").lower()
    document_type = (document.document_type or "").upper()
    normalized_report_type = report_type.upper()

    if normalized_report_type == "DIABETES_MONITORING":
        return (
            "diabetes" in filename
            or "glucose" in filename
            or "HBA1C" in document_type
            or "DIABETES" in document_type
        )

    if normalized_report_type == "PRESCRIPTION":
        return (
            "prescription" in filename
            or "medication" in filename
            or "plan" in filename
            or "PRESCRIPTION" in document_type
        )

    if normalized_report_type in document_type:
        return True

    return normalized_report_type.lower() in filename


def get_latest_document(db: Session, user_id: int, medical_record_id: int):
    """
    Returns the most recently uploaded document
    for the selected patient.
    """

    return (
        db.query(Document)
        .filter(
            Document.user_id == user_id, Document.medical_record_id == medical_record_id
        )
        .order_by(Document.uploaded_at.desc())
        .first()
    )


def list_patient_documents(db: Session, user_id: int, medical_record_id: int):
    return (
        db.query(Document)
        .filter(
            Document.user_id == user_id, Document.medical_record_id == medical_record_id
        )
        .order_by(Document.uploaded_at.desc())
        .all()
    )


def select_document(
    db: Session,
    question: str,
    user_id: int,
    medical_record_id: int,
    active_document_id: int | None = None,
):
    documents = list_patient_documents(
        db=db, user_id=user_id, medical_record_id=medical_record_id
    )

    if not documents:
        return None

    question_lower = question.lower()
    requested_report_type = infer_report_type_from_question(question)

    for document in documents:
        filename = (document.filename or "").lower()
        document_type = (document.document_type or "").lower()

        if requested_report_type and _document_matches_report_type(
            document=document, report_type=requested_report_type
        ):
            return document

        if filename and filename in question_lower:
            return document

        if document_type and document_type.replace("_", " ") in question_lower:
            return document

    if active_document_id:
        for document in documents:
            if document.id == active_document_id:
                return document

    latest_markers = [
        "latest",
        "last report",
        "recent",
        "newest",
        "this report",
        "this document",
        "this paper",
    ]

    if any(marker in question_lower for marker in latest_markers):
        return documents[0]

    return documents[0]


def select_compare_documents(
    db: Session, question: str, user_id: int, medical_record_id: int, limit: int = 2
):
    documents = list_patient_documents(
        db=db, user_id=user_id, medical_record_id=medical_record_id
    )

    requested_report_type = infer_report_type_from_question(question)

    if requested_report_type:
        matching_documents = [
            document
            for document in documents
            if _document_matches_report_type(
                document=document, report_type=requested_report_type
            )
        ]

        if len(matching_documents) >= limit:
            return matching_documents[:limit]

    logger.info(
        "Compare document selection completed",
        extra={
            "user_id": user_id,
            "medical_record_id": medical_record_id,
            "report_type": requested_report_type,
            "returned_documents": [doc.id for doc in documents[:limit]],
        },
    )

    return documents[:limit]


def get_document_chunks(db: Session, document_id: int):
    """
    Returns every chunk belonging to a document,
    ordered exactly as it appears in the report.
    """

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )

    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "filename": chunk.document.filename if chunk.document else None,
            "chunk_index": chunk.chunk_index,
            "score": 1.0,
            "chunk_text": chunk.chunk_text,
        }
        for chunk in chunks
    ]

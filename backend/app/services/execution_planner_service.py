from typing import Dict, List

from app.core.logging import logger
from app.services.conversation_state_service import is_ambiguous_follow_up
from app.services.document_selector_service import (
    get_display_document_type,
    select_compare_documents,
    select_document,
)
from sqlalchemy.orm import Session

SUMMARY_MARKERS = {
    "summarize",
    "summary",
    "overview",
    "what happened",
    "what does this report say",
    "what is this paper about",
    "medical story",
    "summarize everything",
}

COMPARE_MARKERS = {
    "compare",
    "changed",
    "change",
    "improved",
    "worse",
    "previous",
    "since last time",
}

DOCUMENT_LIST_MARKERS = {
    "what reports do i have",
    "which reports",
    "show me my reports",
    "list reports",
}


def _contains_any(question: str, markers: set[str]) -> bool:
    question_lower = question.lower()
    return any(marker in question_lower for marker in markers)


def normalize_intent(intent: str, question: str) -> str:
    if _contains_any(question, COMPARE_MARKERS):
        return "COMPARE_REPORTS"

    if _contains_any(question, DOCUMENT_LIST_MARKERS):
        return "DOCUMENT_LIST"

    if _contains_any(question, SUMMARY_MARKERS):
        return "REPORT_SUMMARY"

    return intent


def build_execution_plan(
    db: Session,
    question: str,
    decision: Dict,
    user_id: int,
    medical_record_id: int,
    conversation_state: Dict,
    trace=None,
) -> Dict:
    intent = normalize_intent(intent=decision["intent"], question=question)

    route = decision["route"]
    selected_documents: List = []
    retrieval_strategy = "none"
    needs_semantic_retrieval = False
    needs_metadata_retrieval = False
    needs_query_rewrite = intent == "OUT_OF_SCOPE" and is_ambiguous_follow_up(question)

    if intent == "REPORT_SUMMARY":
        route = "PATIENT_RAG"
        if trace:
            with trace.stage("Document Selection", intent=intent):
                document = select_document(
                    db=db,
                    question=question,
                    user_id=user_id,
                    medical_record_id=medical_record_id,
                    active_document_id=conversation_state.get("active_document"),
                )
        else:
            document = select_document(
                db=db,
                question=question,
                user_id=user_id,
                medical_record_id=medical_record_id,
                active_document_id=conversation_state.get("active_document"),
            )
        selected_documents = [document] if document else []
        retrieval_strategy = "full_document"

    elif intent == "COMPARE_REPORTS":
        route = "PATIENT_RAG"
        if trace:
            with trace.stage("Document Selection", intent=intent):
                selected_documents = select_compare_documents(
                    db=db,
                    question=question,
                    user_id=user_id,
                    medical_record_id=medical_record_id,
                )
        else:
            selected_documents = select_compare_documents(
                db=db,
                question=question,
                user_id=user_id,
                medical_record_id=medical_record_id,
            )
        retrieval_strategy = "compare_documents"

    elif intent == "DOCUMENT_LIST":
        route = "PATIENT_RAG"
        if trace:
            with trace.stage("Metadata Filtering", intent=intent):
                needs_metadata_retrieval = True
                retrieval_strategy = "metadata"
        else:
            needs_metadata_retrieval = True
            retrieval_strategy = "metadata"

    elif intent == "PATIENT_QA":
        route = "PATIENT_RAG"
        if trace:
            with trace.stage("Document Selection", intent=intent):
                document = select_document(
                    db=db,
                    question=question,
                    user_id=user_id,
                    medical_record_id=medical_record_id,
                    active_document_id=conversation_state.get("active_document"),
                )
        else:
            document = select_document(
                db=db,
                question=question,
                user_id=user_id,
                medical_record_id=medical_record_id,
                active_document_id=conversation_state.get("active_document"),
            )
        selected_documents = [document] if document else []
        needs_semantic_retrieval = True
        retrieval_strategy = "semantic"

    elif intent == "GENERAL_HEALTH":
        route = "GENERAL_HEALTH"
        retrieval_strategy = "none"

    logger.info(
        "Execution plan created",
        extra={"intent": intent, "strategy": retrieval_strategy, "route": route},
    )

    return {
        "intent": intent,
        "route": route,
        "confidence": decision["confidence"],
        "retrieval_strategy": retrieval_strategy,
        "selected_document_ids": [
            document.id for document in selected_documents if document
        ],
        "selected_documents": [
            {
                "document_id": document.id,
                "filename": document.filename,
                "document_type": get_display_document_type(document),
                "report_date": document.report_date,
            }
            for document in selected_documents
            if document
        ],
        "needs_semantic_retrieval": needs_semantic_retrieval,
        "needs_metadata_retrieval": needs_metadata_retrieval,
        "needs_query_rewrite": needs_query_rewrite,
        "query": question,
    }

from app.core.logging import logger

logger.info("RAG A - importing contextmanager")
from contextlib import contextmanager

logger.info("RAG B - importing retrieval_pipeline")
from app.pipelines.retrival_pipeline import run as retrieve

logger.info("RAG C - importing context_builder")
from app.services.context_builder import build_context

logger.info("RAG D - importing conversation_state_service")
from app.services.conversation_state_service import format_structured_section

logger.info("RAG E - importing document_selector_service")
from app.services.document_selector_service import get_document_chunks

logger.info("RAG F - importing llm_service")
from app.services.llm_service import generate_chat_answer

logger.info("RAG G - importing patient_context_service")
from app.services.patient_context_service import build_patient_context

logger.info("RAG H - importing prompt_builder")
from app.services.prompt_builder import build_prompt

logger.info("RAG I - importing SQLAlchemy")
from sqlalchemy.orm import Session

logger.info("RAG IMPORT COMPLETE")


@contextmanager
def _null_stage():
    yield


def run(
    question: str,
    execution_plan: dict,
    structured_memory: dict,
    conversation_state: dict,
    user_id: int,
    medical_record_id: int,
    db: Session,
    trace=None,
):
    chunks = []
    active_state = dict(conversation_state)

    if execution_plan["selected_documents"]:
        current_document = execution_plan["selected_documents"][0]
        active_state.update(
            {
                "active_document": current_document["document_id"],
                "active_document_name": current_document["filename"],
                "active_report_type": current_document["document_type"],
            }
        )

    if execution_plan["retrieval_strategy"] in ["full_document", "compare_documents"]:
        with (
            trace.stage(
                "Document Retrieval",
                strategy=execution_plan["retrieval_strategy"],
                document_count=len(execution_plan["selected_documents"]),
            )
            if trace
            else _null_stage()
        ):
            for document in execution_plan["selected_documents"]:
                document_chunks = get_document_chunks(
                    db=db, document_id=document["document_id"]
                )

                for chunk in document_chunks:
                    chunk["filename"] = document["filename"]

                chunks.extend(document_chunks)

    elif execution_plan["retrieval_strategy"] == "semantic":

        chunks = retrieve(
            query=execution_plan["query"],
            user_id=user_id,
            medical_record_id=medical_record_id,
            document_ids=execution_plan["selected_document_ids"],
            db=db,
            trace=trace,
        )

    elif execution_plan["retrieval_strategy"] == "metadata":
        with trace.stage("Metadata Retrieval") if trace else _null_stage():
            chunks = [
                {
                    "chunk_id": document["document_id"],
                    "document_id": document["document_id"],
                    "filename": document["filename"],
                    "chunk_index": 0,
                    "score": 1.0,
                    "chunk_text": (
                        f"Document: {document['filename']}\n"
                        f"Type: {document.get('document_type') or 'Unknown'}\n"
                        f"Report Date: {document.get('report_date') or 'Unknown'}"
                    ),
                }
                for document in conversation_state.get("available_documents", [])
            ]

        with trace.stage("Source Formatting") if trace else _null_stage():
            sources = [
                {
                    "document_id": chunk["document_id"],
                    "filename": chunk["filename"],
                    "chunk_index": chunk["chunk_index"],
                }
                for chunk in chunks
            ]

        with trace.stage("Deterministic Document List") if trace else _null_stage():
            if chunks:
                lines = ["You have the following documents:"]

                for index, chunk in enumerate(chunks, start=1):
                    metadata = {}

                    for line in chunk["chunk_text"].splitlines():
                        if ": " not in line:
                            continue

                        key, value = line.split(": ", 1)
                        metadata[key] = value

                    lines.append(
                        (
                            f"{index}. {metadata.get('Document', chunk['filename'])} "
                            f"({metadata.get('Type', 'Unknown')}) - "
                            f"Report Date: {metadata.get('Report Date', 'Unknown')}"
                        )
                    )

                answer = "\n".join(lines)
            else:
                answer = "No uploaded documents were found for this patient."

        return {
            "answer": answer,
            "sources": sources,
            "chunks_used": len(chunks),
            "retrieved_chunks": chunks,
            "execution_plan": execution_plan,
            "response_source": "deterministic_metadata",
        }

    patient_context = ""

    if execution_plan["intent"] != "GENERAL_HEALTH":
        with trace.stage("Patient Profile") if trace else _null_stage():
            patient_context = build_patient_context(
                db=db, medical_record_id=medical_record_id, user_id=user_id
            )

    with (
        trace.stage("Context Builder", chunk_count=len(chunks))
        if trace
        else _null_stage()
    ):
        document_context = build_context(retrieved_chunks=chunks)

        active_document = format_structured_section(
            "Active document",
            {
                "document_id": active_state.get("active_document"),
                "filename": active_state.get("active_document_name"),
                "report_type": active_state.get("active_report_type"),
            },
        )

        memory = format_structured_section("Structured memory", structured_memory)

    with (
        trace.stage(
            "Prompt Builder",
            document_context_chars=len(document_context),
            patient_profile_chars=len(patient_context),
        )
        if trace
        else _null_stage()
    ):
        prompt = build_prompt(
            question=question,
            patient_profile=patient_context,
            active_document=active_document,
            document_context=document_context,
            structured_memory=memory,
        )

    answer = generate_chat_answer(prompt, trace=trace)

    # Build citations from retrieved chunks
    with trace.stage("Source Formatting") if trace else _null_stage():
        sources = []

        for chunk in chunks:
            sources.append(
                {
                    "document_id": chunk["document_id"],
                    "filename": chunk["filename"],
                    "chunk_index": chunk["chunk_index"],
                }
            )

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(chunks),
        "retrieved_chunks": chunks,
        "execution_plan": execution_plan,
    }

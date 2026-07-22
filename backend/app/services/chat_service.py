from app.core.logging import logger

logger.info("CHAT_SERVICE A - importing perf_counter")
from time import perf_counter

logger.info("CHAT_SERVICE B - importing config")
from app.core.config import CHAT_RATE_LIMIT, CHAT_RATE_WINDOW

logger.info("CHAT_SERVICE C - importing rate limiter")
from app.core.rate_limiter import rate_limiter

logger.info("CHAT_SERVICE D - importing rag_pipeline")
from app.pipelines.rag_pipeline import run as rag_pipeline

logger.info("CHAT_SERVICE E - importing cached_response_service")
from app.services.cached_response_service import get_cached_response

logger.info("CHAT_SERVICE F - importing chat_session_service")
from app.services.chat_session_service import (
    get_recent_messages,
    save_message,
    validate_chat_session,
    get_or_create_latest_session,
)

logger.info("CHAT_SERVICE G - importing conversation_builder")
from app.services.conversation_builder import build_conversation_context

logger.info("CHAT_SERVICE H - importing conversation_state_service")
from app.services.conversation_state_service import (
    build_conversation_state,
    build_structured_memory,
)

logger.info("CHAT_SERVICE I - importing execution_planner_service")
from app.services.execution_planner_service import build_execution_plan

logger.info("CHAT_SERVICE J - importing latency_service")
from app.services.latency_service import LatencyTrace

logger.info("CHAT_SERVICE K - importing query_rewriter_service")
from app.services.query_rewriter_service import rewrite_question

logger.info("CHAT_SERVICE L - importing router_service")
from app.services.router_service import route_question

logger.info("CHAT_SERVICE M - importing FastAPI dependencies")
from fastapi import HTTPException

logger.info("CHAT_SERVICE N - importing SQLAlchemy")
from sqlalchemy.orm import Session

logger.info("CHAT_SERVICE IMPORT COMPLETE")


def persist_message(db: Session, session_id: int, role: str, content: str):
    """
    Wrapper around save_message().
    Keeps all message persistence in one place so
    future metadata (citations, latency, tokens, etc.)
    can be added without changing chat logic.
    """

    save_message(db=db, session_id=session_id, role=role, content=content)


def suggest_questions(intent: str):
    suggestions = {
        "PATIENT_QA": [
            "Summarize this report",
            "Explain abnormal values",
            "Show medications",
        ],
        "REPORT_SUMMARY": [
            "Explain important findings",
            "Show abnormal values",
            "Compare previous report",
        ],
        "COMPARE_REPORTS": [
            "What improved?",
            "What got worse?",
            "Show important changes",
        ],
        "GENERAL_HEALTH": [
            "Tell me more",
            "What causes this?",
            "What should I ask my doctor?",
        ],
    }

    return suggestions.get(intent, [])


def build_warning(intent: str):
    if intent in [
        "MEDICAL_ADVICE",
        "DIAGNOSIS_REQUEST",
    ]:
        return (
            "This assistant provides educational "
            "information only and does not diagnose "
            "or prescribe treatment."
        )

    return None


def _blocked_response(execution_plan: dict):
    return {
        "answer": (
            "I can help explain medical reports, "
            "patient records, and healthcare documents, "
            "but I cannot provide diagnoses, treatment "
            "plans, or medication recommendations."
        ),
        "intent": execution_plan["intent"],
        "confidence": execution_plan["confidence"],
        "sources": [],
        "suggested_questions": [],
        "warning": build_warning(execution_plan["intent"]),
    }


def _out_of_scope_response(execution_plan: dict):
    return {
        "answer": "This question is outside the scope.",
        "intent": execution_plan["intent"],
        "confidence": execution_plan["confidence"],
        "sources": [],
        "suggested_questions": [],
        "warning": build_warning(execution_plan["intent"]),
    }


def ask_question(
    session_id: int | None, 
    question: str, 
    user_id: int, 
    medical_record_id: int, 
    db: Session
):

    rate_limiter.allow(
        key=f"chat:{user_id}", limit=CHAT_RATE_LIMIT, window_seconds=CHAT_RATE_WINDOW
    )

    logger.info(
        "Chat request received",
        extra={
            "session_id": session_id,
            "patient_id": medical_record_id,
            "user_id": user_id,
        },
    )
    started_at = perf_counter()
    trace = LatencyTrace(
        request_label=(f"session={session_id} " f"patient={medical_record_id}")
    )

    with trace.stage("Session Validation"):
        session = validate_chat_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
            medical_record_id=medical_record_id,
        )

    if session_id is None:
        session = get_or_create_latest_session(
            db=db,
            user_id=user_id,
            medical_record_id=medical_record_id,
        )

        session_id = session.id

    with trace.stage("Cached Response Lookup"):
        cached_response = get_cached_response(question)

    if cached_response:
        with trace.stage("Persist User Message"):
            persist_message(db=db, session_id=session_id, role="user", content=question)

        with trace.stage("Response Formatting", response_source="cache"):
            result = {
                "answer": cached_response["answer"],
                "intent": cached_response["intent"],
                "confidence": 1.0,
                "sources": [],
                "suggested_questions": [],
                "warning": cached_response["warning"],
                "response_source": "cache",
            }

        with trace.stage("Persist Assistant Message"):
            persist_message(
                db=db, session_id=session_id, role="assistant", content=result["answer"]
            )

        result["processing_time_ms"] = round((perf_counter() - started_at) * 1000, 2)
        result["latency_trace"] = trace.as_dict()
        trace.log_summary()

        return result

    with trace.stage("Recent Message Load"):
        recent_messages = get_recent_messages(db=db, session_id=session_id, limit=10)

    with trace.stage("Intent Classification"):
        decision = route_question(question)

    with trace.stage("Structured Memory", message_count=len(recent_messages)):
        structured_memory = build_structured_memory(recent_messages)

    with trace.stage("Conversation State"):
        conversation_state = build_conversation_state(
            db=db,
            medical_record_id=medical_record_id,
            user_id=user_id,
            messages=recent_messages,
            intent=decision["intent"],
        )

    with trace.stage("Execution Planner"):
        execution_plan = build_execution_plan(
            db=db,
            question=question,
            decision=decision,
            user_id=user_id,
            medical_record_id=medical_record_id,
            conversation_state=conversation_state,
            trace=trace,
        )

    rewritten_question = question

    if execution_plan["needs_query_rewrite"]:
        with trace.stage("Query Rewrite"):
            conversation_context = build_conversation_context(recent_messages)

            rewritten_question = rewrite_question(
                question=question, conversation_context=conversation_context
            )

        with trace.stage("Intent Classification After Rewrite"):
            decision = route_question(rewritten_question)

        with trace.stage("Execution Planner After Rewrite"):
            execution_plan = build_execution_plan(
                db=db,
                question=rewritten_question,
                decision=decision,
                user_id=user_id,
                medical_record_id=medical_record_id,
                conversation_state=conversation_state,
                trace=trace,
            )

    with trace.stage("Persist User Message"):
        persist_message(db=db, session_id=session_id, role="user", content=question)

    route = execution_plan["route"]

    if route == "BLOCK":
        with trace.stage("Response Formatting"):
            result = _blocked_response(execution_plan)

    elif route in ["PATIENT_RAG", "GENERAL_HEALTH"]:
        rag_result = rag_pipeline(
            question=rewritten_question,
            execution_plan=execution_plan,
            structured_memory=structured_memory,
            conversation_state=conversation_state,
            user_id=user_id,
            medical_record_id=medical_record_id,
            db=db,
            trace=trace,
        )

        with trace.stage(
            "Response Formatting", source_count=len(rag_result.get("sources", []))
        ):
            result = {
                "answer": rag_result["answer"],
                "intent": execution_plan["intent"],
                "confidence": execution_plan["confidence"],
                "sources": rag_result.get("sources", []),
                "suggested_questions": suggest_questions(execution_plan["intent"]),
                "warning": build_warning(execution_plan["intent"]),
                "response_source": rag_result.get("response_source"),
            }

            if route == "GENERAL_HEALTH":
                result["sources"] = []

    else:
        with trace.stage("Response Formatting"):
            result = _out_of_scope_response(execution_plan)

    with trace.stage("Persist Assistant Message"):
        persist_message(
            db=db, session_id=session_id, role="assistant", content=result["answer"]
        )

    result["processing_time_ms"] = round((perf_counter() - started_at) * 1000, 2)
    result["latency_trace"] = trace.as_dict()
    trace.log_summary()

    logger.info(
        "Chat request completed",
        extra={"intent": result["intent"], "confidence": result["confidence"]},
    )

    return result

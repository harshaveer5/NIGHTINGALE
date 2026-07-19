from app.core.config import DEBUG
from app.db.database import SessionLocal
from app.services.llm.provider_factory import get_provider
from app.services.qdrant_service import client
from sqlalchemy import text


def check_database() -> str:

    db = SessionLocal()

    try:

        db.execute(text("SELECT 1"))

        return "healthy"

    except Exception:

        return "unhealthy"

    finally:

        db.close()


def check_qdrant() -> str:

    try:

        client.get_collection(collection_name="medical_chunks")

        return "healthy"

    except Exception:

        return "unhealthy"


def check_llm() -> str:

    try:

        provider = get_provider()

        provider.health_check()

        return "healthy"

    except Exception:

        return "unhealthy"


def get_health():

    database = check_database()

    qdrant = check_qdrant()

    llm = check_llm()

    overall = "healthy"

    if database == "unhealthy" or qdrant == "unhealthy" or llm == "unhealthy":
        overall = "degraded"

    return {
        "status": overall,
        "application": "NIGHTINGALE",
        "version": "1.0.0",
        "environment": ("development" if DEBUG else "production"),
        "services": {"database": database, "qdrant": qdrant, "llm": llm},
    }

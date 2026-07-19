from app.schemas.health import HealthResponse
from app.services.health_service import get_health
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Application health",
    description="Returns the health status of NIGHTINGALE and its dependencies.",
)
def health():

    return get_health()

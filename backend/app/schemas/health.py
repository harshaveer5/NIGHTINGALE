from pydantic import BaseModel


class ServiceStatus(BaseModel):
    database: str
    qdrant: str
    llm: str

    model_config = {
        "json_schema_extra": {
            "example": {"database": "healthy", "qdrant": "healthy", "llm": "healthy"}
        }
    }


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    services: ServiceStatus

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "production",
                "services": {
                    "database": "healthy",
                    "qdrant": "healthy",
                    "llm": "healthy",
                },
            }
        }
    }

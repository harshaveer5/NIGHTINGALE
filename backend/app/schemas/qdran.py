from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    medical_record_id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Compare my latest blood report with the previous one.",
                "medical_record_id": 1,
            }
        }
    }

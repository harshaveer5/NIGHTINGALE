from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    chunk_text: str

    class Config:

        orm_mode = True

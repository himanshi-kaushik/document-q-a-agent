from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    document_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=1000)


class SourceReference(BaseModel):
    source: str
    chunk_index: int
    distance: float


class AskQuestionResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[SourceReference]

from datetime import datetime

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="UUID identifying the user session")
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list[ConversationMessage] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    status: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    uploaded_at: datetime
    public_url: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total_chunks: int


class DeleteDocumentResponse(BaseModel):
    deleted: bool
    document_id: str
    chunks_removed: int


class ClearSessionResponse(BaseModel):
    cleared: bool
    session_id: str
    documents_removed: int
    chunks_removed: int


class HealthResponse(BaseModel):
    status: str
    vector_store: str | None = None
    timestamp: datetime


class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: str | None = None
    request_id: str | None = None

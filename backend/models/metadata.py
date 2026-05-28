from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocumentMetadata:
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    session_id: str
    uploaded_at: datetime
    public_url: str | None = None


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    doc_name: str
    page_number: int
    text: str
    chunk_index: int


@dataclass
class RetrievedChunk:
    chunk_id: str
    doc_id: str
    doc_name: str
    page_number: int
    text: str
    score: float | None = None
    public_url: str | None = None

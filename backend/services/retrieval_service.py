"""Retrieval service."""

from __future__ import annotations

from typing import Optional

try:  # pragma: no cover - import path depends on execution entry point
    from models.metadata import RetrievedChunk
except ModuleNotFoundError:  # pragma: no cover
    from backend.models.metadata import RetrievedChunk


class RetrievalService:
    """Embed a query and retrieve the most relevant chunks from the vector store."""

    def __init__(self, embedding_service, vector_store) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        session_id: str,
        top_k: int = 5,
        doc_ids_filter: Optional[list[str]] = None,
    ) -> list[RetrievedChunk]:
        query_embedding = self.embedding_service.generate_embedding(query)
        return self.vector_store.similarity_search(
            query_embedding=query_embedding,
            session_id=session_id,
            top_k=top_k,
            doc_ids_filter=doc_ids_filter,
        )

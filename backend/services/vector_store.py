"""Vector store service."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import chromadb

try:  # pragma: no cover - import path depends on execution entry point
    from config.settings import get_settings
    from models.metadata import Chunk, RetrievedChunk
except ModuleNotFoundError:  # pragma: no cover
    from backend.config.settings import get_settings
    from backend.models.metadata import Chunk, RetrievedChunk

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage ChromaDB collections scoped to a session id."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = self._build_client()

    def _build_client(self):
        backend = self.settings.CHROMA_BACKEND.strip().lower()
        if backend == "local":
            return chromadb.EphemeralClient()

        if not self.settings.CHROMA_API_KEY or not self.settings.CHROMA_TENANT or not self.settings.CHROMA_DATABASE:
            raise ValueError(
                "Chroma Cloud is enabled but CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE must be set"
            )

        return chromadb.CloudClient(
            tenant=self.settings.CHROMA_TENANT,
            database=self.settings.CHROMA_DATABASE,
            api_key=self.settings.CHROMA_API_KEY,
            cloud_host=self.settings.CHROMA_HOST,
            cloud_port=self.settings.CHROMA_PORT,
            enable_ssl=self.settings.CHROMA_SSL,
        )

    def _collection_name(self, session_id: str) -> str:
        return f"session_{session_id}"

    def get_or_create_collection(self, session_id: str):
        return self.client.get_or_create_collection(name=self._collection_name(session_id))

    def _get_collection(self, session_id: str):
        collection_name = self._collection_name(session_id)
        try:
            return self.client.get_collection(name=collection_name)
        except Exception:
            return None

    def upsert_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
        session_id: str,
        uploaded_at: datetime | None = None,
        public_url: str | None = None,
    ) -> None:
        collection = self.get_or_create_collection(session_id)
        timestamp = uploaded_at or datetime.now(timezone.utc)
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            chunk_batch = chunks[i:i + batch_size]
            emb_batch = embeddings[i:i + batch_size]
            
            collection.upsert(
                ids=[chunk.chunk_id for chunk in chunk_batch],
                embeddings=emb_batch,
                documents=[chunk.text for chunk in chunk_batch],
                metadatas=[
                    {
                        "doc_id": chunk.doc_id,
                        "doc_name": chunk.doc_name,
                        "page_number": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "uploaded_at": timestamp.isoformat(),
                        "public_url": public_url or "",
                    }
                    for chunk in chunk_batch
                ],
            )
        logger.info("Upserted %s chunks into session %s", len(chunks), session_id)

    def get_session_documents(self, session_id: str) -> dict[str, Any]:
        collection = self._get_collection(session_id)
        if collection is None:
            return {}

        payload = collection.get(include=["metadatas"])
        metadatas = payload.get("metadatas", [[]])[0]
        documents: dict[str, Any] = {}

        for metadata in metadatas:
            doc_id = metadata.get("doc_id")
            if not doc_id:
                continue

            existing = documents.get(doc_id)
            page_number = int(metadata.get("page_number", 1))
            uploaded_at_value = metadata.get("uploaded_at")
            uploaded_at = (
                datetime.fromisoformat(uploaded_at_value)
                if isinstance(uploaded_at_value, str)
                else datetime.now(timezone.utc)
            )

            if existing is None:
                documents[doc_id] = {
                    "document_id": doc_id,
                    "filename": metadata.get("doc_name", "document.pdf"),
                    "page_count": page_number,
                    "chunk_count": 1,
                    "session_id": session_id,
                    "uploaded_at": uploaded_at,
                    "public_url": metadata.get("public_url") or None,
                }
            else:
                existing["chunk_count"] += 1
                existing["page_count"] = max(existing["page_count"], page_number)

        return documents

    def similarity_search(
        self,
        query_embedding: list[float],
        session_id: str,
        top_k: int,
        doc_ids_filter: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        collection = self._get_collection(session_id)
        if collection is None:
            return []

        where: dict[str, Any] | None = None
        if doc_ids_filter:
            where = {"doc_id": {"$in": doc_ids_filter}}

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        retrieved_chunks: list[RetrievedChunk] = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            retrieved_chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    doc_id=metadata["doc_id"],
                    doc_name=metadata["doc_name"],
                    page_number=metadata["page_number"],
                    text=document,
                    score=distance,
                    public_url=metadata.get("public_url") or None,
                )
            )

        logger.info("Retrieved %s chunks from session %s", len(retrieved_chunks), session_id)
        return retrieved_chunks

    def delete_by_doc_id(self, doc_id: str, session_id: str) -> int:
        collection = self._get_collection(session_id)
        if collection is None:
            return 0

        before = collection.get(where={"doc_id": doc_id}, include=[])
        chunk_count = len(before.get("ids", []))
        collection.delete(where={"doc_id": doc_id})
        logger.info("Deleted %s chunks for doc %s in session %s", chunk_count, doc_id, session_id)
        return chunk_count

    def delete_collection(self, session_id: str) -> None:
        collection_name = self._collection_name(session_id)
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            return
        logger.info("Deleted collection for session %s", session_id)

    def health_check(self) -> bool:
        self.client.heartbeat()
        return True

from __future__ import annotations

from backend.models.metadata import RetrievedChunk
from backend.services.retrieval_service import RetrievalService


class DummyEmbeddingService:
    def __init__(self) -> None:
        self.seen_queries: list[str] = []

    def generate_embedding(self, text: str) -> list[float]:
        self.seen_queries.append(text)
        return [1.0, 0.0, 0.0]


class DummyVectorStore:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def similarity_search(self, query_embedding, session_id, top_k, doc_ids_filter=None):
        self.calls.append(
            {
                "query_embedding": query_embedding,
                "session_id": session_id,
                "top_k": top_k,
                "doc_ids_filter": doc_ids_filter,
            }
        )
        return [
            RetrievedChunk(
                chunk_id="chunk-1",
                doc_id="doc-1",
                doc_name="report.pdf",
                page_number=2,
                text="Relevant content",
                score=0.1,
            )
        ]


def test_retrieve_embeds_query_and_searches_vector_store() -> None:
    embedding_service = DummyEmbeddingService()
    vector_store = DummyVectorStore()
    retrieval_service = RetrievalService(embedding_service, vector_store)

    results = retrieval_service.retrieve(
        query="What does the report say?",
        session_id="session-1",
        top_k=3,
        doc_ids_filter=["doc-1"],
    )

    assert embedding_service.seen_queries == ["What does the report say?"]
    assert vector_store.calls == [
        {
            "query_embedding": [1.0, 0.0, 0.0],
            "session_id": "session-1",
            "top_k": 3,
            "doc_ids_filter": ["doc-1"],
        }
    ]
    assert len(results) == 1
    assert results[0].doc_name == "report.pdf"
    assert results[0].page_number == 2

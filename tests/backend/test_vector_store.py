from __future__ import annotations

from backend.models.metadata import Chunk
from backend.services.vector_store import VectorStore


def make_chunks(doc_id: str, doc_name: str, prefix: str, count: int) -> list[Chunk]:
    return [
        Chunk(
            chunk_id=f"{prefix}-{index}",
            doc_id=doc_id,
            doc_name=doc_name,
            page_number=index + 1,
            text=f"{prefix} chunk {index}",
            chunk_index=index,
        )
        for index in range(count)
    ]


def test_upsert_and_retrieve() -> None:
    vector_store = VectorStore()
    session_id = "session-upsert"
    chunks = make_chunks("doc-1", "report.pdf", "alpha", 5)
    embeddings = [[1.0, 0.0, 0.0] for _ in chunks]

    vector_store.upsert_chunks(chunks, embeddings, session_id)
    results = vector_store.similarity_search([1.0, 0.0, 0.0], session_id, top_k=3)

    assert len(results) == 3
    assert all(result.doc_id == "doc-1" for result in results)
    assert all(result.doc_name == "report.pdf" for result in results)


def test_session_isolation() -> None:
    vector_store = VectorStore()
    chunks_a = make_chunks("doc-a", "a.pdf", "session-a", 2)
    chunks_b = make_chunks("doc-b", "b.pdf", "session-b", 2)

    vector_store.upsert_chunks(chunks_a, [[1.0, 0.0, 0.0] for _ in chunks_a], "session-a")
    vector_store.upsert_chunks(chunks_b, [[0.0, 1.0, 0.0] for _ in chunks_b], "session-b")

    results_a = vector_store.similarity_search([1.0, 0.0, 0.0], "session-a", top_k=5)
    results_b = vector_store.similarity_search([0.0, 1.0, 0.0], "session-b", top_k=5)

    assert {result.doc_id for result in results_a} == {"doc-a"}
    assert {result.doc_id for result in results_b} == {"doc-b"}


def test_delete_by_doc_id() -> None:
    vector_store = VectorStore()
    session_id = "session-delete-doc"
    doc_a_chunks = make_chunks("doc-a", "a.pdf", "doc-a", 2)
    doc_b_chunks = make_chunks("doc-b", "b.pdf", "doc-b", 2)

    vector_store.upsert_chunks(doc_a_chunks, [[1.0, 0.0, 0.0] for _ in doc_a_chunks], session_id)
    vector_store.upsert_chunks(doc_b_chunks, [[0.0, 1.0, 0.0] for _ in doc_b_chunks], session_id)

    removed = vector_store.delete_by_doc_id("doc-a", session_id)
    remaining = vector_store.similarity_search([1.0, 0.0, 0.0], session_id, top_k=5)

    assert removed == 2
    assert {result.doc_id for result in remaining} == {"doc-b"}


def test_delete_collection() -> None:
    vector_store = VectorStore()
    session_id = "session-delete-collection"
    chunks = make_chunks("doc-a", "a.pdf", "doc-a", 2)

    vector_store.upsert_chunks(chunks, [[1.0, 0.0, 0.0] for _ in chunks], session_id)
    vector_store.delete_collection(session_id)

    results = vector_store.similarity_search([1.0, 0.0, 0.0], session_id, top_k=5)

    assert results == []


def test_metadata_preserved_in_results() -> None:
    vector_store = VectorStore()
    session_id = "session-metadata"
    chunks = make_chunks("doc-meta", "meta.pdf", "meta", 1)

    vector_store.upsert_chunks(chunks, [[1.0, 0.0, 0.0] for _ in chunks], session_id)
    results = vector_store.similarity_search([1.0, 0.0, 0.0], session_id, top_k=1)

    assert len(results) == 1
    assert results[0].doc_name == "meta.pdf"
    assert results[0].page_number == 1
    assert results[0].text == "meta chunk 0"

from __future__ import annotations

import os

from backend.models.metadata import RetrievedChunk
from backend.services.rag_orchestrator import RAGOrchestrator


os.environ.setdefault("GROQ_API_KEY", "test")


def make_history(turns: int) -> list[dict]:
    history: list[dict] = []
    for index in range(turns):
        history.append({"role": "user", "content": f"user {index}"})
        history.append({"role": "assistant", "content": f"assistant {index}"})
    return history


def make_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            chunk_id="chunk-a",
            doc_id="doc-a",
            doc_name="report.pdf",
            page_number=3,
            text="A" * 250,
            score=0.2,
        ),
        RetrievedChunk(
            chunk_id="chunk-b",
            doc_id="doc-b",
            doc_name="summary.pdf",
            page_number=7,
            text="B" * 100,
            score=0.3,
        ),
        RetrievedChunk(
            chunk_id="chunk-c",
            doc_id="doc-a",
            doc_name="report.pdf",
            page_number=3,
            text="duplicate",
            score=0.4,
        ),
    ]


def test_prompt_contains_context() -> None:
    orchestrator = RAGOrchestrator()
    messages = orchestrator.build_messages("What is the main point?", make_chunks()[:1], [])

    assert messages[0]["role"] == "system"
    assert "report.pdf" in messages[0]["content"]
    assert "A" * 10 in messages[0]["content"]


def test_history_truncation() -> None:
    orchestrator = RAGOrchestrator()
    messages = orchestrator.build_messages("Current question", [], make_history(15))

    history_messages = messages[1:-1]
    assert len(history_messages) == 20
    assert history_messages[0]["content"] == "user 5"
    assert history_messages[-1]["content"] == "assistant 14"


def test_context_format_includes_page_numbers() -> None:
    orchestrator = RAGOrchestrator()
    context = orchestrator.format_chunks_as_context(make_chunks()[:2])

    assert "Page 3" in context
    assert "Page 7" in context


def test_user_message_is_last() -> None:
    orchestrator = RAGOrchestrator()
    messages = orchestrator.build_messages("Final query", [], make_history(2))

    assert messages[-1] == {"role": "user", "content": "Final query"}


def test_format_citations_deduplicates() -> None:
    orchestrator = RAGOrchestrator()
    citations = orchestrator.format_citations(make_chunks())

    assert citations == [
        {"doc_name": "report.pdf", "page": 3, "excerpt": "A" * 200, "public_url": None},
        {"doc_name": "summary.pdf", "page": 7, "excerpt": "B" * 100, "public_url": None},
    ]


def test_format_citations_sorts_by_doc_then_page() -> None:
    orchestrator = RAGOrchestrator()
    chunks = [
        RetrievedChunk(chunk_id="1", doc_id="d1", doc_name="zeta.pdf", page_number=5, text="z", score=0.1),
        RetrievedChunk(chunk_id="2", doc_id="d2", doc_name="alpha.pdf", page_number=2, text="a", score=0.2),
    ]

    citations = orchestrator.format_citations(chunks)

    assert [citation["doc_name"] for citation in citations] == ["alpha.pdf", "zeta.pdf"]

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("GROQ_API_KEY", "test")

import backend.main as main_module
from backend.models.metadata import Chunk, RetrievedChunk
from backend.services.pdf_processor import PageContent


class DummyPDFProcessor:
    def extract_text_by_page(self, file_bytes: bytes) -> list[PageContent]:
        return [PageContent(page_number=1, text="Dummy PDF text")]


class DummyChunker:
    def split_pages_into_chunks(self, pages, doc_id: str, doc_name: str) -> list[Chunk]:
        return [
            Chunk(
                chunk_id="chunk-1",
                doc_id=doc_id,
                doc_name=doc_name,
                page_number=1,
                text=pages[0].text,
                chunk_index=0,
            )
        ]


class DummyEmbeddingService:
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


class DummyVectorStore:
    def __init__(self, *args, **kwargs) -> None:
        self.deleted_docs: list[tuple[str, str]] = []
        self.deleted_collections: list[str] = []

    def upsert_chunks(self, chunks, embeddings, session_id: str, uploaded_at=None, public_url=None) -> None:
        return None

    def delete_by_doc_id(self, doc_id: str, session_id: str) -> int:
        self.deleted_docs.append((doc_id, session_id))
        return 1

    def delete_collection(self, session_id: str) -> None:
        self.deleted_collections.append(session_id)

    def get_session_documents(self, session_id: str):
        return {}

    def health_check(self) -> bool:
        return True


class DummyRetrievalService:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def retrieve(self, query: str, session_id: str, top_k: int = 5, doc_ids_filter=None):
        return [
            RetrievedChunk(
                chunk_id="chunk-1",
                doc_id="doc-1",
                doc_name="report.pdf",
                page_number=2,
                text="Relevant snippet from the document.",
                score=0.12,
            )
        ]


class DummyLLMClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def stream_completion(self, messages):
        yield "The"
        yield " answer"
        yield " is grounded."


class DummyRAGOrchestrator:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def build_messages(self, query: str, retrieved_chunks, conversation_history):
        return [{"role": "system", "content": "system"}, *conversation_history, {"role": "user", "content": query}]

    def format_citations(self, chunks):
        return [
            {
                "doc_name": chunk.doc_name,
                "page": chunk.page_number,
                "excerpt": chunk.text[:200],
            }
            for chunk in chunks
        ]


@pytest.fixture()
def client() -> TestClient:
    with patch.object(main_module, "PDFProcessor", DummyPDFProcessor), patch.object(
        main_module, "Chunker", DummyChunker
    ), patch.object(main_module, "EmbeddingService", DummyEmbeddingService), patch.object(
        main_module, "VectorStore", DummyVectorStore
    ), patch.object(main_module, "RetrievalService", DummyRetrievalService), patch.object(
        main_module, "LLMClient", DummyLLMClient
    ), patch.object(main_module, "RAGOrchestrator", DummyRAGOrchestrator):
        with TestClient(main_module.app) as test_client:
            yield test_client


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["vector_store"] == "connected"


def test_upload_valid_pdf(client: TestClient, test_pdf_bytes: bytes) -> None:
    response = client.post(
        "/api/v1/documents/upload",
        params={"session_id": "session-1"},
        files={"file": ("report.pdf", test_pdf_bytes, "application/pdf")},
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "indexed"
    assert payload["filename"] == "report.pdf"
    assert payload["page_count"] == 1
    assert payload["chunk_count"] == 1


def test_upload_invalid_type(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents/upload",
        params={"session_id": "session-1"},
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "INVALID_FILE_TYPE"


def test_upload_oversized(client: TestClient) -> None:
    oversized_bytes = b"0" * (21 * 1024 * 1024)
    response = client.post(
        "/api/v1/documents/upload",
        params={"session_id": "session-1"},
        files={"file": ("report.pdf", oversized_bytes, "application/pdf")},
    )

    assert response.status_code == 413
    assert response.json()["error"] == "FILE_TOO_LARGE"


def test_list_documents(client: TestClient, test_pdf_bytes: bytes) -> None:
    client.post(
        "/api/v1/documents/upload",
        params={"session_id": "session-2"},
        files={"file": ("report.pdf", test_pdf_bytes, "application/pdf")},
    )

    response = client.get("/api/v1/documents", params={"session_id": "session-2"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_chunks"] == 1
    assert len(payload["documents"]) == 1
    assert payload["documents"][0]["filename"] == "report.pdf"


def test_delete_document(client: TestClient, test_pdf_bytes: bytes) -> None:
    upload_response = client.post(
        "/api/v1/documents/upload",
        params={"session_id": "session-3"},
        files={"file": ("report.pdf", test_pdf_bytes, "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]

    delete_response = client.delete(
        f"/api/v1/documents/{document_id}", params={"session_id": "session-3"}
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True

    list_response = client.get("/api/v1/documents", params={"session_id": "session-3"})
    assert list_response.json()["documents"] == []


def test_chat_no_documents(client: TestClient) -> None:
    response = client.post(
        "/api/v1/query/chat",
        json={
            "session_id": "empty-session",
            "query": "What is this about?",
            "conversation_history": [],
            "top_k": 5,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NO_DOCUMENTS"


def test_chat_with_document(client: TestClient, test_pdf_bytes: bytes) -> None:
    client.post(
        "/api/v1/documents/upload",
        params={"session_id": "session-4"},
        files={"file": ("report.pdf", test_pdf_bytes, "application/pdf")},
    )

    with client.stream(
        "POST",
        "/api/v1/query/chat",
        json={
            "session_id": "session-4",
            "query": "What is in the document?",
            "conversation_history": [],
            "top_k": 5,
        },
    ) as response:
        body = "\n".join(line for line in response.iter_lines() if line)

    assert response.status_code == 200
    assert '"type": "token"' in body
    assert '"type": "sources"' in body
    assert '"type": "done"' in body

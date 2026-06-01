from __future__ import annotations

import os

import pytest

from backend.services.chunker import Chunker
from backend.services.pdf_processor import PageContent


@pytest.fixture(scope="module")
def chunker() -> Chunker:
    os.environ.setdefault("GROQ_API_KEY", "test")
    return Chunker()


def test_chunks_have_correct_metadata(chunker: Chunker) -> None:
    pages = [PageContent(page_number=1, text="A" * 700)]

    chunks = chunker.split_pages_into_chunks(pages, doc_id="doc-1", doc_name="report.pdf")

    assert len(chunks) >= 2
    assert all(chunk.doc_id == "doc-1" for chunk in chunks)
    assert all(chunk.doc_name == "report.pdf" for chunk in chunks)
    assert all(chunk.page_number == 1 for chunk in chunks)


def test_chunk_overlap_is_applied(chunker: Chunker) -> None:
    text = "abcdefghijklmnopqrstuvwxyz" * 30
    pages = [PageContent(page_number=1, text=text)]

    chunks = chunker.split_pages_into_chunks(pages, doc_id="doc-1", doc_name="report.pdf")

    assert len(chunks) >= 2
    assert chunks[0].text[-50:] == chunks[1].text[:50]


def test_chunk_index_is_sequential(chunker: Chunker) -> None:
    pages = [
        PageContent(page_number=1, text="A" * 700),
        PageContent(page_number=2, text="B" * 700),
    ]

    chunks = chunker.split_pages_into_chunks(pages, doc_id="doc-1", doc_name="report.pdf")

    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_chunker_preserves_page_numbers(chunker: Chunker) -> None:
    pages = [
        PageContent(page_number=1, text="Page one text " * 40),
        PageContent(page_number=2, text="Page two text " * 40),
        PageContent(page_number=3, text="Page three text " * 40),
    ]

    chunks = chunker.split_pages_into_chunks(pages, doc_id="doc-1", doc_name="report.pdf")

    assert {chunk.page_number for chunk in chunks} == {1, 2, 3}

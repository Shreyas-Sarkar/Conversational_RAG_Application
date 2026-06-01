from __future__ import annotations

import base64
import os

import fitz
import pytest


os.environ.setdefault("GROQ_API_KEY", "test")
os.environ["CHROMA_BACKEND"] = "local"


@pytest.fixture()
def test_pdf_bytes() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Hello from the test PDF.")
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


@pytest.fixture()
def test_session_id() -> str:
    return "test-session-id"


@pytest.fixture()
def multi_page_pdf_bytes() -> bytes:
    document = fitz.open()
    for page_number in range(3):
        page = document.new_page()
        page.insert_text((72, 72), f"Page {page_number + 1} text")
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


@pytest.fixture()
def pdf_with_blank_page_bytes() -> bytes:
    document = fitz.open()
    first_page = document.new_page()
    first_page.insert_text((72, 72), "Page one text")
    document.new_page()
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


@pytest.fixture()
def image_only_pdf_bytes() -> bytes:
    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7ZKXkAAAAASUVORK5CYII="
    )
    document = fitz.open()
    page = document.new_page()
    page.insert_image(fitz.Rect(72, 72, 96, 96), stream=png_bytes)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes

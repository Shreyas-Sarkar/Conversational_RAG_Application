from __future__ import annotations

import pytest

from backend.services.pdf_processor import PDFProcessor


@pytest.fixture()
def processor() -> PDFProcessor:
    return PDFProcessor()


def test_extract_text_by_page_valid_pdf(processor: PDFProcessor, test_pdf_bytes: bytes) -> None:
    pages = processor.extract_text_by_page(test_pdf_bytes)

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "Hello from the test PDF." in pages[0].text


def test_multi_page_pdf_returns_correct_count(
    processor: PDFProcessor, multi_page_pdf_bytes: bytes
) -> None:
    pages = processor.extract_text_by_page(multi_page_pdf_bytes)

    assert len(pages) == 3
    assert [page.page_number for page in pages] == [1, 2, 3]


def test_page_numbers_are_one_indexed(processor: PDFProcessor, test_pdf_bytes: bytes) -> None:
    pages = processor.extract_text_by_page(test_pdf_bytes)

    assert pages[0].page_number == 1


def test_empty_pages_are_skipped(
    processor: PDFProcessor, pdf_with_blank_page_bytes: bytes
) -> None:
    pages = processor.extract_text_by_page(pdf_with_blank_page_bytes)

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert pages[0].text == "Page one text"


def test_raises_for_invalid_bytes(processor: PDFProcessor) -> None:
    with pytest.raises(ValueError, match="Could not parse PDF"):
        processor.extract_text_by_page(b"not a pdf")


def test_raises_for_image_only_pdf(processor: PDFProcessor, image_only_pdf_bytes: bytes) -> None:
    with pytest.raises(ValueError, match="No extractable text found"):
        processor.extract_text_by_page(image_only_pdf_bytes)

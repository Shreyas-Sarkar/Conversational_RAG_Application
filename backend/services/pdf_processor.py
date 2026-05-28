"""PDF processing service."""

from __future__ import annotations

from dataclasses import dataclass
import logging

import fitz

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PageContent:
    page_number: int
    text: str


class PDFProcessor:
    """Extract page-level text from PDF bytes."""

    def extract_text_by_page(self, file_bytes: bytes) -> list[PageContent]:
        """Return a list of extracted text pages from a PDF.

        Raises:
            ValueError: If the bytes cannot be parsed as a PDF or no text can be extracted.
        """

        try:
            document = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:  # pragma: no cover - PyMuPDF raises multiple exception types
            raise ValueError(f"Could not parse PDF: {exc}") from exc

        pages: list[PageContent] = []
        try:
            for page_index in range(len(document)):
                page = document[page_index]
                text = page.get_text("text").strip()
                if text:
                    pages.append(PageContent(page_number=page_index + 1, text=text))
        finally:
            document.close()

        if not pages:
            raise ValueError(
                "No extractable text found in this PDF. It may be a scanned image-only document."
            )

        logger.info("Extracted text from %s pages", len(pages))
        return pages

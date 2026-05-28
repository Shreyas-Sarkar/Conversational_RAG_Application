"""Chunking service."""

from __future__ import annotations

import logging
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

try:  # pragma: no cover - import path depends on execution entry point
    from config.settings import get_settings
    from models.metadata import Chunk
    from services.pdf_processor import PageContent
except ModuleNotFoundError:  # pragma: no cover
    from backend.config.settings import get_settings
    from backend.models.metadata import Chunk
    from backend.services.pdf_processor import PageContent

logger = logging.getLogger(__name__)


class Chunker:
    """Split page text into overlapping chunks with metadata."""

    def __init__(self) -> None:
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    def split_pages_into_chunks(
        self,
        pages: list[PageContent],
        doc_id: str,
        doc_name: str,
    ) -> list[Chunk]:
        """Split page content into chunk objects while preserving page metadata."""

        chunks: list[Chunk] = []
        chunk_index = 0

        for page in pages:
            page_chunks = self.splitter.split_text(page.text)
            for chunk_text in page_chunks:
                chunks.append(
                    Chunk(
                        chunk_id=str(uuid4()),
                        doc_id=doc_id,
                        doc_name=doc_name,
                        page_number=page.page_number,
                        text=chunk_text,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1

        logger.info("Split %s pages into %s chunks for %s", len(pages), len(chunks), doc_name)
        return chunks

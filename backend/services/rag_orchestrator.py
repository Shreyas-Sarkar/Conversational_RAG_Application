"""RAG orchestration service."""

from __future__ import annotations

import logging

try:  # pragma: no cover - import path depends on execution entry point
    from config.settings import get_settings
    from models.metadata import RetrievedChunk
except ModuleNotFoundError:  # pragma: no cover
    from backend.config.settings import get_settings
    from backend.models.metadata import RetrievedChunk

logger = logging.getLogger(__name__)

RAG_SYSTEM_PROMPT_TEMPLATE = """You are a helpful document assistant.
Answer questions based ONLY on the context provided below.
If the answer is not present in the context, respond exactly with:
"I cannot find information about this in the uploaded documents."

Do not speculate, invent facts, or use knowledge outside the provided context.
When referencing information, note the document name and page number.

--- DOCUMENT CONTEXT ---
{context_block}
--- END CONTEXT ---"""


class RAGOrchestrator:
    """Build prompts and citation payloads for retrieval-augmented generation."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def format_chunks_as_context(self, chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks for inclusion in the system prompt."""

        if not chunks:
            return ""

        sections: list[str] = []
        for chunk in chunks:
            sections.append(f"--- [{chunk.doc_name}, Page {chunk.page_number}] ---\n{chunk.text}")
        return "\n\n".join(sections)

    def build_messages(
        self,
        query: str,
        retrieved_chunks: list[RetrievedChunk],
        conversation_history: list[dict],
    ) -> list[dict]:
        """Assemble the OpenAI-compatible message list for Groq."""

        context_block = self.format_chunks_as_context(retrieved_chunks)
        messages: list[dict] = [
            {
                "role": "system",
                "content": RAG_SYSTEM_PROMPT_TEMPLATE.format(context_block=context_block),
            }
        ]

        history_limit = self.settings.MAX_HISTORY_TURNS * 2
        truncated_history = conversation_history[-history_limit:] if history_limit > 0 else []
        messages.extend(truncated_history)
        messages.append({"role": "user", "content": query})

        logger.info(
            "Built RAG messages with %s history messages and %s retrieved chunks",
            len(truncated_history),
            len(retrieved_chunks),
        )
        return messages

    def format_citations(self, chunks: list[RetrievedChunk]) -> list[dict]:
        """Deduplicate and format citation payloads for the frontend."""

        unique: dict[tuple[str, int], RetrievedChunk] = {}
        for chunk in chunks:
            unique.setdefault((chunk.doc_name, chunk.page_number), chunk)

        ordered_chunks = sorted(unique.values(), key=lambda chunk: (chunk.doc_name, chunk.page_number))
        citations = [
            {
                "doc_name": chunk.doc_name,
                "page": chunk.page_number,
                "excerpt": chunk.text[:200],
                "public_url": chunk.public_url,
            }
            for chunk in ordered_chunks
        ]
        return citations

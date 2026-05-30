"""LLM client service."""

from __future__ import annotations

import logging
import os
import time
from typing import Generator, Iterable

from groq import APIStatusError, Groq, RateLimitError

try:  # pragma: no cover - import path depends on execution entry point
    from config.settings import get_settings
except ModuleNotFoundError:  # pragma: no cover
    from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Stream chat completions from Groq with retry and fallback handling."""

    def __init__(self) -> None:
        settings = get_settings()
        api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.settings = settings
        self.client = Groq(api_key=api_key)

    def stream_completion(
        self,
        messages: list[dict],
        model: str | None = None,
    ) -> Generator[str, None, None]:
        """Yield streamed response text from Groq, retrying and falling back when needed."""

        selected_model = model or self.settings.PRIMARY_MODEL
        yield from self._stream_with_resilience(messages, selected_model, allow_fallback=True)

    def _stream_with_resilience(
        self,
        messages: list[dict],
        model: str,
        allow_fallback: bool,
    ) -> Generator[str, None, None]:
        retry_delays = [2, 4, 8]
        last_error: Exception | None = None

        for attempt, delay in enumerate([0, *retry_delays], start=1):
            try:
                logger.info("Groq completion requested with model=%s attempt=%s", model, attempt)
                stream = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                    temperature=0.1,
                    max_tokens=1000,
                )
                yield from self._yield_stream(stream)
                return
            except RateLimitError as exc:
                last_error = exc
                logger.warning("Groq rate limit for model=%s attempt=%s", model, attempt)
                if attempt >= len(retry_delays) + 1:
                    break
                time.sleep(delay)
            except APIStatusError as exc:
                last_error = exc
                status_code = getattr(exc, "status_code", None)
                if status_code is not None and status_code >= 500 and allow_fallback and model == self.settings.PRIMARY_MODEL:
                    logger.warning("Groq server error for model=%s, falling back to %s", model, self.settings.FALLBACK_MODEL)
                    yield from self._stream_with_resilience(messages, self.settings.FALLBACK_MODEL, allow_fallback=False)
                    return
                raise

        if allow_fallback and model == self.settings.PRIMARY_MODEL:
            logger.warning("Groq retries exhausted for primary model=%s, falling back to %s", model, self.settings.FALLBACK_MODEL)
            yield from self._stream_with_resilience(messages, self.settings.FALLBACK_MODEL, allow_fallback=False)
            return

        if last_error is not None:
            raise last_error

    def _yield_stream(self, stream: Iterable) -> Generator[str, None, None]:
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta

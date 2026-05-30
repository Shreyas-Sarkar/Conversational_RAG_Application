"""Embedding service."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import requests

try:  # pragma: no cover - import path depends on execution entry point
    from config.settings import get_settings
except ModuleNotFoundError:  # pragma: no cover
    from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        pass

    def generate_embedding(self, text: str) -> list[float]:
        return self.generate_embeddings([text])[0]


class JinaEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider using Jina AI's API."""

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.JINA_API_KEY:
            raise ValueError("JINA_API_KEY is not set in environment variables.")
        self.api_key = self.settings.JINA_API_KEY
        self.model_name = self.settings.EMBEDDING_MODEL
        self.url = "https://api.jina.ai/v1/embeddings"
        logger.info("Initialized Jina embedding provider with model %s", self.model_name)

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model_name,
            "input": texts
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Log token usage if present
            if "usage" in result:
                logger.info(f"Jina API Token Usage: {result['usage'].get('total_tokens', 'unknown')} tokens")
                
            # The API returns a list of dictionaries in 'data', each containing an 'embedding' list of floats
            # Sort them by 'index' just in case the API returns them out of order (though usually they are ordered)
            sorted_data = sorted(result["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in sorted_data]
            
        except requests.exceptions.RequestException as e:
            logger.error("Jina API Request failed: %s", str(e))
            if hasattr(e, "response") and e.response is not None:
                logger.error("Raw response: %s", e.response.text)
            raise ValueError(f"Failed to generate embeddings from Jina API: {str(e)}") from e


class EmbeddingService:
    """Service to handle generating embeddings via the configured provider."""

    def __init__(self) -> None:
        # Load the Jina provider
        self.provider: BaseEmbeddingProvider = JinaEmbeddingProvider()

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        return self.provider.generate_embeddings(texts)

    def generate_embedding(self, text: str) -> list[float]:
        return self.provider.generate_embedding(text)

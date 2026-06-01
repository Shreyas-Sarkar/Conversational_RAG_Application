from __future__ import annotations

import os
import math

import pytest

from backend.services.embedding_service import EmbeddingService


@pytest.fixture(scope="module")
def embedding_service() -> EmbeddingService:
    os.environ.setdefault("GROQ_API_KEY", "test")
    return EmbeddingService()


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot_product = sum(l * r for l, r in zip(left, right))
    left_magnitude = math.sqrt(sum(value * value for value in left))
    right_magnitude = math.sqrt(sum(value * value for value in right))
    return dot_product / (left_magnitude * right_magnitude)


def test_embedding_dimensionality(embedding_service: EmbeddingService) -> None:
    result = embedding_service.generate_embeddings(["hello world"])

    assert len(result) == 1
    assert len(result[0]) == 1024


def test_batch_embedding_length(embedding_service: EmbeddingService) -> None:
    result = embedding_service.generate_embeddings(["hello", "world", "test"])

    assert len(result) == 3


def test_similar_texts_have_high_cosine_similarity(embedding_service: EmbeddingService) -> None:
    dog_vector, puppy_vector = embedding_service.generate_embeddings(["dog", "puppy"])

    assert cosine_similarity(dog_vector, puppy_vector) > 0.7


def test_dissimilar_texts_have_lower_similarity(embedding_service: EmbeddingService) -> None:
    dog_vector, physics_vector = embedding_service.generate_embeddings(["dog", "quantum physics"])

    assert cosine_similarity(dog_vector, physics_vector) < 0.5

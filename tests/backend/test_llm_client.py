from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import backend.services.llm_client as llm_client_module
from backend.services.llm_client import LLMClient


class FakeRateLimitError(Exception):
    pass


class FakeAPIStatusError(Exception):
    def __init__(self, status_code: int):
        super().__init__(f"status {status_code}")
        self.status_code = status_code


def make_stream(*parts: str):
    return [
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=part))])
        for part in parts
    ]


@pytest.fixture(autouse=True)
def groq_env() -> None:
    os.environ.setdefault("GROQ_API_KEY", "test")


def test_stream_yields_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_create = MagicMock(return_value=make_stream("The", " answer", " streams"))
    mock_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=mock_create)))

    with patch.object(llm_client_module, "Groq", return_value=mock_client):
        client = LLMClient()
        tokens = list(client.stream_completion([{"role": "user", "content": "hello"}]))

    assert tokens == ["The", " answer", " streams"]


def test_fallback_on_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    primary_model = "llama-3.3-70b-versatile"
    fallback_model = "llama-3.1-8b-instant"

    def create_side_effect(**kwargs):
        if kwargs["model"] == primary_model:
            raise FakeRateLimitError()
        return make_stream("fallback", " response")

    mock_create = MagicMock(side_effect=create_side_effect)
    mock_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=mock_create)))

    with patch.object(llm_client_module, "Groq", return_value=mock_client), patch.object(
        llm_client_module, "RateLimitError", FakeRateLimitError
    ), patch.object(llm_client_module.time, "sleep", return_value=None):
        client = LLMClient()
        tokens = list(client.stream_completion([{"role": "user", "content": "hello"}]))

    assert tokens == ["fallback", " response"]
    assert any(call.kwargs["model"] == fallback_model for call in mock_create.mock_calls)


def test_raises_after_fallback_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def create_side_effect(**kwargs):
        raise FakeRateLimitError()

    mock_create = MagicMock(side_effect=create_side_effect)
    mock_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=mock_create)))

    with patch.object(llm_client_module, "Groq", return_value=mock_client), patch.object(
        llm_client_module, "RateLimitError", FakeRateLimitError
    ), patch.object(llm_client_module.time, "sleep", return_value=None):
        client = LLMClient()
        with pytest.raises(FakeRateLimitError):
            list(client.stream_completion([{"role": "user", "content": "hello"}]))


def test_temperature_is_low(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_create = MagicMock(return_value=make_stream("ok"))
    mock_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=mock_create)))

    with patch.object(llm_client_module, "Groq", return_value=mock_client):
        client = LLMClient()
        list(client.stream_completion([{"role": "user", "content": "hello"}]))

    assert mock_create.call_args.kwargs["temperature"] == 0.1

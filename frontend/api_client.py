from __future__ import annotations

import json
import os
from typing import Generator

import httpx
from dotenv import load_dotenv

load_dotenv()


class RAGAPIClient:
    def __init__(self, base_url: str | None = None):
        import streamlit as st
        try:
            env_url = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))
        except Exception:
            env_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.base_url = base_url or env_url
        self._last_sources: list[dict] = []

    def upload_document(self, file_bytes: bytes, filename: str, session_id: str):
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/v1/documents/upload",
                params={"session_id": session_id},
                files={"file": (filename, file_bytes, "application/pdf")},
            )
            response.raise_for_status()
            return response.json()

    def list_documents(self, session_id: str):
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{self.base_url}/api/v1/documents", params={"session_id": session_id})
            response.raise_for_status()
            return response.json()

    def delete_document(self, doc_id: str, session_id: str):
        with httpx.Client(timeout=30.0) as client:
            response = client.delete(
                f"{self.base_url}/api/v1/documents/{doc_id}",
                params={"session_id": session_id},
            )
            response.raise_for_status()
            return response.json()

    def clear_session(self, session_id: str):
        with httpx.Client(timeout=30.0) as client:
            response = client.delete(f"{self.base_url}/api/v1/session/{session_id}")
            response.raise_for_status()
            return response.json()

    def stream_chat(self, request: dict) -> Generator[str, None, None]:
        self._last_sources = []
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", f"{self.base_url}/api/v1/query/chat", json=request) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    event = json.loads(line[6:])
                    event_type = event.get("type")
                    if event_type == "token":
                        yield event["content"]
                    elif event_type == "sources":
                        self._last_sources = event.get("content", [])
                    elif event_type == "error":
                        raise RuntimeError(event.get("content", {}).get("message", "Unable to generate response."))
                    elif event_type == "done":
                        return

from __future__ import annotations

from datetime import datetime, timezone
import json

import streamlit as st

try:  # pragma: no cover - depends on how Streamlit launches the app
    from api_client import RAGAPIClient
except ModuleNotFoundError:  # pragma: no cover
    from frontend.api_client import RAGAPIClient

from components.citations import render_citations


def _request_history() -> list[dict]:
    history: list[dict] = []
    for message in st.session_state.messages:
        history.append({"role": message["role"], "content": message["content"]})
    return history


def _cache_key(session_id: str, prompt: str, history: list[dict], top_k: int = 5) -> str:
    payload = {
        "session_id": session_id,
        "query": prompt,
        "conversation_history": history,
        "top_k": top_k,
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True)


def _render_role_tag(role: str) -> None:
    label = "User" if role == "user" else "Agent"
    st.markdown(f'<span class="message-role-tag message-role-tag-{role}">{label}</span>', unsafe_allow_html=True)


def render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            _render_role_tag(message["role"])
            st.markdown(message["content"])
            st.caption(message.get("timestamp", ""))
            if message["role"] == "assistant":
                render_citations(message.get("sources", []))

    if st.session_state.is_querying:
        st.chat_input("Ask a question about your documents...", disabled=True)
        return

    prompt = st.chat_input("Ask a question about your documents...")
    if not prompt:
        return

    client = RAGAPIClient()
    st.session_state.is_querying = True
    user_message = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    st.session_state.messages.append(user_message)
    request_history = _request_history()[:-1]
    cache_key = _cache_key(st.session_state.session_id, prompt, request_history)

    with st.chat_message("user"):
        _render_role_tag("user")
        st.markdown(prompt)
        st.caption(user_message["timestamp"])

    try:
        cached_response = st.session_state.query_cache.get(cache_key)
        if cached_response is not None:
            response_text = cached_response["content"]
            sources = cached_response.get("sources", [])
            with st.chat_message("assistant"):
                _render_role_tag("assistant")
                st.markdown(response_text)
                st.caption(cached_response.get("timestamp", datetime.now(timezone.utc).isoformat()))
                render_citations(sources)
        else:
            with st.chat_message("assistant"):
                _render_role_tag("assistant")
                response_text = st.write_stream(
                    client.stream_chat(
                        {
                            "session_id": st.session_state.session_id,
                            "query": prompt,
                            "conversation_history": request_history,
                            "top_k": 5,
                        }
                    )
                )
                sources = client._last_sources
                render_citations(sources)

            st.session_state.query_cache[cache_key] = {
                "content": response_text,
                "sources": sources,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sources": sources,
            }
        )
    except Exception as exc:
        st.session_state.last_error = str(exc)
        st.error(str(exc))
    finally:
        st.session_state.is_querying = False

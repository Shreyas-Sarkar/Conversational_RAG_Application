from __future__ import annotations

import streamlit as st

try:  # pragma: no cover - depends on how Streamlit launches the app
    from api_client import RAGAPIClient
except ModuleNotFoundError:  # pragma: no cover
    from frontend.api_client import RAGAPIClient


def render_upload_zone() -> None:
    st.subheader("Upload PDFs")
    uploaded_files = st.file_uploader(
        "Drag and drop PDF documents here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=f"document_uploader_{st.session_state.upload_widget_key}",
    )

    if not uploaded_files:
        st.caption("Drop one or more PDFs to start chatting with them.")
        return

    client = RAGAPIClient()
    progress = st.progress(0)
    for index, uploaded_file in enumerate(uploaded_files, start=1):
        st.session_state.is_processing = True
        try:
            result = client.upload_document(uploaded_file.getvalue(), uploaded_file.name, st.session_state.session_id)
            st.session_state.documents[result["document_id"]] = result
            st.success(f"Processed {result['filename']}")
        except Exception as exc:
            st.session_state.last_error = str(exc)
            st.error(str(exc))
        progress.progress(index / len(uploaded_files))
    st.session_state.is_processing = False
    st.session_state.upload_widget_key += 1
    st.rerun()

from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

try:  # pragma: no cover - depends on how Streamlit launches the app
    from api_client import RAGAPIClient
except ModuleNotFoundError:  # pragma: no cover
    from frontend.api_client import RAGAPIClient


def render_document_panel() -> None:
    client = RAGAPIClient()
    documents = st.session_state.documents

    st.markdown("### Session")
    st.metric("Documents", len(documents))
    st.metric("Chunks", sum(doc.get("chunk_count", 0) for doc in documents.values()))

    if not documents:
        st.caption("No documents uploaded yet.")
    else:
        for document_id, document in documents.items():
            if document.get("public_url"):
                st.markdown(f"**[{document['filename']}]({document['public_url']})**")
            else:
                st.markdown(f"**{document['filename']}**")
            st.caption(f"{document['page_count']} pages • {document['chunk_count']} chunks")
            if st.button("Remove", key=f"remove_{document_id}"):
                try:
                    client.delete_document(document_id, st.session_state.session_id)
                    st.session_state.documents.pop(document_id, None)
                    st.rerun()
                except Exception as exc:
                    st.session_state.last_error = str(exc)

    if st.session_state.messages:
        export_data = json.dumps(st.session_state.messages, indent=2, default=str)
        st.download_button(
            label="Download Chat",
            data=export_data,
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            icon=":material/download:",
        )

    if documents and st.button("Clear Session"):
        try:
            client.clear_session(st.session_state.session_id)
            st.session_state.documents = {}
            st.session_state.messages = []
            st.rerun()
        except Exception as exc:
            st.session_state.last_error = str(exc)

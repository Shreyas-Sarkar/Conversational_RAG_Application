from __future__ import annotations

import streamlit as st

from components.chat import render_chat_history
from components.document_panel import render_document_panel
from components.help_panel import render_help_panel
from components.theme_toggle import render_theme_toggle
from components.upload import render_upload_zone
from state import initialize_session_state
from styles.neo_brutalist import inject_neo_brutalist_css

st.set_page_config(
    page_title="PDF Based Conversational RAG Platform",
    page_icon=":material/article:",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
inject_neo_brutalist_css(st.session_state.theme)

if st.session_state.last_error:
    st.error(st.session_state.last_error)

with st.sidebar:
    render_theme_toggle()
    st.markdown("---")
    render_document_panel()
    st.markdown("---")
    render_help_panel()

st.title("PDF Based Conversational RAG Platform")
st.caption("Upload PDF documents and chat with them using AI")

if not st.session_state.documents:
    render_upload_zone()
else:
    render_upload_zone()
    st.markdown("---")
    render_chat_history()

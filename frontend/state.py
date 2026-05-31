import uuid

import streamlit as st


def initialize_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents" not in st.session_state:
        st.session_state.documents = {}
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "is_querying" not in st.session_state:
        st.session_state.is_querying = False
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    if "upload_widget_key" not in st.session_state:
        st.session_state.upload_widget_key = 0
    if "query_cache" not in st.session_state:
        st.session_state.query_cache = {}

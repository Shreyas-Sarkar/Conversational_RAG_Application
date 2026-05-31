from __future__ import annotations

import streamlit as st


def render_help_panel() -> None:
    with st.expander("How it works", expanded=False, icon=":material/info:"):
        st.markdown(
            """
            The app keeps your uploaded PDFs and chat history in the current browser session.

            Use it like this:
            1. Upload one or more PDFs.
            2. Wait for processing to complete.
            3. Ask a focused question.
            4. Read the answer and expand the citations to verify the source pages.

            Tips:
            - Use searchable PDF text whenever possible.
            - Ask one question at a time for the clearest answer.
            - Remove documents or clear the session to start over.
            """
        )

    with st.expander("FAQ", expanded=False, icon=":material/help:"):
        st.markdown(
            """
            **Why do I need to upload files again?**
            Each browser session is isolated, so documents stay tied to that session.

            **Why do answers show citations?**
            The assistant grounds responses in the uploaded PDFs and shows the matching pages.

            **Can I use multiple PDFs at once?**
            Yes. Upload several PDFs and ask questions across the combined document set.

            **How do I reset everything?**
            Use Clear Session in the sidebar to remove the documents and chat history for the current session.
            """
        )
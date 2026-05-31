from __future__ import annotations

import streamlit as st


def render_citations(sources: list[dict]) -> None:
    if not sources:
        return

    st.caption("Sources")
    for source in sources:
        doc_name = source['doc_name']
        if source.get('public_url'):
            header = f"[{doc_name}]({source['public_url']}) - Page {source['page']}"
        else:
            header = f"{doc_name} - Page {source['page']}"
            
        with st.expander(header, icon=":material/article:"):
            st.caption(source.get("excerpt", ""))

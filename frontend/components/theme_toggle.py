from __future__ import annotations

import streamlit as st


def render_theme_toggle() -> None:
    current = st.session_state.theme
    label = "Use dark mode" if current == "light" else "Use light mode"
    icon = ":material/dark_mode:" if current == "light" else ":material/light_mode:"
    if st.button(label, key="theme_toggle", icon=icon):
        st.session_state.theme = "dark" if current == "light" else "light"
        st.rerun()

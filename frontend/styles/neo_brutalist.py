from __future__ import annotations

import streamlit as st


def inject_neo_brutalist_css(theme: str) -> None:
    dark_mode = theme == "dark"
    background_color = "#0A0A0A" if dark_mode else "#F7F2EA"
    text_color = "#FFFFFF" if dark_mode else "#151515"
    secondary_color = "#1A1A1A" if dark_mode else "#FFF9F2"
    border_color = "#FFFFFF" if dark_mode else "#151515"
    surface_color = "#111111" if dark_mode else "#FFFDF9"
    muted_text_color = "#C8C8C8" if dark_mode else "#4A4A4A"
    input_background = "#0B0B0B" if dark_mode else "#FFFDF7"
    input_window_background = "#050505" if dark_mode else "#FFFDF9"
    input_window_border = "#3A3A3A" if dark_mode else "#151515"
    shadow_color = "rgba(0, 0, 0, 0.45)" if dark_mode else "rgba(21, 21, 21, 0.18)"
    accent_text_color = "#151515"

    css = f"""
    <style>
        :root {{
            --color-bg: {background_color};
            --color-text: {text_color};
            --color-secondary: {secondary_color};
            --color-border: {border_color};
            --color-primary: #FF4B00;
            --color-accent: #FFE600;
            --color-surface: {surface_color};
            --color-muted: {muted_text_color};
            --color-input: {input_background};
            --color-input-window: {input_window_background};
            --color-input-window-border: {input_window_border};
            --color-shadow: {shadow_color};
            --color-accent-text: {accent_text_color};
        }}

        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"], .main, .block-container, .stApp {{
            background: var(--color-bg) !important;
            color: var(--color-text) !important;
        }}

        [data-testid="stSidebar"] {{
            background: var(--color-surface) !important;
            color: var(--color-text) !important;
            border-right: 2px solid var(--color-border);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--color-text);
        }}

        .stMarkdown, .stCaption, .stMetric, .stMetricLabel, .stMetricValue, .stMetricDelta {{
            color: var(--color-text) !important;
        }}

        .stCaption, .stMarkdown p, .stMarkdown li {{
            color: var(--color-muted) !important;
        }}

        .stApp {{
            background: var(--color-bg);
            color: var(--color-text);
        }}

        .stButton > button, .stDownloadButton > button {{
            border: 2px solid var(--color-border);
            border-radius: 2px;
            box-shadow: 4px 4px 0px var(--color-shadow);
            font-weight: 700;
            background: var(--color-primary);
            color: var(--color-accent-text);
            transition: transform 0.12s ease;
        }}

        .stButton > button:hover, .stDownloadButton > button:hover {{
            transform: translate(-2px, -2px);
        }}

        .stFileUploader, [data-testid="stFileUploaderDropzone"] {{
            border: 2px dashed var(--color-border);
            padding: 0.5rem;
            background: var(--color-secondary);
        }}

        [data-testid="stFileChips"] {{
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}

        [data-testid="stFileChip"] {{
            background: var(--color-input-window) !important;
            border: 1px solid var(--color-input-window-border) !important;
            color: var(--color-text) !important;
            border-radius: 2px !important;
            padding: 0.5rem 0.6rem !important;
            box-shadow: 4px 4px 0px var(--color-shadow);
        }}

        [data-testid="stFileChipName"] {{
            color: var(--color-text) !important;
            font-weight: 700;
        }}

        [data-testid="stFileChipDeleteBtn"] {{
            color: var(--color-text) !important;
        }}

        .stFileUploader * {{
            color: var(--color-text);
        }}

        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stFileUploaderDropzone"] button:hover,
        [data-testid="stFileUploaderDropzone"] button:focus-visible {{
            background: var(--color-primary) !important;
            color: var(--color-accent-text) !important;
            border-color: var(--color-border) !important;
        }}

        [data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"],
        [data-testid="stFileUploaderDropzone"] label,
        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] p {{
            color: var(--color-text) !important;
        }}

        .stTextInput input, .stTextArea textarea, .stChatInput textarea, [data-testid="stChatInput"] textarea {{
            background: var(--color-input) !important;
            color: var(--color-text) !important;
            border: 2px solid var(--color-border) !important;
            border-radius: 2px !important;
        }}

        .stChatInput, [data-testid="stChatInput"] {{
            background: var(--color-input-window) !important;
            border: 2px solid var(--color-input-window-border) !important;
            border-radius: 2px !important;
            box-shadow: 6px 6px 0px var(--color-shadow);
            padding: 0.2rem 0.35rem 0.35rem;
        }}

        [data-testid="stChatInput"] textarea {{
            background: var(--color-input-window) !important;
            color: var(--color-text) !important;
            border-color: var(--color-input-window-border) !important;
        }}

        [data-testid="stChatInput"] button {{
            background: var(--color-primary) !important;
            color: var(--color-accent-text) !important;
            border: 2px solid var(--color-border) !important;
        }}

        .stTextInput input::placeholder, .stTextArea textarea::placeholder, .stChatInput textarea::placeholder {{
            color: var(--color-muted) !important;
            opacity: 1;
        }}

        .stExpander {{
            border: 2px solid var(--color-border);
            background: var(--color-secondary);
            border-radius: 2px;
        }}

        .stExpander summary,
        .stExpander summary:hover,
        .stExpander summary:focus,
        .stExpander summary:focus-visible {{
            background: var(--color-secondary) !important;
            color: var(--color-text) !important;
            border-bottom: 1px solid var(--color-border) !important;
        }}

        .stExpander summary * {{
            color: var(--color-text) !important;
        }}

        .stExpander summary svg,
        .stExpander summary svg * {{
            fill: var(--color-text) !important;
            stroke: var(--color-text) !important;
        }}

        .stExpander > div {{
            background: var(--color-surface) !important;
            color: var(--color-text) !important;
        }}

        .stChatMessage {{
            border: 2px solid var(--color-border);
            border-radius: 2px;
            box-shadow: 4px 4px 0px var(--color-shadow);
            margin-bottom: 0.5rem;
            background: var(--color-surface);
            color: var(--color-text);
        }}

        .stChatMessage > div:first-child,
        .stChatMessage [data-testid*="avatar"],
        .stChatMessage [data-testid*="Avatar"] {{
            display: none !important;
        }}

        .stChatMessage > div:last-child {{
            width: 100%;
        }}

        .stChatMessage [data-testid="stMarkdownContainer"] {{
            color: var(--color-text);
        }}

        .stChatMessage[data-testid="stChatMessageUser"] {{
            background: var(--color-accent);
            color: var(--color-accent-text);
        }}

        .stChatMessage[data-testid="stChatMessageAssistant"] {{
            background: var(--color-secondary);
        }}

        .stChatMessage[data-testid="stChatMessageUser"] p,
        .stChatMessage[data-testid="stChatMessageUser"] div,
        .stChatMessage[data-testid="stChatMessageUser"] span {{
            color: var(--color-accent-text) !important;
        }}

        .stChatMessage[data-testid="stChatMessageAssistant"] p,
        .stChatMessage[data-testid="stChatMessageAssistant"] div,
        .stChatMessage[data-testid="stChatMessageAssistant"] span {{
            color: var(--color-text) !important;
        }}

        .message-role-tag {{
            display: inline-flex;
            align-items: center;
            padding: 0.12rem 0.5rem;
            margin-bottom: 0.45rem;
            border: 1px solid var(--color-border);
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            background: var(--color-surface);
            color: var(--color-text);
        }}

        .message-role-tag-user {{
            background: var(--color-accent);
            color: var(--color-accent-text);
        }}

        .message-role-tag-assistant {{
            background: var(--color-secondary);
            color: var(--color-text);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

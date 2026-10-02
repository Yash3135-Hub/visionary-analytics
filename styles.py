import streamlit as st

def load_css(file_path="style.css"):
    try:
        with open(file_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

CHATBOT_STYLES = """
<style>
div[class*="st-key-fab_button"] button {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9999;
    width: 56px;
    height: 56px;
    border-radius: 50% !important;
    font-size: 24px;
    padding: 0;
    box-shadow: 0 8px 24px rgba(255, 75, 75, 0.45);
}

div[class*="st-key-chat_panel"] {
    position: fixed;
    bottom: 92px;
    right: 24px;
    width: 360px;
    max-height: 480px;
    overflow-y: auto;
    z-index: 9998;
    background: #0C1A22;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55);
}
</style>
"""
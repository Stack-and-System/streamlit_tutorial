"""
Entrypoint / router for the Streamlit Best Practices demo.

Kept intentionally thin: it only configures the page and wires pages
together via st.Page / st.navigation. All content and logic live in
app_pages/ and utils/.
"""
import streamlit as st

from app_pages import home, data_explorer, interactive_form, live_updates, ai_chat

st.set_page_config(
    page_title="Streamlit Best Practices Demo",
    page_icon="✅",
    layout="wide",
)

pages = [
    st.Page(home.render, title="Home", icon="🏠", url_path="home", default=True),
    st.Page(data_explorer.render, title="Data Explorer", icon="📊", url_path="data-explorer"),
    st.Page(interactive_form.render, title="Forms & State", icon="📝", url_path="forms-state"),
    st.Page(live_updates.render, title="Live Fragment", icon="⚡", url_path="live-updates"),
    st.Page(ai_chat.render, title="AI Chatbot", icon=":material/robot_2:", url_path="ai_chat")
]

with st.sidebar:
    st.caption("Streamlit Best Practices Demo")
    st.caption("Each page maps to a section of the tutorial.")

nav = st.navigation(pages)
nav.run()

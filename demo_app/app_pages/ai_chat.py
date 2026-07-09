from time import sleep

import streamlit as st
from ollama import chat

def stream_data(message: str):
    for letter in message:
        yield letter
        sleep(0.1)


def render():
    ai_col, human_col = st.columns(2, width="stretch")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    message = st.chat_input()
    if message:
        st.session_state.messages.append({"human": message})
    if st.session_state.messages:
        for text_dict in st.session_state.messages:
            if "human" in text_dict.keys():
                with human_col:
                    with st.chat_message(name="human", avatar="human", width="content"):
                        st.write_stream(stream_data(text_dict["human"]))


"""
AI Chatbot page: a streaming chat interface backed by a local Ollama model
(Section 9 of the tutorial).

Uses Streamlit's built-in `st.chat_message` / `st.chat_input` / `st.write_stream`
elements instead of hand-rolled HTML: message content is escaped safely by
default, and `st.write_stream` handles the chunk-by-chunk rendering that used
to require a manually managed `st.empty()` placeholder. The call to the
external Ollama server is wrapped in `try/except` (Section 7) so a missing
model or unreachable server surfaces as a clear `st.error` instead of a raw
traceback.
"""
import streamlit as st
from ollama import chat

MODEL_NAME = "llama3.2"


def _stream_response(messages):
    """Yield response text chunks from Ollama for st.write_stream to consume."""
    response_stream = chat(model=MODEL_NAME, messages=messages, stream=True)
    for chunk in response_stream:
        yield chunk.message.content


def render() -> None:
    st.title("AI Chatbot")
    st.write(
        "A minimal streaming chat UI backed by a local Ollama model "
        f"(`{MODEL_NAME}`). Requires Ollama running locally with the model "
        "pulled -- see the demo README for setup."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                full_response = st.write_stream(
                    _stream_response(st.session_state.messages)
                )
            except Exception as exc:
                st.error(
                    "Couldn't reach the local Ollama server. Make sure Ollama "
                    f"is running and `{MODEL_NAME}` is pulled "
                    f"(`ollama pull {MODEL_NAME}`). Details: {exc}"
                )
                st.stop()

        st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    render()
import streamlit as st
from ollama import chat


def render():
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for text in st.session_state.messages:
        role = text.get("role")
        if role == "user":
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; text-align: right; margin-bottom: 15px;">
                    <div style="background-color: #007aff; color: white; padding: 10px 15px; border-radius: 15px 15px 0px 15px; max-width: 80%;">
                        {text.get("content")}
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        elif role == "assistant":
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-start; text-align: left; margin-bottom: 15px;">
                    <div style="background-color: #f0f2f6; color: #31333F; padding: 10px 15px; border-radius: 15px 15px 15px 0px; max-width: 80%;">
                        {text.get("content")}
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )

    # --- 2. HANDLE NEW INPUT ---
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})    
        
        # Render the new user message instantly
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; text-align: right; margin-bottom: 15px;">
                <div style="background-color: #007aff; color: white; padding: 10px 15px; border-radius: 15px 15px 0px 15px; max-width: 80%;">
                    {prompt}
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
        # Render and stream the new AI response
        # We use st.empty() as a dynamic slot to handle streaming inside custom HTML
        ai_placeholder = st.empty()
        
        response_stream = chat(
            model="llama3.2",
            messages=st.session_state.messages,
            stream=True
        )
        
        full_response = ""
        for chunk in response_stream:
            full_response += chunk.message.content
            # Update the placeholder container chunk by chunk (with a subtle typing cursor)
            ai_placeholder.markdown(
                f"""
                <div style="display: flex; justify-content: flex-start; text-align: left; margin-bottom: 15px;">
                    <div style="background-color: #f0f2f6; color: #31333F; padding: 10px 15px; border-radius: 15px 15px 15px 0px; max-width: 80%;">
                        <br>{full_response}▒
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Final rewrite to drop the typing cursor once generation finishes
        ai_placeholder.markdown(
            f"""
            <div style="display: flex; justify-content: flex-start; text-align: left; margin-bottom: 15px;">
                <div style="background-color: #f0f2f6; color: #31333F; padding: 10px 15px; border-radius: 15px 15px 15px 0px; max-width: 80%;">
                    <br>{full_response}
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Commit response to history and rerun layout cleanly
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

if __name__ == "__main__":
    render()
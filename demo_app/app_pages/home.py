"""
Home page: layout and UX patterns (Section 4 of the tutorial).

Demonstrates columns, containers, tabs, expanders, and an st.status flow.
"""
import time

import streamlit as st


def render() -> None:
    st.title("Streamlit Best Practices Demo")
    st.write(
        "This app is the companion to `../README.md`. "
        "Each page in the sidebar implements one section of the guide with "
        "working, commented code."
    )

    st.subheader("Layout: columns for side-by-side content")
    col1, col2, col3 = st.columns(3)
    col1.metric("Pages", "5", help="Home, Data Explorer, Forms & State, Live Fragment, AI Chatbot")
    col2.metric("Pattern", "st.navigation", help="Preferred multipage API since Streamlit 1.36")
    col3.metric("Status", "Ready", help="This app runs standalone, no external services required")

    st.subheader("Containers and tabs")
    tab1, tab2 = st.tabs(["What this page shows", "Why it matters"])
    with tab1:
        st.write(
            "Columns, tabs, expanders, and containers are the basic building "
            "blocks for organizing a page before you add content to it."
        )
        with st.expander("See a nested container example"):
            with st.container(border=True):
                st.write("Content inside a bordered container.")
                st.write("Useful for visually grouping related widgets or results.")

    with tab2:
        st.write(
            "Deciding on structure first (sidebar vs. main area, columns vs. "
            "tabs) keeps a page readable as it grows, instead of widgets "
            "being appended in whatever order they were written."
        )

    st.subheader("Giving feedback during multi-step work")
    if st.button("Run a simulated multi-step task"):
        with st.status("Running task...", expanded=True) as status:
            st.write("Step 1: preparing")
            time.sleep(0.4)
            st.write("Step 2: processing")
            time.sleep(0.4)
            st.write("Step 3: finishing up")
            time.sleep(0.4)
            status.update(label="Task complete", state="complete")
        st.toast("Done!", icon="✅")

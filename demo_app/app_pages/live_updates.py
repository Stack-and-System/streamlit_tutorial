"""
Live Fragment page: @st.fragment for isolated reruns (Section 5), plus
st.cache_resource for a shared, expensive-to-create object (Section 2).
"""
import random
import time

import streamlit as st


@st.cache_resource
def get_shared_counter_store() -> dict:
    """Stands in for an expensive shared resource: a DB connection, a
    loaded model, an SDK client. Created once per server process and
    reused across every user and every rerun -- st.cache_resource caches
    the object itself, not a copy, so mutations are visible everywhere.
    """
    return {"created_at": time.time(), "ticks": 0}


@st.fragment(run_every="2s")
def live_metric_fragment() -> None:
    """Only this function reruns every 2 seconds -- not the whole page.

    Compare this to a manual st.rerun() loop, which would redraw and reset
    scroll position on every element on the page, not just this one.
    """
    store = get_shared_counter_store()
    store["ticks"] += 1

    col1, col2 = st.columns(2)
    col1.metric("Fragment ticks", store["ticks"])
    col2.metric("Simulated live value", f"{random.uniform(20, 30):.1f}°C")
    st.caption(f"Shared resource created at {time.strftime('%H:%M:%S', time.localtime(store['created_at']))}")


def render() -> None:
    st.title("Live Fragment")
    st.write(
        "The metrics below live inside a function decorated with "
        "`@st.fragment(run_every=\"2s\")`. Only that fragment reruns on its "
        "own timer -- the rest of this page (including anything you type "
        "below) is untouched."
    )

    live_metric_fragment()

    st.divider()
    st.subheader("The rest of the page is unaffected")
    note = st.text_input("Type here and watch the fragment keep ticking above")
    if note:
        st.write(f"You typed: {note}")

    st.caption(
        "If this used a manual rerun loop instead of a fragment, every "
        "keystroke above and every fragment tick would rerun the entire "
        "page, including this text input losing focus."
    )

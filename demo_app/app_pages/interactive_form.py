"""
Forms & State page: session_state and st.form patterns (Section 3).

Key ideas demonstrated:
- Initialize every session_state key before it's read (st.session_state.setdefault).
- Use a callback (on_click) to mutate state once, before the rerun, instead
  of scattering `if button:` checks through the page body.
- Batch multiple inputs in st.form so widgets don't trigger a rerun per
  keystroke -- only on submit.
"""
import streamlit as st


def _init_state() -> None:
    # Guarded initialization. Note this lives inside a function, called at
    # the top of render(), rather than at module level: a page module is
    # only *imported* once per server process, but render() runs on every
    # rerun for every session, which is what session_state initialization
    # actually needs to track.
    st.session_state.setdefault("submit_count", 0)
    st.session_state.setdefault("history", [])


def _add_entry(name: str, quantity: int) -> None:
    """Callback: runs once, before the script reruns, when the form submits."""
    st.session_state.submit_count += 1
    st.session_state.history.append({"name": name, "quantity": quantity})


def _clear_history() -> None:
    st.session_state.history = []
    st.session_state.submit_count = 0


def render() -> None:
    _init_state()

    st.title("Forms & Session State")
    st.write(
        "Session state remembers *this user's* current interaction across "
        "reruns -- it's the counterpart to caching, which remembers "
        "computed *results* for everyone."
    )

    st.subheader("Batched input with st.form")
    st.caption(
        "Widgets inside a form don't rerun the app on every change -- only "
        "when 'Add item' is pressed. Try typing in the text field: nothing "
        "happens until you submit."
    )

    with st.form("add_item_form", clear_on_submit=True):
        name = st.text_input("Item name")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        submitted = st.form_submit_button("Add item")

    if submitted and name:
        _add_entry(name, quantity)

    st.subheader("State that persists across reruns")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric("Items added this session", st.session_state.submit_count)
    with col2:
        st.button("Clear history", on_click=_clear_history)

    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
    else:
        st.caption("No items added yet.")

    st.divider()
    st.subheader("Callback vs. inline check")
    st.code(
        "# Preferred: mutate state in a callback, once, before rerun.\n"
        "st.button('Submit', on_click=my_callback)\n\n"
        "# Avoid: checking a button's truthiness inline mixes UI\n"
        "# rendering with state mutation and is easy to duplicate.\n"
        "if st.button('Submit'):\n"
        "    st.session_state.count += 1",
        language="python",
    )

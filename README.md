# Streamlit Best Practices: A Professional Tutorial

This tutorial covers how to structure, write, and ship Streamlit applications the way experienced teams do it. It pairs with a runnable demo project (`demo_app/`) in this same folder, where every practice below is implemented in working code. Section headers here match the files in that project, so you can read a section and immediately open the corresponding page.

Streamlit reruns your entire script top to bottom on every interaction. Nearly every best practice in this guide exists because of that one fact — it explains why caching matters, why session state exists, why fragments were added, and why widget state needs to be initialized deliberately.

## 1. Project structure and the entrypoint

Keep the entrypoint file thin. `streamlit_app.py` should only wire pages together and hold elements that are genuinely shared across the whole app, such as a sidebar logo or a global page config call. Business logic, data loading, and page content belong in their own modules.

Since Streamlit 1.36, `st.Page` and `st.navigation` are the preferred way to build multipage apps, replacing the older convention of dropping numbered files into a `pages/` folder. `st.Page` wraps a page function or file and lets you control its title, icon, and URL path explicitly rather than inferring them from a filename. `st.navigation` then assembles those pages into a router:

```python
import streamlit as st
from app_pages import home, data_explorer, interactive_form, live_updates

st.set_page_config(page_title="Streamlit Best Practices Demo", layout="wide")

pages = [
    st.Page(home.render, title="Home", icon="🏠", default=True),
    st.Page(data_explorer.render, title="Data Explorer", icon="📊"),
    st.Page(interactive_form.render, title="Forms & State", icon="📝"),
    st.Page(live_updates.render, title="Live Fragment", icon="⚡"),
]

nav = st.navigation(pages)
nav.run()
```

Anything placed in `streamlit_app.py` outside the navigation block (a sidebar header, a footer) becomes a frame around every page, so use that sparingly. Put reusable logic — data loaders, formatting helpers, API clients — in a plain `utils/` package that has no Streamlit widgets in it at all. This separation makes the logic testable with ordinary `pytest`, independent of a running Streamlit server.

A typical layout:

```
demo_app/
├── streamlit_app.py        # entrypoint / router only
├── app_pages/               # one module per page, a render() function each
├── utils/                   # pure Python: data access, calculations
├── .streamlit/
│   ├── config.toml          # theme, server settings
│   └── secrets.toml         # local only, never committed
└── requirements.txt
```

## 2. Caching: st.cache_data vs st.cache_resource

Caching is the single highest-leverage performance tool in Streamlit, because without it, every widget interaction reruns your whole script — including expensive data loads and computations — from scratch.

Use `st.cache_data` for anything that returns serializable data: a DataFrame from a query, a parsed CSV, an API response, a computed summary. Streamlit hashes the function's inputs and returns a copy of the cached value on repeat calls, so mutating the returned object in one place can't corrupt the cache for everyone else.

```python
import pandas as pd
import streamlit as st

@st.cache_data(ttl="1h", max_entries=10, show_spinner="Loading data…")
def load_sales_data(region: str) -> pd.DataFrame:
    # Expensive: a DB query, API call, or heavy computation.
    return pd.read_csv(f"data/{region}.csv")
```

Use `st.cache_resource` for unserializable, expensive-to-create objects meant to be shared across users and reruns: a database connection pool, a loaded ML model, an API client. It caches the object itself rather than a copy, so mutations are visible everywhere — which is exactly what you want for a shared connection, but a hazard if you reuse it for plain data.

```python
@st.cache_resource
def get_db_connection():
    return create_engine(st.secrets["db_url"])
```

Three practices keep caching safe and useful. First, only cache functions that are pure — same inputs always produce the same output, with no side effects — otherwise the cache silently serves stale or wrong results. Second, set a `ttl` whenever the underlying data changes over time, so the cache doesn't go stale forever. Third, don't reach for caching by default; caching every small function adds hashing overhead without payoff. Reserve it for genuinely expensive work.

## 3. Session state

Session state (`st.session_state`) is a per-user, per-session dictionary that survives reruns. It exists to answer a different question than caching does: caching avoids recomputing the same thing twice; session state remembers what a specific user is currently doing (a filter they picked, a multi-step wizard's current step, a running counter).

Always initialize a key before you use it, and do it once, guarded, near the top of the page:

```python
if "filter_region" not in st.session_state:
    st.session_state.filter_region = "All"

# or, equivalently and slightly more concise:
st.session_state.setdefault("submit_count", 0)
```

Avoid overwriting a session state value with a widget's default `value=` argument on every rerun — if a key already exists in `st.session_state`, let the widget read from it instead of re-supplying a default, or you'll fight your own state.

Prefer callbacks (`on_click`, `on_change`) for state mutations that should happen exactly once, before the rest of the script reruns, rather than scattering `if button:` checks through the page body:

```python
def increment():
    st.session_state.submit_count += 1

st.button("Submit", on_click=increment)
st.write(f"Submitted {st.session_state.submit_count} times")
```

For any input group where you don't want a rerun on every keystroke, wrap it in `st.form`. Widgets inside a form only report their values when the form's submit button is pressed, which both reduces reruns and lets you validate a whole batch of inputs together.

## 4. Layout and UX

Structure the page before you populate it. `st.columns` for side-by-side content, `st.container` for logical grouping (especially useful when you want to write into a placeholder from code that runs later), `st.tabs` for mutually exclusive views, and the sidebar (`st.sidebar` or pages passed to it via navigation) for filters and controls that should persist across the main content. Reach for `st.expander` to keep secondary detail out of the way by default.

Give the user feedback during anything that takes noticeable time. `st.spinner` for a single blocking operation, `st.status` for a multi-step process where you want to show progress and a final state (complete or error), and `st.toast` for a brief, non-blocking confirmation after an action completes. Silence during a multi-second data load reads as a bug even when the app is working correctly.

```python
with st.status("Refreshing report...", expanded=True) as status:
    st.write("Fetching data")
    df = load_sales_data(region)
    st.write("Computing summary")
    summary = summarize(df)
    status.update(label="Report ready", state="complete")
```

## 5. Performance beyond caching: fragments

`@st.fragment` lets part of a page rerun independently of the rest of the script. A widget inside a fragment only reruns that fragment's code, not the entire page — valuable when one section (a chart with its own filter, a live counter) shouldn't force everything else to redraw.

```python
@st.fragment(run_every="5s")
def live_metric():
    st.metric("Active sessions", get_current_sessions())
```

`run_every` turns a fragment into a lightweight auto-refreshing widget without a manual rerun loop. Use fragments for isolated, frequently-updating pieces of UI; for one-off heavy computations, caching is still the first tool to reach for.

## 6. Secrets and configuration

Never hardcode credentials, API keys, or connection strings in your source files. Put them in `.streamlit/secrets.toml` locally (and the equivalent secrets manager in whatever platform you deploy to), read them with `st.secrets["key"]`, and add `secrets.toml` to `.gitignore` so it never reaches version control. Ship a `secrets.toml.example` with placeholder values so collaborators know what to fill in.

Use `.streamlit/config.toml` for app-level and theme settings — page title defaults, server options, color theme — rather than passing the same arguments in code. This keeps environment-specific configuration out of your Python and makes it overridable per-deployment.

## 7. Error handling and resilience

Wrap operations that can fail for reasons outside your control — network calls, file reads, external APIs — in `try/except`, and surface a clear message with `st.error` rather than letting a raw traceback reach the user. Reserve `st.exception` for development or internal tooling where a full traceback is actually useful to the viewer.

```python
try:
    df = load_sales_data(region)
except FileNotFoundError:
    st.error(f"No data found for region '{region}'. Check the region name and try again.")
    st.stop()
```

`st.stop()` halts execution of the rest of the script cleanly, which is usually preferable to letting the page continue rendering with missing data.

## 8. Code organization and testability

Keep Streamlit calls (`st.write`, `st.button`, and so on) out of your data and business logic. A function like `load_sales_data(region)` or `calculate_churn(df)` should take plain arguments and return plain values, with no awareness that Streamlit exists — that's what makes it possible to unit test with `pytest` without spinning up a Streamlit server. Page modules then become thin: call the logic functions, and use Streamlit calls only to display the results and collect input.

## 9. Chat interfaces and streaming responses

Streamlit ships purpose-built elements for chat UIs: `st.chat_message` renders a message bubble for a given role ("user", "assistant") and `st.chat_input` pins a text box to the bottom of the page. Reach for these instead of hand-rolling chat bubbles with raw HTML — beyond saving you the CSS, content passed to `st.chat_message` is rendered through normal Streamlit/Markdown escaping, so you don't need `unsafe_allow_html` and don't have to worry about user input breaking out of your markup.

```python
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
        full_response = st.write_stream(stream_from_llm(st.session_state.messages))
    st.session_state.messages.append({"role": "assistant", "content": full_response})
```

`st.write_stream` consumes a generator (or any iterable of string chunks) and renders it incrementally, which replaces the older pattern of managing an `st.empty()` placeholder and concatenating chunks by hand. Because the call to an LLM API or a local model server is an external call like any other, wrap it in `try/except` and surface a clear `st.error` (Section 7) rather than letting a connection failure crash the page.

## 10. Deployment considerations

Pin dependencies in `requirements.txt` (or a lockfile) rather than leaving versions unconstrained, since an unpinned Streamlit or pandas upgrade can silently change behavior. Set `server.headless = true` and any resource limits in `config.toml` for containerized or cloud deployments. Whatever platform you use — Streamlit Community Cloud, a Docker container, or an internal PaaS — confirm secrets are injected through that platform's secret store, not baked into the image or repo.

## Quick-reference checklist

- Entrypoint file is thin; pages and logic live in their own modules.
- Expensive data loads and computations are wrapped in `st.cache_data` or `st.cache_resource`, with a `ttl` where the source data changes.
- Every `st.session_state` key is initialized before first use.
- State-changing logic lives in callbacks (`on_click` / `on_change`), not inline conditionals.
- Multi-field input uses `st.form` to avoid a rerun per keystroke.
- Long-running operations show a spinner, status, or toast.
- Frequently-updating, isolated UI uses `@st.fragment` instead of forcing a full-page rerun.
- Chat UIs use `st.chat_message` / `st.chat_input` / `st.write_stream` rather than hand-rolled HTML, with external model calls wrapped in `try/except`.
- Secrets live in `secrets.toml` / a secrets manager, never in source.
- Business logic is plain Python, testable without Streamlit running.
- Dependencies are pinned before deployment.

## Sources

This guide draws on Streamlit's official documentation:

- [Caching overview](https://docs.streamlit.io/develop/concepts/architecture/caching)
- [st.cache_data](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data)
- [st.cache_resource](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource)
- [Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Multipage apps overview](https://docs.streamlit.io/develop/concepts/multipage-apps/overview)
- [Define multipage apps with st.Page and st.navigation](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation)
- [Chat elements: st.chat_message and st.chat_input](https://docs.streamlit.io/develop/api-reference/chat)
- [Build a basic LLM chat app](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps)

## The accompanying demo project

Everything above is implemented in `demo_app/` next to this file: `streamlit_app.py` as the router, `app_pages/home.py` for layout patterns, `app_pages/data_explorer.py` for caching, `app_pages/interactive_form.py` for session state and forms, `app_pages/live_updates.py` for fragments, and `app_pages/ai_chat.py` for chat interfaces and streaming. See `demo_app/README.md` to run it (the chat page needs a local Ollama install).

# Streamlit Best Practices Demo

Companion project to `../streamlit_best_practices_tutorial.md`. Each page implements one section of that guide.

## Run it

```bash
cd demo_app
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # optional, not required to run
streamlit run streamlit_app.py
```

## Run the tests

```bash
cd demo_app
pip install pytest
pytest
```

## Structure

| Path | Tutorial section | What it shows |
|---|---|---|
| `streamlit_app.py` | 1. Project structure | Thin entrypoint using `st.Page` / `st.navigation` |
| `app_pages/home.py` | 4. Layout & UX | Columns, tabs, containers, `st.status`, `st.toast` |
| `app_pages/data_explorer.py` | 2. Caching, 7. Error handling | `st.cache_data`, `try/except` + `st.error` |
| `app_pages/interactive_form.py` | 3. Session state | `st.form`, callbacks, guarded state init |
| `app_pages/live_updates.py` | 5. Fragments, 2. Caching | `@st.fragment(run_every=...)`, `st.cache_resource` |
| `utils/data.py` | 8. Code organization | Pure Python logic, no Streamlit imports, unit-testable |
| `.streamlit/config.toml` | 6. Configuration | Theme and server settings |
| `.streamlit/secrets.toml.example` | 6. Secrets | Template for local secrets (never commit the real file) |
| `tests/test_data.py` | 8. Code organization | Plain `pytest` tests against `utils/data.py` |

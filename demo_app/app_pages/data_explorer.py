"""
Data Explorer page: caching (Section 2) and error handling (Section 7).

The expensive "load" step is wrapped in st.cache_data so switching filters
back and forth doesn't repeat the work. utils.data has no Streamlit
imports, so it stays independently testable; this module is the thin,
Streamlit-aware layer on top of it.
"""
import pandas as pd
import streamlit as st

from utils.data import REGIONS, generate_sales_data, summarize_sales


@st.cache_data(ttl="10m", show_spinner="Loading sales data...")
def load_sales_data(region: str) -> pd.DataFrame:
    # Stands in for a slow DB query or API call. Cached per distinct
    # `region` argument, so re-selecting a region already seen this
    # session returns instantly instead of recomputing.
    return generate_sales_data(region)


def render() -> None:
    st.title("Data Explorer")
    st.write(
        "Selecting a region below calls a `@st.cache_data`-wrapped loader. "
        "Switch regions a few times, then switch back — the repeat is instant "
        "because the result is served from cache instead of regenerated."
    )

    region = st.selectbox("Region", ["All"] + REGIONS)

    try:
        df = load_sales_data(region)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    summary = summarize_sales(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total revenue", f"${summary['total_revenue']:,.0f}")
    col2.metric("Units sold", f"{summary['total_units']:,}")
    col3.metric("Avg order value", f"${summary['avg_order_value']:.2f}")

    with st.expander("Raw data", expanded=False):
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download as CSV",
        data=df.to_csv(index=False),
        file_name=f"sales_{region.lower()}.csv",
        mime="text/csv",
    )

    st.caption(
        "Cache key here is the `region` argument. `ttl=\"10m\"` means the "
        "cache entry expires after 10 minutes even without a code change, so "
        "the data doesn't go stale indefinitely."
    )

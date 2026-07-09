"""
Plain-Python data helpers: no Streamlit imports here.

Keeping this module free of `st.*` calls means it can be unit tested with
plain pytest, independent of a running Streamlit app. The Streamlit-aware
caching wrapper lives in app_pages/data_explorer.py, right next to where
it's used.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

REGIONS = ["North", "South", "East", "West"]


def generate_sales_data(region: str, rows: int = 500, seed: int | None = None) -> pd.DataFrame:
    """Simulate a sales dataset for a region.

    Stands in for an expensive operation (a DB query or API call) that
    you would not want to repeat on every widget interaction.
    """
    if region not in REGIONS and region != "All":
        raise ValueError(f"Unknown region '{region}'. Expected one of {REGIONS + ['All']}.")

    rng = np.random.default_rng(seed if seed is not None else hash(region) % (2**32))
    dates = pd.date_range("2025-01-01", periods=rows, freq="D")
    regions = [region] * rows if region != "All" else rng.choice(REGIONS, size=rows)

    df = pd.DataFrame(
        {
            "date": dates,
            "region": regions,
            "units_sold": rng.poisson(lam=40, size=rows),
            "unit_price": rng.normal(loc=25, scale=4, size=rows).round(2),
        }
    )
    df["revenue"] = (df["units_sold"] * df["unit_price"]).round(2)
    return df


def summarize_sales(df: pd.DataFrame) -> dict:
    """Pure aggregation logic, easy to unit test on its own."""
    if df.empty:
        return {"total_revenue": 0.0, "total_units": 0, "avg_order_value": 0.0}

    total_revenue = float(df["revenue"].sum())
    total_units = int(df["units_sold"].sum())
    avg_order_value = float(df["revenue"].mean())
    return {
        "total_revenue": total_revenue,
        "total_units": total_units,
        "avg_order_value": avg_order_value,
    }

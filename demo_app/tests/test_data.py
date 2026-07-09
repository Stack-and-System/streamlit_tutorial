"""
Unit tests for utils/data.py. These run with plain pytest -- no Streamlit
server needed -- because utils.data has no Streamlit imports (Section 8).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.data import REGIONS, generate_sales_data, summarize_sales


def test_generate_sales_data_shape():
    df = generate_sales_data("North", rows=50, seed=1)
    assert len(df) == 50
    assert set(df["region"]) == {"North"}
    assert "revenue" in df.columns


def test_generate_sales_data_all_regions():
    df = generate_sales_data("All", rows=100, seed=1)
    assert set(df["region"]).issubset(set(REGIONS))


def test_generate_sales_data_invalid_region():
    try:
        generate_sales_data("Nowhere")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_summarize_sales_empty():
    import pandas as pd

    summary = summarize_sales(pd.DataFrame(columns=["units_sold", "revenue"]))
    assert summary == {"total_revenue": 0.0, "total_units": 0, "avg_order_value": 0.0}


def test_summarize_sales_basic():
    df = generate_sales_data("East", rows=20, seed=42)
    summary = summarize_sales(df)
    assert summary["total_units"] > 0
    assert summary["total_revenue"] > 0

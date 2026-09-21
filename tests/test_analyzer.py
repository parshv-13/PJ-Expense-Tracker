"""
Unit tests for Financial Analytics Calculations
"""

import pytest
import pandas as pd
from src.analyzer import (
    calculate_kpis,
    get_monthly_spending,
    get_category_spending,
    get_highest_spending_days
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "date": ["2026-01-05", "2026-01-10", "2026-01-15", "2026-02-01", "2026-02-05"],
        "description": ["Swiggy", "Uber", "Amazon", "Swiggy", "Zomato"],
        "amount": [500.0, 250.0, 1250.0, 400.0, 600.0],
        "category": ["Food", "Transport", "Shopping", "Food", "Food"]
    })


def test_calculate_kpis_empty():
    empty_df = pd.DataFrame()
    kpis = calculate_kpis(empty_df)
    assert kpis["total_spending"] == 0.0
    assert kpis["total_transactions"] == 0
    assert kpis["largest_transaction"]["amount"] == 0.0


def test_calculate_kpis_totals(sample_df):
    kpis = calculate_kpis(sample_df)
    # Total sum: 500 + 250 + 1250 + 400 + 600 = 3000
    assert kpis["total_spending"] == 3000.0
    assert kpis["total_transactions"] == 5
    # Largest is Amazon: 1250.0
    assert kpis["largest_transaction"]["amount"] == 1250.0
    assert kpis["largest_transaction"]["description"] == "Amazon"
    # Current month is Feb 2026: 400 + 600 = 1000.0
    assert kpis["current_month_spending"] == 1000.0
    # Top category overall is Food: 500 + 400 + 600 = 1500.0 (50%)
    assert kpis["top_category"]["category"] == "Food"
    assert kpis["top_category"]["amount"] == 1500.0
    assert kpis["top_category"]["percent"] == 50.0


def test_get_monthly_spending(sample_df):
    monthly = get_monthly_spending(sample_df)
    assert len(monthly) == 2
    # Jan total: 2000, Feb total: 1000
    assert monthly.iloc[0]["amount"] == 2000.0
    assert monthly.iloc[1]["amount"] == 1000.0
    assert monthly.iloc[1]["mom_change_amount"] == -1000.0


def test_get_category_spending(sample_df):
    cat_df = get_category_spending(sample_df)
    assert len(cat_df) == 3
    # Food is highest
    assert cat_df.iloc[0]["category"] == "Food"
    assert cat_df.iloc[0]["amount"] == 1500.0
    assert cat_df.iloc[0]["percentage"] == 50.0


def test_highest_spending_days(sample_df):
    high_days = get_highest_spending_days(sample_df, top_n=2)
    assert len(high_days) == 2
    assert high_days.iloc[0]["amount"] == 1250.0

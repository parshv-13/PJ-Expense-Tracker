"""
Unit tests for Recurring Expense Detection
"""

import pytest
import pandas as pd
from src.recurring import detect_recurring_expenses


def test_detect_recurring_subscriptions():
    df = pd.DataFrame({
        "date": [
            "2026-01-05", "2026-02-05", "2026-03-05",
            "2026-01-10", "2026-02-10", "2026-03-10",
            "2026-01-15"
        ],
        "description": [
            "Netflix Subscription", "Netflix Subscription", "Netflix Subscription",
            "Spotify Premium", "Spotify Premium", "Spotify Premium",
            "One-time shopping"
        ],
        "amount": [649.0, 649.0, 649.0, 119.0, 119.0, 119.0, 4500.0],
        "category": ["Entertainment", "Entertainment", "Entertainment", "Entertainment", "Entertainment", "Shopping"]
    })

    result = detect_recurring_expenses(df)
    recurring_items = result["recurring_items"]

    assert len(recurring_items) == 2
    descriptions = [item["description"] for item in recurring_items]
    assert "Netflix Subscription" in descriptions
    assert "Spotify Premium" in descriptions

    # Estimated monthly total = 649 + 119 = 768
    assert result["total_estimated_monthly"] == 768.0


def test_no_recurring_when_single_occurrences():
    df = pd.DataFrame({
        "date": ["2026-01-05", "2026-01-10"],
        "description": ["Swiggy", "Uber"],
        "amount": [300.0, 200.0],
        "category": ["Food", "Transport"]
    })

    result = detect_recurring_expenses(df)
    assert len(result["recurring_items"]) == 0
    assert result["total_estimated_monthly"] == 0.0

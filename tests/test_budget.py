"""
Unit tests for Budget Calculations and Threshold Alerts
"""

import pytest
import pandas as pd
from src.budget import calculate_budget_status, get_budget_alerts


def test_budget_status_healthy_warning_exceeded():
    tx_df = pd.DataFrame({
        "date": ["2026-01-05", "2026-01-10", "2026-01-12"],
        "description": ["Swiggy", "Zara", "Gas Bill"],
        "amount": [450.0, 4200.0, 3100.0],
        "category": ["Food", "Shopping", "Utilities"]
    })

    budgets = {
        "Food": 1000.0,         # 450 spent -> 45% (Healthy)
        "Shopping": 5000.0,     # 4200 spent -> 84% (Warning)
        "Utilities": 3000.0     # 3100 spent -> 103.3% (Exceeded)
    }

    budget_df = calculate_budget_status(tx_df, budgets, month="2026-01")

    # Verify status assignments
    food_row = budget_df[budget_df["category"] == "Food"].iloc[0]
    assert food_row["status"] == "Healthy"
    assert food_row["usage_pct"] == 45.0
    assert food_row["remaining"] == 550.0

    shopping_row = budget_df[budget_df["category"] == "Shopping"].iloc[0]
    assert shopping_row["status"] == "Warning"
    assert shopping_row["usage_pct"] == 84.0

    util_row = budget_df[budget_df["category"] == "Utilities"].iloc[0]
    assert util_row["status"] == "Exceeded"
    assert util_row["remaining"] == -100.0


def test_budget_alerts():
    budget_df = pd.DataFrame([
        {"category": "Food", "budget": 1000.0, "spent": 400.0, "usage_pct": 40.0},
        {"category": "Shopping", "budget": 5000.0, "spent": 4500.0, "usage_pct": 90.0},
        {"category": "Entertainment", "budget": 2000.0, "spent": 2500.0, "usage_pct": 125.0}
    ])

    alerts = get_budget_alerts(budget_df)
    assert len(alerts) == 2

    # Verify danger alert for Entertainment
    danger_alert = [a for a in alerts if a["type"] == "danger"][0]
    assert danger_alert["category"] == "Entertainment"
    assert "Exceeded" in danger_alert["message"]

    # Verify warning alert for Shopping
    warning_alert = [a for a in alerts if a["type"] == "warning"][0]
    assert warning_alert["category"] == "Shopping"
    assert "Approaching Limit" in warning_alert["message"]

"""
Unit tests for Anomaly Detection
"""

import pytest
import pandas as pd
from src.anomaly import detect_unusual_expenses


def test_detect_unusual_expenses():
    # Normal spending around 300-500, with one 5000 outlier in Food
    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "date": ["2026-01-01", "2026-01-05", "2026-01-10", "2026-01-15", "2026-01-20", "2026-01-25"],
        "description": ["Swiggy", "Zomato", "Cafe Coffee", "Burger King", "Swiggy", "Fine Dining Luxury"],
        "amount": [300.0, 350.0, 400.0, 320.0, 380.0, 5000.0],
        "category": ["Food", "Food", "Food", "Food", "Food", "Food"]
    })

    anomalies = detect_unusual_expenses(df, threshold_multiplier=2.0)
    assert not anomalies.empty
    assert len(anomalies) == 1
    assert anomalies.iloc[0]["description"] == "Fine Dining Luxury"
    assert anomalies.iloc[0]["amount"] == 5000.0
    assert "higher than your average Food expense" in anomalies.iloc[0]["explanation"]


def test_detect_no_anomalies_when_uniform():
    df = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "date": ["2026-01-01", "2026-01-05", "2026-01-10", "2026-01-15"],
        "description": ["Uber", "Uber", "Uber", "Uber"],
        "amount": [200.0, 210.0, 205.0, 215.0],
        "category": ["Transport", "Transport", "Transport", "Transport"]
    })

    anomalies = detect_unusual_expenses(df, threshold_multiplier=2.0)
    assert anomalies.empty

"""
Unit tests for Keyword Categorization Engine
"""

import pytest
import pandas as pd
from src.categorizer import categorize_transaction, categorize_dataframe, KEYWORD_RULES


def test_food_categorization():
    assert categorize_transaction("Swiggy Order #9021") == "Food"
    assert categorize_transaction("Zomato Delivery biryani") == "Food"
    assert categorize_transaction("McDonalds Burger") == "Food"
    assert categorize_transaction("Starbucks Coffee") == "Food"


def test_transport_categorization():
    assert categorize_transaction("Uber Ride Downtown") == "Transport"
    assert categorize_transaction("Ola Cab") == "Transport"
    assert categorize_transaction("HPCL Petrol Pump") == "Transport"
    assert categorize_transaction("Metro card recharge") == "Transport"


def test_entertainment_categorization():
    assert categorize_transaction("Netflix Monthly") == "Entertainment"
    assert categorize_transaction("Spotify Premium") == "Entertainment"
    assert categorize_transaction("BookMyShow Movie PVR") == "Entertainment"


def test_utilities_and_groceries():
    assert categorize_transaction("Airtel Broadband Fiber") == "Utilities"
    assert categorize_transaction("Electricity Power Utility") == "Utilities"
    assert categorize_transaction("Blinkit Quick Delivery") == "Groceries"
    assert categorize_transaction("BigBasket Vegetables") == "Groceries"


def test_unmatched_returns_other():
    assert categorize_transaction("Random Unlabeled Expense") == "Other"
    assert categorize_transaction("") == "Other"
    assert categorize_transaction(None) == "Other"


def test_categorize_dataframe():
    df = pd.DataFrame({
        "description": ["Swiggy", "Uber", "Amazon", "Unlisted Item"]
    })
    categories = categorize_dataframe(df)
    assert categories == ["Food", "Transport", "Shopping", "Other"]

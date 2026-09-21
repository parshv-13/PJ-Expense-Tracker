"""
Budget Management & Tracking Module
-----------------------------------
Compares actual spending against allocated monthly budgets.
Provides status indicators:
- Healthy: Under 80%
- Warning (Orange): 80% to 100%
- Exceeded (Red): Over 100%
"""

import pandas as pd
from typing import Dict, List, Any


def calculate_budget_status(
    transactions_df: pd.DataFrame,
    budgets: Dict[str, float],
    month: str = None
) -> pd.DataFrame:
    """
    Computes budget usage for each budgeted category for a given month ('YYYY-MM').
    If month is None, uses the latest month found in transactions_df.
    
    Returns a DataFrame with columns:
    ['category', 'budget', 'spent', 'remaining', 'usage_pct', 'status', 'status_color']
    """
    if transactions_df.empty:
        # Return empty rows with zero spending
        records = []
        for cat, limit in budgets.items():
            records.append({
                "category": cat,
                "budget": limit,
                "spent": 0.0,
                "remaining": limit,
                "usage_pct": 0.0,
                "status": "Healthy",
                "status_color": "green"
            })
        return pd.DataFrame(records)

    clean_df = transactions_df.copy()
    clean_df["date"] = pd.to_datetime(clean_df["date"])
    clean_df["month_year"] = clean_df["date"].dt.strftime("%Y-%m")
    clean_df["amount"] = pd.to_numeric(clean_df["amount"], errors="coerce").fillna(0.0)

    target_month = month if month else clean_df["month_year"].max()
    curr_month_df = clean_df[clean_df["month_year"] == target_month]

    # Calculate spent per category
    spent_series = curr_month_df.groupby("category")["amount"].sum()

    # Combine with budgets
    all_categories = set(budgets.keys()).union(set(spent_series.index))
    records = []

    for cat in sorted(all_categories):
        budget_limit = budgets.get(cat, 0.0)
        spent_amt = float(spent_series.get(cat, 0.0))
        remaining = budget_limit - spent_amt
        usage_pct = (spent_amt / budget_limit * 100) if budget_limit > 0 else (100.0 if spent_amt > 0 else 0.0)

        if budget_limit == 0.0:
            status = "No Budget"
            status_color = "gray"
        elif usage_pct > 100.0:
            status = "Exceeded"
            status_color = "red"
        elif usage_pct >= 80.0:
            status = "Warning"
            status_color = "orange"
        else:
            status = "Healthy"
            status_color = "green"

        records.append({
            "category": cat,
            "budget": budget_limit,
            "spent": spent_amt,
            "remaining": remaining,
            "usage_pct": round(usage_pct, 1),
            "status": status,
            "status_color": status_color
        })

    budget_df = pd.DataFrame(records)
    # Sort with exceeded and warning first, then alphabetical
    budget_df["sort_order"] = budget_df["status"].map({"Exceeded": 0, "Warning": 1, "Healthy": 2, "No Budget": 3})
    budget_df = budget_df.sort_values(by=["sort_order", "spent"], ascending=[True, False]).drop(columns=["sort_order"])
    return budget_df


def get_budget_alerts(budget_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generates notification alert messages based on budget usage.
    """
    alerts = []
    if budget_df.empty:
        return alerts

    for _, row in budget_df.iterrows():
        cat = row["category"]
        usage = row["usage_pct"]
        spent = row["spent"]
        limit = row["budget"]

        if limit <= 0:
            continue

        if usage > 100.0:
            over = spent - limit
            alerts.append({
                "type": "danger",
                "category": cat,
                "message": f"🚨 Budget Exceeded for **{cat}**: Spent {spent:,.0f} of {limit:,.0f} ({usage:.0f}% - over by {over:,.0f})"
            })
        elif usage >= 80.0:
            remaining = limit - spent
            alerts.append({
                "type": "warning",
                "category": cat,
                "message": f"⚠️ Approaching Limit for **{cat}**: Spent {spent:,.0f} of {limit:,.0f} ({usage:.0f}% - only {remaining:,.0f} left)"
            })

    return alerts

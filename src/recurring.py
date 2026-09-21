"""
Recurring Expense Detection Module
----------------------------------
Identifies recurring periodic expenses (such as subscriptions, rent, gym memberships,
utility bills) based on repeated descriptions, recurring intervals, and similar amounts.
"""

import pandas as pd
from typing import List, Dict, Any


def detect_recurring_expenses(
    df: pd.DataFrame,
    min_occurrences: int = 2,
    amount_tolerance_pct: float = 0.15
) -> Dict[str, Any]:
    """
    Identifies recurring transactions by grouping by standardized description
    and checking for repeating intervals (e.g. roughly monthly or periodic)
    and consistent amounts (within tolerance).

    Returns a dictionary:
    {
        "recurring_items": list of dicts with details,
        "total_estimated_monthly": float
    }
    """
    if df.empty or len(df) < min_occurrences:
        return {
            "recurring_items": [],
            "total_estimated_monthly": 0.0
        }

    clean_df = df.copy()
    clean_df["date"] = pd.to_datetime(clean_df["date"])
    clean_df["amount"] = pd.to_numeric(clean_df["amount"], errors="coerce").fillna(0.0)
    clean_df["desc_clean"] = clean_df["description"].str.strip().str.lower()

    recurring_items: List[Dict[str, Any]] = []
    total_estimated_monthly = 0.0

    # Group by cleaned description
    grouped = clean_df.groupby("desc_clean")

    for desc_clean, group in grouped:
        if len(group) < min_occurrences:
            continue

        sorted_group = group.sort_values("date")
        amounts = sorted_group["amount"].values

        # Check amount consistency: standard deviation relative to mean
        mean_amt = amounts.mean()
        if mean_amt <= 0:
            continue

        # Check if max variation is within tolerance
        max_diff = max(abs(amounts - mean_amt))
        if (max_diff / mean_amt) <= amount_tolerance_pct:
            # Check dates interval
            date_diffs = sorted_group["date"].diff().dropna().dt.days
            avg_interval_days = date_diffs.mean() if len(date_diffs) > 0 else 30

            # Categorize frequency
            if 20 <= avg_interval_days <= 40:
                frequency = "Monthly"
                monthly_impact = mean_amt
            elif 5 <= avg_interval_days <= 10:
                frequency = "Weekly"
                monthly_impact = mean_amt * 4.33
            elif avg_interval_days > 40:
                frequency = "Bi-Monthly / Periodic"
                monthly_impact = mean_amt / (avg_interval_days / 30)
            else:
                frequency = "Frequent / Repeating"
                monthly_impact = mean_amt * (30 / max(avg_interval_days, 1))

            latest_row = sorted_group.iloc[-1]
            original_desc = latest_row["description"]
            category = latest_row["category"]

            recurring_items.append({
                "description": original_desc,
                "category": category,
                "average_amount": round(mean_amt, 2),
                "frequency": frequency,
                "occurrences": len(group),
                "last_paid_date": latest_row["date"].strftime("%Y-%m-%d"),
                "estimated_monthly_cost": round(monthly_impact, 2)
            })

            total_estimated_monthly += monthly_impact

    # Sort recurring items by monthly impact descending
    recurring_items.sort(key=lambda x: x["estimated_monthly_cost"], reverse=True)

    return {
        "recurring_items": recurring_items,
        "total_estimated_monthly": round(total_estimated_monthly, 2)
    }

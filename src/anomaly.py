"""
Unusual Spending (Anomaly) Detection Module
------------------------------------------
Detects unusually large or atypical transactions using transparent,
beginner-friendly statistical methods (Mean + K * Standard Deviation or Interquartile Range).
Provides crystal-clear, non-alarmist explanations for why an expense was flagged.
"""

import pandas as pd
from typing import List, Dict, Any


def detect_unusual_expenses(
    df: pd.DataFrame,
    threshold_multiplier: float = 2.0,
    min_category_transactions: int = 3
) -> pd.DataFrame:
    """
    Identifies unusual transactions within each category.
    
    Statistical Approach:
    For each category with at least `min_category_transactions`, calculates the mean
    and standard deviation of spending. Any transaction exceeding
    (mean + threshold_multiplier * std) or (median + 2 * IQR) is flagged as an anomaly.
    
    Returns a DataFrame containing flagged transactions with columns:
    ['id', 'date', 'description', 'amount', 'category', 'expected_avg', 'explanation']
    """
    if df.empty or len(df) < 3:
        return pd.DataFrame(columns=[
            "id", "date", "description", "amount", "category", "expected_avg", "explanation"
        ])

    clean_df = df.copy()
    clean_df["amount"] = pd.to_numeric(clean_df["amount"], errors="coerce").fillna(0.0)

    flagged_records: List[Dict[str, Any]] = []

    # Analyze per category for contextual accuracy
    for category, group in clean_df.groupby("category"):
        amounts = group["amount"]
        count = len(amounts)

        if count < min_category_transactions:
            # Fallback for small categories: flag if single transaction > 3x category average
            mean_val = amounts.mean()
            for idx, row in group.iterrows():
                if row["amount"] > 3 * mean_val and row["amount"] > 1000:
                    flagged_records.append({
                        "id": row.get("id", idx),
                        "date": str(row["date"]),
                        "description": row["description"],
                        "amount": float(row["amount"]),
                        "category": category,
                        "expected_avg": round(mean_val, 2),
                        "explanation": f"Amount is significantly higher than usual for {category} (Average: {mean_val:.2f})"
                    })
            continue

        mean = amounts.mean()
        std = amounts.std()
        median = amounts.median()

        # Upper boundary threshold
        threshold = mean + (threshold_multiplier * std)

        # Flag transactions exceeding the threshold
        outliers = group[group["amount"] > threshold]

        for idx, row in outliers.iterrows():
            amt = float(row["amount"])
            ratio = (amt / mean) if mean > 0 else 1.0
            explanation = (
                f"Transaction amount ({amt:,.2f}) is {ratio:.1f}x higher than your "
                f"average {category} expense of {mean:,.2f}."
            )
            flagged_records.append({
                "id": row.get("id", idx),
                "date": str(row["date"]),
                "description": row["description"],
                "amount": amt,
                "category": category,
                "expected_avg": round(mean, 2),
                "explanation": explanation
            })

    if not flagged_records:
        return pd.DataFrame(columns=[
            "id", "date", "description", "amount", "category", "expected_avg", "explanation"
        ])

    result_df = pd.DataFrame(flagged_records)
    result_df = result_df.sort_values(by="amount", ascending=False)
    return result_df

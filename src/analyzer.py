"""
Analytics Module
----------------
Provides statistical and aggregate financial computations:
- Dashboard KPI summaries (total, current month, daily average, largest transaction)
- Monthly spending rollups and Month-over-Month (MoM) growth calculations
- Category-wise totals and percentages
- Day-of-week and highest spending day insights
"""

import pandas as pd
from typing import Dict, Any, Optional, Tuple


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Ensures dates are datetime and amounts are numeric."""
    if df.empty:
        return df.copy()

    clean_df = df.copy()
    clean_df["date"] = pd.to_datetime(clean_df["date"])
    clean_df["amount"] = pd.to_numeric(clean_df["amount"], errors="coerce").fillna(0.0)
    clean_df["month_year"] = clean_df["date"].dt.strftime("%Y-%m")
    clean_df["day_name"] = clean_df["date"].dt.day_name()
    return clean_df


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes top-level dashboard metrics:
    - total_spending: sum of all transactions
    - current_month_spending: total spent in the most recent calendar month
    - avg_daily_spending: average daily spending in the current month
    - total_transactions: number of transactions recorded
    - largest_transaction: dictionary of the single biggest expense
    - top_category: category with highest spending and its amount
    """
    if df.empty:
        return {
            "total_spending": 0.0,
            "current_month_spending": 0.0,
            "avg_daily_spending": 0.0,
            "total_transactions": 0,
            "largest_transaction": {"description": "N/A", "amount": 0.0, "category": "N/A", "date": "N/A"},
            "top_category": {"category": "N/A", "amount": 0.0, "percent": 0.0},
            "current_month_name": "N/A"
        }

    clean_df = prepare_dataframe(df)

    total_spending = float(clean_df["amount"].sum())
    total_transactions = len(clean_df)

    # Find the most recent month present in data
    latest_month = clean_df["month_year"].max()
    curr_month_df = clean_df[clean_df["month_year"] == latest_month]
    current_month_spending = float(curr_month_df["amount"].sum())

    # Average daily spending in the current active month
    num_days = curr_month_df["date"].dt.day.nunique()
    avg_daily_spending = current_month_spending / max(num_days, 1)

    # Largest transaction
    max_idx = clean_df["amount"].idxmax()
    largest_row = clean_df.loc[max_idx]
    largest_transaction = {
        "description": str(largest_row["description"]),
        "amount": float(largest_row["amount"]),
        "category": str(largest_row["category"]),
        "date": largest_row["date"].strftime("%Y-%m-%d")
    }

    # Top category overall
    cat_totals = clean_df.groupby("category")["amount"].sum()
    top_cat_name = str(cat_totals.idxmax())
    top_cat_amt = float(cat_totals.max())
    top_cat_pct = (top_cat_amt / total_spending * 100) if total_spending > 0 else 0.0

    return {
        "total_spending": total_spending,
        "current_month_spending": current_month_spending,
        "avg_daily_spending": avg_daily_spending,
        "total_transactions": total_transactions,
        "largest_transaction": largest_transaction,
        "top_category": {
            "category": top_cat_name,
            "amount": top_cat_amt,
            "percent": top_cat_pct
        },
        "current_month_name": pd.to_datetime(latest_month + "-01").strftime("%B %Y")
    }


def get_monthly_spending(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns monthly spending aggregated by month with Month-over-Month (MoM) growth %.
    Output columns: ['month_year', 'month_label', 'amount', 'mom_change_pct', 'mom_change_amount']
    """
    if df.empty:
        return pd.DataFrame(columns=["month_year", "month_label", "amount", "mom_change_pct", "mom_change_amount"])

    clean_df = prepare_dataframe(df)
    monthly = clean_df.groupby("month_year")["amount"].sum().reset_index()
    monthly = monthly.sort_values("month_year")

    # Format human-readable month labels e.g. "Jan 2026"
    monthly["month_label"] = pd.to_datetime(monthly["month_year"] + "-01").dt.strftime("%b %Y")
    
    # Calculate Month-over-Month change
    monthly["mom_change_amount"] = monthly["amount"].diff().fillna(0.0)
    monthly["mom_change_pct"] = (monthly["amount"].pct_change() * 100).fillna(0.0)

    return monthly


def get_category_spending(df: pd.DataFrame, month: Optional[str] = None) -> pd.DataFrame:
    """
    Returns category spending totals and percentages, optionally filtered by month ('YYYY-MM').
    """
    if df.empty:
        return pd.DataFrame(columns=["category", "amount", "percentage"])

    clean_df = prepare_dataframe(df)
    if month:
        clean_df = clean_df[clean_df["month_year"] == month]

    if clean_df.empty:
        return pd.DataFrame(columns=["category", "amount", "percentage"])

    cat_df = clean_df.groupby("category")["amount"].sum().reset_index()
    cat_df = cat_df.sort_values("amount", ascending=False)
    total = cat_df["amount"].sum()
    cat_df["percentage"] = (cat_df["amount"] / total * 100).round(1) if total > 0 else 0.0

    return cat_df


def get_daily_spending(df: pd.DataFrame) -> pd.DataFrame:
    """Returns daily spending totals for line/bar trend charts."""
    if df.empty:
        return pd.DataFrame(columns=["date", "amount"])

    clean_df = prepare_dataframe(df)
    daily = clean_df.groupby(clean_df["date"].dt.strftime("%Y-%m-%d"))["amount"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")
    return daily


def get_highest_spending_days(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Returns the top N days with highest spending."""
    if df.empty:
        return pd.DataFrame(columns=["date", "amount", "day_name"])

    clean_df = prepare_dataframe(df)
    daily = clean_df.groupby(["date", "day_name"])["amount"].sum().reset_index()
    daily = daily.sort_values("amount", ascending=False).head(top_n)
    daily["date_str"] = daily["date"].dt.strftime("%d %b %Y")
    return daily

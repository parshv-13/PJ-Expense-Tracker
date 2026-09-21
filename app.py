"""
PJ Expense Tracker - Streamlit Application
------------------------------------------
A portfolio-ready personal finance app built with Streamlit, SQLite, Pandas, and Plotly.
Visual Theme: Emerald Green, Teal, Off-White, Dark Charcoal, Orange warning, Red alert.
Strict Rule: ZERO purple, indigo, or blue anywhere.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

from src.database import (
    init_db,
    get_all_transactions,
    add_transaction,
    insert_transactions_bulk,
    update_transaction_category,
    delete_transaction,
    clear_all_transactions,
    get_budgets,
    set_budget,
    get_setting,
    set_setting
)
from src.categorizer import CATEGORIES, categorize_transaction, categorize_dataframe
from src.analyzer import (
    calculate_kpis,
    get_monthly_spending,
    get_category_spending,
    get_daily_spending,
    get_highest_spending_days
)
from src.budget import calculate_budget_status, get_budget_alerts
from src.anomaly import detect_unusual_expenses
from src.recurring import detect_recurring_expenses
from src.reports import export_to_csv, generate_pdf_report

# -------------------------------------------------------------
# 1. Page Configuration & Custom Styling
# -------------------------------------------------------------
st.set_page_config(
    page_title="PJ Expense Tracker",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema on startup
init_db()

# Custom Clean CSS (strictly adhering to: Teal, Green, Charcoal, Off-White, Orange, Red)
CUSTOM_CSS = """
<style>
    /* Global Base */
    :root {
        --primary-green: #10B981;
        --dark-green: #059669;
        --teal-accent: #0D9488;
        --charcoal-dark: #111827;
        --charcoal-light: #1F2937;
        --neutral-gray: #6B7280;
        --card-bg: #FFFFFF;
        --warning-orange: #F59E0B;
        --alert-red: #EF4444;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border-left: 4px solid var(--teal-accent);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #4B5563;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        color: #111827;
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .metric-sub {
        color: #6B7280;
        font-size: 0.78rem;
        margin-top: 0.25rem;
    }

    /* Status Badges */
    .badge-healthy {
        background-color: #ECFDF5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-warning {
        background-color: #FFFBEB;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-exceeded {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }

    /* Buttons override - Green/Teal only */
    div.stButton > button:first-child {
        background-color: #0D9488;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.45rem 1rem;
        transition: background-color 0.2s;
    }
    div.stButton > button:first-child:hover {
        background-color: #0F766E;
        color: white;
        border: none;
    }

    /* Progress bar tint override */
    .stProgress > div > div > div > div {
        background-color: #10B981;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Strict Color Palette for Plotly Charts (Teal, Emerald, Mint, Olive, Charcoal, Amber, Coral)
# Explicitly NO purple, indigo, or blue.
PALETTE = [
    "#0D9488",  # Deep Teal
    "#10B981",  # Emerald Green
    "#14B8A6",  # Light Teal
    "#34D399",  # Mint Green
    "#84CC16",  # Lime Green
    "#EAB308",  # Amber Yellow
    "#F97316",  # Bright Orange
    "#F59E0B",  # Warm Orange
    "#EF4444",  # Coral Red
    "#374151",  # Dark Slate
    "#6B7280"   # Neutral Gray
]

# Currency Symbol
currency_symbol = get_setting("currency", "₹")


# -------------------------------------------------------------
# 2. Sidebar Navigation
# -------------------------------------------------------------
st.sidebar.markdown(
    f"""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom: 1rem;'>
        <div style='background-color:#0D9488; width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:1.1rem;'>
            ₹
        </div>
        <div>
            <div style='font-size:1.05rem; font-weight:700; color:#111827;'>PJ Expense Tracker</div>
            <div style='font-size:0.75rem; color:#6B7280;'>Personal Finance Assistant</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

menu_selection = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Transactions", "CSV Import", "Budgets", "Analytics", "Reports", "Settings"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='font-size:0.78rem; color:#6B7280;'>
        <strong>Quick Tip:</strong> Upload <code>data/sample_transactions.csv</code> in the <em>CSV Import</em> tab to instantly see realistic insights!
    </div>
    """,
    unsafe_allow_html=True
)


# Fetch data
all_tx_df = get_all_transactions()
budgets_dict = get_budgets()


# =============================================================
# PAGE 1: DASHBOARD
# =============================================================
if menu_selection == "Dashboard":
    st.title("📊 Financial Dashboard")
    st.markdown("Real-time summary of your expenditures, active budgets, and recent alerts.")

    if all_tx_df.empty:
        st.info("👋 Welcome! No transactions recorded yet. Go to **CSV Import** to load sample data or add transactions manually in **Transactions**.")
    else:
        kpis = calculate_kpis(all_tx_df)
        budget_df = calculate_budget_status(all_tx_df, budgets_dict)
        alerts = get_budget_alerts(budget_df)

        # Budget overall usage calculation
        total_budget = sum(budgets_dict.values())
        total_month_spent = kpis["current_month_spending"]
        budget_usage_pct = (total_month_spent / total_budget * 100) if total_budget > 0 else 0.0

        # KPI Metrics Cards (Row 1)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: #0D9488;">
                    <div class="metric-title">Total Spending</div>
                    <div class="metric-value">{currency_symbol}{kpis['total_spending']:,.2f}</div>
                    <div class="metric-sub">Across all recorded dates</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: #10B981;">
                    <div class="metric-title">{kpis['current_month_name']} Spending</div>
                    <div class="metric-value">{currency_symbol}{kpis['current_month_spending']:,.2f}</div>
                    <div class="metric-sub">Active period spending</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: #059669;">
                    <div class="metric-title">Daily Average</div>
                    <div class="metric-value">{currency_symbol}{kpis['avg_daily_spending']:,.2f}</div>
                    <div class="metric-sub">Average per active day</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col4:
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: #374151;">
                    <div class="metric-title">Transactions</div>
                    <div class="metric-value">{kpis['total_transactions']}</div>
                    <div class="metric-sub">Total records tracked</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # KPI Metrics Cards (Row 2)
        col5, col6, col7 = st.columns(3)
        with col5:
            lt = kpis["largest_transaction"]
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: #F97316;">
                    <div class="metric-title">Largest Transaction</div>
                    <div class="metric-value">{currency_symbol}{lt['amount']:,.2f}</div>
                    <div class="metric-sub">{lt['description']} ({lt['category']})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col6:
            top_cat = kpis["top_category"]
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: #14B8A6;">
                    <div class="metric-title">Top Spending Category</div>
                    <div class="metric-value">{top_cat['category']}</div>
                    <div class="metric-sub">{currency_symbol}{top_cat['amount']:,.2f} ({top_cat['percent']:.1f}% of total)</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col7:
            status_color = "#10B981" if budget_usage_pct < 80 else ("#F59E0B" if budget_usage_pct <= 100 else "#EF4444")
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: {status_color};">
                    <div class="metric-title">Overall Budget Usage</div>
                    <div class="metric-value">{budget_usage_pct:.1f}%</div>
                    <div class="metric-sub">{currency_symbol}{total_month_spent:,.0f} of {currency_symbol}{total_budget:,.0f} limit</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        # Alerts section if applicable
        if alerts:
            st.subheader("⚠️ Spending Alerts")
            for alert in alerts[:3]:
                if alert["type"] == "danger":
                    st.error(alert["message"])
                else:
                    st.warning(alert["message"])

        # Charts Row
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([3, 2])

        with col_c1:
            st.subheader("Monthly Spending Trend")
            monthly_df = get_monthly_spending(all_tx_df)
            if not monthly_df.empty:
                fig_monthly = px.bar(
                    monthly_df,
                    x="month_label",
                    y="amount",
                    text="amount",
                    labels={"month_label": "Month", "amount": f"Total Spent ({currency_symbol})"},
                    color_discrete_sequence=["#0D9488"]
                )
                fig_monthly.update_traces(
                    texttemplate=f'{currency_symbol}%{{text:,.0f}}',
                    textposition='outside',
                    marker_line_color="#0F766E",
                    marker_line_width=1.5
                )
                fig_monthly.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#374151"),
                    margin=dict(l=10, r=10, t=30, b=10),
                    yaxis=dict(gridcolor="#E5E7EB")
                )
                st.plotly_chart(fig_monthly, use_container_width=True)

        with col_c2:
            st.subheader("Category Distribution")
            cat_df = get_category_spending(all_tx_df)
            if not cat_df.empty:
                fig_donut = px.pie(
                    cat_df,
                    names="category",
                    values="amount",
                    hole=0.55,
                    color_discrete_sequence=PALETTE
                )
                fig_donut.update_traces(
                    textinfo="percent+label",
                    textfont_size=11,
                    marker=dict(line=dict(color="#FFFFFF", width=2))
                )
                fig_donut.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#374151"),
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_donut, use_container_width=True)


# =============================================================
# PAGE 2: TRANSACTIONS (CRUD + Search & Filter)
# =============================================================
elif menu_selection == "Transactions":
    st.title("💳 Manage Transactions")
    st.markdown("Search, filter, categorize, or manually record new transactions.")

    # Tab 1: View & Filter, Tab 2: Add Transaction
    tab_view, tab_add = st.tabs(["📋 View & Filter", "➕ Add Single Transaction"])

    with tab_view:
        if all_tx_df.empty:
            st.info("No transactions found. Add a transaction or upload a CSV file.")
        else:
            # Filter bar
            f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
            with f_col1:
                search_query = st.text_input("🔍 Search Description", placeholder="e.g. Swiggy, Uber...")
            with f_col2:
                selected_categories = st.multiselect(
                    "Filter Categories",
                    options=sorted(all_tx_df["category"].unique()),
                    default=[]
                )
            with f_col3:
                min_amt = float(all_tx_df["amount"].min())
                max_amt = float(all_tx_df["amount"].max())
                amt_range = st.slider(
                    f"Amount Range ({currency_symbol})",
                    min_value=0.0,
                    max_value=max(max_amt, 100.0),
                    value=(0.0, max(max_amt, 100.0))
                )

            # Apply filters
            filtered_df = all_tx_df.copy()
            if search_query:
                filtered_df = filtered_df[filtered_df["description"].str.contains(search_query, case=False, na=False)]
            if selected_categories:
                filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
            filtered_df = filtered_df[
                (filtered_df["amount"] >= amt_range[0]) & (filtered_df["amount"] <= amt_range[1])
            ]

            st.write(f"Showing **{len(filtered_df)}** of {len(all_tx_df)} transactions (Total: {currency_symbol}{filtered_df['amount'].sum():,.2f})")

            # Display table with edit options
            st.dataframe(
                filtered_df[["id", "date", "description", "amount", "category", "notes"]],
                use_container_width=True,
                hide_index=True
            )

            # Quick Category Override & Delete tool
            st.markdown("---")
            st.subheader("✏️ Quick Modify / Delete Transaction")
            mod_col1, mod_col2, mod_col3, mod_col4 = st.columns([1.5, 2, 1.5, 1])
            with mod_col1:
                selected_id = st.number_input("Transaction ID", min_value=1, step=1)
            with mod_col2:
                new_cat = st.selectbox("New Category", options=CATEGORIES, index=0)
            with mod_col3:
                st.write("")
                st.write("")
                if st.button("Update Category", use_container_width=True):
                    if selected_id in all_tx_df["id"].values:
                        update_transaction_category(int(selected_id), new_cat)
                        st.success(f"Updated Transaction #{selected_id} to '{new_cat}'!")
                        st.rerun()
                    else:
                        st.error(f"Transaction ID #{selected_id} not found.")
            with mod_col4:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete", use_container_width=True):
                    if selected_id in all_tx_df["id"].values:
                        delete_transaction(int(selected_id))
                        st.warning(f"Deleted Transaction #{selected_id}!")
                        st.rerun()
                    else:
                        st.error("ID not found.")

    with tab_add:
        st.subheader("➕ Record an Expense")
        with st.form("add_tx_form", clear_on_submit=True):
            in_col1, in_col2 = st.columns(2)
            with in_col1:
                in_date = st.date_input("Transaction Date", value=date.today())
                in_desc = st.text_input("Description / Merchant", placeholder="e.g. Swiggy Lunch")
            with in_col2:
                in_amt = st.number_input(f"Amount ({currency_symbol})", min_value=0.01, step=10.0, format="%.2f")
                auto_suggest = categorize_transaction(in_desc) if in_desc else "Other"
                default_idx = CATEGORIES.index(auto_suggest) if auto_suggest in CATEGORIES else 0
                in_cat = st.selectbox("Category", options=CATEGORIES, index=default_idx)

            in_notes = st.text_input("Notes (Optional)", placeholder="e.g. Split with friends")
            submitted = st.form_submit_button("Save Transaction")

            if submitted:
                if not in_desc.strip():
                    st.error("Please enter a valid description.")
                elif in_amt <= 0:
                    st.error("Amount must be greater than 0.")
                else:
                    add_transaction(
                        date=in_date.strftime("%Y-%m-%d"),
                        description=in_desc.strip(),
                        amount=in_amt,
                        category=in_cat,
                        notes=in_notes.strip()
                    )
                    st.success(f"✅ Added {currency_symbol}{in_amt:.2f} for '{in_desc}' under '{in_cat}'!")
                    st.rerun()


# =============================================================
# PAGE 3: CSV IMPORT & VALIDATION
# =============================================================
elif menu_selection == "CSV Import":
    st.title("📥 Import CSV Transactions")
    st.markdown("Upload bank or expense CSV files to batch import and auto-categorize expenses.")

    st.markdown(
        """
        > **Expected Format:** CSV must contain `date`, `description`, and `amount` columns.
        > *Dates* should be `YYYY-MM-DD` (e.g. `2026-01-05`).
        """
    )

    # Quick download sample button
    sample_col1, sample_col2 = st.columns([2, 3])
    with sample_col1:
        with open("data/sample_transactions.csv", "r") as f:
            st.download_button(
                label="📄 Download Sample CSV Template",
                data=f.read(),
                file_name="sample_transactions.csv",
                mime="text/csv"
            )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            st.write(f"📁 Loaded `{uploaded_file.name}` ({len(raw_df)} rows)")

            # Column standardization
            raw_df.columns = [c.strip().lower() for c in raw_df.columns]

            required_cols = {"date", "description", "amount"}
            missing_cols = required_cols - set(raw_df.columns)

            if missing_cols:
                st.error(f"❌ Missing required columns: `{', '.join(missing_cols)}`. Expected `date, description, amount`.")
            else:
                # Validation checks
                validation_errors = []
                
                # Check for nulls
                null_counts = raw_df[list(required_cols)].isnull().sum()
                if null_counts.any():
                    validation_errors.append(f"Found missing values: {dict(null_counts[null_counts > 0])}")

                # Date parsing validation
                parsed_dates = pd.to_datetime(raw_df["date"], errors="coerce")
                invalid_dates = parsed_dates.isnull().sum()
                if invalid_dates > 0:
                    validation_errors.append(f"{invalid_dates} rows contain invalid date formats.")

                # Amount validation
                numeric_amounts = pd.to_numeric(raw_df["amount"], errors="coerce")
                invalid_amounts = numeric_amounts.isnull().sum()
                if invalid_amounts > 0:
                    validation_errors.append(f"{invalid_amounts} rows contain non-numeric amounts.")

                if validation_errors:
                    st.warning("⚠️ CSV Validation Issues Detected:")
                    for err in validation_errors:
                        st.write(f"- {err}")

                # Clean and prepare preview
                clean_preview = raw_df.copy()
                clean_preview["date"] = parsed_dates.dt.strftime("%Y-%m-%d")
                clean_preview["amount"] = numeric_amounts.abs()
                clean_preview = clean_preview.dropna(subset=["date", "amount", "description"])

                # Auto-categorize
                if "category" not in clean_preview.columns:
                    clean_preview["category"] = categorize_dataframe(clean_preview, "description")
                else:
                    # Fill missing categories with auto-categorizer
                    clean_preview["category"] = clean_preview.apply(
                        lambda r: str(r["category"]) if pd.notnull(r["category"]) and str(r["category"]).strip() != ""
                        else categorize_transaction(str(r["description"])),
                        axis=1
                    )

                st.subheader("Preview with Auto-Categorization")
                st.dataframe(clean_preview.head(10), use_container_width=True)

                import_action_col1, import_action_col2 = st.columns([1.5, 3])
                with import_action_col1:
                    if st.button("🚀 Confirm & Import into Database", use_container_width=True):
                        inserted = insert_transactions_bulk(clean_preview)
                        st.success(f"🎉 Successfully imported {inserted} transactions!")
                        st.balloons()
                        st.rerun()

        except Exception as e:
            st.error(f"Error reading CSV file: {e}")


# =============================================================
# PAGE 4: BUDGETS & LIMITS
# =============================================================
elif menu_selection == "Budgets":
    st.title("🎯 Category Budgets")
    st.markdown("Set monthly spending limits per category and monitor your threshold status.")

    b_tab_overview, b_tab_edit = st.tabs(["📊 Budget Status", "⚙️ Configure Limits"])

    with b_tab_overview:
        if all_tx_df.empty:
            st.info("No transaction data available. Add transactions to see budget consumption.")
        else:
            budget_df = calculate_budget_status(all_tx_df, budgets_dict)

            # Overview Cards
            total_budget_amt = budget_df["budget"].sum()
            total_spent_amt = budget_df["spent"].sum()
            overall_pct = (total_spent_amt / total_budget_amt * 100) if total_budget_amt > 0 else 0.0

            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                st.markdown(
                    f"""
                    <div class="metric-card" style="border-left-color: #0D9488;">
                        <div class="metric-title">Total Allocated Budget</div>
                        <div class="metric-value">{currency_symbol}{total_budget_amt:,.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with b_col2:
                st.markdown(
                    f"""
                    <div class="metric-card" style="border-left-color: #10B981;">
                        <div class="metric-title">Actual Spent</div>
                        <div class="metric-value">{currency_symbol}{total_spent_amt:,.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with b_col3:
                color = "#10B981" if overall_pct < 80 else ("#F59E0B" if overall_pct <= 100 else "#EF4444")
                st.markdown(
                    f"""
                    <div class="metric-card" style="border-left-color: {color};">
                        <div class="metric-title">Overall Consumption</div>
                        <div class="metric-value">{overall_pct:.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

            # Category Budget Cards with Progress Bars
            st.subheader("Category Usage Breakdown")
            for _, row in budget_df.iterrows():
                cat = row["category"]
                spent = row["spent"]
                limit = row["budget"]
                rem = row["remaining"]
                pct = row["usage_pct"]
                status = row["status"]

                if status == "Exceeded":
                    badge = f'<span class="badge-exceeded">Exceeded ({pct}%)</span>'
                    prog_color = "#EF4444"
                elif status == "Warning":
                    badge = f'<span class="badge-warning">Approaching Limit ({pct}%)</span>'
                    prog_color = "#F59E0B"
                else:
                    badge = f'<span class="badge-healthy">Healthy ({pct}%)</span>'
                    prog_color = "#10B981"

                card_html = f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 12px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div style="font-weight: 700; color: #111827; font-size: 1rem;">{cat}</div>
                        <div>{badge}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #4B5563; margin-bottom: 6px;">
                        <span>Spent: <strong>{currency_symbol}{spent:,.2f}</strong> of {currency_symbol}{limit:,.2f}</span>
                        <span>Remaining: <strong style="color: {'#EF4444' if rem < 0 else '#059669'};">{currency_symbol}{rem:,.2f}</strong></span>
                    </div>
                    <div style="background-color: #E5E7EB; border-radius: 9999px; height: 8px; overflow: hidden;">
                        <div style="background-color: {prog_color}; width: {min(pct, 100.0)}%; height: 100%;"></div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    with b_tab_edit:
        st.subheader("Edit Category Monthly Limits")
        st.markdown("Set or adjust the monthly spending ceiling for each category.")

        with st.form("edit_budgets_form"):
            new_limits = {}
            for cat in CATEGORIES:
                curr_val = budgets_dict.get(cat, 3000.0)
                new_limits[cat] = st.number_input(
                    f"{cat} Budget ({currency_symbol})",
                    min_value=0.0,
                    value=float(curr_val),
                    step=500.0,
                    key=f"budget_{cat}"
                )

            if st.form_submit_button("Save All Budgets"):
                for cat, val in new_limits.items():
                    set_budget(cat, val)
                st.success("✅ Budgets successfully updated!")
                st.rerun()


# =============================================================
# PAGE 5: ANALYTICS & PATTERNS
# =============================================================
elif menu_selection == "Analytics":
    st.title("📈 In-Depth Financial Analytics")
    st.markdown("Discover spending patterns, identify recurring subscriptions, and detect spending anomalies.")

    if all_tx_df.empty:
        st.info("No transaction data available. Import data to view analytics.")
    else:
        # Section A: Daily & Category Deep Dives
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.subheader("Daily Spending Timeline")
            daily_df = get_daily_spending(all_tx_df)
            fig_daily = px.line(
                daily_df,
                x="date",
                y="amount",
                labels={"date": "Date", "amount": f"Amount ({currency_symbol})"},
                color_discrete_sequence=["#0D9488"]
            )
            fig_daily.update_traces(line=dict(width=2.5))
            fig_daily.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#374151"),
                yaxis=dict(gridcolor="#E5E7EB"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_daily, use_container_width=True)

        with col_a2:
            st.subheader("Highest Spending Days")
            high_days = get_highest_spending_days(all_tx_df, top_n=5)
            fig_high = px.bar(
                high_days,
                x="date_str",
                y="amount",
                color="day_name",
                labels={"date_str": "Date", "amount": f"Total Spent ({currency_symbol})"},
                color_discrete_sequence=PALETTE
            )
            fig_high.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#374151"),
                yaxis=dict(gridcolor="#E5E7EB"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_high, use_container_width=True)

        st.markdown("---")

        # Section B: Recurring Expense Detection
        st.subheader("🔄 Recurring Expenses & Subscriptions")
        st.markdown(
            "Identifies repeated periodic transactions (e.g. Netflix, Spotify, Broadband, Gym memberships) "
            "based on description patterns and recurring intervals."
        )

        recurring_data = detect_recurring_expenses(all_tx_df)
        rec_items = recurring_data["recurring_items"]
        total_rec_monthly = recurring_data["total_estimated_monthly"]

        rec_col1, rec_col2 = st.columns([1, 2])
        with rec_col1:
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: #0D9488;">
                    <div class="metric-title">Estimated Monthly Recurring Cost</div>
                    <div class="metric-value">{currency_symbol}{total_rec_monthly:,.2f}</div>
                    <div class="metric-sub">{len(rec_items)} active recurring services</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with rec_col2:
            if rec_items:
                rec_df = pd.DataFrame(rec_items)
                st.dataframe(
                    rec_df[["description", "category", "frequency", "average_amount", "occurrences", "last_paid_date"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No recurring expenses detected yet.")

        st.markdown("---")

        # Section C: Unusual Spending (Anomaly Detection)
        st.subheader("🔍 Unusual Spending Detection")
        st.markdown(
            "Statistical detection of transactions that significantly diverge from your category average. "
            "Helps pinpoint unexpected spikes, large one-offs, or lifestyle creep."
        )

        anomalies_df = detect_unusual_expenses(all_tx_df, threshold_multiplier=2.0)

        if anomalies_df.empty:
            st.success("✅ No unusual spending spikes detected. All transactions align with normal patterns.")
        else:
            for _, row in anomalies_df.iterrows():
                st.markdown(
                    f"""
                    <div style="background-color: #FFFBEB; border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 700; color: #92400E; font-size: 1rem;">
                                ⚠️ {row['description']} ({row['category']})
                            </span>
                            <span style="font-weight: 700; color: #B45309; font-size: 1.1rem;">
                                {currency_symbol}{row['amount']:,.2f}
                            </span>
                        </div>
                        <div style="color: #78350F; font-size: 0.85rem; margin-top: 4px;">
                            {row['explanation']}
                        </div>
                        <div style="color: #A16207; font-size: 0.78rem; margin-top: 2px;">
                            Date: {row['date']} | Category Avg: {currency_symbol}{row['expected_avg']:,.2f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# =============================================================
# PAGE 6: REPORTS & EXPORT
# =============================================================
elif menu_selection == "Reports":
    st.title("📄 Export & PDF Reports")
    st.markdown("Download raw transaction data or export an executive PDF spending summary.")

    if all_tx_df.empty:
        st.info("No data available to generate reports. Import transactions first.")
    else:
        kpis = calculate_kpis(all_tx_df)
        cat_df = get_category_spending(all_tx_df)
        budget_df = calculate_budget_status(all_tx_df, budgets_dict)
        alerts = get_budget_alerts(budget_df)

        rep_col1, rep_col2 = st.columns(2)

        with rep_col1:
            st.markdown(
                """
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 2.2rem; margin-bottom: 8px;">📊</div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #111827;">Export Raw CSV</div>
                    <p style="color: #6B7280; font-size: 0.85rem; margin-top: 6px;">
                        Download all cleaned transactions including categories and notes in CSV format.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            csv_bytes = export_to_csv(all_tx_df)
            st.download_button(
                label="📥 Download CSV",
                data=csv_bytes,
                file_name=f"transactions_export_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with rep_col2:
            st.markdown(
                """
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 2.2rem; margin-bottom: 8px;">📑</div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #111827;">Executive PDF Summary</div>
                    <p style="color: #6B7280; font-size: 0.85rem; margin-top: 6px;">
                        Generate an executive PDF report containing KPIs, category share, budget status, and alerts.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Safe ASCII fallback for PDF font compatibility
            pdf_currency = "Rs." if currency_symbol == "₹" else currency_symbol
            pdf_bytes = generate_pdf_report(
                kpis=kpis,
                category_df=cat_df,
                budget_df=budget_df,
                alerts=alerts,
                currency=pdf_currency
            )
            st.download_button(
                label="📥 Generate & Download PDF",
                data=pdf_bytes,
                file_name=f"expense_report_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )


# =============================================================
# PAGE 7: SETTINGS & DATABASE MANAGEMENT
# =============================================================
elif menu_selection == "Settings":
    st.title("⚙️ Application Settings")
    st.markdown("Configure currency symbols, manage database states, or load demonstration data.")

    set_col1, set_col2 = st.columns(2)

    with set_col1:
        st.subheader("Preferences")
        curr_options = ["₹", "$", "€", "£", "AED", "Rs."]
        curr_idx = curr_options.index(currency_symbol) if currency_symbol in curr_options else 0
        new_curr = st.selectbox("Display Currency Symbol", options=curr_options, index=curr_idx)

        if st.button("Save Preferences"):
            set_setting("currency", new_curr)
            st.success(f"Currency updated to '{new_curr}'!")
            st.rerun()

    with set_col2:
        st.subheader("Database Maintenance")
        st.markdown(f"Total Transactions in DB: **{len(all_tx_df)}**")

        if st.button("📥 Load Sample Transactions (Demo)", use_container_width=True):
            sample_df = pd.read_csv("data/sample_transactions.csv")
            sample_df["category"] = categorize_dataframe(sample_df, "description")
            inserted = insert_transactions_bulk(sample_df)
            st.success(f"Loaded {inserted} sample demo transactions into database!")
            st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if st.button("🗑️ Reset & Wipe All Transactions", use_container_width=True):
            clear_all_transactions()
            st.warning("All transactions wiped from database.")
            st.rerun()

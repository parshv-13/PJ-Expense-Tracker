"""
Reports & Data Export Module
----------------------------
Generates CSV downloads and formatted PDF reports containing:
- Executive summary (Total spending, current month, transaction count)
- Category breakdown table
- Monthly trend summary
- Budget status & alerts
Uses fpdf2 for lightweight, dependable PDF generation with our strict
Teal/Emerald/Charcoal palette.
"""

import io
import pandas as pd
from typing import Dict, Any, List
from fpdf import FPDF


def export_to_csv(df: pd.DataFrame) -> bytes:
    """Exports a pandas DataFrame to UTF-8 CSV bytes."""
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue().encode("utf-8")


class ExpensePDFReport(FPDF):
    """Custom PDF generator for Expense Analysis Report with clean styling."""

    def __init__(self, currency: str = "Rs."):
        super().__init__()
        self.currency = currency
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Teal header banner
        self.set_fill_color(13, 148, 136)  # Teal #0D9488
        self.rect(0, 0, 210, 20, "F")
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "PERSONAL EXPENSE ANALYZER - SUMMARY REPORT", align="C", ln=True)
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_pdf_report(
    kpis: Dict[str, Any],
    category_df: pd.DataFrame,
    budget_df: pd.DataFrame,
    alerts: List[Dict[str, Any]],
    currency: str = "Rs."
) -> bytes:
    """
    Constructs a complete multi-section PDF report and returns the PDF bytes.
    Avoids purple/blue, using Emerald/Teal/Charcoal tones.
    """
    pdf = ExpensePDFReport(currency=currency)
    pdf.add_page()

    # Section 1: Executive Summary Box
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(31, 41, 55)  # Dark Charcoal #1F2937
    pdf.cell(0, 8, "1. Executive Summary", ln=True)
    pdf.ln(2)

    pdf.set_fill_color(243, 244, 246)  # Light gray fill
    pdf.rect(10, pdf.get_y(), 190, 26, "F")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(55, 65, 81)
    
    total = kpis.get("total_spending", 0.0)
    curr_month = kpis.get("current_month_spending", 0.0)
    count = kpis.get("total_transactions", 0)
    daily_avg = kpis.get("avg_daily_spending", 0.0)
    top_cat = kpis.get("top_category", {}).get("category", "N/A")

    pdf.set_xy(14, pdf.get_y() + 3)
    pdf.cell(90, 6, f"Total Spending: {currency} {total:,.2f}", ln=False)
    pdf.cell(90, 6, f"Transactions Count: {count}", ln=True)

    pdf.set_x(14)
    pdf.cell(90, 6, f"Current Month Spending: {currency} {curr_month:,.2f}", ln=False)
    pdf.cell(90, 6, f"Daily Average: {currency} {daily_avg:,.2f}", ln=True)

    pdf.set_x(14)
    pdf.cell(90, 6, f"Top Category: {top_cat}", ln=True)

    pdf.ln(10)

    # Section 2: Spending Alerts (if any)
    if alerts:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(31, 41, 55)
        pdf.cell(0, 8, "2. Key Spending Alerts", ln=True)
        pdf.ln(1)

        for alert in alerts[:5]:
            # Alert box
            if alert["type"] == "danger":
                pdf.set_fill_color(254, 242, 242)  # soft red
                pdf.set_text_color(185, 28, 28)
            else:
                pdf.set_fill_color(255, 251, 235)  # soft orange
                pdf.set_text_color(180, 83, 9)

            msg = alert["message"].replace("**", "").replace("🚨", "[!]").replace("⚠️", "[!]")
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 7, f"  {msg}", fill=True, ln=True)
            pdf.ln(1)
        pdf.ln(6)

    # Section 3: Category Breakdown Table
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 8, "3. Category Breakdown", ln=True)
    pdf.ln(2)

    # Table Header
    pdf.set_fill_color(16, 185, 129)  # Emerald Green
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(80, 7, "Category", 1, 0, "L", fill=True)
    pdf.cell(60, 7, f"Amount ({currency})", 1, 0, "R", fill=True)
    pdf.cell(50, 7, "Share (%)", 1, 1, "R", fill=True)

    # Table Body
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(31, 41, 55)
    for _, row in category_df.head(10).iterrows():
        pdf.cell(80, 6, str(row["category"]), 1, 0, "L")
        pdf.cell(60, 6, f"{row['amount']:,.2f}", 1, 0, "R")
        pdf.cell(50, 6, f"{row['percentage']:.1f}%", 1, 1, "R")

    pdf.ln(8)

    # Section 4: Budget Status Table
    if not budget_df.empty:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(31, 41, 55)
        pdf.cell(0, 8, "4. Monthly Budget Status", ln=True)
        pdf.ln(2)

        pdf.set_fill_color(13, 148, 136)  # Teal
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(55, 7, "Category", 1, 0, "L", fill=True)
        pdf.cell(45, 7, f"Budget ({currency})", 1, 0, "R", fill=True)
        pdf.cell(45, 7, f"Spent ({currency})", 1, 0, "R", fill=True)
        pdf.cell(45, 7, "Status", 1, 1, "C", fill=True)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(31, 41, 55)
        for _, row in budget_df.iterrows():
            pdf.cell(55, 6, str(row["category"]), 1, 0, "L")
            pdf.cell(45, 6, f"{row['budget']:,.2f}", 1, 0, "R")
            pdf.cell(45, 6, f"{row['spent']:,.2f}", 1, 0, "R")
            pdf.cell(45, 6, f"{row['status']} ({row['usage_pct']}%)", 1, 1, "C")

    # Output to byte stream
    return bytes(pdf.output())

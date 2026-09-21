# 🌿 PJ Expense Tracker

A beginner-friendly yet feature-packed **PJ Expense Tracker** built with **Python**, **Streamlit**, **Pandas**, **Plotly**, and **SQLite**.

Designed to track, categorize, and analyze daily spending habits with smart automated insights, recurring expense detection, and budget limit notifications.

![Python](https://img.shields.io/badge/Python-3.9+-0D9488?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-10B981?style=flat&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-374151?style=flat&logo=sqlite&logoColor=white)

---

## ✨ Features

* **📊 Interactive Dashboard:** Live KPI cards showing total spending, current month spending, daily averages, transaction count, top category, and budget consumption.
* **💳 Full Transaction Management:** Add, search, filter, and delete transactions. Real-time manual category overrides with instant persistence.
* **📥 Robust CSV Import:** Upload bank or expense statements. Validates required columns, parses dates, handles missing amounts, flags malformed data, and previews auto-categorized records.
* **🤖 Automatic Categorization:** Instant rule-based categorization based on intelligent merchant/keyword mappings (e.g. Swiggy/Zomato → Food, Uber/Ola → Transport, Netflix/Spotify → Entertainment).
* **🎯 Category Budget Tracking:** Set monthly limits per category. Visual indicators and color-coded status badges:
  * 🟢 **Healthy** (< 80% used)
  * 🟠 **Warning** (80% – 100% used)
  * 🔴 **Exceeded** (> 100% used)
* **🔄 Recurring Expense Detection:** Identifies recurring subscriptions and fixed commitments (Netflix, Spotify, Internet, Gym) by analyzing description patterns, recurring cycles, and amount stability.
* **🔍 Spending Anomaly Detection:** Flags statistical outliers (unusually high single expenses) with transparent, friendly explanations.
* **📑 Report Exports:** One-click export of cleaned transactions to CSV or download a clean executive PDF report.
* **🎨 Strict Professional Palette:** Designed in modern **Teal, Emerald Green, and Charcoal** with amber warnings and red alerts.

---

## 🏗️ Project Architecture

```text
expense-analyzer/
│
├── app.py                      # Streamlit application UI and navigation
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore definitions
│
├── src/                        # Core application modules
│   ├── database.py             # SQLite schema creation & CRUD operations
│   ├── categorizer.py          # Keyword-based categorization engine
│   ├── analyzer.py             # Financial KPI calculations & rollups
│   ├── budget.py               # Budget monitoring and alerts
│   ├── anomaly.py              # Statistical outlier detection
│   ├── recurring.py            # Recurring subscription detection
│   └── reports.py              # CSV & PDF generation
│
├── tests/                      # Pytest automated test suite
│   ├── test_categorizer.py     # Categorization logic tests
│   ├── test_analyzer.py        # Financial calculations & KPI tests
│   ├── test_budget.py          # Budget threshold & alert tests
│   ├── test_anomaly.py         # Outlier detection tests
│   └── test_recurring.py       # Recurring subscription logic tests
│
└── data/
    └── sample_transactions.csv # Realistic demonstration dataset
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/personal-expense-analyzer.git
cd personal-expense-analyzer
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

The app will automatically launch in your browser at `http://localhost:8501`.

---

## 📂 Sample CSV Format

You can upload transactions using a CSV file formatted as follows:

```csv
date,description,amount
2026-01-05,Swiggy Lunch,450
2026-01-06,Uber ride to office,220
2026-01-07,Amazon Headphones,1500
2026-01-08,Netflix Monthly Subscription,649
```

> **Note:** A ready-to-use sample file is included at [`data/sample_transactions.csv`](data/sample_transactions.csv). You can also load it directly within the app via **Settings > Load Sample Transactions**.

---

## 🧪 Running Automated Tests

Run the full test suite using `pytest`:

```bash
python -m pytest -v
```

All tests verify calculations, budget alerts, categorization rules, recurring pattern detection, and anomaly logic.

---

## 💡 How It Works (For Beginners)

* **SQLite Persistence (`src/database.py`):** Stores transactions and user preferences locally in an `expenses.db` file without needing any external database servers.
* **Auto-Categorizer (`src/categorizer.py`):** Checks transaction descriptions for matching keywords (like "uber", "swiggy", "netflix") and tags the appropriate category.
* **Anomaly Detection (`src/anomaly.py`):** Calculates average spending per category and flags any expense that is more than $2\times$ standard deviations above normal.
* **Recurring Detection (`src/recurring.py`):** Groups recurring merchant descriptions over time to highlight subscriptions and estimated monthly recurring costs.

---

## 🔮 Future Improvements

- [ ] Multi-account support (Checking, Credit Card, Savings)
- [ ] Split expenses / shared household ledger
- [ ] Export directly to Excel (`.xlsx`) format with built-in formulas
- [ ] Machine learning categorization model for ambiguous merchant names

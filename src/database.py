"""
Database Management Module
--------------------------
Handles all SQLite database connections, schema migrations, and queries.
Beginner-friendly and robust, using parameterized SQL queries to prevent SQL injection.
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Tuple

DATABASE_NAME = "expenses.db"


def get_connection(db_path: str = DATABASE_NAME) -> sqlite3.Connection:
    """Returns a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DATABASE_NAME) -> None:
    """
    Initializes the SQLite database with required tables:
    - transactions: stores date, description, amount, category, notes
    - budgets: stores category and monthly budget limit
    - categories: default category lists
    - settings: stores user preferences like currency symbol
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Create transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            notes TEXT DEFAULT ''
        )
    """)

    # Create budgets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            monthly_limit REAL NOT NULL
        )
    """)

    # Create settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Insert default settings if not exists
    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value) VALUES ('currency', '₹')
    """)

    # Default budgets if none exist
    default_budgets = [
        ("Food", 8000.0),
        ("Transport", 3000.0),
        ("Shopping", 5000.0),
        ("Entertainment", 2500.0),
        ("Utilities", 3500.0),
        ("Healthcare", 2000.0),
        ("Groceries", 6000.0),
        ("Other", 3000.0)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO budgets (category, monthly_limit) VALUES (?, ?)
    """, default_budgets)

    conn.commit()
    conn.close()


def add_transaction(
    date: str,
    description: str,
    amount: float,
    category: str,
    notes: str = "",
    db_path: str = DATABASE_NAME
) -> int:
    """Inserts a single transaction and returns the inserted ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (date, description, amount, category, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (date, description.strip(), float(amount), category.strip(), notes.strip()))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id


def insert_transactions_bulk(
    transactions_df: pd.DataFrame,
    db_path: str = DATABASE_NAME
) -> int:
    """
    Inserts multiple transactions from a Pandas DataFrame.
    Expected columns: 'date', 'description', 'amount', 'category' (optional 'notes').
    Returns the count of inserted rows.
    """
    if transactions_df.empty:
        return 0

    df_to_save = transactions_df.copy()
    if 'notes' not in df_to_save.columns:
        df_to_save['notes'] = ''

    records = df_to_save[['date', 'description', 'amount', 'category', 'notes']].to_dict(orient='records')

    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO transactions (date, description, amount, category, notes)
        VALUES (:date, :description, :amount, :category, :notes)
    """, records)
    conn.commit()
    count = len(records)
    conn.close()
    return count


def get_all_transactions(db_path: str = DATABASE_NAME) -> pd.DataFrame:
    """Retrieves all transactions as a Pandas DataFrame, sorted newest to oldest."""
    conn = get_connection(db_path)
    query = "SELECT id, date, description, amount, category, notes FROM transactions ORDER BY date DESC, id DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        df['amount'] = pd.to_numeric(df['amount'])
    return df


def update_transaction_category(
    transaction_id: int,
    new_category: str,
    db_path: str = DATABASE_NAME
) -> bool:
    """Updates the category of a specific transaction."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions SET category = ? WHERE id = ?
    """, (new_category.strip(), transaction_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_transaction(transaction_id: int, db_path: str = DATABASE_NAME) -> bool:
    """Deletes a transaction by its ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def clear_all_transactions(db_path: str = DATABASE_NAME) -> None:
    """Clears all transactions (useful for resetting or uploading fresh data)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()


def get_budgets(db_path: str = DATABASE_NAME) -> Dict[str, float]:
    """Returns a dictionary of category: monthly_limit."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT category, monthly_limit FROM budgets ORDER BY category ASC")
    rows = cursor.fetchall()
    conn.close()
    return {row["category"]: float(row["monthly_limit"]) for row in rows}


def set_budget(category: str, monthly_limit: float, db_path: str = DATABASE_NAME) -> None:
    """Sets or updates the monthly budget limit for a category."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (category, monthly_limit)
        VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
    """, (category.strip(), float(monthly_limit)))
    conn.commit()
    conn.close()


def get_setting(key: str, default: str = "", db_path: str = DATABASE_NAME) -> str:
    """Gets a user setting value."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str, db_path: str = DATABASE_NAME) -> None:
    """Sets or updates a user setting."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()

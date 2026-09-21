"""
Categorization Engine Module
----------------------------
Automatically categorizes transactions based on keyword rules.
Transparent, beginner-friendly, and easily customizable by modifying or extending KEYWORD_RULES.
"""

from typing import Dict, List

# Standard, clean expense categories
CATEGORIES: List[str] = [
    "Food",
    "Groceries",
    "Transport",
    "Shopping",
    "Entertainment",
    "Utilities",
    "Healthcare",
    "Education",
    "Personal Care",
    "Investment & Savings",
    "Other"
]

# Keyword dictionary mapping substrings to categories.
# Uses lowercase keywords for case-insensitive matching.
KEYWORD_RULES: Dict[str, List[str]] = {
    "Food": [
        "swiggy", "zomato", "restaurant", "cafe", "coffee", "starbucks", 
        "mcdonald", "burger", "pizza", "domino", "kfc", "dine", "bistro",
        "subway", "tea", "chai", "lunch", "dinner", "breakfast", "eats"
    ],
    "Groceries": [
        "blinkit", "zepto", "instamart", "bigbasket", "supermarket", "grocery",
        "mart", "dmart", "spencer", "nature's basket", "vegetable", "fruits", "dairy", "milk"
    ],
    "Transport": [
        "uber", "ola", "rapido", "metro", "fuel", "petrol", "diesel", 
        "gas station", "shell", "hpcl", "bpcl", "toll", "fastag", "parking", 
        "railway", "irctc", "flight", "indigo", "air india", "train", "bus"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "zara", "h&m", "nike", "adidas", 
        "ikea", "uniqlo", "mall", "clothing", "apparel", "electronics", "croma", "reliance digital"
    ],
    "Entertainment": [
        "netflix", "spotify", "prime", "disney", "hotstar", "youtube", 
        "cinema", "pvr", "inox", "bookmyshow", "playstation", "xbox", "game", "steam", "concert"
    ],
    "Utilities": [
        "electricity", "power", "water", "wifi", "broadband", "internet", 
        "airtel", "jio", "vi", "recharge", "mobile bill", "gas bill", "maintenance", "rent"
    ],
    "Healthcare": [
        "pharmacy", "apollo", "medplus", "hospital", "clinic", "doctor", 
        "dental", "lab", "diagnostic", "1mg", "pharmeasy", "medicine"
    ],
    "Education": [
        "coursera", "udemy", "book", "tuition", "school", "college", 
        "course", "exam", "stationary", "kindle"
    ],
    "Personal Care": [
        "salon", "spa", "haircut", "gym", "fitness", "cult", "barber"
    ],
    "Investment & Savings": [
        "zerodha", "groww", "mutual fund", "sip", "stocks", "deposit", "gold"
    ]
}


def categorize_transaction(description: str) -> str:
    """
    Categorizes a transaction based on its description using keyword matching.
    Returns the matched category name, or 'Other' if no keywords match.
    
    Example:
    >>> categorize_transaction("Swiggy Order #123")
    'Food'
    >>> categorize_transaction("Uber ride to office")
    'Transport'
    """
    if not description or not isinstance(description, str):
        return "Other"

    desc_lower = description.lower()

    for category, keywords in KEYWORD_RULES.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category

    return "Other"


def categorize_dataframe(df, description_col: str = "description") -> List[str]:
    """
    Applies categorization to an entire column or list of descriptions.
    """
    return [categorize_transaction(desc) for desc in df[description_col]]

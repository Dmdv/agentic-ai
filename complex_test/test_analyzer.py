import os
from datetime import datetime
from analyzer import parse_financial_data, calculate_totals, get_highest_expense_category

# Get the directory of this script to safely locate the csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "transactions.csv")

def test_parse_financial_data():
    transactions = parse_financial_data(CSV_PATH)
    
    # We have 10 transactions in the file
    assert len(transactions) == 10
    
    # First transaction is Groceries for -50.00
    assert transactions[0]["category"] == "Groceries"
    assert transactions[0]["amount"] == -50.00
    assert transactions[0]["date"].year == 2026
    assert transactions[0]["date"].month == 1

def test_calculate_totals():
    transactions = [
        {"amount": 2000.00},
        {"amount": -50.00},
        {"amount": -150.00},
        {"amount": 500.00}
    ]
    
    totals = calculate_totals(transactions)
    assert totals["income"] == 2500.00
    assert totals["expenses"] == 200.00  # Note: we want expenses represented as a positive absolute number here

def test_get_highest_expense_category():
    transactions = [
        {"amount": -50.00, "category": "Groceries"},
        {"amount": -150.00, "category": "Utilities"},
        {"amount": -20.00, "category": "Groceries"},
        {"amount": 2000.00, "category": "Salary"} # Income should be ignored
    ]
    
    # Utilities total = -150, Groceries total = -70. 
    # Therefore, Utilities is the highest expense.
    category = get_highest_expense_category(transactions)
    assert category == "Utilities"

import csv
from datetime import datetime

def parse_financial_data(filepath):
    transactions = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            date_str = row[0]
            amount = row[1]
            category = row[2]
            
            # Correct date format
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            transactions.append({
                "date": date_obj,
                "amount": float(amount),
                "category": category
            })
    return transactions

def calculate_totals(transactions):
    income = 0
    expenses = 0
    for t in transactions:
        if t["amount"] > 0:
            income += t["amount"]
        else:
            expenses += abs(t["amount"])  # Take the absolute value of expenses
    
    return {"income": income, "expenses": expenses}

def get_highest_expense_category(transactions):
    categories = {}
    for t in transactions:
        if t["amount"] < 0:
            if t["category"] not in categories:
                categories[t["category"]] = 0
            categories[t["category"]] += t["amount"]
            
    # Find the category with the highest absolute expense
    highest_category = min(categories, key=categories.get)
    return highest_category

if __name__ == "__main__":
    data = parse_financial_data("transactions.csv")
    print(calculate_totals(data))
    print(get_highest_expense_category(data))
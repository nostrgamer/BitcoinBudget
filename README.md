# Bitcoin Budget Desktop

A simple, single-file envelope budgeting application for Bitcoin users.

## What It Does

- Track Bitcoin income and expenses in satoshis
- Create spending categories (groceries, rent, etc.)
- Allocate income to categories monthly
- Track category balances with rollover
- View transaction history

## Why This Approach?

- **One Python file** (~2000 lines total)
- **SQLite database** (one file, no setup)
- **Tkinter GUI** (built into Python)
- **Zero configuration** (just run it)

## Requirements

- Python 3.8+ (comes with Tkinter)
- matplotlib (for reports - installed automatically)
- That's it!

## Usage

### Run from Source
```bash
python bitcoin_budget.py
```

### Build Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed bitcoin_budget.py
```

This creates a single `bitcoin_budget.exe` file (~15MB) that runs anywhere.

## Features

### Core Zero Balance Budget-Style Budgeting
- ✅ Add income transactions
- ✅ Create spending categories
- ✅ Allocate income to categories
- ✅ Add expenses to categories
- ✅ Track category balances
- ✅ Month-by-month navigation
- ✅ Available to assign calculation
- ✅ Transaction history

### Bitcoin-Specific
- ✅ All amounts in satoshis (no floating point errors)
- ✅ Supports "1000" or "0.001 BTC" input formats
- ✅ Displays as "1,000,000 sats"
- ✅ No decimal confusion

### Reports & Analytics
- ✅ Spending breakdown by category (pie chart)
- ✅ Net worth analysis (bar chart with trend line)
- ✅ Future purchasing power predictions (Bitcoin power law analysis)
- ✅ Economic analysis with inflation vs Bitcoin appreciation
- ✅ Side-by-side pie chart comparisons (current vs future with "Bitcoin Vibes")
- ✅ Multiple time periods (current month, 3/6/12 months, custom range)
- ✅ Visual charts using matplotlib

### Simple & Reliable
- ✅ Single file you can read in 10 minutes
- ✅ SQLite database (just copy file to backup)
- ✅ No installation required
- ✅ Works offline
- ✅ No external dependencies

## How It Works

### Database (3 Tables)
```sql
transactions - all income/expenses with dates
categories   - spending envelopes (groceries, rent, etc.)
allocations  - monthly budget assignments
```

### Core Logic
```python
# Simple functions, no complexity
def get_available_to_assign(month):
    income = get_total_income(month)
    allocated = get_total_allocated(month)
    return income - allocated

def get_category_balance(category_id, month):
    allocated = get_category_allocated(category_id, month)
    spent = get_category_spent(category_id, month)
    return allocated - spent
```

### GUI Layout
```
┌─────────────────────────────────────────┐
│ Bitcoin Budget - June 2025    📊 Reports│
├─────────────────────────────────────────┤
│ Total Income: 1,000,000 sats           │
│ Available to Assign: 250,000 sats      │
├─────────────────────────────────────────┤
│ Add Income: [Amount] [Description] [+] │
├─────────────────────────────────────────┤
│ Categories with balances and buttons    │
├─────────────────────────────────────────┤
│ Recent transaction history              │
└─────────────────────────────────────────┘
```

## Example Workflow

1. **Add Income**: Enter "500000" (sats) or "0.005 BTC", description "Salary"
2. **Create Categories**: "Groceries", "Rent", "Savings"
3. **Allocate Budget**: Assign 100,000 sats to Groceries, 300,000 to Rent
4. **Add Expenses**: Spend 25,000 sats from Groceries category
5. **Check Balances**: See remaining amounts in each envelope
6. **View Reports**: 📊 Reports → Spending Breakdown, Net Worth Analysis, or Future Purchasing Power
7. **Analyze Future**: See how Bitcoin's power law reduces your future spending needs

## File Structure

```
bitcoin_budget.py    # Everything in one file
budget.db           # SQLite database (auto-created)
requirements.txt    # Just PyInstaller
README.md          # This file
```
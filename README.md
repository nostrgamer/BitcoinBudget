# Bitcoin Budget Desktop

A simple, single-file envelope budgeting application for Bitcoin users with advanced opportunity cost analysis.

## What It Does

- Track Bitcoin income and expenses in satoshis
- Create spending categories (groceries, rent, etc.)
- Allocate income to categories monthly
- Track category balances with rollover
- View transaction history
- **NEW**: Analyze opportunity cost of individual purchases
- **NEW**: Visual charts and graphs for all reports
- **NEW**: Professional maximized window experience

## Why This Approach?

- **One Python file** (~2400 lines total)
- **SQLite database** (one file, no setup)
- **Tkinter GUI** (built into Python)
- **Zero configuration** (just run it)
- **Maximized by default** (professional experience)

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

This creates a single `bitcoin_budget.exe` file (~25MB) that runs anywhere.

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

### Advanced Reports & Analytics
- ✅ **Spending Breakdown**: Category analysis with interactive pie charts
- ✅ **Net Worth Analysis**: Monthly income vs expenses with cumulative trend
- ✅ **Future Purchasing Power**: Bitcoin power law vs inflation predictions
- ✅ **NEW: Lifecycle Cost Analysis**: Individual transaction opportunity cost visualization
- ✅ **Visual Analytics**: 4-chart dashboard with bar charts, line graphs, and pie charts
- ✅ **Economic Analysis**: Bitcoin appreciation vs inflation modeling
- ✅ **Multiple Time Periods**: Current month, 3/6/12 months, custom ranges
- ✅ **Interactive Charts**: Professional matplotlib visualizations with tabbed interfaces

### Professional User Experience
- ✅ **Maximized windows by default** for optimal screen utilization
- ✅ **Standard window controls** (minimize, maximize, restore, close)
- ✅ **Responsive layouts** optimized for 1900x1200+ screens
- ✅ **Tabbed interfaces** for complex analysis reports
- ✅ **Professional styling** with consistent visual hierarchy

### Simple & Reliable
- ✅ Single file you can read in 15 minutes
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

### Economic Analysis
```python
# Bitcoin Power Law: 1.0117e-17 * days_since_genesis^5.82
def calculate_btc_fair_value(days_since_genesis):
    return 1.0117e-17 * (days_since_genesis ** 5.82)

# Opportunity cost calculation
def calculate_future_purchasing_power(current_budget_sats, years_ahead, inflation_rate):
    btc_multiplier = future_btc_price / current_btc_price
    inflation_multiplier = (1 + inflation_rate) ** years_ahead
    return current_budget_sats * inflation_multiplier / btc_multiplier
```

### GUI Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ Bitcoin Budget - June 2025 (MAXIMIZED)      📊 Reports          │
├─────────────────────────────────────────────────────────────────┤
│ Total Income: 1,000,000 sats | Available to Assign: 250,000 sats│
├─────────────────────────────────────────────────────────────────┤
│ Add Income: [Amount] [Description] [+] │ Categories & Balances   │
├─────────────────────────────────────────────────────────────────┤
│ Recent transaction history with full details                    │
└─────────────────────────────────────────────────────────────────┘
```

## Example Workflow

1. **Add Income**: Enter "500000" (sats) or "0.005 BTC", description "Salary"
2. **Create Categories**: "Groceries", "Rent", "Savings"
3. **Allocate Budget**: Assign 100,000 sats to Groceries, 300,000 to Rent
4. **Add Expenses**: Spend 25,000 sats from Groceries category
5. **Check Balances**: See remaining amounts in each envelope
6. **Analyze Reports**: 
   - 📊 **Spending Breakdown**: See category distribution with pie charts
   - 📈 **Net Worth Analysis**: Track monthly income vs expenses trends
   - 🔮 **Future Purchasing Power**: Model Bitcoin vs inflation over time
   - ⏳ **Lifecycle Cost**: Analyze individual purchase opportunity costs
7. **Visual Analysis**: View 4-chart dashboard showing Bitcoin amount comparisons, USD values, price projections, and opportunity cost breakdowns

## New: Lifecycle Cost Analysis

The most powerful feature for Bitcoin holders - analyze the true opportunity cost of any purchase:

### Features
- **Transaction Selection**: Browse all your expenses
- **Time Horizon**: 1, 2, 5, or 10-year analysis
- **Visual Dashboard**: 4 interactive charts showing:
  - Bitcoin amount comparison (spent vs future value)
  - USD value analysis (purchase vs future BTC value vs inflation)
  - Bitcoin price projection (power law modeling)
  - Opportunity cost breakdown (pie chart)
- **Detailed Analysis**: Comprehensive text breakdown with bottom-line impact

### Example Analysis
*Purchase*: Coffee for 50,000 sats  
*5-Year Opportunity Cost*: ~300,000 sats (6x multiplier)  
*Bottom Line*: That coffee costs you 250,000 sats in foregone Bitcoin gains

## File Structure

```
bitcoin_budget.py    # Everything in one file (~2400 lines)
budget.db           # SQLite database (auto-created)
requirements.txt    # Just PyInstaller + matplotlib
README.md          # This file
ARCHITECTURE.md    # Technical details
```
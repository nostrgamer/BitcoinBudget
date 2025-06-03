# Bitcoin Budget Desktop - Simple Architecture

## Philosophy: Excel-Level Simplicity

This is a **simple, single-file budgeting application** for Bitcoin users. No over-engineering, no complex patterns, just straightforward envelope budgeting that works.

**Core Principle: If you can do it in Excel, it should be simple in code.**

## Technology Stack

- **Language**: Python 3.8+
- **GUI**: Tkinter (built into Python)
- **Database**: SQLite (single file database)
- **Deployment**: PyInstaller (single executable)
- **Total Code**: ~300-500 lines in one file

## Why This Stack?

### Python + Tkinter
- ✅ **Simple**: No complex frameworks to learn
- ✅ **Cross-platform**: Works on Windows, Mac, Linux
- ✅ **Self-contained**: No external dependencies
- ✅ **Debuggable**: Step through every line of code
- ✅ **Fast development**: Working prototype in hours

### SQLite
- ✅ **Zero configuration**: Just a file
- ✅ **Reliable**: Used by millions of apps
- ✅ **Portable**: Copy file = backup entire budget
- ✅ **Fast**: More than sufficient for personal budgets

### Single File Architecture
- ✅ **No complexity**: All logic in one place
- ✅ **Easy to understand**: Read the entire codebase in 10 minutes
- ✅ **Easy to debug**: No layers hiding problems
- ✅ **Easy to extend**: Just add functions

## Database Schema (3 Tables, That's It)

```sql
-- Transactions: Income and expenses
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,              -- '2025-06-03'
    description TEXT NOT NULL,
    amount INTEGER NOT NULL,         -- satoshis (always positive)
    category_id INTEGER,             -- NULL for income
    type TEXT NOT NULL,              -- 'income' or 'expense'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Categories: Spending envelopes
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,       -- 'Groceries', 'Rent', etc.
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Allocations: Monthly budget assignments
CREATE TABLE allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    month TEXT NOT NULL,             -- '2025-06'
    amount INTEGER NOT NULL,         -- satoshis allocated to category
    UNIQUE(category_id, month),
    FOREIGN KEY(category_id) REFERENCES categories(id)
);
```

## Core Logic (Simple Functions)

### Budget Math
```python
def get_total_income(month=None):
    """Get total income for a month (or all time if None)"""
    return sum(amount for transactions where type='income')

def get_available_to_assign(month):
    """Unallocated income for the month"""
    total_income = get_total_income(month)
    total_allocated = sum(allocations for month)
    return total_income - total_allocated

def get_category_balance(category_id, month):
    """Available balance in category envelope"""
    allocated = get_allocation(category_id, month)
    spent = sum(expenses for category in month)
    previous_balance = get_category_balance(category_id, previous_month)
    return previous_balance + allocated - spent
```

### Bitcoin Units
```python
def sats_to_btc(satoshis):
    """Convert satoshis to BTC display"""
    return satoshis / 100_000_000

def btc_to_sats(btc):
    """Convert BTC to satoshis"""
    return int(btc * 100_000_000)

def format_sats(satoshis):
    """Display satoshis with commas"""
    return f"{satoshis:,} sats"
```

## File Structure

```
bitcoin_budget/
├── bitcoin_budget.py          # Main application (everything in one file)
├── budget.db                  # SQLite database (created automatically)
├── requirements.txt           # Just PyInstaller for building executable
└── README.md                  # Simple usage instructions
```

## GUI Layout (Simple Tkinter)

```
┌─────────────────────────────────────────┐
│ Bitcoin Budget - June 2025             │
├─────────────────────────────────────────┤
│ Total Income: 1,000,000 sats           │
│ Total Allocated: 750,000 sats          │
│ Available to Assign: 250,000 sats      │
├─────────────────────────────────────────┤
│ Add Income: [Amount] [Description] [+] │
├─────────────────────────────────────────┤
│ Categories:                             │
│ ┌─ Groceries ───────── 50,000 sats ─┐  │
│ │  Allocated: 100,000 | Spent: 50,000│  │
│ │  [+Allocate] [+Expense]            │  │
│ └────────────────────────────────────┘  │
│ ┌─ Rent ──────────── 200,000 sats ─┐   │
│ │  Allocated: 200,000 | Spent: 0    │   │
│ │  [+Allocate] [+Expense]            │   │
│ └────────────────────────────────────┘   │
│ [Add New Category]                      │
├─────────────────────────────────────────┤
│ Recent Transactions:                    │
│ 2025-06-03  Income         +500,000     │
│ 2025-06-03  Groceries      -25,000      │
│ 2025-06-02  Rent           -200,000     │
└─────────────────────────────────────────┘
```

## Development Workflow

### Phase 1: Basic Functions (1-2 hours)
1. Create database and tables
2. Add income/expense functions
3. Basic category management

### Phase 2: GUI (2-3 hours)
1. Simple Tkinter interface
2. Display totals and categories
3. Basic input forms

### Phase 3: Polish (1-2 hours)
1. Month navigation
2. Transaction history
3. Error handling

### Phase 4: Distribution (1 hour)
1. PyInstaller executable
2. Basic testing

**Total Development Time: 1 weekend**

## Key Benefits

### For Users
- **Instant startup**: No loading time
- **Local data**: Everything stays on your machine
- **Portable**: Copy `.exe` file anywhere
- **Bitcoin-focused**: Satoshis as first-class citizen

### For Developers
- **Understandable**: Read entire codebase in 10 minutes
- **Debuggable**: Set breakpoints anywhere
- **Testable**: Run individual functions in Python REPL
- **Extensible**: Just add more functions

## Anti-Patterns We're Avoiding

❌ **No Clean Architecture** - Just functions and classes  
❌ **No CQRS** - Direct database calls  
❌ **No Repository Pattern** - SQLite is simple enough  
❌ **No Domain Events** - This isn't a distributed system  
❌ **No Value Objects** - Python's built-in types are fine  
❌ **No Dependency Injection** - Global SQLite connection  
❌ **No MediatR** - Function calls are fine  
❌ **No Multiple Projects** - One file, one executable  

## Deployment

### Building Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed bitcoin_budget.py
```

### Result
- Single `.exe` file (~15MB)
- No installation required
- Runs anywhere

## Comparison: Before vs After

| Aspect | C# Clean Architecture | Python Simple |
|--------|----------------------|---------------|
| **Files** | 50+ files, 20+ classes | 1 file |
| **Lines of Code** | 3,000+ lines | 300-500 lines |
| **Concepts to Learn** | Clean Architecture, CQRS, DDD | Functions, SQLite |
| **Time to Understand** | Hours/Days | 10 minutes |
| **Time to Build** | Weeks | Weekend |
| **Dependencies** | 10+ NuGet packages | Python stdlib |
| **Executable Size** | 200MB+ (with .NET runtime) | 15MB |
| **Startup Time** | 2-3 seconds | Instant |
| **Debugging** | Complex layers | Straightforward |

## Future Enhancements (If Needed)

- **Web version**: Port core logic to HTML+JavaScript
- **Mobile**: Use Kivy or React Native
- **Prettier UI**: Switch to PyQt or web-based Electron
- **Cloud sync**: Add simple file-based sync

But start simple. Most users need basic envelope budgeting, not enterprise features.

## Success Metrics

- ✅ Working prototype in one weekend
- ✅ Single executable under 20MB
- ✅ All YNAB core features working
- ✅ Zero configuration setup
- ✅ Readable codebase under 500 lines 
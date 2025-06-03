#!/usr/bin/env python3
"""
Bitcoin Budget Desktop - Simple Envelope Budgeting for Bitcoin Users

A single-file application using Python + Tkinter + SQLite for maximum simplicity.
No over-engineering, just straightforward budgeting that works.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date, timedelta
import calendar
import os

# Import matplotlib for charts (with Tkinter backend)
try:
    import matplotlib
    matplotlib.use('TkAgg')  # Use Tkinter backend
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# === DATABASE FUNCTIONS ===

def init_database():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    
    # Transactions table - all income and expenses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount INTEGER NOT NULL,
            category_id INTEGER,
            type TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')
    
    # Categories table - spending envelopes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Allocations table - monthly budget assignments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            amount INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category_id, month),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')
    
    conn.commit()
    conn.close()


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('budget.db')


def add_income(amount_sats, description, transaction_date):
    """Add income transaction"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO transactions (date, description, amount, type)
            VALUES (?, ?, ?, 'income')
        """, (transaction_date, description, amount_sats))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding income: {e}")
        return False
    finally:
        conn.close()


def add_expense(amount_sats, description, category_id, transaction_date):
    """Add expense transaction"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO transactions (date, description, amount, category_id, type)
            VALUES (?, ?, ?, ?, 'expense')
        """, (transaction_date, description, amount_sats, category_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding expense: {e}")
        return False
    finally:
        conn.close()


def add_category(name):
    """Add a new spending category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicate name
    finally:
        conn.close()


def get_categories():
    """Get all categories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1]} for row in categories]


def allocate_to_category(category_id, month, amount_sats):
    """Allocate amount to category for specific month"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO allocations (category_id, month, amount)
            VALUES (?, ?, ?)
        """, (category_id, month, amount_sats))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error allocating to category: {e}")
        return False
    finally:
        conn.close()


def delete_transaction(transaction_id):
    """Delete a transaction by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        return cursor.rowcount > 0  # Returns True if a row was deleted
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        return False
    finally:
        conn.close()


def delete_category(category_id):
    """Delete a category and all its associated allocations and transactions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # First check if category has transactions or allocations
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,))
        transaction_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM allocations WHERE category_id = ?", (category_id,))
        allocation_count = cursor.fetchone()[0]
        
        # Delete allocations first
        cursor.execute("DELETE FROM allocations WHERE category_id = ?", (category_id,))
        # Delete transactions
        cursor.execute("DELETE FROM transactions WHERE category_id = ?", (category_id,))
        # Delete the category
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        
        return True, transaction_count, allocation_count
    except Exception as e:
        print(f"Error deleting category: {e}")
        return False, 0, 0
    finally:
        conn.close()


def delete_allocation(category_id, month):
    """Delete allocation for a specific category and month"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM allocations WHERE category_id = ? AND month = ?", (category_id, month))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting allocation: {e}")
        return False
    finally:
        conn.close()


def get_transaction_with_details(transaction_id):
    """Get transaction details by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.date, t.description, t.amount, t.type, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    """, (transaction_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_spending_breakdown(start_date, end_date):
    """Get spending breakdown by category for a given date range"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.name, SUM(t.amount) as total_spent
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type = 'expense' AND t.date BETWEEN ? AND ?
        GROUP BY c.id, c.name
        HAVING total_spent > 0
        ORDER BY total_spent DESC
    """, (start_date, end_date))
    
    results = cursor.fetchall()
    conn.close()
    
    # Calculate total and percentages
    breakdown = []
    total_spent = sum(row[1] for row in results)
    
    for category_name, amount in results:
        percentage = (amount / total_spent * 100) if total_spent > 0 else 0
        breakdown.append({
            'category': category_name,
            'amount': amount,
            'percentage': percentage
        })
    
    return breakdown, total_spent


def get_net_worth_data(start_date, end_date):
    """Get monthly income vs expenses data for net worth analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get monthly income and expenses
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', date) as month,
            type,
            SUM(amount) as total
        FROM transactions 
        WHERE date BETWEEN ? AND ?
        GROUP BY strftime('%Y-%m', date), type
        ORDER BY month
    """, (start_date, end_date))
    
    results = cursor.fetchall()
    conn.close()
    
    # Organize data by month
    monthly_data = {}
    all_months = set()
    
    for month, transaction_type, total in results:
        all_months.add(month)
        if month not in monthly_data:
            monthly_data[month] = {'income': 0, 'expenses': 0}
        
        if transaction_type == 'income':
            monthly_data[month]['income'] = total
        elif transaction_type == 'expense':
            monthly_data[month]['expenses'] = total
    
    # Fill in missing months with zero values
    for month in all_months:
        if month not in monthly_data:
            monthly_data[month] = {'income': 0, 'expenses': 0}
    
    # Convert to sorted list and calculate net worth progression
    months = sorted(all_months)
    net_worth_data = []
    cumulative_net_worth = 0
    
    for month in months:
        data = monthly_data.get(month, {'income': 0, 'expenses': 0})
        monthly_net = data['income'] - data['expenses']
        cumulative_net_worth += monthly_net
        
        net_worth_data.append({
            'month': month,
            'income': data['income'],
            'expenses': data['expenses'],
            'monthly_net': monthly_net,
            'cumulative_net_worth': cumulative_net_worth
        })
    
    return net_worth_data


def get_date_range_for_period(base_month, period_type):
    """Get start and end dates for different time periods"""
    year, month = map(int, base_month.split('-'))
    
    if period_type == "current_month":
        start_date = f"{base_month}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{base_month}-{last_day:02d}"
        return start_date, end_date
    
    elif period_type == "last_3_months":
        # Go back 3 months from the current month
        start_year, start_month = year, month
        for _ in range(2):  # Go back 2 more months (total 3 including current)
            start_month -= 1
            if start_month == 0:
                start_month = 12
                start_year -= 1
        
        start_date = f"{start_year}-{start_month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        return start_date, end_date
    
    elif period_type == "last_6_months":
        # Go back 6 months from the current month
        start_year, start_month = year, month
        for _ in range(5):  # Go back 5 more months (total 6 including current)
            start_month -= 1
            if start_month == 0:
                start_month = 12
                start_year -= 1
        
        start_date = f"{start_year}-{start_month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        return start_date, end_date
    
    elif period_type == "last_12_months":
        # Go back 12 months from the current month
        start_year, start_month = year, month
        for _ in range(11):  # Go back 11 more months (total 12 including current)
            start_month -= 1
            if start_month == 0:
                start_month = 12
                start_year -= 1
        
        start_date = f"{start_year}-{start_month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        return start_date, end_date
    
    else:
        # Default to current month
        return get_date_range_for_period(base_month, "current_month")


# === BUDGET LOGIC ===

def get_total_income(month=None):
    """Get total income for month or all time"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if month:
        start_date = f"{month}-01"
        last_day = calendar.monthrange(int(month[:4]), int(month[5:]))[1]
        end_date = f"{month}-{last_day:02d}"
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE type = 'income' AND date BETWEEN ? AND ?
        """, (start_date, end_date))
    else:
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
    
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0


def get_total_allocated(month):
    """Get total allocated for month"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM allocations WHERE month = ?", (month,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0


def get_available_to_assign(month):
    """Calculate unallocated income for the month including rollover from previous months"""
    current_month_income = get_total_income(month)
    current_month_allocated = get_total_allocated_direct(month)  # Use direct, not auto-rollover
    rollover_from_previous = get_rollover_amount(month)
    
    return current_month_income + rollover_from_previous - current_month_allocated


def get_rollover_amount(month):
    """Calculate unallocated income rollover from previous month (not category balances)"""
    year, month_num = map(int, month.split('-'))
    
    # Get previous month
    if month_num == 1:
        prev_month = f"{year-1}-12"
    else:
        prev_month = f"{year}-{month_num-1:02d}"
    
    # Base case - if this is the first month with any data, no rollover
    prev_income = get_total_income(prev_month)
    if prev_income == 0:
        return 0
    
    # Calculate previous month's unallocated income only
    # Use direct allocation to avoid recursion
    prev_allocated = get_total_allocated_direct(prev_month)
    prev_unallocated = prev_income - prev_allocated
    
    return max(0, prev_unallocated)  # Only positive unallocated amounts roll forward


def get_total_allocated_direct(month):
    """Get total allocated for month without rollover logic"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM allocations WHERE month = ?", (month,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0


def get_category_spent(category_id, month):
    """Get amount spent in category for month"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    start_date = f"{month}-01"
    last_day = calendar.monthrange(int(month[:4]), int(month[5:]))[1]
    end_date = f"{month}-{last_day:02d}"
    
    cursor.execute("""
        SELECT SUM(amount) FROM transactions 
        WHERE category_id = ? AND type = 'expense' AND date BETWEEN ? AND ?
    """, (category_id, start_date, end_date))
    
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0


def get_category_allocated(category_id, month):
    """Get amount allocated to category for month (direct allocation only, no auto-rollover)"""
    return get_category_allocated_direct(category_id, month)


def get_category_rollover_balance(category_id, month):
    """Get the rollover balance for a category from the previous month only"""
    year, month_num = map(int, month.split('-'))
    
    # Get previous month
    if month_num == 1:
        prev_month = f"{year-1}-12"
    else:
        prev_month = f"{year}-{month_num-1:02d}"
    
    # Base case - if no previous data, no rollover
    prev_income = get_total_income(prev_month)
    if prev_income == 0:
        return 0
    
    # Get previous month's simple balance (allocated - spent) without recursion
    prev_allocated = get_category_allocated_direct(category_id, prev_month)
    prev_spent = get_category_spent(category_id, prev_month)
    prev_balance = prev_allocated - prev_spent
    
    return max(0, prev_balance)  # Only positive balances roll forward


def get_category_allocated_direct(category_id, month):
    """Get amount allocated to category for month without rollover logic"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT amount FROM allocations WHERE category_id = ? AND month = ?
    """, (category_id, month))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 0


def get_category_balance(category_id, month):
    """Get current balance for category envelope including rollover from previous months"""
    allocated = get_category_allocated_direct(category_id, month)
    spent = get_category_spent(category_id, month)
    
    # Add rollover from previous month
    rollover = get_category_rollover_balance(category_id, month)
    
    return allocated + rollover - spent


def get_recent_transactions(limit=10):
    """Get recent transactions with IDs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.date, t.description, t.amount, t.type, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        ORDER BY t.date DESC, t.created_at DESC
        LIMIT ?
    """, (limit,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions


# === UTILITY FUNCTIONS ===

def format_sats(satoshis):
    """Format satoshis for display"""
    return f"{satoshis:,} sats"


def format_btc(satoshis):
    """Format as BTC"""
    btc = satoshis / 100_000_000
    return f"{btc:.8f} BTC"


def parse_amount_input(text):
    """Parse user input to satoshis"""
    text = text.strip().replace(',', '')
    
    if text.lower().endswith(' btc'):
        # Handle BTC input
        btc_amount = float(text[:-4])
        return int(btc_amount * 100_000_000)
    else:
        # Handle sats input
        return int(text)


def get_current_month():
    """Return current month as 'YYYY-MM'"""
    return datetime.now().strftime('%Y-%m')


# === GUI APPLICATION ===

class BitcoinBudgetApp:
    def __init__(self):
        """Initialize the main application"""
        self.root = tk.Tk()
        self.root.title("Bitcoin Budget Desktop")
        self.root.geometry("1300x700")  # Increased from 1200x700
        
        self.current_month = get_current_month()
        
        self.create_widgets()
        self.refresh_display()
    
    def create_widgets(self):
        """Create the main interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Month selector
        month_frame = ttk.Frame(main_frame)
        month_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(month_frame, text="← Prev", command=self.prev_month).grid(row=0, column=0)
        self.month_label = ttk.Label(month_frame, text=self.current_month, font=("Arial", 14, "bold"))
        self.month_label.grid(row=0, column=1, padx=20)
        ttk.Button(month_frame, text="Next →", command=self.next_month).grid(row=0, column=2)
        
        # Add Reports button
        ttk.Button(month_frame, text="📊 Reports", command=self.show_reports).grid(row=0, column=3, padx=(20, 0))
        
        # Budget summary
        summary_frame = ttk.LabelFrame(main_frame, text="Budget Summary", padding="10")
        summary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.income_label = ttk.Label(summary_frame, text="Total Income: 0 sats")
        self.income_label.grid(row=0, column=0, sticky=tk.W)
        
        self.rollover_label = ttk.Label(summary_frame, text="Rollover: 0 sats")
        self.rollover_label.grid(row=1, column=0, sticky=tk.W)
        
        self.allocated_label = ttk.Label(summary_frame, text="Total Allocated: 0 sats")
        self.allocated_label.grid(row=2, column=0, sticky=tk.W)
        
        self.available_label = ttk.Label(summary_frame, text="Available to Assign: 0 sats")
        self.available_label.grid(row=3, column=0, sticky=tk.W)
        
        # Add Income section
        income_frame = ttk.LabelFrame(main_frame, text="Add Income", padding="10")
        income_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Label(income_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W)
        self.income_date = ttk.Entry(income_frame, width=15)
        self.income_date.grid(row=0, column=1, padx=5)
        self.income_date.insert(0, datetime.now().strftime('%Y-%m-%d'))  # Default to today
        
        ttk.Label(income_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W)
        self.income_amount = ttk.Entry(income_frame, width=15)
        self.income_amount.grid(row=1, column=1, padx=5)
        
        ttk.Label(income_frame, text="Description:").grid(row=2, column=0, sticky=tk.W)
        self.income_desc = ttk.Entry(income_frame, width=20)
        self.income_desc.grid(row=2, column=1, padx=5)
        
        ttk.Button(income_frame, text="Add Income", command=self.add_income_clicked).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Categories section
        categories_frame = ttk.LabelFrame(main_frame, text="Categories", padding="10")
        categories_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Category listbox with scrollbar
        list_frame = ttk.Frame(categories_frame)
        list_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.categories_listbox = tk.Listbox(list_frame, height=8, width=100)
        self.categories_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.categories_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.categories_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Category buttons
        ttk.Button(categories_frame, text="Add Category", command=self.add_category_clicked).grid(row=1, column=0, pady=5)
        ttk.Button(categories_frame, text="Allocate", command=self.allocate_clicked).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(categories_frame, text="Add Expense", command=self.add_expense_clicked).grid(row=1, column=2, pady=5)
        
        # Row 2 for delete buttons
        ttk.Button(categories_frame, text="Delete Category", command=self.delete_category_clicked).grid(row=2, column=0, pady=5)
        ttk.Button(categories_frame, text="Remove Allocation", command=self.remove_allocation_clicked).grid(row=2, column=1, padx=5, pady=5)
        
        # Recent transactions
        transactions_frame = ttk.LabelFrame(main_frame, text="Recent Transactions", padding="10")
        transactions_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Transaction treeview - add hidden ID column
        columns = ("ID", "Date", "Description", "Amount", "Category")
        self.transactions_tree = ttk.Treeview(transactions_frame, columns=columns, show="headings", height=6)
        
        # Hide the ID column
        self.transactions_tree.column("ID", width=0, stretch=False)
        self.transactions_tree.heading("ID", text="")
        
        # Configure visible columns
        visible_columns = ["Date", "Description", "Amount", "Category"]
        for col in visible_columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=150)
        
        self.transactions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Transaction scrollbar
        trans_scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        trans_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.transactions_tree.configure(yscrollcommand=trans_scrollbar.set)
        
        # Transaction buttons
        trans_button_frame = ttk.Frame(transactions_frame)
        trans_button_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(trans_button_frame, text="Delete Selected Transaction", command=self.delete_transaction_clicked).grid(row=0, column=0, padx=5)
        
        # Configure grid weights
        main_frame.rowconfigure(3, weight=1)
        main_frame.columnconfigure(1, weight=1)
        categories_frame.rowconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        transactions_frame.rowconfigure(0, weight=1)
        transactions_frame.columnconfigure(0, weight=1)
    
    def refresh_display(self):
        """Update all displays with current data"""
        # Update month label
        self.month_label.config(text=self.current_month)
        
        # Update budget summary
        total_income = get_total_income(self.current_month)
        rollover = get_rollover_amount(self.current_month)
        total_allocated = get_total_allocated(self.current_month)
        available = get_available_to_assign(self.current_month)
        
        self.income_label.config(text=f"Total Income: {format_sats(total_income)}")
        self.rollover_label.config(text=f"Rollover: {format_sats(rollover)}")
        self.allocated_label.config(text=f"Total Allocated: {format_sats(total_allocated)}")
        self.available_label.config(text=f"Available to Assign: {format_sats(available)}")
        
        # Update categories
        self.categories_listbox.delete(0, tk.END)
        categories = get_categories()
        for cat in categories:
            balance = get_category_balance(cat['id'], self.current_month)
            allocated = get_category_allocated(cat['id'], self.current_month)
            spent = get_category_spent(cat['id'], self.current_month)
            display_text = f"{cat['name']} | Allocated: {format_sats(allocated)} | Spent: {format_sats(spent)} | Balance: {format_sats(balance)}"
            self.categories_listbox.insert(tk.END, display_text)
        
        # Update transactions
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        transactions = get_recent_transactions(20)
        for trans in transactions:
            trans_id, date_str, desc, amount, trans_type, category = trans
            if trans_type == 'income':
                amount_str = f"+{format_sats(amount)}"
                category_str = "Income"
            else:
                amount_str = f"-{format_sats(amount)}"
                category_str = category or "Unknown"
            
            # Store transaction ID in the item for deletion purposes
            item_id = self.transactions_tree.insert("", "end", values=(trans_id, date_str, desc, amount_str, category_str))
    
    def prev_month(self):
        """Go to previous month"""
        year, month = map(int, self.current_month.split('-'))
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        self.current_month = f"{year:04d}-{month:02d}"
        self.refresh_display()
    
    def next_month(self):
        """Go to next month"""
        year, month = map(int, self.current_month.split('-'))
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        self.current_month = f"{year:04d}-{month:02d}"
        self.refresh_display()
    
    def add_income_clicked(self):
        """Handle add income button click"""
        try:
            date = self.income_date.get().strip()
            amount_text = self.income_amount.get()
            description = self.income_desc.get()
            
            if not date or not amount_text or not description:
                self.show_error("Error", "Please enter all fields")
                return
            
            # Validate date format
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                self.show_error("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            amount_sats = parse_amount_input(amount_text)
            
            if add_income(amount_sats, description, date):
                self.income_date.delete(0, tk.END)
                self.income_date.insert(0, datetime.now().strftime('%Y-%m-%d'))  # Reset to today
                self.income_amount.delete(0, tk.END)
                self.income_desc.delete(0, tk.END)
                self.refresh_display()
                self.show_info("Success", f"Added income: {format_sats(amount_sats)}")
            else:
                self.show_error("Error", "Failed to add income")
                
        except ValueError:
            self.show_error("Error", "Invalid amount format")
        except Exception as e:
            self.show_error("Error", f"Unexpected error: {e}")
    
    def add_category_clicked(self):
        """Handle add category button click"""
        name = self.ask_string("Add Category", "Enter category name:")
        if name:
            if add_category(name):
                self.refresh_display()
                self.show_info("Success", f"Added category: {name}")
            else:
                self.show_error("Error", "Category name already exists")
    
    def allocate_clicked(self):
        """Handle allocate button click"""
        selection = self.categories_listbox.curselection()
        if not selection:
            self.show_error("Error", "Please select a category")
            return
        
        categories = get_categories()
        if selection[0] >= len(categories):
            self.show_error("Error", "Invalid category selection")
            return
        
        category = categories[selection[0]]
        
        amount_text = self.ask_string("Allocate", f"Enter amount to allocate to {category['name']}:")
        if amount_text:
            try:
                amount_sats = parse_amount_input(amount_text)
                
                # Check if we have enough available
                available = get_available_to_assign(self.current_month)
                current_allocation = get_category_allocated(category['id'], self.current_month)
                additional_needed = amount_sats - current_allocation
                
                if additional_needed > available:
                    self.show_error("Error", f"Not enough available to assign. Available: {format_sats(available)}")
                    return
                
                if allocate_to_category(category['id'], self.current_month, amount_sats):
                    self.refresh_display()
                    self.show_info("Success", f"Allocated {format_sats(amount_sats)} to {category['name']}")
                else:
                    self.show_error("Error", "Failed to allocate")
                    
            except ValueError:
                self.show_error("Error", "Invalid amount format")
    
    def add_expense_clicked(self):
        """Handle add expense button click"""
        selection = self.categories_listbox.curselection()
        if not selection:
            self.show_error("Error", "Please select a category")
            return
        
        categories = get_categories()
        if selection[0] >= len(categories):
            self.show_error("Error", "Invalid category selection")
            return
        
        category = categories[selection[0]]
        
        # Get date
        today_str = datetime.now().strftime('%Y-%m-%d')
        date = self.ask_string("Add Expense", f"Enter date (YYYY-MM-DD):", initial_value=today_str)
        if not date:
            return
        
        # Validate date format
        try:
            datetime.strptime(date.strip(), '%Y-%m-%d')
        except ValueError:
            self.show_error("Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        # Get amount
        amount_text = self.ask_string("Add Expense", f"Enter expense amount for {category['name']}:")
        if not amount_text:
            return
        
        # Get description
        description = self.ask_string("Add Expense", "Enter description:")
        if not description:
            return
        
        try:
            amount_sats = parse_amount_input(amount_text)
            
            if add_expense(amount_sats, description, category['id'], date.strip()):
                self.refresh_display()
                self.show_info("Success", f"Added expense: {format_sats(amount_sats)} to {category['name']}")
            else:
                self.show_error("Error", "Failed to add expense")
                
        except ValueError:
            self.show_error("Error", "Invalid amount format")
        except Exception as e:
            self.show_error("Error", f"Unexpected error: {e}")
    
    def delete_category_clicked(self):
        """Handle delete category button click"""
        selection = self.categories_listbox.curselection()
        if not selection:
            self.show_error("Error", "Please select a category")
            return
        
        categories = get_categories()
        if selection[0] >= len(categories):
            self.show_error("Error", "Invalid category selection")
            return
        
        category = categories[selection[0]]
        
        # Show confirmation with warning about associated data
        message = f"Are you sure you want to delete the category '{category['name']}'?\n\n"
        message += "This will also delete ALL transactions and allocations for this category.\n"
        message += "This action cannot be undone!"
        
        if self.ask_yes_no("Confirm Deletion", message):
            success, transaction_count, allocation_count = delete_category(category['id'])
            if success:
                self.refresh_display()
                result_msg = f"Deleted category: {category['name']}\n"
                result_msg += f"Also deleted {transaction_count} transactions and {allocation_count} allocations."
                self.show_info("Success", result_msg)
            else:
                self.show_error("Error", "Failed to delete category")
    
    def remove_allocation_clicked(self):
        """Handle remove allocation button click"""
        selection = self.categories_listbox.curselection()
        if not selection:
            self.show_error("Error", "Please select a category")
            return
        
        categories = get_categories()
        if selection[0] >= len(categories):
            self.show_error("Error", "Invalid category selection")
            return
        
        category = categories[selection[0]]
        
        if self.ask_yes_no("Confirm Removal", f"Are you sure you want to remove all allocations for the category '{category['name']}'?"):
            if delete_allocation(category['id'], self.current_month):
                self.refresh_display()
                self.show_info("Success", f"Removed all allocations for: {category['name']}")
            else:
                self.show_error("Error", "Failed to remove allocation")
    
    def delete_transaction_clicked(self):
        """Handle delete transaction button click"""
        selection = self.transactions_tree.selection()
        if not selection:
            self.show_error("Error", "Please select a transaction")
            return
        
        # Get the selected item
        item = selection[0]
        # Get all values including the hidden ID
        values = self.transactions_tree.item(item, "values")
        trans_id, date_str, desc, amount_str, category_str = values
        
        if self.ask_yes_no("Confirm Deletion", f"Are you sure you want to delete this transaction?\n\nDate: {date_str}\nDescription: {desc}\nAmount: {amount_str}\nCategory: {category_str}"):
            if delete_transaction(trans_id):
                self.refresh_display()
                self.show_info("Success", f"Deleted transaction: {desc}")
            else:
                self.show_error("Error", "Failed to delete transaction")
    
    def show_reports(self):
        """Handle show reports button click"""
        if not MATPLOTLIB_AVAILABLE:
            self.show_error("Reports", "Matplotlib is required for reports.\nInstall with: pip install matplotlib")
            return
        
        # Create a simple menu to choose report type
        menu_window = tk.Toplevel(self.root)
        menu_window.title("Choose Report Type")
        menu_window.geometry("500x400")
        menu_window.transient(self.root)
        menu_window.grab_set()
        
        # Center the dialog
        menu_window.geometry("+%d+%d" % (self.root.winfo_rootx()+100, self.root.winfo_rooty()+100))
        
        frame = ttk.Frame(menu_window, padding="30")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure frame to expand
        menu_window.grid_rowconfigure(0, weight=1)
        menu_window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(5, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(frame, text="Select Report Type:", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(0, 20))
        
        def open_spending_report():
            menu_window.destroy()
            SpendingReportWindow(self.root, self.current_month)
        
        def open_networth_report():
            menu_window.destroy()
            NetWorthReportWindow(self.root, self.current_month)
        
        def open_purchasing_power_report():
            menu_window.destroy()
            PurchasingPowerReportWindow(self.root, self.current_month)
        
        # Create larger, more readable buttons
        spending_btn = ttk.Button(frame, text="📊 Spending Breakdown", 
                  command=open_spending_report)
        spending_btn.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E), ipadx=10, ipady=8)
        
        networth_btn = ttk.Button(frame, text="📈 Net Worth Analysis", 
                  command=open_networth_report)
        networth_btn.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E), ipadx=10, ipady=8)
        
        purchasing_btn = ttk.Button(frame, text="🔮 Future Purchasing Power", 
                  command=open_purchasing_power_report)
        purchasing_btn.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E), ipadx=10, ipady=8)
        
        # Add separator
        separator = ttk.Separator(frame, orient='horizontal')
        separator.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=15)
        
        cancel_btn = ttk.Button(frame, text="Cancel", 
                  command=menu_window.destroy)
        cancel_btn.grid(row=5, column=0, pady=(10, 0), ipadx=10, ipady=8, sticky=(tk.W, tk.E))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

    # Dialog helper methods to ensure dialogs stay on top
    def show_error(self, title, message):
        """Show error message that stays on top"""
        messagebox.showerror(title, message, parent=self.root)
    
    def show_info(self, title, message):
        """Show info message that stays on top"""
        messagebox.showinfo(title, message, parent=self.root)
    
    def ask_yes_no(self, title, message):
        """Ask yes/no question that stays on top"""
        return messagebox.askyesno(title, message, parent=self.root)
    
    def ask_string(self, title, prompt, initial_value=""):
        """Ask for string input that stays on top"""
        if initial_value:
            return simpledialog.askstring(title, prompt, initialvalue=initial_value, parent=self.root)
        else:
            return simpledialog.askstring(title, prompt, parent=self.root)


class SpendingReportWindow:
    def __init__(self, parent, month):
        """Initialize the spending report window"""
        self.parent = parent
        self.month = month
        self.current_period = "current_month"
        self.custom_start_date = ""
        self.custom_end_date = ""
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Spending Breakdown")
        self.window.geometry("1200x700")  # Made wider for controls
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.update_chart()
    
    def create_widgets(self):
        """Create the report interface"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ttk.Label(main_frame, text=f"Spending Breakdown - {self.month}", 
                               font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Time period controls
        period_frame = ttk.LabelFrame(main_frame, text="Time Period", padding="10")
        period_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Period selection buttons
        ttk.Button(period_frame, text="Current Month", 
                  command=lambda: self.set_period("current_month")).grid(row=0, column=0, padx=5)
        ttk.Button(period_frame, text="Last 3 Months", 
                  command=lambda: self.set_period("last_3_months")).grid(row=0, column=1, padx=5)
        ttk.Button(period_frame, text="Last 6 Months", 
                  command=lambda: self.set_period("last_6_months")).grid(row=0, column=2, padx=5)
        ttk.Button(period_frame, text="Last 12 Months", 
                  command=lambda: self.set_period("last_12_months")).grid(row=0, column=3, padx=5)
        ttk.Button(period_frame, text="Custom Range", 
                  command=self.set_custom_period).grid(row=0, column=4, padx=5)
        
        # Period info label
        self.period_info_label = ttk.Label(period_frame, text="", font=("Arial", 9))
        self.period_info_label.grid(row=1, column=0, columnspan=5, pady=(5, 0))
        
        # Chart frame (left side)
        chart_frame = ttk.Frame(main_frame)
        chart_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)
        
        # Details frame (right side)
        details_frame = ttk.LabelFrame(main_frame, text="Category Details", padding="10")
        details_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create treeview for category details
        columns = ("Category", "Amount", "Percentage")
        self.details_tree = ttk.Treeview(details_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.details_tree.heading(col, text=col)
            if col == "Category":
                self.details_tree.column(col, width=150)
            else:
                self.details_tree.column(col, width=100)
        
        self.details_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.details_tree.configure(yscrollcommand=scrollbar.set)
        
        details_frame.grid_rowconfigure(0, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.window.destroy).grid(row=3, column=0, columnspan=2, pady=(10, 0))
    
    def set_period(self, period_type):
        """Set the time period and update the chart"""
        self.current_period = period_type
        self.update_chart()
    
    def set_custom_period(self):
        """Set a custom date range"""
        # Create custom date range dialog
        custom_window = tk.Toplevel(self.window)
        custom_window.title("Custom Date Range")
        custom_window.geometry("350x200")
        custom_window.transient(self.window)
        custom_window.grab_set()
        
        # Center the dialog
        custom_window.geometry("+%d+%d" % (self.window.winfo_rootx()+50, self.window.winfo_rooty()+50))
        
        frame = ttk.Frame(custom_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, pady=5)
        start_entry = ttk.Entry(frame, width=20)
        start_entry.grid(row=0, column=1, padx=10, pady=5)
        start_entry.insert(0, self.custom_start_date or f"{self.month}-01")
        
        ttk.Label(frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=5)
        end_entry = ttk.Entry(frame, width=20)
        end_entry.grid(row=1, column=1, padx=10, pady=5)
        end_entry.insert(0, self.custom_end_date or f"{self.month}-28")
        
        def apply_custom():
            start_date = start_entry.get().strip()
            end_date = end_entry.get().strip()
            
            # Validate dates
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
                
                if start_date <= end_date:
                    self.custom_start_date = start_date
                    self.custom_end_date = end_date
                    self.current_period = "custom"
                    custom_window.destroy()
                    self.update_chart()
                else:
                    messagebox.showerror("Error", "Start date must be before end date", parent=custom_window)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD", parent=custom_window)
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Apply", command=apply_custom).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=custom_window.destroy).grid(row=0, column=1, padx=5)
    
    def get_period_description(self):
        """Get a description of the current time period"""
        if self.current_period == "current_month":
            return f"Current Month: {self.month}"
        elif self.current_period == "last_3_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_3_months")
            return f"Last 3 Months: {start_date} to {end_date}"
        elif self.current_period == "last_6_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_6_months")
            return f"Last 6 Months: {start_date} to {end_date}"
        elif self.current_period == "last_12_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_12_months")
            return f"Last 12 Months: {start_date} to {end_date}"
        elif self.current_period == "custom":
            return f"Custom Range: {self.custom_start_date} to {self.custom_end_date}"
        else:
            return ""
    
    def update_chart(self):
        """Update the pie chart and details"""
        # Get date range based on current period
        if self.current_period == "custom":
            start_date = self.custom_start_date
            end_date = self.custom_end_date
        else:
            start_date, end_date = get_date_range_for_period(self.month, self.current_period)
        
        # Get spending data
        breakdown, total_spent = get_spending_breakdown(start_date, end_date)
        
        # Update title and period info
        self.title_label.config(text="Spending Breakdown")
        self.period_info_label.config(text=self.get_period_description())
        
        if not breakdown:
            # No spending data
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'No spending data for this period', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=12)
            self.ax.set_title(f"Total Spending: {format_sats(0)}", fontsize=14, fontweight='bold')
            
            # Clear details
            for item in self.details_tree.get_children():
                self.details_tree.delete(item)
            
            self.canvas.draw()
            return
        
        # Clear previous chart
        self.ax.clear()
        
        # Prepare data for pie chart
        categories = [item['category'] for item in breakdown]
        amounts = [item['amount'] for item in breakdown]
        percentages = [item['percentage'] for item in breakdown]
        
        # Create color palette
        colors = plt.cm.Set3(range(len(categories)))
        
        # Create pie chart
        wedges, texts, autotexts = self.ax.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
        
        # Customize appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        for text in texts:
            text.set_fontsize(8)
        
        # Add title with total spending
        self.ax.set_title(f"Total Spending: {format_sats(total_spent)}", 
                         fontsize=14, fontweight='bold', pad=20)
        
        # Update details treeview
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
        
        for item in breakdown:
            self.details_tree.insert("", "end", values=(
                item['category'],
                format_sats(item['amount']),
                f"{item['percentage']:.1f}%"
            ))
        
        # Draw the chart
        self.canvas.draw()


class NetWorthReportWindow:
    def __init__(self, parent, month):
        """Initialize the net worth report window"""
        self.parent = parent
        self.month = month
        self.current_period = "last_6_months"  # Default to 6 months for better visualization
        self.custom_start_date = ""
        self.custom_end_date = ""
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Net Worth Analysis")
        self.window.geometry("1200x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.update_chart()
    
    def create_widgets(self):
        """Create the report interface"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ttk.Label(main_frame, text="Net Worth Analysis", 
                               font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Time period controls (reuse from spending report)
        period_frame = ttk.LabelFrame(main_frame, text="Time Period", padding="10")
        period_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Period selection buttons
        ttk.Button(period_frame, text="Current Month", 
                  command=lambda: self.set_period("current_month")).grid(row=0, column=0, padx=5)
        ttk.Button(period_frame, text="Last 3 Months", 
                  command=lambda: self.set_period("last_3_months")).grid(row=0, column=1, padx=5)
        ttk.Button(period_frame, text="Last 6 Months", 
                  command=lambda: self.set_period("last_6_months")).grid(row=0, column=2, padx=5)
        ttk.Button(period_frame, text="Last 12 Months", 
                  command=lambda: self.set_period("last_12_months")).grid(row=0, column=3, padx=5)
        ttk.Button(period_frame, text="Custom Range", 
                  command=self.set_custom_period).grid(row=0, column=4, padx=5)
        
        # Period info label
        self.period_info_label = ttk.Label(period_frame, text="", font=("Arial", 9))
        self.period_info_label.grid(row=1, column=0, columnspan=5, pady=(5, 0))
        
        # Chart frame (takes full width)
        chart_frame = ttk.Frame(main_frame)
        chart_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 6), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.window.destroy).grid(row=3, column=0, columnspan=2, pady=(10, 0))
    
    def set_period(self, period_type):
        """Set the time period and update the chart"""
        self.current_period = period_type
        self.update_chart()
    
    def set_custom_period(self):
        """Set a custom date range (reuse logic from spending report)"""
        # Create custom date range dialog
        custom_window = tk.Toplevel(self.window)
        custom_window.title("Custom Date Range")
        custom_window.geometry("350x200")
        custom_window.transient(self.window)
        custom_window.grab_set()
        
        # Center the dialog
        custom_window.geometry("+%d+%d" % (self.window.winfo_rootx()+50, self.window.winfo_rooty()+50))
        
        frame = ttk.Frame(custom_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, pady=5)
        start_entry = ttk.Entry(frame, width=20)
        start_entry.grid(row=0, column=1, padx=10, pady=5)
        start_entry.insert(0, self.custom_start_date or f"{self.month}-01")
        
        ttk.Label(frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=5)
        end_entry = ttk.Entry(frame, width=20)
        end_entry.grid(row=1, column=1, padx=10, pady=5)
        end_entry.insert(0, self.custom_end_date or f"{self.month}-28")
        
        def apply_custom():
            start_date = start_entry.get().strip()
            end_date = end_entry.get().strip()
            
            # Validate dates
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
                
                if start_date <= end_date:
                    self.custom_start_date = start_date
                    self.custom_end_date = end_date
                    self.current_period = "custom"
                    custom_window.destroy()
                    self.update_chart()
                else:
                    messagebox.showerror("Error", "Start date must be before end date", parent=custom_window)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD", parent=custom_window)
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Apply", command=apply_custom).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=custom_window.destroy).grid(row=0, column=1, padx=5)
    
    def get_period_description(self):
        """Get a description of the current time period"""
        if self.current_period == "current_month":
            return f"Current Month: {self.month}"
        elif self.current_period == "last_3_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_3_months")
            return f"Last 3 Months: {start_date} to {end_date}"
        elif self.current_period == "last_6_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_6_months")
            return f"Last 6 Months: {start_date} to {end_date}"
        elif self.current_period == "last_12_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_12_months")
            return f"Last 12 Months: {start_date} to {end_date}"
        elif self.current_period == "custom":
            return f"Custom Range: {self.custom_start_date} to {self.custom_end_date}"
        else:
            return ""
    
    def update_chart(self):
        """Update the bar chart and analysis"""
        # Get date range based on current period
        if self.current_period == "custom":
            start_date = self.custom_start_date
            end_date = self.custom_end_date
        else:
            start_date, end_date = get_date_range_for_period(self.month, self.current_period)
        
        # Get net worth data
        net_worth_data = get_net_worth_data(start_date, end_date)
        
        # Update period info
        self.period_info_label.config(text=self.get_period_description())
        
        # Clear previous chart
        self.ax1.clear()
        
        if not net_worth_data:
            # No data
            self.ax1.text(0.5, 0.5, 'No financial data for this period', 
                         horizontalalignment='center', verticalalignment='center', 
                         transform=self.ax1.transAxes, fontsize=12)
            self.ax1.set_title("Net Worth Analysis", fontsize=14, fontweight='bold')
            self.canvas.draw()
            return
        
        # Prepare data for bar chart
        months = [item['month'] for item in net_worth_data]
        income = [item['income'] for item in net_worth_data]
        expenses = [item['expenses'] for item in net_worth_data]
        cumulative_net_worth = [item['cumulative_net_worth'] for item in net_worth_data]
        
        # Create bar chart
        x = range(len(months))
        width = 0.35
        
        # Income bars (green)
        bars1 = self.ax1.bar([i - width/2 for i in x], income, width, 
                            label='Income', color='#2E8B57', alpha=0.8)
        
        # Expense bars (red)
        bars2 = self.ax1.bar([i + width/2 for i in x], expenses, width,
                            label='Expenses', color='#DC143C', alpha=0.8)
        
        # Format y-axis to show satoshis nicely
        self.ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K' if x >= 1000 else f'{int(x)}'))
        
        # Set labels and title
        self.ax1.set_xlabel('Month')
        self.ax1.set_ylabel('Amount (sats)')
        self.ax1.set_title('Monthly Income vs Expenses', fontsize=14, fontweight='bold')
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(months, rotation=45)
        self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)
        
        # Add cumulative net worth line on secondary y-axis
        ax2 = self.ax1.twinx()
        line = ax2.plot(x, cumulative_net_worth, color='#4169E1', linewidth=3, 
                       marker='o', markersize=6, label='Cumulative Net Worth')
        ax2.set_ylabel('Cumulative Net Worth (sats)', color='#4169E1')
        ax2.tick_params(axis='y', labelcolor='#4169E1')
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K' if x >= 1000 else f'{int(x)}'))
        
        # Add legend for line
        lines, labels = self.ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.ax1.legend(lines + lines2, labels + labels2, loc='upper left')
        
        # Adjust layout to prevent clipping
        self.fig.tight_layout()
        
        # Draw the chart
        self.canvas.draw()


class PurchasingPowerReportWindow:
    def __init__(self, parent, month):
        """Initialize the purchasing power report window"""
        self.parent = parent
        self.month = month
        self.current_period = "last_6_months"  # Default to 6 months for budget calculation
        self.custom_start_date = ""
        self.custom_end_date = ""
        self.inflation_rate = 0.08  # Default 8% inflation
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title("Future Purchasing Power Analysis")
        self.window.geometry("1400x900")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.update_analysis()
    
    def create_widgets(self):
        """Create the report interface"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Future Purchasing Power Analysis", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Analysis Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Budget period selection
        ttk.Label(settings_frame, text="Base Budget Period:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        period_frame = ttk.Frame(settings_frame)
        period_frame.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Button(period_frame, text="Current Month", 
                  command=lambda: self.set_period("current_month")).grid(row=0, column=0, padx=2)
        ttk.Button(period_frame, text="Last 3 Months", 
                  command=lambda: self.set_period("last_3_months")).grid(row=0, column=1, padx=2)
        ttk.Button(period_frame, text="Last 6 Months", 
                  command=lambda: self.set_period("last_6_months")).grid(row=0, column=2, padx=2)
        ttk.Button(period_frame, text="Last 12 Months", 
                  command=lambda: self.set_period("last_12_months")).grid(row=0, column=3, padx=2)
        
        # Inflation rate setting
        ttk.Label(settings_frame, text="Annual Inflation Rate:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0), padx=(0, 10))
        inflation_frame = ttk.Frame(settings_frame)
        inflation_frame.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        self.inflation_var = tk.StringVar(value="8.0")
        inflation_entry = ttk.Entry(inflation_frame, textvariable=self.inflation_var, width=10)
        inflation_entry.grid(row=0, column=0)
        ttk.Label(inflation_frame, text="%").grid(row=0, column=1, padx=(2, 10))
        ttk.Button(inflation_frame, text="Update", command=self.update_inflation).grid(row=0, column=2)
        
        # Time horizon selection
        ttk.Label(settings_frame, text="Future Time Horizon:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0), padx=(0, 10))
        horizon_frame = ttk.Frame(settings_frame)
        horizon_frame.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        
        self.horizon_var = tk.StringVar(value="5")
        horizon_buttons = [
            ("1 Year", "1"), ("2 Years", "2"), ("5 Years", "5"), ("10 Years", "10")
        ]
        for i, (text, value) in enumerate(horizon_buttons):
            ttk.Radiobutton(horizon_frame, text=text, variable=self.horizon_var, 
                           value=value, command=self.update_analysis).grid(row=0, column=i, padx=5)
        
        # Period info
        self.period_info_label = ttk.Label(settings_frame, text="", font=("Arial", 9), foreground="blue")
        self.period_info_label.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
        
        # Charts frame - side by side pie charts
        charts_frame = ttk.LabelFrame(main_frame, text="Spending Comparison: Current vs Future", padding="10")
        charts_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create matplotlib figure with two subplots
        self.fig = Figure(figsize=(14, 6), dpi=100)
        self.ax1 = self.fig.add_subplot(121)  # Current spending pie
        self.ax2 = self.fig.add_subplot(122)  # Future spending pie
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        charts_frame.grid_rowconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(0, weight=1)
        
        # Results table frame
        results_frame = ttk.LabelFrame(main_frame, text="Future Purchasing Power Projections", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create treeview for results
        columns = ("Years", "Current Budget", "Future Equivalent", "Reduction", "Bitcoin Price", "Purchasing Power Gain")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=6)
        
        # Configure columns
        self.results_tree.heading("Years", text="Years Ahead")
        self.results_tree.heading("Current Budget", text="Current Budget")
        self.results_tree.heading("Future Equivalent", text="Future Equivalent")
        self.results_tree.heading("Reduction", text="Reduction")
        self.results_tree.heading("Bitcoin Price", text="Bitcoin Price")
        self.results_tree.heading("Purchasing Power Gain", text="Purchasing Power Gain")
        
        self.results_tree.column("Years", width=100)
        self.results_tree.column("Current Budget", width=150)
        self.results_tree.column("Future Equivalent", width=150)
        self.results_tree.column("Reduction", width=120)
        self.results_tree.column("Bitcoin Price", width=130)
        self.results_tree.column("Purchasing Power Gain", width=180)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.window.destroy).grid(row=4, column=0, columnspan=2, pady=(10, 0))
    
    def set_period(self, period_type):
        """Set the budget calculation period"""
        self.current_period = period_type
        self.update_analysis()
    
    def update_inflation(self):
        """Update inflation rate from user input"""
        try:
            self.inflation_rate = float(self.inflation_var.get()) / 100.0
            self.update_analysis()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid inflation rate", parent=self.window)
            self.inflation_var.set("8.0")
    
    def get_period_description(self):
        """Get description of current budget period"""
        if self.current_period == "current_month":
            return f"Based on current month ({self.month}) spending"
        elif self.current_period == "last_3_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_3_months")
            return f"Based on actual spending from {start_date} to {end_date}"
        elif self.current_period == "last_6_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_6_months")
            return f"Based on actual spending from {start_date} to {end_date}"
        elif self.current_period == "last_12_months":
            start_date, end_date = get_date_range_for_period(self.month, "last_12_months")
            return f"Based on actual spending from {start_date} to {end_date}"
        else:
            return ""
    
    def get_base_budget(self):
        """Calculate base budget based on selected period using actual spending"""
        breakdown, total = self.get_spending_breakdown_for_period()
        return total
    
    def get_spending_breakdown_for_period(self):
        """Get spending breakdown by category for the selected period"""
        if self.current_period == "current_month":
            # Get current month spending breakdown (actual expenses)
            start_date = f"{self.month}-01"
            year, month = map(int, self.month.split('-'))
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{self.month}-{last_day:02d}"
            
            breakdown, total = get_spending_breakdown(start_date, end_date)
            return breakdown, total
        else:
            # For multi-month periods, get actual spending breakdown
            start_date, end_date = get_date_range_for_period(self.month, self.current_period)
            breakdown, total = get_spending_breakdown(start_date, end_date)
            return breakdown, total
    
    def update_pie_charts(self):
        """Update the pie charts showing current vs future spending"""
        # Clear previous charts
        self.ax1.clear()
        self.ax2.clear()
        
        # Get current spending breakdown
        current_breakdown, current_total = self.get_spending_breakdown_for_period()
        
        if not current_breakdown or current_total <= 0:
            # No spending data
            self.ax1.text(0.5, 0.5, 'No spending data\nfor selected period', 
                         horizontalalignment='center', verticalalignment='center', 
                         transform=self.ax1.transAxes, fontsize=12)
            self.ax1.set_title("Current Spending", fontsize=14, fontweight='bold')
            
            self.ax2.text(0.5, 0.5, 'No data to analyze', 
                         horizontalalignment='center', verticalalignment='center', 
                         transform=self.ax2.transAxes, fontsize=12)
            self.ax2.set_title("Future Spending", fontsize=14, fontweight='bold')
            
            self.canvas.draw()
            return
        
        # Get future purchasing power calculation
        years_ahead = int(self.horizon_var.get())
        future_total, reduction_percentage = calculate_future_purchasing_power(
            current_total, years_ahead, self.inflation_rate
        )
        
        # Current spending pie chart
        current_categories = [item['category'] for item in current_breakdown]
        current_amounts = [item['amount'] for item in current_breakdown]
        current_colors = plt.cm.Set3(range(len(current_categories)))
        
        wedges1, texts1, autotexts1 = self.ax1.pie(current_amounts, labels=current_categories, 
                                                   autopct='%1.1f%%', colors=current_colors, 
                                                   startangle=90)
        
        self.ax1.set_title(f"Current Spending\n{format_sats(int(current_total))}", 
                          fontsize=14, fontweight='bold')
        
        # Future spending pie chart with Bitcoin Vibes
        future_categories = []
        future_amounts = []
        future_colors = []
        
        # Scale down current categories proportionally
        scale_factor = future_total / current_total
        for i, item in enumerate(current_breakdown):
            future_categories.append(item['category'])
            future_amounts.append(item['amount'] * scale_factor)
            future_colors.append(current_colors[i])
        
        # Add Bitcoin Vibes category for the savings
        bitcoin_vibes_amount = current_total - future_total
        if bitcoin_vibes_amount > 0:
            future_categories.append("🚀 Bitcoin Vibes")
            future_amounts.append(bitcoin_vibes_amount)
            future_colors.append('#FFD700')  # Gold color for Bitcoin Vibes
        
        wedges2, texts2, autotexts2 = self.ax2.pie(future_amounts, labels=future_categories, 
                                                   autopct='%1.1f%%', colors=future_colors, 
                                                   startangle=90)
        
        self.ax2.set_title(f"Future Spending ({years_ahead} year{'s' if years_ahead > 1 else ''})\n" +
                          f"Same purchasing power: {format_sats(int(future_total))}", 
                          fontsize=14, fontweight='bold')
        
        # Style the charts
        for autotext in autotexts1:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        for autotext in autotexts2:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        for text in texts1:
            text.set_fontsize(8)
        
        for text in texts2:
            text.set_fontsize(8)
        
        # Adjust layout
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_analysis(self):
        """Update the purchasing power analysis table"""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Update period description
        self.period_info_label.config(text=self.get_period_description())
        
        # Update pie charts
        self.update_pie_charts()
        
        # Get base budget
        base_budget = self.get_base_budget()
        
        if base_budget <= 0:
            self.results_tree.insert("", "end", values=(
                "No Data", "No budget data", "N/A", "N/A", "N/A", "N/A"
            ))
            return
        
        # Calculate projections for 1, 2, 5, and 10 years
        years_ahead = [1, 2, 5, 10]
        today = datetime.now()
        current_days = get_days_since_genesis(today)
        current_btc_price = calculate_btc_fair_value(current_days)
        
        for years in years_ahead:
            future_budget, reduction_percentage = calculate_future_purchasing_power(
                base_budget, years, self.inflation_rate
            )
            
            # Calculate future Bitcoin price
            future_date = today + timedelta(days=years * 365.25)
            future_days = get_days_since_genesis(future_date)
            future_btc_price = calculate_btc_fair_value(future_days)
            
            # Calculate purchasing power gain
            btc_gain = ((future_btc_price / current_btc_price) - 1) * 100
            
            self.results_tree.insert("", "end", values=(
                f"{years} year{'s' if years > 1 else ''}",
                format_sats(int(base_budget)),
                format_sats(int(future_budget)),
                f"-{reduction_percentage:.1f}%",
                f"${future_btc_price:,.0f}",
                f"+{btc_gain:.1f}%"
            ))


def calculate_btc_fair_value(days_since_genesis):
    """Calculate Bitcoin fair value using power law: 1.0117e-17 * days^5.82"""
    return 1.0117e-17 * (days_since_genesis ** 5.82)


def get_days_since_genesis(target_date):
    """Get days since Bitcoin genesis block (Jan 3, 2009)"""
    genesis_date = datetime(2009, 1, 3)
    return (target_date - genesis_date).days


def calculate_future_purchasing_power(current_budget_sats, years_ahead, inflation_rate=0.08):
    """Calculate future purchasing power based on Bitcoin power law and inflation"""
    today = datetime.now()
    future_date = today + timedelta(days=years_ahead * 365.25)
    
    current_days = get_days_since_genesis(today)
    future_days = get_days_since_genesis(future_date)
    
    current_btc_price = calculate_btc_fair_value(current_days)
    future_btc_price = calculate_btc_fair_value(future_days)
    
    btc_multiplier = future_btc_price / current_btc_price
    inflation_multiplier = (1 + inflation_rate) ** years_ahead
    
    future_budget = current_budget_sats * inflation_multiplier / btc_multiplier
    reduction_percentage = (1 - future_budget / current_budget_sats) * 100
    
    return future_budget, reduction_percentage


# === MAIN EXECUTION ===

if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Create and run the application
    app = BitcoinBudgetApp()
    app.run() 
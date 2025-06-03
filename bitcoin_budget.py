#!/usr/bin/env python3
"""
Bitcoin Budget Desktop - Simple Envelope Budgeting for Bitcoin Users

A single-file application using Python + Tkinter + SQLite for maximum simplicity.
No over-engineering, just straightforward budgeting that works.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import calendar
import os


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
    current_month_allocated = get_total_allocated(month)
    rollover_from_previous = get_rollover_amount(month)
    
    return current_month_income + rollover_from_previous - current_month_allocated


def get_rollover_amount(month):
    """Calculate total rollover available from previous month"""
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
    
    # Calculate previous month's leftover
    prev_available = get_total_income(prev_month) - get_total_allocated(prev_month)
    
    # Add unspent category balances from previous month
    prev_category_balances = 0
    categories = get_categories()
    for cat in categories:
        balance = get_category_balance(cat['id'], prev_month)
        if balance > 0:  # Only positive balances roll forward
            prev_category_balances += balance
    
    return prev_available + prev_category_balances


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
    """Get amount allocated to category for month"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT amount FROM allocations WHERE category_id = ? AND month = ?
    """, (category_id, month))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def get_category_balance(category_id, month):
    """Get current balance for category envelope"""
    allocated = get_category_allocated(category_id, month)
    spent = get_category_spent(category_id, month)
    return allocated - spent


def get_recent_transactions(limit=10):
    """Get recent transactions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.date, t.description, t.amount, t.type, c.name as category_name
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
        self.root.geometry("1000x700")  # Increased from 800x600
        
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
        
        ttk.Label(income_frame, text="Amount:").grid(row=0, column=0, sticky=tk.W)
        self.income_amount = ttk.Entry(income_frame, width=15)
        self.income_amount.grid(row=0, column=1, padx=5)
        
        ttk.Label(income_frame, text="Description:").grid(row=1, column=0, sticky=tk.W)
        self.income_desc = ttk.Entry(income_frame, width=20)
        self.income_desc.grid(row=1, column=1, padx=5)
        
        ttk.Button(income_frame, text="Add Income", command=self.add_income_clicked).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Categories section
        categories_frame = ttk.LabelFrame(main_frame, text="Categories", padding="10")
        categories_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Category listbox with scrollbar
        list_frame = ttk.Frame(categories_frame)
        list_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.categories_listbox = tk.Listbox(list_frame, height=8, width=60)
        self.categories_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.categories_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.categories_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Category buttons
        ttk.Button(categories_frame, text="Add Category", command=self.add_category_clicked).grid(row=1, column=0, pady=5)
        ttk.Button(categories_frame, text="Allocate", command=self.allocate_clicked).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(categories_frame, text="Add Expense", command=self.add_expense_clicked).grid(row=1, column=2, pady=5)
        
        # Recent transactions
        transactions_frame = ttk.LabelFrame(main_frame, text="Recent Transactions", padding="10")
        transactions_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Transaction treeview
        columns = ("Date", "Description", "Amount", "Category")
        self.transactions_tree = ttk.Treeview(transactions_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=150)
        
        self.transactions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Transaction scrollbar
        trans_scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        trans_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.transactions_tree.configure(yscrollcommand=trans_scrollbar.set)
        
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
            date_str, desc, amount, trans_type, category = trans
            if trans_type == 'income':
                amount_str = f"+{format_sats(amount)}"
                category_str = "Income"
            else:
                amount_str = f"-{format_sats(amount)}"
                category_str = category or "Unknown"
            
            self.transactions_tree.insert("", "end", values=(date_str, desc, amount_str, category_str))
    
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
            amount_text = self.income_amount.get()
            description = self.income_desc.get()
            
            if not amount_text or not description:
                messagebox.showerror("Error", "Please enter both amount and description")
                return
            
            amount_sats = parse_amount_input(amount_text)
            today = datetime.now().strftime('%Y-%m-%d')
            
            if add_income(amount_sats, description, today):
                self.income_amount.delete(0, tk.END)
                self.income_desc.delete(0, tk.END)
                self.refresh_display()
                messagebox.showinfo("Success", f"Added income: {format_sats(amount_sats)}")
            else:
                messagebox.showerror("Error", "Failed to add income")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
    
    def add_category_clicked(self):
        """Handle add category button click"""
        name = simpledialog.askstring("Add Category", "Enter category name:")
        if name:
            if add_category(name):
                self.refresh_display()
                messagebox.showinfo("Success", f"Added category: {name}")
            else:
                messagebox.showerror("Error", "Category name already exists")
    
    def allocate_clicked(self):
        """Handle allocate button click"""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a category")
            return
        
        categories = get_categories()
        if selection[0] >= len(categories):
            messagebox.showerror("Error", "Invalid category selection")
            return
        
        category = categories[selection[0]]
        
        amount_text = simpledialog.askstring("Allocate", f"Enter amount to allocate to {category['name']}:")
        if amount_text:
            try:
                amount_sats = parse_amount_input(amount_text)
                
                # Check if we have enough available
                available = get_available_to_assign(self.current_month)
                current_allocation = get_category_allocated(category['id'], self.current_month)
                additional_needed = amount_sats - current_allocation
                
                if additional_needed > available:
                    messagebox.showerror("Error", f"Not enough available to assign. Available: {format_sats(available)}")
                    return
                
                if allocate_to_category(category['id'], self.current_month, amount_sats):
                    self.refresh_display()
                    messagebox.showinfo("Success", f"Allocated {format_sats(amount_sats)} to {category['name']}")
                else:
                    messagebox.showerror("Error", "Failed to allocate")
                    
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format")
    
    def add_expense_clicked(self):
        """Handle add expense button click"""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a category")
            return
        
        categories = get_categories()
        if selection[0] >= len(categories):
            messagebox.showerror("Error", "Invalid category selection")
            return
        
        category = categories[selection[0]]
        
        # Get amount
        amount_text = simpledialog.askstring("Add Expense", f"Enter expense amount for {category['name']}:")
        if not amount_text:
            return
        
        # Get description
        description = simpledialog.askstring("Add Expense", "Enter description:")
        if not description:
            return
        
        try:
            amount_sats = parse_amount_input(amount_text)
            today = datetime.now().strftime('%Y-%m-%d')
            
            if add_expense(amount_sats, description, category['id'], today):
                self.refresh_display()
                messagebox.showinfo("Success", f"Added expense: {format_sats(amount_sats)} to {category['name']}")
            else:
                messagebox.showerror("Error", "Failed to add expense")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


# === MAIN EXECUTION ===

if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Create and run the application
    app = BitcoinBudgetApp()
    app.run() 
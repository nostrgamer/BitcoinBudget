#!/usr/bin/env python3
"""
Bitcoin Budget - Streamlit Web Application
Modern web-based envelope budgeting for Bitcoin users
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import calendar
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# === STREAMLIT PAGE CONFIG ===
st.set_page_config(
    page_title="Bitcoin Budget",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === DATABASE FUNCTIONS (UNCHANGED FROM ORIGINAL) ===

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
        st.error(f"Error adding income: {e}")
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
        st.error(f"Error adding expense: {e}")
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
        st.error(f"Error allocating to category: {e}")
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
        return cursor.rowcount > 0
    except Exception as e:
        st.error(f"Error deleting transaction: {e}")
        return False
    finally:
        conn.close()

def delete_category(category_id):
    """Delete a category and all its associated allocations and transactions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,))
        transaction_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM allocations WHERE category_id = ?", (category_id,))
        allocation_count = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM allocations WHERE category_id = ?", (category_id,))
        cursor.execute("DELETE FROM transactions WHERE category_id = ?", (category_id,))
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        
        return True, transaction_count, allocation_count
    except Exception as e:
        st.error(f"Error deleting category: {e}")
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
        st.error(f"Error deleting allocation: {e}")
        return False
    finally:
        conn.close()

# === BUDGET LOGIC (UNCHANGED FROM ORIGINAL) ===

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
    current_month_allocated = get_total_allocated_direct(month)
    rollover_from_previous = get_rollover_amount(month)
    
    return current_month_income + rollover_from_previous - current_month_allocated

def get_rollover_amount(month):
    """Calculate unallocated income rollover from previous month"""
    year, month_num = map(int, month.split('-'))
    
    if month_num == 1:
        prev_month = f"{year-1}-12"
    else:
        prev_month = f"{year}-{month_num-1:02d}"
    
    prev_income = get_total_income(prev_month)
    if prev_income == 0:
        return 0
    
    prev_allocated = get_total_allocated_direct(prev_month)
    prev_unallocated = prev_income - prev_allocated
    
    return max(0, prev_unallocated)

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
    """Get amount allocated to category for month"""
    return get_category_allocated_direct(category_id, month)

def get_category_rollover_balance(category_id, month):
    """Get the rollover balance for a category from the previous month only"""
    year, month_num = map(int, month.split('-'))
    
    if month_num == 1:
        prev_month = f"{year-1}-12"
    else:
        prev_month = f"{year}-{month_num-1:02d}"
    
    prev_income = get_total_income(prev_month)
    if prev_income == 0:
        return 0
    
    prev_allocated = get_category_allocated_direct(category_id, prev_month)
    prev_spent = get_category_spent(category_id, prev_month)
    prev_balance = prev_allocated - prev_spent
    
    return max(0, prev_balance)

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
    rollover = get_category_rollover_balance(category_id, month)
    
    return allocated + rollover - spent

def get_recent_transactions(limit=20):
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

def get_expense_transactions(limit=50):
    """Get recent expense transactions for lifecycle cost analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.date, t.description, t.amount, c.name as category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type = 'expense'
        ORDER BY t.date DESC, t.created_at DESC
        LIMIT ?
    """, (limit,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# === UTILITY FUNCTIONS (UNCHANGED FROM ORIGINAL) ===

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
        btc_amount = float(text[:-4])
        return int(btc_amount * 100_000_000)
    else:
        return int(text)

def get_current_month():
    """Return current month as 'YYYY-MM'"""
    return datetime.now().strftime('%Y-%m')

# === STREAMLIT APPLICATION ===

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_month' not in st.session_state:
        st.session_state.current_month = get_current_month()
    if 'page' not in st.session_state:
        st.session_state.page = 'main'

def main_page():
    """Main budget application page"""
    current_month = st.session_state.current_month
    
    # Header with current month
    st.title(f"₿ Bitcoin Budget - {current_month}")
    
    # === BUDGET SUMMARY METRICS ===
    st.markdown("### 💰 Budget Summary")
    
    total_income = get_total_income(current_month)
    rollover = get_rollover_amount(current_month)
    total_allocated = get_total_allocated(current_month)
    available = get_available_to_assign(current_month)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💵 Total Income",
            value=format_sats(total_income),
            delta=None
        )
    
    with col2:
        st.metric(
            label="🔄 Rollover",
            value=format_sats(rollover),
            delta=None
        )
    
    with col3:
        st.metric(
            label="📋 Allocated",
            value=format_sats(total_allocated),
            delta=None
        )
    
    with col4:
        st.metric(
            label="🎯 Available to Assign",
            value=format_sats(available),
            delta=None
        )

    st.markdown("---")

    # === MAIN FUNCTIONALITY TABS ===
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Add Income", "📁 Categories", "💸 Expenses", "📋 Transactions"])
    
    # === TAB 1: ADD INCOME ===
    with tab1:
        st.markdown("### 💰 Add Income")
        
        with st.form("add_income_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                income_date = st.date_input(
                    "Date",
                    value=datetime.now().date(),
                    help="Date of income receipt"
                )
                
                income_amount = st.text_input(
                    "Amount",
                    placeholder="1000000 or 0.01 BTC",
                    help="Enter amount in sats or BTC"
                )
            
            with col2:
                income_description = st.text_input(
                    "Description",
                    placeholder="Salary, freelance, etc.",
                    help="Brief description of income source"
                )
            
            submitted = st.form_submit_button("➕ Add Income", use_container_width=True, type="primary")
            
            if submitted:
                if income_amount and income_description:
                    try:
                        amount_sats = parse_amount_input(income_amount)
                        if add_income(amount_sats, income_description, str(income_date)):
                            st.success(f"✅ Added income: {format_sats(amount_sats)} - {income_description}")
                            st.rerun()
                        else:
                            st.error("❌ Failed to add income")
                    except ValueError:
                        st.error("❌ Invalid amount format")
                else:
                    st.error("❌ Please fill in all fields")

    # === TAB 2: CATEGORIES ===
    with tab2:
        st.markdown("### 📁 Category Management")
        
        # Add new category
        with st.expander("➕ Add New Category", expanded=False):
            with st.form("add_category_form"):
                new_category = st.text_input("Category Name", placeholder="e.g., Transportation")
                if st.form_submit_button("Add Category"):
                    if new_category:
                        if add_category(new_category):
                            st.success(f"✅ Added category: {new_category}")
                            st.rerun()
                        else:
                            st.error("❌ Category name already exists")
                    else:
                        st.error("❌ Please enter a category name")

        # Display categories
        categories = get_categories()
        
        if categories:
            # Create category dataframe
            category_data = []
            for cat in categories:
                allocated = get_category_allocated(cat['id'], current_month)
                spent = get_category_spent(cat['id'], current_month)
                balance = get_category_balance(cat['id'], current_month)
                
                category_data.append({
                    'Category': cat['name'],
                    'Allocated': format_sats(allocated),
                    'Spent': format_sats(spent),
                    'Balance': format_sats(balance),
                    'Status': '✅ Good' if balance >= 0 else '⚠️ Overspent'
                })
            
            df = pd.DataFrame(category_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Allocation form
            st.markdown("#### 💼 Allocate to Categories")
            with st.form("allocate_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_category = st.selectbox(
                        "Select Category",
                        options=[cat['name'] for cat in categories],
                        help="Choose category to allocate funds to"
                    )
                
                with col2:
                    allocation_amount = st.text_input(
                        "Allocation Amount",
                        placeholder="Amount in sats",
                        help=f"Available: {format_sats(available)}"
                    )
                
                if st.form_submit_button("💼 Allocate Funds", type="primary"):
                    if allocation_amount:
                        try:
                            amount_sats = parse_amount_input(allocation_amount)
                            
                            # Find category ID
                            category_id = None
                            for cat in categories:
                                if cat['name'] == selected_category:
                                    category_id = cat['id']
                                    break
                            
                            if category_id:
                                current_allocation = get_category_allocated(category_id, current_month)
                                additional_needed = amount_sats - current_allocation
                                
                                if additional_needed <= available:
                                    if allocate_to_category(category_id, current_month, amount_sats):
                                        st.success(f"✅ Allocated {format_sats(amount_sats)} to {selected_category}")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to allocate")
                                else:
                                    st.error(f"❌ Not enough available funds. Available: {format_sats(available)}")
                        except ValueError:
                            st.error("❌ Invalid amount format")
                    else:
                        st.error("❌ Please enter an allocation amount")
        else:
            st.info("No categories yet. Add your first category above!")

    # === TAB 3: EXPENSES ===
    with tab3:
        st.markdown("### 💸 Add Expense")
        
        categories = get_categories()
        if categories:
            with st.form("add_expense_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    expense_date = st.date_input(
                        "Date",
                        value=datetime.now().date()
                    )
                    
                    expense_category = st.selectbox(
                        "Category",
                        options=[cat['name'] for cat in categories]
                    )
                
                with col2:
                    expense_amount = st.text_input(
                        "Amount",
                        placeholder="50000 or 0.0005 BTC"
                    )
                    
                    expense_description = st.text_input(
                        "Description",
                        placeholder="Coffee, groceries, etc."
                    )
                
                if st.form_submit_button("💸 Add Expense", type="primary"):
                    if expense_amount and expense_description:
                        try:
                            amount_sats = parse_amount_input(expense_amount)
                            
                            # Find category ID
                            category_id = None
                            for cat in categories:
                                if cat['name'] == expense_category:
                                    category_id = cat['id']
                                    break
                            
                            if category_id:
                                if add_expense(amount_sats, expense_description, category_id, str(expense_date)):
                                    st.success(f"✅ Added expense: {format_sats(amount_sats)} - {expense_description}")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to add expense")
                        except ValueError:
                            st.error("❌ Invalid amount format")
                    else:
                        st.error("❌ Please fill in all fields")
        else:
            st.warning("⚠️ Add categories first before recording expenses.")

    # === TAB 4: TRANSACTIONS ===
    with tab4:
        st.markdown("### 📋 Recent Transactions")
        
        transactions = get_recent_transactions(20)
        
        if transactions:
            # Convert to dataframe
            trans_data = []
            for trans in transactions:
                trans_id, date_str, desc, amount, trans_type, category = trans
                
                if trans_type == 'income':
                    amount_str = f"+{format_sats(amount)}"
                    emoji = "💰"
                    category_str = "Income"
                else:
                    amount_str = f"-{format_sats(amount)}"
                    emoji = "💸"
                    category_str = category or "Unknown"
                
                trans_data.append({
                    'ID': trans_id,
                    'Type': emoji,
                    'Date': date_str,
                    'Description': desc,
                    'Amount': amount_str,
                    'Category': category_str
                })
            
            df = pd.DataFrame(trans_data)
            
            # Display transactions with selection
            selected_rows = st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": None,  # Hide ID column
                    "Type": st.column_config.TextColumn("", width="small"),
                    "Amount": st.column_config.TextColumn("Amount", width="medium")
                },
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Delete transaction button
            if selected_rows.selection.rows:
                selected_idx = selected_rows.selection.rows[0]
                selected_transaction = trans_data[selected_idx]
                
                st.markdown("#### 🗑️ Delete Transaction")
                st.write(f"Selected: **{selected_transaction['Description']}** - {selected_transaction['Amount']}")
                
                if st.button("🗑️ Delete Selected Transaction", type="secondary"):
                    if delete_transaction(selected_transaction['ID']):
                        st.success("✅ Transaction deleted")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete transaction")
        else:
            st.info("No transactions yet. Add some income or expenses to get started!")

def sidebar_navigation():
    """Sidebar for navigation and month selection"""
    with st.sidebar:
        st.title("₿ Bitcoin Budget")
        
        st.markdown("### 📅 Month Navigation")
        
        # Month selector
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("←", help="Previous month"):
                year, month = map(int, st.session_state.current_month.split('-'))
                if month == 1:
                    month = 12
                    year -= 1
                else:
                    month -= 1
                st.session_state.current_month = f"{year:04d}-{month:02d}"
                st.rerun()
        
        with col2:
            st.markdown(f"**{st.session_state.current_month}**")
        
        with col3:
            if st.button("→", help="Next month"):
                year, month = map(int, st.session_state.current_month.split('-'))
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                st.session_state.current_month = f"{year:04d}-{month:02d}"
                st.rerun()

        st.markdown("---")
        
        # Navigation
        st.markdown("### 🚀 Navigation")
        
        if st.button("🏠 Main Budget", use_container_width=True):
            st.session_state.page = 'main'
            st.rerun()
        
        if st.button("📊 Reports", use_container_width=True):
            st.session_state.page = 'reports'
            st.rerun()

def main():
    """Main application entry point"""
    # Initialize database and session state
    init_database()
    initialize_session_state()
    
    # Sidebar navigation
    sidebar_navigation()
    
    # Page routing
    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'reports':
        # Import and show reports page
        from pages import reports
        reports.show()

if __name__ == "__main__":
    main() 
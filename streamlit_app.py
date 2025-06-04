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
    
    # Master Categories table - groups for organizing categories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    # Categories table - spending envelopes (now with master category grouping)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            master_category_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(master_category_id) REFERENCES master_categories(id)
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
    
    # Add master_category_id column to existing categories table if it doesn't exist
    cursor.execute("PRAGMA table_info(categories)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'master_category_id' not in columns:
        cursor.execute("ALTER TABLE categories ADD COLUMN master_category_id INTEGER REFERENCES master_categories(id)")
    
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

def add_master_category(name):
    """Add a new master category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO master_categories (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicate name
    finally:
        conn.close()

def get_master_categories():
    """Get all master categories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM master_categories ORDER BY sort_order, name")
    master_categories = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1]} for row in master_categories]

def get_categories():
    """Get all categories with their master category information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.master_category_id, mc.name as master_category_name
        FROM categories c
        LEFT JOIN master_categories mc ON c.master_category_id = mc.id
        ORDER BY mc.sort_order, mc.name, c.name
    """)
    categories = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1], 'master_category_id': row[2], 'master_category_name': row[3]} for row in categories]

def get_categories_grouped():
    """Get categories grouped by master category"""
    categories = get_categories()
    grouped = {}
    
    for cat in categories:
        master_name = cat['master_category_name'] or 'Uncategorized'
        if master_name not in grouped:
            grouped[master_name] = []
        grouped[master_name].append(cat)
    
    return grouped

def assign_category_to_master(category_id, master_category_id):
    """Assign a category to a master category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE categories SET master_category_id = ? WHERE id = ?
        """, (master_category_id, category_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error assigning category: {e}")
        return False
    finally:
        conn.close()

def rename_master_category(master_category_id, new_name):
    """Rename a master category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE master_categories SET name = ? WHERE id = ?
        """, (new_name, master_category_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicate name
    except Exception as e:
        st.error(f"Error renaming master category: {e}")
        return False
    finally:
        conn.close()

def rename_category(category_id, new_name):
    """Rename a category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE categories SET name = ? WHERE id = ?
        """, (new_name, category_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicate name
    except Exception as e:
        st.error(f"Error renaming category: {e}")
        return False
    finally:
        conn.close()

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
        # Check if over budget (allocated > income + rollover)
        total_available = total_income + rollover
        if total_allocated > total_available:
            st.metric(
                label="📋 Allocated",
                value=format_sats(total_allocated),
                delta="⚠️ Over Budget",
                delta_color="inverse"
            )
        else:
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
    tab1, tab2 = st.tabs(["📁 Categories", "💳 Transactions"])
    
    # === TAB 1: CATEGORIES (Now the primary/default tab) ===
    with tab1:
        st.markdown("### 📁 Category Management")
        
        # Add new master category and category sections
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Add Master Category", expanded=False):
                with st.form("add_master_category_form"):
                    new_master_category = st.text_input("Master Category Name", placeholder="e.g., Fixed Expenses, Variable Expenses, Savings")
                    if st.form_submit_button("Add Master Category"):
                        if new_master_category:
                            if add_master_category(new_master_category):
                                st.success(f"✅ Added master category: {new_master_category}")
                                st.rerun()
                            else:
                                st.error("❌ Master category name already exists")
                        else:
                            st.error("❌ Please enter a master category name")
        
        with col2:
            with st.expander("➕ Add Category", expanded=False):
                with st.form("add_category_form"):
                    new_category = st.text_input("Category Name", placeholder="e.g., Transportation")
                    
                    # Master category selection
                    master_categories = get_master_categories()
                    master_options = ['None'] + [mc['name'] for mc in master_categories]
                    selected_master = st.selectbox("Assign to Master Category", master_options)
                    
                    if st.form_submit_button("Add Category"):
                        if new_category:
                            if add_category(new_category):
                                # Assign to master category if selected
                                if selected_master != 'None':
                                    master_id = None
                                    for mc in master_categories:
                                        if mc['name'] == selected_master:
                                            master_id = mc['id']
                                            break
                                    
                                    if master_id:
                                        # Get the newly created category ID
                                        conn = get_db_connection()
                                        cursor = conn.cursor()
                                        cursor.execute("SELECT id FROM categories WHERE name = ?", (new_category,))
                                        category_id = cursor.fetchone()[0]
                                        conn.close()
                                        
                                        assign_category_to_master(category_id, master_id)
                                
                                st.success(f"✅ Added category: {new_category}")
                                st.rerun()
                            else:
                                st.error("❌ Category name already exists")
                        else:
                            st.error("❌ Please enter a category name")

        st.markdown("---")

        # Get all master categories and categories
        master_categories = get_master_categories()
        all_categories = get_categories()
        
        if master_categories or all_categories:
            # Build unified table data with proper grouping
            table_data = []
            grand_allocated = 0
            grand_spent = 0
            grand_balance = 0
            
            # Get all master category names (including empty ones)
            master_names = [mc['name'] for mc in master_categories]
            
            # Add "Uncategorized" for categories without master category
            master_names.append('Uncategorized')
            
            # Group categories by master category
            for master_name in master_names:
                # Find categories for this master category
                if master_name == 'Uncategorized':
                    categories_in_group = [cat for cat in all_categories if cat['master_category_id'] is None]
                else:
                    master_id = next((mc['id'] for mc in master_categories if mc['name'] == master_name), None)
                    categories_in_group = [cat for cat in all_categories if cat['master_category_id'] == master_id]
                
                # Calculate master category totals
                master_allocated = 0
                master_spent = 0
                master_balance = 0
                
                # Add master category header row
                table_data.append({
                    'ID': f"master_{master_name}",
                    'Type': 'master',
                    'Category': f"📂 {master_name}",
                    'Master_Category_Assignment': master_name,
                    'Allocated': 0,  # Will be calculated
                    'Spent': 0,      # Will be calculated
                    'Balance': 0,    # Will be calculated
                    'Status': '📊 Total'
                })
                
                # Add individual categories under this master category
                for cat in categories_in_group:
                    allocated = get_category_allocated(cat['id'], current_month)
                    spent = get_category_spent(cat['id'], current_month)
                    balance = get_category_balance(cat['id'], current_month)
                    
                    master_allocated += allocated
                    master_spent += spent
                    master_balance += balance
                    
                    # Get master category options for reassignment
                    master_options_for_cat = ['Uncategorized'] + [mc['name'] for mc in master_categories]
                    current_master = cat['master_category_name'] or 'Uncategorized'
                    
                    table_data.append({
                        'ID': cat['id'],
                        'Type': 'category',
                        'Category': f"    {cat['name']}", # Indent to show hierarchy
                        'Master_Category_Assignment': current_master,
                        'Allocated': allocated,
                        'Spent': spent,
                        'Balance': balance,
                        'Status': '✅ Good' if balance >= 0 else '⚠️ Overspent'
                    })
                
                # Update master category totals in the header row
                for row in table_data:
                    if row['ID'] == f"master_{master_name}":
                        row['Allocated'] = master_allocated
                        row['Spent'] = master_spent
                        row['Balance'] = master_balance
                        row['Status'] = '📊 Total' if master_balance >= 0 else '⚠️ Over'
                        break
                
                # Add to grand totals
                grand_allocated += master_allocated
                grand_spent += master_spent
                grand_balance += master_balance
            
            # Add grand total row
            table_data.append({
                'ID': 'grand_total',
                'Type': 'grand_total',
                'Category': '📊 GRAND TOTAL',
                'Master_Category_Assignment': 'Grand Total',
                'Allocated': grand_allocated,
                'Spent': grand_spent,
                'Balance': grand_balance,
                'Status': '🎯 Total' if grand_balance >= 0 else '⚠️ Over'
            })
            
            # Create DataFrame
            df = pd.DataFrame(table_data)
            
            # Display editable table
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": None,  # Hide ID column
                    "Type": None,  # Hide type column
                    "Category": st.column_config.TextColumn(
                        "Category", 
                        help="Click to rename categories or master categories",
                        width="large"
                    ),
                    "Master_Category_Assignment": st.column_config.SelectboxColumn(
                        "Master Category",
                        help="Click dropdown to reassign category to different master category",
                        options=['Uncategorized'] + [mc['name'] for mc in master_categories]
                    ),
                    "Allocated": st.column_config.NumberColumn(
                        "Allocated (sats)",
                        help="Enter allocation amount in satoshis (only works for individual categories)",
                        min_value=0,
                        step=1,
                        format="%d"
                    ),
                    "Spent": st.column_config.NumberColumn(
                        "Spent (sats)", 
                        disabled=True,
                        format="%d"
                    ),
                    "Balance": st.column_config.NumberColumn(
                        "Balance (sats)", 
                        disabled=True,
                        format="%d"
                    ),
                    "Status": st.column_config.TextColumn("Status", disabled=True)
                },
                key="unified_categories"
            )
            
            # Process changes
            if not edited_df.equals(df):
                changes_made = False
                for idx, row in edited_df.iterrows():
                    row_type = row['Type']
                    
                    # Check for category/master category name changes
                    original_category_name = df.iloc[idx]['Category']
                    new_category_name = row['Category']
                    
                    if original_category_name != new_category_name:
                        if row_type == 'master':
                            # Rename master category
                            master_name = original_category_name.replace('📂 ', '')
                            new_master_name = new_category_name.replace('📂 ', '')
                            
                            master_id = next((mc['id'] for mc in master_categories if mc['name'] == master_name), None)
                            if master_id and new_master_name.strip():
                                if rename_master_category(master_id, new_master_name.strip()):
                                    st.success(f"✅ Renamed master category from '{master_name}' to '{new_master_name}'")
                                    changes_made = True
                                else:
                                    st.error(f"❌ Failed to rename master category (name may already exist)")
                        
                        elif row_type == 'category':
                            # Rename individual category
                            old_name = original_category_name.strip()
                            new_name = new_category_name.strip()
                            
                            category_id = row['ID']
                            if new_name:
                                if rename_category(category_id, new_name):
                                    st.success(f"✅ Renamed category from '{old_name}' to '{new_name}'")
                                    changes_made = True
                                else:
                                    st.error(f"❌ Failed to rename category (name may already exist)")
                    
                    if row_type == 'category':  # Only process other changes for individual categories
                        # Check for allocation changes
                        original_allocated = df.iloc[idx]['Allocated']
                        new_allocated = row['Allocated']
                        
                        if original_allocated != new_allocated:
                            category_id = row['ID']
                            
                            if new_allocated == 0 or pd.isna(new_allocated):
                                if delete_allocation(category_id, current_month):
                                    st.success(f"✅ Removed allocation for {row['Category'].strip()}")
                                    changes_made = True
                                else:
                                    st.error(f"❌ Failed to remove allocation for {row['Category'].strip()}")
                            else:
                                if allocate_to_category(category_id, current_month, int(new_allocated)):
                                    st.success(f"✅ Allocated {format_sats(int(new_allocated))} to {row['Category'].strip()}")
                                    changes_made = True
                                else:
                                    st.error(f"❌ Failed to allocate to {row['Category'].strip()}")
                        
                        # Check for master category reassignment
                        original_master = df.iloc[idx]['Master_Category_Assignment']
                        new_master = row['Master_Category_Assignment']
                        
                        if original_master != new_master:
                            category_id = row['ID']
                            
                            if new_master == 'Uncategorized':
                                master_id = None
                            else:
                                master_id = next((mc['id'] for mc in master_categories if mc['name'] == new_master), None)
                            
                            if assign_category_to_master(category_id, master_id):
                                st.success(f"✅ Moved {row['Category'].strip()} to {new_master}")
                                changes_made = True
                            else:
                                st.error(f"❌ Failed to move {row['Category'].strip()}")
                        
                # Rerun if any changes were made
                if changes_made:
                    st.rerun()
            
            # Delete functionality section
            st.markdown("---")
            st.markdown("#### 🗑️ Delete Categories")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Delete Master Category**")
                if master_categories:
                    selected_master_to_delete = st.selectbox(
                        "Select Master Category to Delete",
                        [mc['name'] for mc in master_categories],
                        key="delete_master_select"
                    )
                    
                    if st.button("🗑️ Delete Master Category", key="delete_master_btn", type="secondary"):
                        master_id = next((mc['id'] for mc in master_categories if mc['name'] == selected_master_to_delete), None)
                        if master_id:
                            # Check if master category has categories assigned
                            categories_in_master = [cat for cat in all_categories if cat['master_category_id'] == master_id]
                            
                            if categories_in_master:
                                # Move categories to Uncategorized before deleting master category
                                for cat in categories_in_master:
                                    assign_category_to_master(cat['id'], None)
                                
                                st.warning(f"⚠️ Moved {len(categories_in_master)} categories to Uncategorized before deleting master category")
                            
                            # Delete master category
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            try:
                                cursor.execute("DELETE FROM master_categories WHERE id = ?", (master_id,))
                                conn.commit()
                                st.success(f"✅ Deleted master category: {selected_master_to_delete}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to delete master category: {e}")
                            finally:
                                conn.close()
                else:
                    st.info("No master categories to delete")
            
            with col2:
                st.markdown("**Delete Category**")
                if all_categories:
                    selected_category_to_delete = st.selectbox(
                        "Select Category to Delete",
                        [cat['name'] for cat in all_categories],
                        key="delete_category_select"
                    )
                    
                    if st.button("🗑️ Delete Category", key="delete_category_btn", type="secondary"):
                        category_id = next((cat['id'] for cat in all_categories if cat['name'] == selected_category_to_delete), None)
                        if category_id:
                            success, transaction_count, allocation_count = delete_category(category_id)
                            if success:
                                st.success(f"✅ Deleted category: {selected_category_to_delete}")
                                if transaction_count > 0 or allocation_count > 0:
                                    st.info(f"📊 Also deleted {transaction_count} transactions and {allocation_count} allocations")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete category: {selected_category_to_delete}")
                else:
                    st.info("No categories to delete")
                    
        else:
            st.info("No categories yet. Add your first master category and categories above!")

    # === TAB 2: TRANSACTIONS (Combined transaction entry + recent transactions) ===
    with tab2:
        st.markdown("### 💳 Enter Transaction")
        
        # Transaction type selection outside the form so it updates dynamically
        transaction_type = st.selectbox(
            "Transaction Type",
            options=["Income", "Expense"],
            help="Select whether this is income or an expense"
        )
        
        # Dynamic form based on transaction type
        if transaction_type == "Income":
            with st.form("add_income_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    transaction_date = st.date_input(
                        "Date",
                        value=datetime.now().date(),
                        help="Date of transaction"
                    )
                    
                    transaction_amount = st.text_input(
                        "Amount",
                        placeholder="1000000 or 0.01 BTC",
                        help="Enter amount in sats or BTC"
                    )
                
                with col2:
                    transaction_description = st.text_input(
                        "Description",
                        placeholder="Salary, freelance, etc.",
                        help="Brief description of income source"
                    )
                
                # Income submit button
                submitted = st.form_submit_button("💰 Add Income", use_container_width=True, type="primary")
                
                if submitted:
                    if transaction_amount and transaction_description:
                        try:
                            amount_sats = parse_amount_input(transaction_amount)
                            if add_income(amount_sats, transaction_description, str(transaction_date)):
                                st.success(f"✅ Added income: {format_sats(amount_sats)} - {transaction_description}")
                                st.rerun()
                            else:
                                st.error("❌ Failed to add income")
                        except ValueError:
                            st.error("❌ Invalid amount format")
                    else:
                        st.error("❌ Please fill in all required fields")
        
        else:  # Expense
            categories = get_categories()
            if categories:
                with st.form("add_expense_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        transaction_date = st.date_input(
                            "Date",
                            value=datetime.now().date(),
                            help="Date of transaction"
                        )
                        
                        transaction_category = st.selectbox(
                            "Category",
                            options=[cat['name'] for cat in categories],
                            help="Select spending category"
                        )
                    
                    with col2:
                        transaction_amount = st.text_input(
                            "Amount",
                            placeholder="50000 or 0.0005 BTC",
                            help="Enter amount in sats or BTC"
                        )
                        
                        transaction_description = st.text_input(
                            "Description",
                            placeholder="Coffee, groceries, etc.",
                            help="Brief description of expense"
                        )
                    
                    # Expense submit button
                    submitted = st.form_submit_button("💸 Add Expense", use_container_width=True, type="primary")
                    
                    if submitted:
                        if transaction_amount and transaction_description:
                            try:
                                amount_sats = parse_amount_input(transaction_amount)
                                
                                # Find category ID
                                category_id = None
                                for cat in categories:
                                    if cat['name'] == transaction_category:
                                        category_id = cat['id']
                                        break
                                
                                if category_id:
                                    if add_expense(amount_sats, transaction_description, category_id, str(transaction_date)):
                                        st.success(f"✅ Added expense: {format_sats(amount_sats)} - {transaction_description}")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to add expense")
                            except ValueError:
                                st.error("❌ Invalid amount format")
                        else:
                            st.error("❌ Please fill in all required fields")
            else:
                st.warning("⚠️ Add categories first before recording expenses.")
                st.info("👆 Go to the Categories tab to add your first spending category.")

        # Add separator between transaction entry and recent transactions
        st.markdown("---")
        
        # Recent transactions section (moved below transaction entry)
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
        from modules import reports
        reports.show()

if __name__ == "__main__":
    main() 
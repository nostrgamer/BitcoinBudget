#!/usr/bin/env python3
"""
Bitcoin Budget - Streamlit Web Application
Modern web-based envelope budgeting for Bitcoin users
"""
# Force preview refresh

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
    try:
        transaction = {
            'id': st.session_state.user_data['next_transaction_id'],
            'date': str(transaction_date),
            'description': description,
            'amount': amount_sats,
            'type': 'income',
            'category_id': None
        }
        st.session_state.user_data['transactions'].append(transaction)
        st.session_state.user_data['next_transaction_id'] += 1
        return True
    except Exception as e:
        st.error(f"Error adding income: {e}")
        return False

def add_expense(amount_sats, description, category_id, transaction_date):
    """Add expense transaction"""
    try:
        transaction = {
            'id': st.session_state.user_data['next_transaction_id'],
            'date': str(transaction_date),
            'description': description,
            'amount': amount_sats,
            'type': 'expense',
            'category_id': category_id
        }
        st.session_state.user_data['transactions'].append(transaction)
        st.session_state.user_data['next_transaction_id'] += 1
        return True
    except Exception as e:
        st.error(f"Error adding expense: {e}")
        return False

def add_category(name):
    """Add a new spending category"""
    try:
        # Check for duplicate name
        for cat in st.session_state.user_data['categories']:
            if cat['name'] == name:
                return False  # Duplicate name
        
        category = {
            'id': st.session_state.user_data['next_category_id'],
            'name': name,
            'master_category_id': None
        }
        st.session_state.user_data['categories'].append(category)
        st.session_state.user_data['next_category_id'] += 1
        return True
    except Exception:
        return False

def add_master_category(name):
    """Add a new master category"""
    try:
        # Check for duplicate name
        for mc in st.session_state.user_data['master_categories']:
            if mc['name'] == name:
                return False  # Duplicate name
        
        master_category = {
            'id': st.session_state.user_data['next_master_category_id'],
            'name': name
        }
        st.session_state.user_data['master_categories'].append(master_category)
        st.session_state.user_data['next_master_category_id'] += 1
        return True
    except Exception:
        return False

def get_master_categories():
    """Get all master categories"""
    return st.session_state.user_data['master_categories'].copy()

def get_categories():
    """Get all categories with their master category information"""
    categories = []
    for cat in st.session_state.user_data['categories']:
        master_category_name = None
        if cat['master_category_id']:
            for mc in st.session_state.user_data['master_categories']:
                if mc['id'] == cat['master_category_id']:
                    master_category_name = mc['name']
                    break
        
        categories.append({
            'id': cat['id'],
            'name': cat['name'],
            'master_category_id': cat['master_category_id'],
            'master_category_name': master_category_name
        })
    
    return categories

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
    try:
        for category in st.session_state.user_data['categories']:
            if category['id'] == category_id:
                category['master_category_id'] = master_category_id
                return True
        return False
    except Exception as e:
        st.error(f"Error assigning category: {e}")
        return False

def rename_master_category(master_category_id, new_name):
    """Rename a master category"""
    try:
        # Check for duplicate name
        for mc in st.session_state.user_data['master_categories']:
            if mc['name'] == new_name and mc['id'] != master_category_id:
                return False  # Duplicate name
        
        # Update the name
        for mc in st.session_state.user_data['master_categories']:
            if mc['id'] == master_category_id:
                mc['name'] = new_name
                return True
        
        return False
    except Exception as e:
        st.error(f"Error renaming master category: {e}")
        return False

def rename_category(category_id, new_name):
    """Rename a category"""
    try:
        # Check for duplicate name
        for cat in st.session_state.user_data['categories']:
            if cat['name'] == new_name and cat['id'] != category_id:
                return False  # Duplicate name
        
        # Update the name
        for cat in st.session_state.user_data['categories']:
            if cat['id'] == category_id:
                cat['name'] = new_name
                return True
        
        return False
    except Exception as e:
        st.error(f"Error renaming category: {e}")
        return False

def allocate_to_category(category_id, month, amount_sats):
    """Allocate amount to category for specific month"""
    try:
        # Find existing allocation for this category and month
        existing_allocation = None
        for i, alloc in enumerate(st.session_state.user_data['allocations']):
            if alloc['category_id'] == category_id and alloc['month'] == month:
                existing_allocation = i
                break
        
        if existing_allocation is not None:
            # Update existing allocation
            st.session_state.user_data['allocations'][existing_allocation]['amount'] = amount_sats
        else:
            # Create new allocation
            allocation = {
                'id': st.session_state.user_data['next_allocation_id'],
                'category_id': category_id,
                'month': month,
                'amount': amount_sats
            }
            st.session_state.user_data['allocations'].append(allocation)
            st.session_state.user_data['next_allocation_id'] += 1
        
        return True
    except Exception as e:
        st.error(f"Error allocating to category: {e}")
        return False

def delete_transaction(transaction_id):
    """Delete a transaction by ID"""
    try:
        for i, transaction in enumerate(st.session_state.user_data['transactions']):
            if transaction['id'] == transaction_id:
                del st.session_state.user_data['transactions'][i]
                return True
        return False
    except Exception as e:
        st.error(f"Error deleting transaction: {e}")
        return False

def update_transaction(transaction_id, date, description, amount, category_id=None):
    """Update a transaction"""
    try:
        for transaction in st.session_state.user_data['transactions']:
            if transaction['id'] == transaction_id:
                transaction['date'] = str(date)
                transaction['description'] = description
                transaction['amount'] = amount
                if category_id is not None:
                    transaction['category_id'] = category_id
                return True
        return False
    except Exception as e:
        st.error(f"Error updating transaction: {e}")
        return False

def delete_category(category_id):
    """Delete a category and all its associated allocations and transactions"""
    try:
        transaction_count = 0
        allocation_count = 0
        
        # Count and delete transactions
        for i in range(len(st.session_state.user_data['transactions']) - 1, -1, -1):
            if st.session_state.user_data['transactions'][i]['category_id'] == category_id:
                del st.session_state.user_data['transactions'][i]
                transaction_count += 1
        
        # Count and delete allocations
        for i in range(len(st.session_state.user_data['allocations']) - 1, -1, -1):
            if st.session_state.user_data['allocations'][i]['category_id'] == category_id:
                del st.session_state.user_data['allocations'][i]
                allocation_count += 1
        
        # Delete category
        for i, category in enumerate(st.session_state.user_data['categories']):
            if category['id'] == category_id:
                del st.session_state.user_data['categories'][i]
                break
        
        return True, transaction_count, allocation_count
    except Exception as e:
        st.error(f"Error deleting category: {e}")
        return False, 0, 0

def delete_allocation(category_id, month):
    """Delete allocation for a specific category and month"""
    try:
        for i, allocation in enumerate(st.session_state.user_data['allocations']):
            if allocation['category_id'] == category_id and allocation['month'] == month:
                del st.session_state.user_data['allocations'][i]
                return True
        return False
    except Exception as e:
        st.error(f"Error deleting allocation: {e}")
        return False

# === BUDGET LOGIC (UNCHANGED FROM ORIGINAL) ===

def get_total_income(month=None):
    """Get total income for month or all time"""
    total = 0
    
    for transaction in st.session_state.user_data['transactions']:
        if transaction['type'] == 'income':
            if month:
                # Check if transaction is in the specified month
                trans_date = transaction['date']
                if trans_date.startswith(month):
                    total += transaction['amount']
            else:
                total += transaction['amount']
    
    return total

def get_total_allocated(month):
    """Get total allocated for month"""
    total = 0
    
    for allocation in st.session_state.user_data['allocations']:
        if allocation['month'] == month:
            total += allocation['amount']
    
    return total

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
    return get_total_allocated(month)  # Same as get_total_allocated now

def get_category_spent(category_id, month):
    """Get amount spent in category for month"""
    total = 0
    
    for transaction in st.session_state.user_data['transactions']:
        if (transaction['type'] == 'expense' and 
            transaction['category_id'] == category_id and
            transaction['date'].startswith(month)):
            total += transaction['amount']
    
    return total

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
    for allocation in st.session_state.user_data['allocations']:
        if allocation['category_id'] == category_id and allocation['month'] == month:
            return allocation['amount']
    
    return 0

def get_category_balance(category_id, month):
    """Get current balance for category envelope including rollover from previous months"""
    allocated = get_category_allocated_direct(category_id, month)
    spent = get_category_spent(category_id, month)
    rollover = get_category_rollover_balance(category_id, month)
    
    return allocated + rollover - spent

def get_recent_transactions(limit=20):
    """Get recent transactions with IDs"""
    transactions = []
    
    # Sort transactions by date (most recent first)
    sorted_transactions = sorted(
        st.session_state.user_data['transactions'], 
        key=lambda x: x['date'], 
        reverse=True
    )[:limit]
    
    for transaction in sorted_transactions:
        category_name = None
        if transaction['category_id']:
            for cat in st.session_state.user_data['categories']:
                if cat['id'] == transaction['category_id']:
                    category_name = cat['name']
                    break
        
        transactions.append((
            transaction['id'],
            transaction['date'],
            transaction['description'],
            transaction['amount'],
            transaction['type'],
            category_name
        ))
    
    return transactions

def get_expense_transactions(limit=50):
    """Get recent expense transactions for lifecycle cost analysis"""
    transactions = []
    
    # Filter and sort expense transactions by date (most recent first)
    expense_transactions = [
        t for t in st.session_state.user_data['transactions'] 
        if t['type'] == 'expense'
    ]
    sorted_transactions = sorted(
        expense_transactions, 
        key=lambda x: x['date'], 
        reverse=True
    )[:limit]
    
    for transaction in sorted_transactions:
        category_name = None
        if transaction['category_id']:
            for cat in st.session_state.user_data['categories']:
                if cat['id'] == transaction['category_id']:
                    category_name = cat['name']
                    break
        
        transactions.append((
            transaction['id'],
            transaction['date'],
            transaction['description'],
            transaction['amount'],
            category_name
        ))
    
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
    """Initialize session state variables and user data"""
    if 'current_month' not in st.session_state:
        st.session_state.current_month = get_current_month()
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
    
    # Initialize user's private data structures
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'transactions': [],  # List of transaction dicts
            'categories': [],    # List of category dicts
            'master_categories': [],  # List of master category dicts
            'allocations': [],   # List of allocation dicts
            'next_transaction_id': 1,
            'next_category_id': 1,
            'next_master_category_id': 1,
            'next_allocation_id': 1
        }
        
        # Add some default master categories and categories for demo
        default_master_cats = [
            {'id': 1, 'name': 'Fixed Expenses'},
            {'id': 2, 'name': 'Variable Expenses'},
            {'id': 3, 'name': 'Savings'}
        ]
        
        default_categories = [
            {'id': 1, 'name': 'Rent', 'master_category_id': 1},
            {'id': 2, 'name': 'Food', 'master_category_id': 2},
            {'id': 3, 'name': 'Bitcoin Stack', 'master_category_id': 3}
        ]
        
        st.session_state.user_data['master_categories'] = default_master_cats
        st.session_state.user_data['categories'] = default_categories
        st.session_state.user_data['next_master_category_id'] = 4
        st.session_state.user_data['next_category_id'] = 4

def landing_page():
    """Beautiful landing page explaining how to use the Bitcoin Budget app"""
    # Hide sidebar for landing page
    st.markdown("""
        <style>
        .css-1d391kg {display: none}
        </style>
    """, unsafe_allow_html=True)
    
    # Hero section
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">₿ Bitcoin Budget</h1>
            <p style="font-size: 1.3rem; color: #666; margin-bottom: 1rem;">
                Modern envelope budgeting for Bitcoin users
            </p>
            <h2 style="font-size: 1.8rem; color: #f7931a; margin-bottom: 2rem;">
                What if you could see the long term implications<br/>of your stacking and spending?
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Show example lifecycle cost analysis with custom styling
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
             padding: 1rem 2rem; border-radius: 10px; margin: 1rem 0 1.5rem 0;">
            <h3 style="color: white; text-align: center; margin: 0; font-size: 1.3rem;">
                🍽️ Example: 10-Year Cost of Fancy Dinner out with Friends
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Create the example metrics that match the image
    example_col1, example_col2, example_col3, example_col4 = st.columns(4)
    
    with example_col1:
        st.markdown("""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #10b981; font-size: 0.8rem; margin-bottom: 0.3rem;">💸 Amount Spent</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">250,000 sats</div>
                <div style="color: #10b981; font-size: 0.8rem;">↗ $245.55</div>
            </div>
        """, unsafe_allow_html=True)
    
    with example_col2:
        st.markdown("""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #f59e0b; font-size: 0.8rem; margin-bottom: 0.3rem;">🚀 Future Value</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">$3,914.52</div>
                <div style="color: #10b981; font-size: 0.8rem;">↗ +1494.2%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with example_col3:
        st.markdown("""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #ef4444; font-size: 0.8rem; margin-bottom: 0.3rem;">💔 Opportunity Cost</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">$3,668.97</div>
                <div style="color: #ef4444; font-size: 0.8rem;">↘ -1494.2%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with example_col4:
        st.markdown("""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #8b5cf6; font-size: 0.8rem; margin-bottom: 0.3rem;">📊 Purchasing Power</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">7.4x</div>
                <div style="color: #10b981; font-size: 0.8rem;">↗ vs inflation</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Create side-by-side charts: pie chart and value comparison
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    chart_col1, chart_col2 = st.columns(2)
    
    # Left column: Opportunity Cost Pie Chart
    with chart_col1:
        st.markdown("#### 💔 Opportunity Cost Analysis")
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Opportunity Cost', 'Purchase Value'],
            values=[3668.97, 245.55],
            hole=.3,
            marker_colors=['#ef4444', '#10b981']
        )])
        
        fig_pie.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont_size=10,
            marker=dict(line=dict(color='#000000', width=2))
        )
        
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=10),
            height=280
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Right column: Value Comparison Bar Chart
    with chart_col2:
        st.markdown("#### 📊 USD Value Comparison")
        
        # Calculate inflation-adjusted value (assuming ~3% annual inflation over 10 years)
        inflation_value = 245.55 * (1.03 ** 10)  # ~$329.73
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=['Purchase Value', 'Future BTC Value', 'Purchase + Inflation'],
                y=[245.55, 3914.52, inflation_value],
                marker_color=['#ef4444', '#10b981', '#f59e0b'],
                text=[f'${245.55:.0f}', f'${3914.52:.0f}', f'${inflation_value:.0f}'],
                textposition='auto',
                textfont=dict(color='white', size=11)
            )
        ])
        
        fig_bar.update_layout(
            title='',
            xaxis=dict(
                tickfont=dict(color='white', size=9),
                gridcolor='rgba(255,255,255,0.1)',
                title=''
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=9),
                gridcolor='rgba(255,255,255,0.1)',
                title=dict(text='USD Value', font=dict(color='white', size=10))
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            showlegend=False
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    # Center the get started button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started", type="primary", use_container_width=True, key="get_started"):
            st.session_state.page = 'main'
            st.session_state.first_visit = False
            st.rerun()
    
    st.markdown("---")
    
    # Feature overview with beautiful icons and descriptions
    st.markdown("## ✨ Visualize Living on a Bitcoin Standard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            ### 🎯 **Envelope Budgeting that is Bitcoin Native**
            You live on a Bitcoin standard by earning and spending. 
            Now track your precious sats with precision and purpose.
        """)
    
    with col2:
        st.markdown("""
            ### ⚡ **Secure and Open Source**
            Manually enter your data to minimize 
            security risk. The original air gapped security with nothing to connect to. 
            Open source project, after all you don't trust, you verify.
        """)
    
    with col3:
        st.markdown("""
            ### 📊 **Smart Analytics**
            Track spending trends, opportunity costs, 
            and make data-driven decisions about your Bitcoin stack.
        """)
    
    st.markdown("---")
    
    # How it works section
    st.markdown("## 🔄 How Bitcoin Budget Works")
    
    # Visual flow - centered and full width
    flow_col1, flow_col2, flow_col3 = st.columns([1, 2, 1])
    
    with flow_col2:
        # Create a clean visual flow using Streamlit components
        
        # Step 1: Bitcoin Income
        st.markdown("""
            <div style="text-align: center; margin: 1.5rem 0;">
                <div style="background: #f59e0b; color: black; padding: 1rem 2rem; border-radius: 8px; 
                     display: inline-block; font-weight: bold; font-size: 1.1rem;">
                    Bitcoin Income
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; font-size: 2rem; color: #6b7280; margin: 1rem 0;'>↓</div>", unsafe_allow_html=True)
        
        # Step 2: Assign to Categories
        st.markdown("""
            <div style="text-align: center; margin: 1.5rem 0;">
                <div style="background: #ef4444; color: white; padding: 1rem 2rem; border-radius: 8px; 
                     display: inline-block; font-weight: bold; font-size: 1.1rem;">
                    Assign to Categories
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; font-size: 2rem; color: #6b7280; margin: 1rem 0;'>↓</div>", unsafe_allow_html=True)
        
        # Step 3: Category Cards
        cat_col1, cat_col2, cat_col3 = st.columns(3)
        
        with cat_col1:
            st.markdown("""
                <div style="background: #1e40af; color: white; padding: 1.2rem; border-radius: 8px; text-align: center; margin: 0.2rem;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem; font-size: 1rem;">Rent</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">50,000 sats</div>
                </div>
            """, unsafe_allow_html=True)
        
        with cat_col2:
            st.markdown("""
                <div style="background: #dc2626; color: white; padding: 1.2rem; border-radius: 8px; text-align: center; margin: 0.2rem;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem; font-size: 1rem;">Food</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">25,000 sats</div>
                </div>
            """, unsafe_allow_html=True)
        
        with cat_col3:
            st.markdown("""
                <div style="background: #f59e0b; color: black; padding: 1.2rem; border-radius: 8px; text-align: center; margin: 0.2rem;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem; font-size: 1rem;">Savings Stack</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">25,000 sats</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; font-size: 2rem; color: #6b7280; margin: 1.5rem 0;'>↓</div>", unsafe_allow_html=True)
        
        # Step 4: Track Spending
        st.markdown("""
            <div style="text-align: center; margin: 1.5rem 0;">
                <div style="background: #10b981; color: white; padding: 1rem 2rem; border-radius: 8px; 
                     display: inline-block; font-weight: bold; font-size: 1.1rem;">
                    Track Spending & Stay on Budget
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")    
   
    # Getting started guide
    st.markdown("## 🚀 Quick Start Guide")
    
    with st.expander("📖 Step-by-Step Tutorial", expanded=False):
        st.markdown("""
            ### Step 1: Add Your First Income 💰
            1. Click "Get Started" to enter the app
            2. Go to the "Transactions" tab
            3. Click "Add Income" in the Income section
            4. Enter amount in satoshis (e.g., 1000000 for 0.01 BTC)
            5. Add a description like "Freelance payment"
            
            ### Step 2: Create Spending Categories 📁
            1. Go to the "Categories" tab
            2. Click "Add Master Category" (e.g., "Fixed Expenses")
            3. Click "Add Category" and assign to master category
            4. Create categories like: Rent, Food, Transportation, Bitcoin Savings
            
            ### Step 3: Allocate Your Income 🎯
            1. In the Categories section, you'll see "Available to Assign"
            2. Click the allocate button for each category
            3. Assign portions of your income to different envelopes
            4. Make sure "Available to Assign" reaches zero
            
            ### Step 4: Track Your Spending 💸
            1. When you spend Bitcoin, add an expense
            2. Choose the correct category
            3. Watch your category balances update
            4. Get warnings when you overspend a category
            
            ### Step 5: Analyze Your Budget 📊
            1. Click "Reports" in the sidebar
            2. View spending breakdowns and trends
            3. See opportunity cost analysis
            4. Make better Bitcoin decisions
        """)
    
    # Sample data section
    with st.expander("📋 Example Budget Layout", expanded=False):
        st.markdown("""
            Here's what a typical Bitcoin budget might look like:
            
            **Monthly Income:** 5,000,000 sats (0.05 BTC)
            
            **Master Categories:**
            
            📊 **Fixed Expenses** - 3,000,000 sats
            - 🏠 Rent: 2,000,000 sats
            - 📱 Phone: 500,000 sats  
            - 🌐 Internet: 300,000 sats
            - 💡 Utilities: 200,000 sats
            
            📊 **Variable Expenses** - 1,500,000 sats
            - 🍕 Food: 800,000 sats
            - 🚗 Transportation: 400,000 sats
            - 🎮 Entertainment: 300,000 sats
            
            📊 **Savings & Investments** - 500,000 sats
            - ⚡ Bitcoin Stack: 300,000 sats
            - 🏦 Emergency Fund: 200,000 sats
        """)
    
    st.markdown("---")
    
    # FAQ section
    st.markdown("## ❓ Frequently Asked Questions")
    
    faq_col1, faq_col2 = st.columns(2)
    
    with faq_col1:
        with st.expander("Why use envelope budgeting?"):
            st.markdown("""
                **Envelope budgeting ensures every satoshi has a purpose.**
                
                Instead of wondering "can I afford this?", you'll know exactly 
                how much you have allocated for each spending category. This 
                prevents overspending and helps you stick to your Bitcoin 
                savings goals.
            """)
        
        with st.expander("How do I handle Bitcoin volatility?"):
            st.markdown("""
                **Budget in satoshis, not fiat value.**
                
                This app works in satoshis, so your budget remains consistent 
                regardless of Bitcoin's USD price. You're budgeting your actual 
                Bitcoin, not its fiat equivalent.
            """)
    
    with faq_col2:
        with st.expander("What if I overspend a category?"):
            st.markdown("""
                **The app will warn you, but won't stop you.**
                
                If you overspend, the category balance goes negative. You can 
                either move money from another category or reduce spending 
                to get back on track.
            """)
        
        with st.expander("Can I use this for fiat expenses?"):
            st.markdown("""
                **Absolutely! Convert fiat to sats when entering.**
                
                If you spend $50 on groceries, convert that to satoshis at 
                the current rate and enter it as an expense. This gives you 
                a Bitcoin-native view of all your spending.
            """)
    
    st.markdown("---")
    
    # Call to action
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #f7931a 0%, #ffb84d 100%); 
             border-radius: 10px; margin: 2rem 0;">
            <h3 style="color: white; margin-bottom: 1rem;">Ready to take control of your Bitcoin budget?</h3>
            <p style="color: white; margin-bottom: 1.5rem;">Start your journey to better Bitcoin financial management today!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Final CTA button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Budgeting Now", type="primary", use_container_width=True, key="start_budgeting"):
            st.session_state.page = 'main'
            st.session_state.first_visit = False
            st.rerun()
    
    # Security notice
    st.info("🔒 **Privacy Notice**: Your data is stored securely in your browser session only. Each user has their own private data that is not shared with others. Data persists during your session but will be lost when you close your browser.")

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
                                        category_id = None
                                        for cat in st.session_state.user_data['categories']:
                                            if cat['name'] == new_category:
                                                category_id = cat['id']
                                                break
                                        
                                        if category_id:
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
                            try:
                                for i, mc in enumerate(st.session_state.user_data['master_categories']):
                                    if mc['id'] == master_id:
                                        del st.session_state.user_data['master_categories'][i]
                                        break
                                
                                st.success(f"✅ Deleted master category: {selected_master_to_delete}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to delete master category: {e}")
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
        
        transactions = get_recent_transactions(50)  # Get more transactions for editing
        
        if transactions:
            # Get all categories for dropdown options
            all_categories = get_categories()
            category_options = ['Income'] + [cat['name'] for cat in all_categories]
            
            # Convert to dataframe with proper data types for editing
            trans_data = []
            for trans in transactions:
                trans_id, date_str, desc, amount, trans_type, category = trans
                
                # Determine category for display
                if trans_type == 'income':
                    category_display = "Income"
                else:
                    category_display = category or "Unknown"
                
                trans_data.append({
                    'ID': trans_id,
                    'Date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                    'Description': desc,
                    'Amount': amount,  # Store as raw number for editing
                    'Category': category_display,
                    'Type': trans_type,  # Keep track of original type
                    'Original_Category_ID': trans[0] if trans_type == 'expense' else None  # For reference
                })
            
            df = pd.DataFrame(trans_data)
            
            # Display editable transactions table
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": None,  # Hide ID column
                    "Type": None,  # Hide type column
                    "Original_Category_ID": None,  # Hide original category ID
                    "Date": st.column_config.DateColumn(
                        "Date",
                        help="Click to edit transaction date",
                        format="YYYY-MM-DD"
                    ),
                    "Description": st.column_config.TextColumn(
                        "Description",
                        help="Click to edit transaction description",
                        width="large"
                    ),
                    "Amount": st.column_config.NumberColumn(
                        "Amount (sats)",
                        help="Click to edit amount in satoshis",
                        min_value=1,
                        step=1,
                        format="%d"
                    ),
                    "Category": st.column_config.SelectboxColumn(
                        "Category",
                        help="Click to change transaction category",
                        options=category_options
                    )
                },
                key="transactions_editor"
            )
            
            # Process transaction edits
            if not edited_df.equals(df):
                changes_made = False
                for idx, row in edited_df.iterrows():
                    transaction_id = row['ID']
                    original_row = df.iloc[idx]
                    
                    # Check if any fields changed
                    date_changed = row['Date'] != original_row['Date']
                    desc_changed = row['Description'] != original_row['Description']
                    amount_changed = row['Amount'] != original_row['Amount']
                    category_changed = row['Category'] != original_row['Category']
                    
                    if date_changed or desc_changed or amount_changed or category_changed:
                        # Determine if this is income or expense based on category
                        new_category = row['Category']
                        new_date = str(row['Date'])
                        new_description = row['Description']
                        new_amount = int(row['Amount'])
                        
                        if new_category == 'Income':
                            # Income transaction
                            if update_transaction(transaction_id, new_date, new_description, new_amount):
                                st.success(f"✅ Updated income: {new_description}")
                                changes_made = True
                            else:
                                st.error(f"❌ Failed to update income: {new_description}")
                        else:
                            # Expense transaction - find category ID
                            category_id = None
                            for cat in all_categories:
                                if cat['name'] == new_category:
                                    category_id = cat['id']
                                    break
                            
                            if category_id:
                                if update_transaction(transaction_id, new_date, new_description, new_amount, category_id):
                                    st.success(f"✅ Updated expense: {new_description}")
                                    changes_made = True
                                else:
                                    st.error(f"❌ Failed to update expense: {new_description}")
                            else:
                                st.error(f"❌ Invalid category: {new_category}")
                
                if changes_made:
                    st.rerun()
            
            # Enhanced delete functionality
            st.markdown("---")
            st.markdown("#### 🗑️ Delete Transactions")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create options for deletion dropdown
                delete_options = []
                delete_mapping = {}
                
                for trans in transactions:
                    trans_id, date_str, desc, amount, trans_type, category = trans
                    
                    if trans_type == 'income':
                        display_text = f"{date_str} | Income | {desc} | +{format_sats(amount)}"
                        emoji = "💰"
                    else:
                        category_name = category or "Unknown"
                        display_text = f"{date_str} | {category_name} | {desc} | -{format_sats(amount)}"
                        emoji = "💸"
                    
                    option = f"{emoji} {display_text}"
                    delete_options.append(option)
                    delete_mapping[option] = trans_id
                
                selected_for_deletion = st.selectbox(
                    "Select Transaction to Delete",
                    delete_options,
                    key="delete_transaction_select"
                )
            
            with col2:
                if st.button("🗑️ Delete Transaction", key="delete_transaction_btn", type="secondary"):
                    if selected_for_deletion:
                        transaction_id = delete_mapping[selected_for_deletion]
                        if delete_transaction(transaction_id):
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
        
        if st.button("📖 How to Use", use_container_width=True):
            st.session_state.page = 'landing'
            st.rerun()
        
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
    
    # Show sidebar only when not on landing page
    if st.session_state.page != 'landing':
        sidebar_navigation()
    
    # Page routing
    if st.session_state.page == 'landing':
        landing_page()
    elif st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'reports':
        # Import and show reports page
        from modules import reports
        reports.show()

if __name__ == "__main__":
    main() 
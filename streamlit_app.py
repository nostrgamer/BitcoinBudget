#!/usr/bin/env python3
"""
Bitcoin Budget - Streamlit Web Application
Modern web-based envelope budgeting for Bitcoin users
"""
# Force preview refresh

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# === STREAMLIT PAGE CONFIG ===
st.set_page_config(
    page_title="Bitcoin Budget - Modern envelope budgeting for Bitcoin users",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add mobile-optimized CSS and meta tags
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Modern envelope budgeting app for Bitcoin users. Track your sats, manage spending categories, and visualize your Bitcoin stack's future value with inflation-adjusted projections.">
<meta name="keywords" content="bitcoin, budget, envelope budgeting, sats, cryptocurrency, financial planning, DCA, hodl">
<meta property="og:title" content="Bitcoin Budget - Modern envelope budgeting for Bitcoin users">
<meta property="og:description" content="Track your sats, manage spending categories, and visualize your Bitcoin stack's future value. See how 1M sats + 250k sats/month DCA becomes 61M sats in 20 years.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://bitcoinbudget.streamlit.app/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Bitcoin Budget - Modern envelope budgeting for Bitcoin users">
<meta name="twitter:description" content="Track your sats, manage spending categories, and visualize your Bitcoin stack's future value with inflation-adjusted projections.">
""", unsafe_allow_html=True)

# === MOBILE RESPONSIVENESS UTILITIES ===

def is_mobile_layout():
    """Detect if mobile layout should be used (based on user preference)"""
    # Initialize mobile preference in session state
    if 'mobile_mode' not in st.session_state:
        st.session_state.mobile_mode = False
    return st.session_state.mobile_mode

def get_responsive_columns(desktop_cols, mobile_cols=None):
    """Get responsive column layout based on mobile detection"""
    if mobile_cols is None:
        # Default mobile behavior: halve the columns (minimum 1)
        mobile_cols = max(1, desktop_cols // 2)
    
    if is_mobile_layout():
        return mobile_cols
    else:
        return desktop_cols

def mobile_friendly_metrics(metrics_data, mobile_stack=True):
    """Display metrics in mobile-friendly layout"""
    if is_mobile_layout() and mobile_stack and len(metrics_data) > 2:
        # Stack metrics in pairs for mobile
        for i in range(0, len(metrics_data), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(metrics_data):
                    metric = metrics_data[i + j]
                    with col:
                        st.metric(**metric)
    else:
        # Regular column layout
        num_cols = get_responsive_columns(len(metrics_data))
        cols = st.columns(num_cols)
        for i, (col, metric) in enumerate(zip(cols, metrics_data)):
            with col:
                st.metric(**metric)

def mobile_responsive_header(text, level=3):
    """Display headers that are smaller on mobile devices"""
    if is_mobile_layout():
        # Mobile: One level smaller (### becomes ####, ## becomes ###, etc.)
        mobile_level = min(level + 1, 6)  # Cap at h6
        mobile_prefix = "#" * mobile_level
        st.markdown(f"{mobile_prefix} {text}")
    else:
        # Desktop: Use original level
        desktop_prefix = "#" * level
        st.markdown(f"{desktop_prefix} {text}")

# === UX ENHANCEMENT FUNCTIONS ===

def show_loading_spinner(message="Processing..."):
    """Show a loading spinner with message"""
    return st.empty().info(f"⏳ {message}")

def show_success_toast(message, auto_clear=True):
    """Show a success toast notification with Bitcoin styling"""
    placeholder = st.empty()
    placeholder.markdown(f"""
        <div style="background: linear-gradient(90deg, #10b981 0%, #059669 100%); 
             color: white; padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0;
             box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2); border-left: 4px solid #047857;">
            <strong>✅ Success!</strong> {message}
        </div>
    """, unsafe_allow_html=True)
    
    if auto_clear:
        # Clear after 3 seconds using JavaScript
        import time
        time.sleep(0.1)  # Brief pause to let user see the message
    
    return placeholder

def show_error_toast(message):
    """Show an error toast notification with Bitcoin styling"""
    return st.markdown(f"""
        <div style="background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%); 
             color: white; padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0;
             box-shadow: 0 4px 6px rgba(239, 68, 68, 0.2); border-left: 4px solid #b91c1c;">
            <strong>❌ Error!</strong> {message}
        </div>
    """, unsafe_allow_html=True)

def show_warning_toast(message):
    """Show a warning toast notification with Bitcoin styling"""
    return st.markdown(f"""
        <div style="background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); 
             color: white; padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0;
             box-shadow: 0 4px 6px rgba(245, 158, 11, 0.2); border-left: 4px solid #b45309;">
            <strong>⚠️ Warning!</strong> {message}
        </div>
    """, unsafe_allow_html=True)

def show_info_toast(message):
    """Show an info toast notification with Bitcoin styling"""
    return st.markdown(f"""
        <div style="background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); 
             color: white; padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0;
             box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2); border-left: 4px solid #1d4ed8;">
            <strong>ℹ️ Info:</strong> {message}
        </div>
    """, unsafe_allow_html=True)

def show_bitcoin_toast(message, toast_type="success"):
    """Show a Bitcoin-themed toast notification"""
    colors = {
        "success": {"bg": "#10b981", "border": "#047857", "icon": "✅"},
        "error": {"bg": "#ef4444", "border": "#b91c1c", "icon": "❌"},
        "warning": {"bg": "#f7931a", "border": "#d97706", "icon": "⚠️"},  # Bitcoin orange
        "info": {"bg": "#3b82f6", "border": "#1d4ed8", "icon": "ℹ️"}
    }
    
    color = colors.get(toast_type, colors["success"])
    
    return st.markdown(f"""
        <div style="background: {color['bg']}; color: white; padding: 0.75rem 1rem; 
             border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid {color['border']};
             box-shadow: 0 4px 6px rgba(247, 147, 26, 0.2);">
            <strong>{color['icon']} {message}</strong>
        </div>
    """, unsafe_allow_html=True)

def with_loading_state(operation_func, loading_message="Processing...", *args, **kwargs):
    """Execute a function with loading state management"""
    # Show loading spinner
    loading_placeholder = st.empty()
    loading_placeholder.info(f"⏳ {loading_message}")
    
    try:
        # Execute the operation
        result = operation_func(*args, **kwargs)
        
        # Clear loading state
        loading_placeholder.empty()
        
        return result
    except Exception as e:
        # Clear loading state and show error
        loading_placeholder.empty()
        show_error_toast(f"Operation failed: {str(e)}")
        return None

# === PHASE 1: ENHANCED SESSION PERSISTENCE + EXPORT/IMPORT ===

import json
from datetime import datetime

def export_budget_data():
    """Export user budget data as JSON file"""
    try:
        if 'user_data' in st.session_state:
            # Add metadata
            export_data = {
                'version': '1.0',
                'export_date': datetime.now().isoformat(),
                'app_name': 'Bitcoin Budget',
                'data': st.session_state.user_data
            }
            
            # Convert to JSON
            json_data = json.dumps(export_data, indent=2, default=str)
            return json_data
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        return None

def import_budget_data(json_data):
    """Import user budget data from JSON string"""
    try:
        # Parse JSON
        imported_data = json.loads(json_data)
        
        # Validate structure
        if 'data' not in imported_data:
            return False, "Invalid file format - missing data section"
        
        data = imported_data['data']
        required_keys = ['transactions', 'categories', 'master_categories', 'allocations', 'accounts']
        
        for key in required_keys:
            if key not in data:
                return False, f"Invalid file format - missing {key}"
        
        # Import the data
        st.session_state.user_data = data
        
        # Ensure next_id fields exist
        if 'next_transaction_id' not in st.session_state.user_data:
            st.session_state.user_data['next_transaction_id'] = max([t.get('id', 0) for t in data['transactions']] + [0]) + 1
        if 'next_category_id' not in st.session_state.user_data:
            st.session_state.user_data['next_category_id'] = max([c.get('id', 0) for c in data['categories']] + [0]) + 1
        if 'next_master_category_id' not in st.session_state.user_data:
            st.session_state.user_data['next_master_category_id'] = max([mc.get('id', 0) for mc in data['master_categories']] + [0]) + 1
        if 'next_allocation_id' not in st.session_state.user_data:
            st.session_state.user_data['next_allocation_id'] = max([a.get('id', 0) for a in data['allocations']] + [0]) + 1
        if 'next_account_id' not in st.session_state.user_data:
            st.session_state.user_data['next_account_id'] = max([acc.get('id', 0) for acc in data['accounts']] + [0]) + 1
        
        return True, "Budget data imported successfully!"
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {e}"
    except Exception as e:
        return False, f"Error importing data: {e}"

def get_demo_data():
    """Get default demo data structure with realistic budget"""
    current_month = get_current_month()
    
    default_master_cats = [
        {'id': 1, 'name': 'Fixed Expenses'},
        {'id': 2, 'name': 'Variable Expenses'},
        {'id': 3, 'name': 'Savings & Goals'},
        {'id': 4, 'name': 'Fun & Entertainment'}
    ]
    
    default_categories = [
        # Fixed Expenses
        {'id': 1, 'name': 'Rent/Mortgage', 'master_category_id': 1},
        {'id': 2, 'name': 'Phone & Internet', 'master_category_id': 1},
        {'id': 3, 'name': 'Insurance', 'master_category_id': 1},
        {'id': 4, 'name': 'Utilities', 'master_category_id': 1},
        
        # Variable Expenses
        {'id': 5, 'name': 'Groceries', 'master_category_id': 2},
        {'id': 6, 'name': 'Gas & Transportation', 'master_category_id': 2},
        {'id': 7, 'name': 'Restaurants', 'master_category_id': 2},
        {'id': 8, 'name': 'Personal Care', 'master_category_id': 2},
        {'id': 9, 'name': 'Clothing', 'master_category_id': 2},
        
        # Savings & Goals
        {'id': 10, 'name': 'Bitcoin Stack', 'master_category_id': 3},
        {'id': 11, 'name': 'Emergency Fund', 'master_category_id': 3},
        {'id': 12, 'name': 'Vacation Fund', 'master_category_id': 3},
        
        # Fun & Entertainment
        {'id': 13, 'name': 'Entertainment', 'master_category_id': 4},
        {'id': 14, 'name': 'Hobbies', 'master_category_id': 4}
    ]
    
    demo_transactions = [
        # Income
        {
            'id': 1,
            'date': current_month + '-01',
            'description': 'Salary',
            'amount': 11400000,  # 11.4M sats (~$8,000)
            'type': 'income',
            'category_id': None,
            'account_id': 1
        },
        {
            'id': 2,
            'date': current_month + '-15',
            'description': 'Freelance Work',
            'amount': 2860000,  # 2.86M sats (~$2,000)
            'type': 'income',
            'category_id': None,
            'account_id': 1
        },
        
        # Fixed Expenses
        {
            'id': 3,
            'date': current_month + '-01',
            'description': 'Rent Payment',
            'amount': 4285000,  # 4.29M sats (~$3,000)
            'type': 'expense',
            'category_id': 1,
            'account_id': 1
        },
        {
            'id': 4,
            'date': current_month + '-05',
            'description': 'Phone & Internet Bill',
            'amount': 143000,  # 143k sats (~$100)
            'type': 'expense',
            'category_id': 2,
            'account_id': 1
        },
        {
            'id': 5,
            'date': current_month + '-10',
            'description': 'Car Insurance',
            'amount': 428000,  # 428k sats (~$300)
            'type': 'expense',
            'category_id': 3,
            'account_id': 1
        },
        {
            'id': 6,
            'date': current_month + '-12',
            'description': 'Electric Bill',
            'amount': 286000,  # 286k sats (~$200)
            'type': 'expense',
            'category_id': 4,
            'account_id': 1
        },
        
        # Variable Expenses
        {
            'id': 7,
            'date': current_month + '-03',
            'description': 'Grocery Shopping',
            'amount': 214000,  # 214k sats (~$150)
            'type': 'expense',
            'category_id': 5,
            'account_id': 1
        },
        {
            'id': 8,
            'date': current_month + '-07',
            'description': 'Gas Station',
            'amount': 71000,  # 71k sats (~$50)
            'type': 'expense',
            'category_id': 6,
            'account_id': 1
        },
        {
            'id': 9,
            'date': current_month + '-14',
            'description': 'Restaurant Dinner',
            'amount': 86000,  # 86k sats (~$60)
            'type': 'expense',
            'category_id': 7,
            'account_id': 1
        },
        {
            'id': 10,
            'date': current_month + '-08',
            'description': 'Haircut',
            'amount': 57000,  # 57k sats (~$40)
            'type': 'expense',
            'category_id': 8,
            'account_id': 1
        },
        {
            'id': 11,
            'date': current_month + '-16',
            'description': 'Grocery Shopping',
            'amount': 286000,  # 286k sats (~$200)
            'type': 'expense',
            'category_id': 5,
            'account_id': 1
        },
        
        # Fun & Entertainment
        {
            'id': 12,
            'date': current_month + '-09',
            'description': 'Movie Tickets',
            'amount': 43000,  # 43k sats (~$30)
            'type': 'expense',
            'category_id': 13,
            'account_id': 1
        },
        {
            'id': 13,
            'date': current_month + '-18',
            'description': 'Book Purchase',
            'amount': 36000,  # 36k sats (~$25)
            'type': 'expense',
            'category_id': 14,
            'account_id': 1
        }
    ]
    
    demo_allocations = [
        # Fixed Expenses - allocated for full amounts
        {'id': 1, 'category_id': 1, 'month': current_month, 'amount': 4300000},   # Rent (~$3,000)
        {'id': 2, 'category_id': 2, 'month': current_month, 'amount': 150000},    # Phone (~$100)
        {'id': 3, 'category_id': 3, 'month': current_month, 'amount': 430000},    # Insurance (~$300)
        {'id': 4, 'category_id': 4, 'month': current_month, 'amount': 290000},    # Utilities (~$200)
        
        # Variable Expenses - allocated for expected amounts
        {'id': 5, 'category_id': 5, 'month': current_month, 'amount': 1070000},   # Groceries (~$750)
        {'id': 6, 'category_id': 6, 'month': current_month, 'amount': 290000},    # Gas (~$200)
        {'id': 7, 'category_id': 7, 'month': current_month, 'amount': 430000},    # Restaurants (~$300)
        {'id': 8, 'category_id': 8, 'month': current_month, 'amount': 140000},    # Personal Care (~$100)
        {'id': 9, 'category_id': 9, 'month': current_month, 'amount': 290000},    # Clothing (~$200)
        
        # Savings & Goals  
        {'id': 10, 'category_id': 10, 'month': current_month, 'amount': 4300000}, # Bitcoin Stack (~$3,000)
        {'id': 11, 'category_id': 11, 'month': current_month, 'amount': 1430000}, # Emergency Fund (~$1,000)
        {'id': 12, 'category_id': 12, 'month': current_month, 'amount': 570000},  # Vacation Fund (~$400)
        
        # Fun & Entertainment
        {'id': 13, 'category_id': 13, 'month': current_month, 'amount': 290000},  # Entertainment (~$200)
        {'id': 14, 'category_id': 14, 'month': current_month, 'amount': 140000}   # Hobbies (~$100)
    ]
    
    demo_accounts = [
        {
            'id': 1,
            'name': 'Checking Account',
            'balance': 8740000,  # Reflects income minus expenses (~$6,100)
            'is_tracked': True,
            'account_type': 'checking'
        },
        {
            'id': 2,
            'name': 'Bitcoin Cold Storage',
            'balance': 71400000,  # 71.4M sats long-term savings (~$50k)
            'is_tracked': False,
            'account_type': 'savings'
        },
        {
            'id': 3,
            'name': 'Emergency Cash',
            'balance': 14300000,  # 14.3M sats emergency fund (~$10k)
            'is_tracked': False,
            'account_type': 'savings'
        }
    ]
    
    return {
        'transactions': demo_transactions,
        'categories': default_categories,
        'master_categories': default_master_cats,
        'allocations': demo_allocations,
        'accounts': demo_accounts,
        'next_transaction_id': 14,
        'next_category_id': 15,
        'next_master_category_id': 5,
        'next_allocation_id': 15,
        'next_account_id': 4
    }

def get_fresh_data():
    """Get empty data structure for fresh start"""
    current_month = get_current_month()
    
    return {
        'transactions': [],
        'categories': [],
        'master_categories': [],
        'allocations': [],
        'accounts': [],
        'next_transaction_id': 1,
        'next_category_id': 1,
        'next_master_category_id': 1,
        'next_allocation_id': 1,
        'next_account_id': 1
    }

# === DATA FUNCTIONS (NO CHANGES NEEDED - ALREADY SESSION-BASED) ===



def add_income(amount_sats, description, transaction_date, account_id=None):
    """Add income transaction"""
    try:
        transaction = {
            'id': st.session_state.user_data['next_transaction_id'],
            'date': str(transaction_date),
            'description': description,
            'amount': amount_sats,
            'type': 'income',
            'category_id': None,
            'account_id': account_id
        }
        st.session_state.user_data['transactions'].append(transaction)
        st.session_state.user_data['next_transaction_id'] += 1
        
        # Update account balance if account is specified
        if account_id:
            for account in st.session_state.user_data['accounts']:
                if account['id'] == account_id:
                    account['balance'] += amount_sats
                    break
        
        return True
    except Exception as e:
        st.error(f"Error adding income: {e}")
        return False

def add_expense(amount_sats, description, category_id, transaction_date, account_id=None):
    """Add expense transaction"""
    try:
        transaction = {
            'id': st.session_state.user_data['next_transaction_id'],
            'date': str(transaction_date),
            'description': description,
            'amount': amount_sats,
            'type': 'expense',
            'category_id': category_id,
            'account_id': account_id
        }
        st.session_state.user_data['transactions'].append(transaction)
        st.session_state.user_data['next_transaction_id'] += 1
        
        # Update account balance if account is specified
        if account_id:
            for account in st.session_state.user_data['accounts']:
                if account['id'] == account_id:
                    account['balance'] -= amount_sats
                    break
        
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
        # Ensure category_id is always an integer (fix for data type issues)
        category_id = int(category_id)
        
        # Find existing allocation for this category and month
        existing_allocation = None
        for i, alloc in enumerate(st.session_state.user_data['allocations']):
            # Compare with both int and string versions to handle existing bad data
            if (int(alloc['category_id']) == category_id and alloc['month'] == month):
                existing_allocation = i
                break
        
        if existing_allocation is not None:
            # Update existing allocation and ensure category_id is integer
            st.session_state.user_data['allocations'][existing_allocation]['amount'] = amount_sats
            st.session_state.user_data['allocations'][existing_allocation]['category_id'] = category_id
        else:
            # Create new allocation with integer category_id
            allocation = {
                'id': st.session_state.user_data['next_allocation_id'],
                'category_id': category_id,  # Ensure this is an integer
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

def update_transaction(transaction_id, date, description, amount, category_id=None, account_id=None):
    """Update a transaction"""
    try:
        for transaction in st.session_state.user_data['transactions']:
            if transaction['id'] == transaction_id:
                transaction['date'] = str(date)
                transaction['description'] = description
                transaction['amount'] = amount
                if category_id is not None:
                    transaction['category_id'] = category_id
                if account_id is not None:
                    transaction['account_id'] = account_id
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

def get_category_allocated_direct(category_id, month):
    """Get amount allocated to category for month without rollover logic"""
    for allocation in st.session_state.user_data['allocations']:
        if allocation['category_id'] == category_id and allocation['month'] == month:
            return allocation['amount']
    
    return 0

def get_category_balance(category_id, month):
    """Get current balance for category envelope (account-based approach)"""
    # Get all allocations ever made to this category
    total_allocated = 0
    for allocation in st.session_state.user_data['allocations']:
        if allocation['category_id'] == category_id:
            # Only count allocations up to and including the current month
            if allocation['month'] <= month:
                total_allocated += allocation['amount']
    
    # Get all spending ever from this category
    total_spent = 0
    for transaction in st.session_state.user_data['transactions']:
        if (transaction['type'] == 'expense' and 
            transaction['category_id'] == category_id and
            transaction['date'][:7] <= month):  # transaction date <= month
            total_spent += transaction['amount']
    
    return total_allocated - total_spent

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

def get_all_transactions():
    """Get ALL transactions with IDs (no limit)"""
    transactions = []
    
    # Sort transactions by date (most recent first)
    sorted_transactions = sorted(
        st.session_state.user_data['transactions'], 
        key=lambda x: x['date'], 
        reverse=True
    )
    
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

# === ACCOUNT FUNCTIONS ===

def add_account(name, initial_balance, is_tracked=True, account_type='checking'):
    """Add a new account"""
    try:
        # Check for duplicate name
        for acc in st.session_state.user_data['accounts']:
            if acc['name'] == name:
                return False  # Duplicate name
        
        account = {
            'id': st.session_state.user_data['next_account_id'],
            'name': name,
            'balance': initial_balance,
            'is_tracked': is_tracked,
            'account_type': account_type
        }
        st.session_state.user_data['accounts'].append(account)
        st.session_state.user_data['next_account_id'] += 1
        return True
    except Exception:
        return False

def get_accounts():
    """Get all accounts"""
    return st.session_state.user_data['accounts'].copy()

def get_tracked_accounts():
    """Get only tracked (on-budget) accounts"""
    return [acc for acc in st.session_state.user_data['accounts'] if acc['is_tracked']]

def get_untracked_accounts():
    """Get only untracked (off-budget) accounts"""
    return [acc for acc in st.session_state.user_data['accounts'] if not acc['is_tracked']]

def get_account_balance(account_id):
    """Get current balance for an account"""
    for account in st.session_state.user_data['accounts']:
        if account['id'] == account_id:
            return account['balance']
    return 0

def update_account_balance(account_id, new_balance):
    """Update account balance"""
    try:
        for account in st.session_state.user_data['accounts']:
            if account['id'] == account_id:
                account['balance'] = new_balance
                return True
        return False
    except Exception:
        return False

def update_account(account_id, new_balance=None, new_type=None, new_name=None):
    """Update account with multiple fields"""
    try:
        for account in st.session_state.user_data['accounts']:
            if account['id'] == account_id:
                if new_balance is not None:
                    account['balance'] = new_balance
                if new_type is not None:
                    account['account_type'] = new_type
                if new_name is not None:
                    account['name'] = new_name
                return True
        return False
    except Exception:
        return False

def transfer_between_accounts(from_account_id, to_account_id, amount):
    """Transfer money between accounts"""
    try:
        from_account = None
        to_account = None
        
        for account in st.session_state.user_data['accounts']:
            if account['id'] == from_account_id:
                from_account = account
            elif account['id'] == to_account_id:
                to_account = account
        
        if from_account and to_account and from_account['balance'] >= amount:
            from_account['balance'] -= amount
            to_account['balance'] += amount
            return True
        return False
    except Exception:
        return False

def get_total_account_balance(tracked_only=True):
    """Get total balance across accounts"""
    total = 0
    for account in st.session_state.user_data['accounts']:
        if not tracked_only or account['is_tracked']:
            total += account['balance']
    return total

def get_total_category_balances_current():
    """Get current total money in all categories (all allocations minus all spending)"""
    total = 0
    categories = get_categories()
    for category in categories:
        # Get ALL allocations ever made to this category (no month filter)
        total_allocated = 0
        for allocation in st.session_state.user_data['allocations']:
            if int(allocation['category_id']) == int(category['id']):
                total_allocated += allocation['amount']
        
        # Get ALL spending ever from this category (no month filter)
        total_spent = 0
        for transaction in st.session_state.user_data['transactions']:
            if (transaction['type'] == 'expense' and 
                transaction['category_id'] == category['id']):
                total_spent += transaction['amount']
        
        category_balance = total_allocated - total_spent
        if category_balance > 0:  # Only count positive balances
            total += category_balance
    
    return total

def get_total_category_balances(month):
    """Get total money currently in all categories"""
    total = 0
    categories = get_categories()
    for category in categories:
        balance = get_category_balance(category['id'], month)
        if balance > 0:  # Only count positive balances
            total += balance
    return total

def get_unaccounted_income(month=None):
    """Get income that's not tied to any account"""
    total_income = get_total_income(month)
    
    # Get income that IS tied to accounts
    accounted_income = 0
    for trans in st.session_state.user_data['transactions']:
        if trans['type'] == 'income' and 'account_id' in trans and trans['account_id']:
            if month is None or trans['date'].startswith(month):
                accounted_income += trans['amount']
    
    return total_income - accounted_income

def delete_account(account_id):
    """Delete an account (only if no transactions reference it)"""
    try:
        # Check if any transactions reference this account
        for trans in st.session_state.user_data['transactions']:
            if 'account_id' in trans and trans['account_id'] == account_id:
                return False  # Cannot delete account with transactions
        
        # Remove the account
        st.session_state.user_data['accounts'] = [
            acc for acc in st.session_state.user_data['accounts'] 
            if acc['id'] != account_id
        ]
        return True
    except Exception:
        return False

# === UTILITY FUNCTIONS (UNCHANGED FROM ORIGINAL) ===

def format_sats(satoshis):
    """Format satoshis for display"""
    return f"{satoshis:,} sats"

def format_btc(satoshis):
    """Format as BTC"""
    btc = satoshis / 100_000_000
    return f"{btc:.8f} BTC"

def parse_amount_input(text):
    """Parse user input to satoshis - sats only, no BTC (rejecting BIP 178)"""
    text = text.strip().replace(',', '')
    
    if not text:
        raise ValueError("Amount cannot be empty")
    
    # Reject BTC input completely (formally rejecting BIP 178)
    if 'btc' in text.lower():
        raise ValueError("BTC input not supported. Please enter amount in satoshis only.")
    
    try:
        result = int(float(text))
        if result < 0:
            raise ValueError("Amount must be positive")
        
        # Check for reasonable limits
        if result > 21_000_000 * 100_000_000:  # More than total Bitcoin supply
            raise ValueError("Amount too large - exceeds total Bitcoin supply")
        
        return result
    except (ValueError, TypeError) as e:
        if "could not convert" in str(e).lower() or "invalid literal" in str(e).lower():
            raise ValueError("Invalid number format. Enter satoshis as numbers only (e.g., 1,000,000)")
        raise e

def validate_amount_input(text):
    """Validate amount input and return (is_valid, message, formatted_preview)"""
    if not text:
        return False, "", ""
    
    try:
        amount_sats = parse_amount_input(text)
        formatted = format_sats(amount_sats)
        return True, f"✅ Valid amount", f"{formatted}"
    except ValueError as e:
        return False, f"❌ {str(e)}", ""



def get_account_type_icon(account_type):
    """Get icon for account type"""
    icons = {
        'checking': '🏦',
        'savings': '💰', 
        'investment': '📈',
        'credit': '💳',
        'loan': '🏠',
        'cold_storage': '🧊',
        'lightning_node': '⚡',
        'hot_wallet': '🔥',
        'other': '📱'
    }
    return icons.get(account_type, '📱')

def get_account_health_status(balance):
    """Get account health status based on balance"""
    if balance <= 0:
        return "🔴", "Empty", "#ff4444"
    elif balance < 100_000:  # Less than 100k sats
        return "🟡", "Low", "#ffaa00"
    elif balance < 1_000_000:  # Less than 1M sats
        return "🟢", "Good", "#44ff44"
    else:  # 1M+ sats
        return "💎", "Excellent", "#44aaff"

def format_account_balance_with_health(balance):
    """Format balance with health indicator"""
    icon, status, color = get_account_health_status(balance)
    return f"{icon} {format_sats(balance)}", status, color

def get_current_month():
    """Return current month as 'YYYY-MM'"""
    return datetime.now().strftime('%Y-%m')

def clean_duplicate_allocations():
    """Remove duplicate allocations for same category/month, keeping the latest one"""
    try:
        # Group allocations by category_id and month (normalize category_id to int)
        seen_combinations = set()
        cleaned_allocations = []
        
        # Process in reverse order to keep the latest allocation
        for allocation in reversed(st.session_state.user_data['allocations']):
            try:
                # Normalize category_id to integer
                normalized_category_id = int(allocation['category_id'])
                key = (normalized_category_id, allocation['month'])
                
                if key not in seen_combinations:
                    seen_combinations.add(key)
                    # Ensure the allocation we keep has integer category_id
                    allocation['category_id'] = normalized_category_id
                    cleaned_allocations.insert(0, allocation)  # Insert at beginning to maintain order
            except (ValueError, TypeError):
                # Skip allocations with invalid category_id
                continue
        
        original_count = len(st.session_state.user_data['allocations'])
        st.session_state.user_data['allocations'] = cleaned_allocations
        removed_count = original_count - len(cleaned_allocations)
        
        return removed_count
    except Exception as e:
        st.error(f"Error cleaning duplicates: {e}")
        return 0

# === STREAMLIT APPLICATION ===

def initialize_session_state():
    """Initialize session state variables and user data"""
    if 'current_month' not in st.session_state:
        st.session_state.current_month = get_current_month()
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
    
    # Initialize user's private data structures (only once)
    if 'user_data' not in st.session_state:
        # Use centralized demo data function
        st.session_state.user_data = get_demo_data()

def landing_page():
    """Beautiful landing page explaining how to use the Bitcoin Budget app"""
    # Hide sidebar for landing page
    st.markdown("""
        <style>
        .css-1d391kg {display: none}
        </style>
    """, unsafe_allow_html=True)
    
    # Hero section - render immediately for better preview
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
    
    # Removed unnecessary orange block as requested
    
    # Import plotly only when needed for charts
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Net Worth Future Value Example - Bitcoin Power Law calculation
    try:
        from datetime import datetime, timedelta
        
        # Calculate example: 10M sats + 500k/month (conservative model parameters)
        initial_sats = 10_000_000
        monthly_dca_sats = 500_000
        years = 15
        inflation_rate = 0.08
        
        # Bitcoin Power Law calculations
        genesis_date = datetime(2009, 1, 3)
        today = datetime.now()
        future_date = today + timedelta(days=years * 365.25)
        
        current_days = (today - genesis_date).days
        future_days = (future_date - genesis_date).days
        
        current_btc_price = 1.0117e-17 * (current_days ** 5.82)
        future_btc_price = 1.0117e-17 * (future_days ** 5.82)
        
        # Calculate total sats and values
        total_dca_sats = monthly_dca_sats * 12 * years
        total_sats = initial_sats + total_dca_sats
        
        current_usd_value = (initial_sats / 100_000_000) * current_btc_price
        future_usd_value = (total_sats / 100_000_000) * future_btc_price
        inflation_adjusted_purchasing_power = future_usd_value / ((1 + inflation_rate) ** years)
        
        bitcoin_gain = ((future_btc_price / current_btc_price) - 1) * 100
        purchasing_power_multiplier = inflation_adjusted_purchasing_power / current_usd_value
        total_invested_usd = (total_dca_sats / 100_000_000) * current_btc_price
        
        calculations_ready = True
    except Exception:
        # Fallback values for preview/error cases
        initial_sats = 10_000_000
        monthly_dca_sats = 1_000_000
        total_sats = 250_000_000
        current_usd_value = 10000
        total_invested_usd = 2400000
        inflation_adjusted_purchasing_power = 3200000
        purchasing_power_multiplier = 12.5
        calculations_ready = False
    
    # Show Net Worth Future Value example with custom styling
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f7931a 0%, #ff6b35 100%); 
             padding: 1rem 2rem; border-radius: 10px; margin: 1rem 0 1.5rem 0;">
            <h3 style="color: white; text-align: center; margin: 0; font-size: 1.3rem;">
                🚀 Example: Net Worth Future Value - Dollar Cost Averaging 500,000 sats/month for 15 Years
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Create the net worth example metrics
    nw_col1, nw_col2, nw_col3, nw_col4 = st.columns(4)
    
    with nw_col1:
        st.markdown(f"""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #f7931a; font-size: 0.8rem; margin-bottom: 0.3rem;">💎 Starting Stack</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">{format_sats(initial_sats)}</div>
                <div style="color: #10b981; font-size: 0.8rem;">↗ ${current_usd_value:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with nw_col2:
        st.markdown(f"""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #10b981; font-size: 0.8rem; margin-bottom: 0.3rem;">📈 Total Investment</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">${total_invested_usd:,.0f}</div>
                <div style="color: #10b981; font-size: 0.8rem;">↗ {format_sats(total_dca_sats)} DCA</div>
            </div>
        """, unsafe_allow_html=True)
    
    with nw_col3:
        st.markdown(f"""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #8b5cf6; font-size: 0.8rem; margin-bottom: 0.3rem;">🎯 Net Present Value</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">${inflation_adjusted_purchasing_power:,.0f}</div>
                <div style="color: #10b981; font-size: 0.8rem;">↗ After 8% inflation</div>
            </div>
        """, unsafe_allow_html=True)
    
    with nw_col4:
        st.markdown(f"""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #ef4444; font-size: 0.8rem; margin-bottom: 0.3rem;">💎 Final Stack</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">{format_sats(total_sats)}</div>
                <div style="color: #10b981; font-size: 0.8rem;">$100k/year inflation adjusted</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Create side-by-side charts for Bitcoin Retirement Analysis (updated with current data)
    if calculations_ready:
        nw_chart_col1, nw_chart_col2 = st.columns(2)
        
        # Left column: Bitcoin Retirement Readiness Chart
        with nw_chart_col1:
            st.markdown("#### 📊 Bitcoin Retirement Readiness")
            
            try:
                # Calculate retirement readiness data (similar to our reports module)
                from datetime import datetime, timedelta
                
                current_year = datetime.now().year
                years_range = list(range(current_year, current_year + 17))  # 16 year projection to include 2040
                
                # Your growing Bitcoin stack projection
                your_stack_btc = []
                min_btc_needed = []
                
                for year in years_range:
                    # Your projected stack for this year
                    years_from_now = year - current_year
                    months_stacking = years_from_now * 12
                    future_sats = initial_sats + (monthly_dca_sats * months_stacking)
                    future_btc = future_sats / 100_000_000
                    your_stack_btc.append(future_btc)
                    
                    # Minimum BTC needed for retirement (conservative model: $100k annual, 8% inflation, 50-year retirement)
                    # These values are calculated from the actual conservative model (42% floor price)
                    conservative_model_values = {
                        2024: 21.303799, 2025: 15.955366, 2026: 12.193688, 2027: 9.484760, 
                        2028: 7.492925, 2029: 6.001527, 2030: 4.867913, 2031: 3.991383, 
                        2032: 3.306332, 2033: 2.763173, 2034: 2.328341, 2035: 1.976661, 
                        2036: 1.689825, 2037: 1.453337, 2038: 1.257281, 2039: 1.094029, 
                        2040: 0.955950
                    }
                    min_btc_for_year = conservative_model_values.get(year, 0.5)  # Default fallback
                    min_btc_needed.append(min_btc_for_year)
                
                # Find retirement year (where your stack exceeds minimum needed)
                retirement_year = None
                for i, (your_btc, min_btc) in enumerate(zip(your_stack_btc, min_btc_needed)):
                    if your_btc >= min_btc:
                        retirement_year = years_range[i]
                        break
                
                # Create retirement readiness chart (copied from Conservative Model in reports.py)
                fig_retirement = go.Figure()
                
                # User's Bitcoin stack projection (exact same as Conservative Model)
                fig_retirement.add_trace(go.Scatter(
                    x=years_range,
                    y=your_stack_btc,
                    mode='lines+markers',
                    name='Your Bitcoin Stack',
                    line=dict(color='#FF8C00', width=3),
                    marker=dict(size=6)
                ))
                
                # Minimum BTC needed for retirement (exact same as Conservative Model)
                fig_retirement.add_trace(go.Scatter(
                    x=years_range,
                    y=min_btc_needed,
                    mode='lines+markers',
                    name='Min BTC for Retirement',
                    line=dict(color='#DC143C', width=3, dash='dash'),
                    marker=dict(size=6)
                ))
                
                # Add retirement readiness line (exact same as Conservative Model)
                if retirement_year:
                    fig_retirement.add_vline(
                        x=retirement_year,
                        line_width=3,
                        line_dash="dash",
                        line_color="green",
                        annotation_text=f"Can Retire: {retirement_year}"
                    )
                
                # Use the exact same layout as Conservative Model
                chart_title = 'Bitcoin Retirement Readiness - Conservative Model'
                legend_config = dict(
                    orientation="h",  # Horizontal orientation  
                    yanchor="top",
                    y=-0.15,  # Below the chart
                    xanchor="center",
                    x=0.5  # Centered
                )
                chart_height = 280  # Adjusted for main page
                
                fig_retirement.update_layout(
                    title=chart_title,
                    xaxis_title='Year',
                    yaxis_title='Bitcoin (BTC)',
                    height=chart_height,
                    hovermode='x unified',
                    legend=legend_config,
                    showlegend=True
                )
                
                st.plotly_chart(fig_retirement, use_container_width=True)
            except Exception:
                st.markdown("📊 *Bitcoin retirement chart loading...*")
        
        # Right column: DCA Accumulation Visualization  
        with nw_chart_col2:
            st.markdown("#### 💎 Final Stack Composition")
            
            try:
                fig_composition = go.Figure(data=[go.Pie(
                    labels=['Initial Stack', 'DCA Accumulation'],
                    values=[initial_sats, total_dca_sats],
                    hole=.3,
                    marker_colors=['#f7931a', '#ff6b35']
                )])
                
                fig_composition.update_traces(
                    textposition='inside', 
                    textinfo='percent',
                    textfont_size=12,
                    marker=dict(line=dict(color='#000000', width=2))
                )
                
                fig_composition.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        font=dict(color='white', size=9)
                    ),
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=10),
                    height=280
                )
                
                st.plotly_chart(fig_composition, use_container_width=True)
            except Exception:
                st.markdown("💎 *Chart loading...*")
    else:
        # Simplified view when calculations aren't ready (for preview)
        st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #1f2937; border-radius: 10px; margin: 1rem 0;">
                <h4 style="color: #f7931a; margin-bottom: 1rem;">📊 Bitcoin Retirement Analysis Available</h4>
                <p style="color: #e2e8f0; margin: 0;">
                    View Bitcoin retirement readiness charts and DCA projections when you enter the app
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Add inspirational message for Bitcoin Retirement Analysis
    st.markdown(f"""
        <div style="background: #0f172a; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #f7931a;">
            <h4 style="color: #f7931a; margin: 0 0 0.5rem 0;">🏖️ Your Path to Bitcoin Retirement</h4>
            <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">
                With a solid starting stack and consistent Dollar Cost Averaging of <strong>{format_sats(monthly_dca_sats)}</strong> per month, you could potentially retire on Bitcoin in <strong>15 years</strong>! 
                The chart above shows exactly when your growing Bitcoin stack intersects with retirement needs. 
                Time + Consistency + Bitcoin's power law growth = Financial Freedom! 🚀
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
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
            <div style="text-align: center; margin: 0.8rem 0;">
                <div style="background: #f59e0b; color: black; padding: 1rem 2rem; border-radius: 8px; 
                     display: inline-block; font-weight: bold; font-size: 1.1rem;">
                    Bitcoin Income
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; font-size: 2rem; color: #6b7280; margin: 0.5rem 0;'>↓</div>", unsafe_allow_html=True)
        
        # Step 2: Assign to Categories
        st.markdown("""
            <div style="text-align: center; margin: 0.8rem 0;">
                <div style="background: #ef4444; color: white; padding: 1rem 2rem; border-radius: 8px; 
                     display: inline-block; font-weight: bold; font-size: 1.1rem;">
                    Assign to Categories
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; font-size: 2rem; color: #6b7280; margin: 0.5rem 0;'>↓</div>", unsafe_allow_html=True)
        
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
        
        st.markdown("<div style='text-align: center; font-size: 2rem; color: #6b7280; margin: 0.5rem 0;'>↓</div>", unsafe_allow_html=True)
        
        # Step 4: Track Spending
        st.markdown("""
            <div style="text-align: center; margin: 0.8rem 0;">
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
            4. Enter amount in satoshis (e.g., 1,000,000 sats = 0.01 BTC, but we only use sats here)
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
            
            **Monthly Income:** 5,000,000 sats
            
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

def show_onboarding_guide():
    """Show interactive onboarding guide for first-time users"""
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f7931a 0%, #ff6b35 100%); 
             padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: white; text-align: center; margin: 0; font-size: 1.4rem;">
                🎯 Welcome to Bitcoin Budget! Let's get you started
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Check current data state to provide contextual guidance
    accounts = get_accounts()
    categories = get_categories()
    transactions = st.session_state.user_data['transactions']
    
    # Determine user's current step in setup
    has_accounts = len(accounts) > 0
    has_categories = len(categories) > 0
    has_income = any(t['type'] == 'income' for t in transactions)
    has_expenses = any(t['type'] == 'expense' for t in transactions)
    has_allocations = len(st.session_state.user_data['allocations']) > 0
    
    # Progress indicators
    steps_completed = sum([has_accounts, has_categories, has_income, has_allocations])
    progress = steps_completed / 4
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Setup Progress: {steps_completed}/4 steps**")
        st.progress(progress)
        
        # Simple step-by-step guidance
        if not has_accounts:
            st.markdown("### 🏦 Step 1: Add Bitcoin Accounts")
            st.markdown("Check the **Accounts** tab - you likely have demo accounts to start with.")
        elif not has_categories:
            st.markdown("### 📁 Step 2: Create Spending Categories")
            st.markdown("Use the **Categories** tab to organize your spending (Food, Rent, etc.)")
        elif not has_income:
            st.markdown("### 💰 Step 3: Add Income")
            st.markdown("Go to **Transactions** → **Add Income** → Enter satoshis")
        elif not has_allocations:
            st.markdown("### 🎯 Step 4: Allocate Money to Categories")
            st.markdown("Look below for 'Available to Assign' - this is envelope budgeting!")
        else:
            st.markdown("### 🎉 Setup Complete!")
            st.markdown("Now track expenses and view reports to analyze your Bitcoin budget.")
    
    with col2:
        # Quick actions based on current state
        st.markdown("**Quick Actions:**")
        
        if not has_accounts and len(accounts) == 0:
            if st.button("🏦 Add First Account", use_container_width=True):
                st.session_state.quick_account_setup = True
                st.rerun()
        elif not has_categories and len(categories) == 0:
            if st.button("📁 Add First Category", use_container_width=True):
                st.session_state.quick_category_setup = True
                st.rerun()
        elif not has_income:
            if st.button("💰 Add Income", use_container_width=True):
                st.session_state.quick_income_setup = True
                st.rerun()
        else:
            if st.button("📊 View Reports", use_container_width=True):
                st.session_state.page = 'reports'
                st.rerun()
        
        if st.button("📖 Back to Tutorial", use_container_width=True):
            st.session_state.page = 'landing'
            st.rerun()
        
        if st.button("✅ Hide This Guide", use_container_width=True):
            st.session_state.first_visit = False
            st.rerun()
    
    # Simple demo data notice
    if has_accounts and has_categories and has_income:
        st.info("💡 **Demo data loaded.** Feel free to experiment or clear it and add your own data.")


def show_quick_setup_modals():
    """Show quick setup modals for guided onboarding"""
    
    # Quick Account Setup
    if st.session_state.get('quick_account_setup', False):
        with st.expander("🏦 Quick Account Setup", expanded=True):
            st.markdown("**Add your first Bitcoin account:**")
            with st.form("quick_account_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Account Name", value="My Bitcoin Wallet", placeholder="e.g., Main Checking, Cold Storage")
                with col2:
                    balance = st.text_input("Current Balance (sats)", value="1,000,000", placeholder="1,000,000")
                
                col3, col4 = st.columns(2)
                with col3:
                    account_type = st.selectbox("Account Type", 
                        ['checking', 'savings', 'hot_wallet', 'cold_storage', 'lightning_node'], 
                        format_func=lambda x: {
                            'checking': '🏦 Checking',
                            'savings': '💰 Savings', 
                            'hot_wallet': '🔥 Hot Wallet',
                            'cold_storage': '🧊 Cold Storage',
                            'lightning_node': '⚡ Lightning Node'
                        }.get(x, x))
                with col4:
                    is_tracked = st.selectbox("Budget Tracking", [True, False], 
                        format_func=lambda x: "✅ On-Budget (Tracked)" if x else "📋 Off-Budget (Savings)")
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    if st.form_submit_button("✅ Add Account", use_container_width=True):
                        try:
                            balance_sats = parse_amount_input(balance)
                            if add_account(name, balance_sats, is_tracked, account_type):
                                st.success(f"✅ Added account: {name}")
                                st.session_state.quick_account_setup = False
                                st.rerun()
                        except ValueError as e:
                            st.error(f"❌ {str(e)}")
                
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.quick_account_setup = False
                        st.rerun()
    
    # Quick Category Setup
    if st.session_state.get('quick_category_setup', False):
        with st.expander("📁 Quick Category Setup", expanded=True):
            st.markdown("**Create your first spending categories:**")
            
            # Suggest common categories
            suggested_categories = [
                ("Fixed Expenses", ["Rent", "Phone", "Internet"]),
                ("Variable Expenses", ["Food", "Transportation", "Entertainment"]),
                ("Savings & Goals", ["Bitcoin Stack", "Emergency Fund"])
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚀 Add Suggested Categories", use_container_width=True):
                    categories_added = 0
                    for master_name, category_names in suggested_categories:
                        # Add master category
                        if add_master_category(master_name):
                            master_categories = get_master_categories()
                            master_cat = next((mc for mc in master_categories if mc['name'] == master_name), None)
                            
                            if master_cat:
                                # Add subcategories
                                for cat_name in category_names:
                                    if add_category(cat_name):
                                        assign_category_to_master(get_categories()[-1]['id'], master_cat['id'])
                                        categories_added += 1
                    
                    if categories_added > 0:
                        st.success(f"✅ Added {categories_added} categories!")
                        st.session_state.quick_category_setup = False
                        st.rerun()
            
            with col2:
                if st.button("❌ I'll Set Up Later", use_container_width=True):
                    st.session_state.quick_category_setup = False
                    st.rerun()
            
            st.markdown("**Or add a custom category:**")
            with st.form("quick_category_form"):
                new_category = st.text_input("Category Name", placeholder="e.g., Food, Rent, Bitcoin Stack")
                
                if st.form_submit_button("Add Category"):
                    if new_category:
                        if add_category(new_category):
                            st.success(f"✅ Added category: {new_category}")
                            st.session_state.quick_category_setup = False
                            st.rerun()
    
    # Quick Income Setup  
    if st.session_state.get('quick_income_setup', False):
        with st.expander("💰 Quick Income Setup", expanded=True):
            st.markdown("**Add your first income transaction:**")
            
            accounts = get_accounts()
            if not accounts:
                st.warning("⚠️ Please add an account first before adding income.")
                if st.button("🏦 Add Account First"):
                    st.session_state.quick_income_setup = False
                    st.session_state.quick_account_setup = True
                    st.rerun()
            else:
                with st.form("quick_income_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        amount = st.text_input("Income Amount (sats)", value="5,000,000", placeholder="5,000,000")
                        description = st.text_input("Description", value="Salary/Work Payment", placeholder="e.g., Freelance payment, Salary")
                    
                    with col2:
                        account_options = [f"{get_account_type_icon(acc['account_type'])} {acc['name']}" for acc in accounts]
                        selected_account = st.selectbox("Account", account_options)
                        
                        # Extract account name for lookup
                        account_name = selected_account.split(" ", 1)[1] if " " in selected_account else selected_account
                        selected_account_obj = next((acc for acc in accounts if acc['name'] == account_name), accounts[0])
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("✅ Add Income", use_container_width=True):
                            try:
                                amount_sats = parse_amount_input(amount)
                                if add_income(amount_sats, description, datetime.now().strftime('%Y-%m-%d'), selected_account_obj['id']):
                                    st.success(f"✅ Added income: {format_sats(amount_sats)}")
                                    st.session_state.quick_income_setup = False
                                    st.rerun()
                            except ValueError as e:
                                st.error(f"❌ {str(e)}")
                    
                    with col_cancel:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.quick_income_setup = False
                            st.rerun()


def main_page():
    """Main budget application page"""
    current_month = st.session_state.current_month
    
    # Header with current month
    st.title(f"₿ Bitcoin Budget - {current_month}")
    
    # === FIRST-TIME USER ONBOARDING ===
    if st.session_state.get('first_visit', True):
        show_onboarding_guide()
        st.markdown("---")
    
    # === QUICK SETUP MODALS ===
    show_quick_setup_modals()
    
    # === BUDGET SUMMARY METRICS ===
    mobile_responsive_header("💰 Budget Summary", 3)
    
    # Simple Bitcoin unit explanation for first-time users
    if st.session_state.get('first_visit', True):
        st.info("💡 **Bitcoin Units:** 100,000,000 sats = 1 BTC. This app uses sats only for precision.")
    
    # Account-based calculations (simplified)
    tracked_balance = get_total_account_balance(tracked_only=True)
    total_balance = get_total_account_balance(tracked_only=False)
    
    # Calculate total outstanding category balances (money already assigned)
    # Use function that counts ALL allocations regardless of month
    total_category_balances = get_total_category_balances_current()
    
    # Available to Assign = Tracked Account Balance - Outstanding Category Balances
    available_to_assign = tracked_balance - total_category_balances
    
    # Show current month allocations for reference (use viewing month for this)
    current_month_allocated = get_total_allocated(current_month)
    
    # Mobile-responsive metrics layout
    if available_to_assign > 0:
        help_text = f"You have {format_sats(available_to_assign)} ready to allocate to spending categories. This is the core of envelope budgeting!"
    elif available_to_assign == 0:
        help_text = "Perfect! All your money is allocated to categories. This means you have a complete budget plan."
    else:
        help_text = f"You're over-allocated by {format_sats(abs(available_to_assign))}. Either reduce allocations or add more income."
    
    # Prepare metrics data
    metrics_data = [
        {
            "label": "🎯 Available to Assign",
            "value": format_sats(available_to_assign),
            "delta": None,
            "help": help_text
        },
        {
            "label": "📋 In Categories",
            "value": format_sats(total_category_balances),
            "delta": "⚠️ Over Budget" if total_category_balances > tracked_balance else f"Viewing {current_month}: {format_sats(current_month_allocated)}",
            "delta_color": "inverse" if total_category_balances > tracked_balance else "normal",
            "help": "Current total money in category envelopes" + (" (exceeds account balance)" if total_category_balances > tracked_balance else " (consistent across all months)")
        },
        {
            "label": "🏦 Account Balance",
            "value": format_sats(tracked_balance),
            "delta": f"Total: {format_sats(total_balance)}",
            "help": "Balance in tracked accounts (affects budget)"
        }
    ]
    
    # Use mobile-friendly metrics display
    mobile_friendly_metrics(metrics_data)
    
    # === BUDGET HEALTH SUMMARY ===
    mobile_responsive_header("📊 Budget Health", 3)
    
    # Calculate budget health metrics
    allocated_percentage = (total_category_balances / tracked_balance * 100) if tracked_balance > 0 else 0
    
    # Responsive columns for budget health
    num_cols = get_responsive_columns(2)
    if num_cols == 1:
        # Mobile: Stack vertically
        cols = [st.container(), st.container()]
        col1, col2 = cols[0], cols[1]
    else:
        # Desktop: Side by side
        col1, col2 = st.columns(2)
    
    with col1:
        # Budget allocation progress
        st.markdown("**Budget Allocation Progress**")
        progress_value = min(allocated_percentage / 100, 1.0)
        st.progress(progress_value)
        
        # Color-coded status
        if allocated_percentage > 100:
            st.error(f"🔴 Over-allocated: {allocated_percentage:.1f}% ({format_sats(total_category_balances - tracked_balance)} over)")
        elif allocated_percentage >= 95:
            st.success(f"🟢 Fully allocated: {allocated_percentage:.1f}%")
        elif allocated_percentage >= 80:
            st.info(f"🔵 Well allocated: {allocated_percentage:.1f}%")
        else:
            st.warning(f"🟡 Under-allocated: {allocated_percentage:.1f}%")
    
    with col2:
        # Available funds status with quick actions
        st.markdown("**Available Funds**")
        
        # Contextual guidance for new users
        if available_to_assign > 0 and st.session_state.get('first_visit', True):
            st.markdown("""
                💡 **Next Step:** Allocate your available funds to spending categories below. 
                This is how envelope budgeting works - every satoshi gets a job!
                """)
        
        if available_to_assign > 0:
            st.success(f"💰 **{format_sats(available_to_assign)}** ready to allocate")
            
            # Quick allocation buttons (mobile-responsive)
            if is_mobile_layout():
                # Mobile: Stack vertically for larger touch targets
                if st.button("🚀 To Bitcoin Stack", help="Allocate all remaining funds to Bitcoin Stack", use_container_width=True):
                    # Find Bitcoin Stack category
                    bitcoin_category = None
                    for cat in get_categories():
                        if 'bitcoin' in cat['name'].lower() or 'stack' in cat['name'].lower():
                            bitcoin_category = cat
                            break
                    
                    if bitcoin_category:
                        current_allocation = get_category_allocated(bitcoin_category['id'], current_month)
                        new_allocation = current_allocation + available_to_assign
                        if allocate_to_category(bitcoin_category['id'], current_month, new_allocation):
                            st.success(f"✅ Allocated {format_sats(available_to_assign)} to {bitcoin_category['name']}")
                            st.rerun()
                    else:
                        st.error("❌ No Bitcoin/Stack category found")
                
                if st.button("⚖️ Distribute Evenly", help="Distribute remaining funds evenly across all categories", use_container_width=True):
                    categories = get_categories()
                    if categories:
                        amount_per_category = available_to_assign // len(categories)
                        if amount_per_category > 0:
                            for cat in categories:
                                current_allocation = get_category_allocated(cat['id'], current_month)
                                new_allocation = current_allocation + amount_per_category
                                allocate_to_category(cat['id'], current_month, new_allocation)
                            st.success(f"✅ Distributed {format_sats(amount_per_category)} to each category")
                            st.rerun()
                        else:
                            st.warning("❌ Amount too small to distribute")
                    else:
                        st.error("❌ No categories found")
            else:
                # Desktop: Side by side
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🚀 To Bitcoin Stack", help="Allocate all remaining funds to Bitcoin Stack"):
                        # Find Bitcoin Stack category
                        bitcoin_category = None
                        for cat in get_categories():
                            if 'bitcoin' in cat['name'].lower() or 'stack' in cat['name'].lower():
                                bitcoin_category = cat
                                break
                        
                        if bitcoin_category:
                            current_allocation = get_category_allocated(bitcoin_category['id'], current_month)
                            new_allocation = current_allocation + available_to_assign
                            if allocate_to_category(bitcoin_category['id'], current_month, new_allocation):
                                st.success(f"✅ Allocated {format_sats(available_to_assign)} to {bitcoin_category['name']}")
                                st.rerun()
                        else:
                            st.error("❌ No Bitcoin/Stack category found")
                
                with col_b:
                    if st.button("⚖️ Distribute Evenly", help="Distribute remaining funds evenly across all categories"):
                        categories = get_categories()
                        if categories:
                            amount_per_category = available_to_assign // len(categories)
                            if amount_per_category > 0:
                                for cat in categories:
                                    current_allocation = get_category_allocated(cat['id'], current_month)
                                    new_allocation = current_allocation + amount_per_category
                                    allocate_to_category(cat['id'], current_month, new_allocation)
                                st.success(f"✅ Distributed {format_sats(amount_per_category)} to each category")
                                st.rerun()
                            else:
                                st.warning("❌ Amount too small to distribute")
                        else:
                            st.error("❌ No categories found")
                        
        elif available_to_assign == 0:
            st.info("✅ **Perfect balance** - all funds allocated")
        else:
            st.error(f"⚠️ **{format_sats(abs(available_to_assign))}** over-allocated")
            
            # Quick fix buttons for over-allocation (mobile-responsive)
            if is_mobile_layout():
                # Mobile: Stack vertically for larger touch targets
                if st.button("🔧 Auto-Fix", help="Automatically reduce allocations to balance budget", use_container_width=True):
                    # Find categories with allocations and reduce proportionally
                    categories = get_categories()
                    categories_with_allocations = []
                    total_allocated = 0
                    
                    for cat in categories:
                        allocation = get_category_allocated(cat['id'], current_month)
                        if allocation > 0:
                            categories_with_allocations.append((cat, allocation))
                            total_allocated += allocation
                    
                    if categories_with_allocations and total_allocated > 0:
                        reduction_needed = abs(available_to_assign)
                        
                        for cat, allocation in categories_with_allocations:
                            # Reduce proportionally
                            reduction = int((allocation / total_allocated) * reduction_needed)
                            new_allocation = max(0, allocation - reduction)
                            allocate_to_category(cat['id'], current_month, new_allocation)
                        
                        st.success(f"✅ Reduced allocations by {format_sats(reduction_needed)}")
                        st.rerun()
                    else:
                        st.error("❌ No allocations to reduce")
                
                if st.button("📥 Clear All", help="Remove all allocations for this month", use_container_width=True):
                    categories = get_categories()
                    cleared_count = 0
                    for cat in categories:
                        if allocate_to_category(cat['id'], current_month, 0):
                            cleared_count += 1
                    
                    if cleared_count > 0:
                        st.success(f"✅ Cleared allocations for {cleared_count} categories")
                        st.rerun()
                    else:
                        st.error("❌ No allocations to clear")
            else:
                # Desktop: Side by side
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🔧 Auto-Fix", help="Automatically reduce allocations to balance budget"):
                        # Find categories with allocations and reduce proportionally
                        categories = get_categories()
                        categories_with_allocations = []
                        total_allocated = 0
                        
                        for cat in categories:
                            allocation = get_category_allocated(cat['id'], current_month)
                            if allocation > 0:
                                categories_with_allocations.append((cat, allocation))
                                total_allocated += allocation
                        
                        if categories_with_allocations and total_allocated > 0:
                            reduction_needed = abs(available_to_assign)
                            
                            for cat, allocation in categories_with_allocations:
                                # Reduce proportionally
                                reduction = int((allocation / total_allocated) * reduction_needed)
                                new_allocation = max(0, allocation - reduction)
                                allocate_to_category(cat['id'], current_month, new_allocation)
                            
                            st.success(f"✅ Reduced allocations by {format_sats(reduction_needed)}")
                            st.rerun()
                        else:
                            st.error("❌ No allocations to reduce")
                
                with col_b:
                    if st.button("📥 Clear All", help="Remove all allocations for this month"):
                        categories = get_categories()
                        cleared_count = 0
                        for cat in categories:
                            if allocate_to_category(cat['id'], current_month, 0):
                                cleared_count += 1
                        
                        if cleared_count > 0:
                            st.success(f"✅ Cleared allocations for {cleared_count} categories")
                            st.rerun()
                        else:
                            st.error("❌ No allocations to clear")

    st.markdown("---")

    # === MAIN FUNCTIONALITY TABS ===
    tab1, tab2, tab3 = st.tabs(["📁 Categories", "🏦 Accounts", "💳 Transactions"])
    
    # === TAB 1: CATEGORIES (Now the primary/default tab) ===
    with tab1:
        mobile_responsive_header("📁 Category Management", 3)
        
        # Add new master category and category sections (mobile-responsive)
        if is_mobile_layout():
            # Mobile: Stack vertically for better form usability
            with st.expander("➕ Add Master Category", expanded=False):
                with st.form("mobile_add_master_category_form"):
                    new_master_category = st.text_input("Master Category Name", placeholder="e.g., Fixed Expenses, Variable Expenses, Savings")
                    if st.form_submit_button("Add Master Category", use_container_width=True):
                        if new_master_category:
                            # Show loading state
                            loading_placeholder = st.empty()
                            loading_placeholder.info("⏳ Creating master category...")
                            
                            if add_master_category(new_master_category):
                                loading_placeholder.empty()
                                show_bitcoin_toast(f"Added master category: {new_master_category}", "success")
                                st.rerun()
                            else:
                                loading_placeholder.empty()
                                show_bitcoin_toast("Master category name already exists", "warning")
                        else:
                            show_bitcoin_toast("Please enter a master category name", "warning")
            
            with st.expander("➕ Add Category", expanded=False):
                with st.form("mobile_add_category_form"):
                    new_category = st.text_input("Category Name", placeholder="e.g., Transportation")
                    
                    # Master category selection
                    master_categories = get_master_categories()
                    master_options = ['None'] + [mc['name'] for mc in master_categories]
                    selected_master = st.selectbox("Assign to Master Category", master_options)
                    
                    if st.form_submit_button("Add Category", use_container_width=True):
                        if new_category:
                            # Show loading state
                            loading_placeholder = st.empty()
                            loading_placeholder.info("⏳ Creating category...")
                            
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
                                
                                loading_placeholder.empty()
                                show_bitcoin_toast(f"Added category: {new_category}", "success")
                                st.rerun()
                            else:
                                loading_placeholder.empty()
                                show_bitcoin_toast("Category name already exists", "warning")
                        else:
                            show_bitcoin_toast("Please enter a category name", "warning")
        else:
            # Desktop: Side by side
            col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Add Master Category", expanded=False):
                with st.form("add_master_category_form"):
                    new_master_category = st.text_input("Master Category Name", placeholder="e.g., Fixed Expenses, Variable Expenses, Savings")
                    if st.form_submit_button("Add Master Category"):
                        if new_master_category:
                            # Show loading state
                            loading_placeholder = st.empty()
                            loading_placeholder.info("⏳ Creating master category...")
                            
                            if add_master_category(new_master_category):
                                loading_placeholder.empty()
                                show_bitcoin_toast(f"Added master category: {new_master_category}", "success")
                                st.rerun()
                            else:
                                loading_placeholder.empty()
                                show_bitcoin_toast("Master category name already exists", "warning")
                        else:
                            show_bitcoin_toast("Please enter a master category name", "warning")
        
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
                            # Show loading state
                            loading_placeholder = st.empty()
                            loading_placeholder.info("⏳ Creating category...")
                            
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
                                
                                loading_placeholder.empty()
                                show_bitcoin_toast(f"Added category: {new_category}", "success")
                                st.rerun()
                            else:
                                loading_placeholder.empty()
                                show_bitcoin_toast("Category name already exists", "warning")
                        else:
                            show_bitcoin_toast("Please enter a category name", "warning")

        st.markdown("---")

        # Initialize collapsed state if not present
        if 'collapsed_master_categories' not in st.session_state:
            st.session_state.collapsed_master_categories = set()
        
        # Get all master categories and categories
        master_categories = get_master_categories()
        all_categories = get_categories()
        
        if master_categories or all_categories:
            # Sort master categories alphabetically and get names first
            master_categories_sorted = sorted(master_categories, key=lambda x: x['name'])
            master_names = [mc['name'] for mc in master_categories_sorted]
            master_names.append('Uncategorized')  # Add "Uncategorized" for categories without master category
            
            # Clean control panel (mobile-responsive)
            with st.expander("🛠️ Category Controls", expanded=False):
                # Mobile-responsive columns
                num_cols = get_responsive_columns(4, 2)
                cols = st.columns(num_cols)
                
                # Distribute buttons across available columns
                button_configs = [
                    ("📊 Sort Master A-Z", "Sort master categories alphabetically"),
                    ("📋 Sort Categories A-Z", "Sort categories within each master category"),
                    ("📂 Expand All", "Expand all master categories"),
                    ("📁 Collapse All", "Collapse all master categories")
                ]
                
                for i, (label, help_text) in enumerate(button_configs):
                    col_index = i % num_cols
                    with cols[col_index]:
                        if label == "📊 Sort Master A-Z":
                            if st.button(label, help=help_text, use_container_width=True):
                                master_categories.sort(key=lambda x: x['name'])
                                st.rerun()
                        elif label == "📋 Sort Categories A-Z":
                            if st.button(label, help=help_text, use_container_width=True):
                                # Sort categories within their master categories
                                for mc in master_categories:
                                    mc_categories = [cat for cat in all_categories if cat['master_category_id'] == mc['id']]
                                    mc_categories.sort(key=lambda x: x['name'])
                                st.rerun()
                        elif label == "📂 Expand All":
                            if st.button(label, help=help_text, use_container_width=True):
                                st.session_state.collapsed_master_categories.clear()
                                st.rerun()
                        elif label == "📁 Collapse All":
                            if st.button(label, help=help_text, use_container_width=True):
                                st.session_state.collapsed_master_categories = set(master_names)
                                st.rerun()
            
            # Build unified table data with proper grouping
            table_data = []
            grand_allocated = 0
            grand_spent = 0
            grand_balance = 0
            
            # Build hierarchy with explicit sort priority
            sort_priority = 0
            
            for master_name in master_names:
                # Find categories for this master category
                if master_name == 'Uncategorized':
                    categories_in_group = [cat for cat in all_categories if cat['master_category_id'] is None]
                else:
                    master_id = next((mc['id'] for mc in master_categories_sorted if mc['name'] == master_name), None)
                    categories_in_group = [cat for cat in all_categories if cat['master_category_id'] == master_id]
                
                # Skip if no categories in this group
                if not categories_in_group:
                    continue
                
                # Sort categories within this group alphabetically
                categories_in_group.sort(key=lambda x: x['name'])
                
                # Calculate master category totals
                master_allocated = 0
                master_spent = 0
                master_balance = 0
                
                for cat in categories_in_group:
                    current_balance = get_category_balance(cat['id'], current_month)
                    spent = get_category_spent(cat['id'], current_month)
                    master_allocated += current_balance
                    master_spent += spent
                    master_balance += current_balance
                
                # Check if this master category is collapsed
                is_collapsed = master_name in st.session_state.collapsed_master_categories
                collapse_icon = "📁" if is_collapsed else "📂"
                
                # Add master category header with explicit sort priority
                master_month_allocation = sum(get_category_allocated(cat['id'], current_month) for cat in categories_in_group)
                
                # Better master category display with visual hierarchy
                category_count_text = f"({len(categories_in_group)} {'category' if len(categories_in_group) == 1 else 'categories'})"
                master_display = f"{collapse_icon} {master_name} {category_count_text}"
                
                # Better status indicators for master categories
                if master_balance >= 0:
                    master_status = "🟢 Good" if master_balance > 0 else "⚪ Zero"
                else:
                    master_status = "🔴 Over"
                
                table_data.append({
                    'ID': f"master_{master_name}",
                    'Type': 'master',
                    'Category': master_display,
                    'Master_Category_Assignment': master_name,
                    'Current_Balance': master_allocated,
                    'This_Month_Allocation': master_month_allocation,
                    'Spent': master_spent,
                    'Status': master_status,
                    'sort_priority': sort_priority
                })
                sort_priority += 1
                
                # Add individual categories immediately after master (if not collapsed)
                if not is_collapsed:
                    for idx, cat in enumerate(categories_in_group):
                        current_balance = get_category_balance(cat['id'], current_month)
                        current_month_allocation = get_category_allocated(cat['id'], current_month)
                        spent = get_category_spent(cat['id'], current_month)
                        current_master = cat['master_category_name'] or 'Uncategorized'
                        
                        # Create tree-style visual hierarchy
                        is_last_in_group = (idx == len(categories_in_group) - 1)
                        tree_symbol = "└─" if is_last_in_group else "├─"
                        category_display = f"  {tree_symbol} {cat['name']}"
                        
                        # Better status indicators for individual categories
                        if current_balance > 0:
                            category_status = "🟢 Good"
                        elif current_balance == 0:
                            category_status = "⚪ Empty"
                        else:
                            category_status = "🔴 Overspent"
                        
                        table_data.append({
                            'ID': cat['id'],
                            'Type': 'category',
                            'Category': category_display,
                            'Master_Category_Assignment': current_master,
                            'Current_Balance': current_balance,
                            'This_Month_Allocation': current_month_allocation,
                            'Spent': spent,
                            'Status': category_status,
                            'sort_priority': sort_priority
                        })
                        sort_priority += 1
                
                # Add to grand totals
                grand_allocated += master_allocated
                grand_spent += master_spent
                grand_balance += master_balance
            
            # Add grand total row at the END (bottom of hierarchy)
            grand_month_allocation = get_total_allocated(current_month)
            
            # Better grand total display and status
            grand_total_display = "📊 GRAND TOTAL"
            if grand_balance >= 0:
                grand_total_status = "🟢 Balanced" if grand_balance > 0 else "⚪ Zero"
            else:
                grand_total_status = "🔴 Overspent"
            
            table_data.append({
                'ID': 'grand_total',
                'Type': 'grand_total',
                'Category': grand_total_display,
                'Master_Category_Assignment': 'Grand Total',
                'Current_Balance': grand_allocated,
                'This_Month_Allocation': grand_month_allocation,
                'Spent': grand_spent,
                'Status': grand_total_status,
                'sort_priority': sort_priority  # Grand total gets highest priority (last)
            })
            
            # Create DataFrame and sort by explicit sort_priority
            df = pd.DataFrame(table_data)
            
            # Sort by sort_priority to maintain hierarchy (this should match our build order)
            df = df.sort_values('sort_priority').reset_index(drop=True)
            
            # Ensure all numeric columns are properly typed as integers
            numeric_columns = ['Current_Balance', 'This_Month_Allocation', 'Spent']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
            
            # Add hierarchical sorting keys to make interactive sorting work correctly
            df['master_group'] = ''
            df['sort_within_group'] = 0
            
            # Assign master group names and within-group sorting
            for idx, row in df.iterrows():
                if row['Type'] == 'master':
                    # Master categories get their own name as group and sort position 0
                    master_name = row['Master_Category_Assignment']
                    df.at[idx, 'master_group'] = master_name
                    df.at[idx, 'sort_within_group'] = 0
                elif row['Type'] == 'category':
                    # Individual categories get their master's name as group and sort position 1
                    master_name = row['Master_Category_Assignment']
                    df.at[idx, 'master_group'] = master_name
                    df.at[idx, 'sort_within_group'] = 1
                elif row['Type'] == 'grand_total':
                    # Grand total gets its own group at the end
                    df.at[idx, 'master_group'] = 'ZZZ_GRAND_TOTAL'  # Ensures it sorts last
                    df.at[idx, 'sort_within_group'] = 0
            
            # Display editable table with hierarchy-preserving sort
            display_df = df[['Category', 'Master_Category_Assignment', 'Current_Balance', 'This_Month_Allocation', 'Spent', 'Status', 'master_group', 'sort_within_group']].copy()
            
            # Remove debug output and use data_editor with proper column config
            refresh_count = st.session_state.get('data_editor_refresh_count', 0)
            # Mobile-responsive column configuration
            if is_mobile_layout():
                # Mobile: Tighten columns, hide master category assignment to save space
                column_config = {
                    "master_group": None,  # Hide grouping column
                    "sort_within_group": None,  # Hide sorting column
                    "Category": st.column_config.TextColumn(
                        "Category", 
                        help="Category hierarchy",
                        width="medium"  # Smaller width for mobile
                    ),
                    "Master_Category_Assignment": None,  # Hide on mobile to save space
                    "Current_Balance": st.column_config.NumberColumn(
                        "Balance",  # Shorter label
                        help="Current balance in sats",
                        format="%d",
                        width="small"
                    ),
                    "This_Month_Allocation": st.column_config.NumberColumn(
                        "This Month",  # Shorter label
                        help="Monthly allocation (editable)",
                        min_value=0,
                        step=1,
                        format="%d",
                        width="small"
                    ),
                    "Spent": st.column_config.NumberColumn(
                        "Spent", 
                        format="%d",
                        width="small"
                    ),
                    "Status": st.column_config.TextColumn("Status", width="small")
                }
            else:
                # Desktop: Keep full layout
                column_config = {
                    "master_group": None,  # Hide grouping column
                    "sort_within_group": None,  # Hide sorting column
                    "Category": st.column_config.TextColumn(
                        "Category", 
                        help="Category hierarchy - sorting preserves master-child relationships",
                        width="large"
                    ),
                    "Master_Category_Assignment": st.column_config.TextColumn(
                        "Master Category",
                        help="Master category assignment",
                        width="medium"
                    ),
                    "Current_Balance": st.column_config.NumberColumn(
                        "Current Balance (sats)",
                        help="Current money in this category envelope",
                        format="%d"
                    ),
                    "This_Month_Allocation": st.column_config.NumberColumn(
                        "This Month Allocation (sats)",
                        help="Set allocation amount for this month (editable for individual categories only)",
                        min_value=0,
                        step=1,
                        format="%d"
                    ),
                    "Spent": st.column_config.NumberColumn(
                        "Spent This Month (sats)", 
                        format="%d"
                    ),
                    "Status": st.column_config.TextColumn("Status")
                }
            
            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config=column_config,
                key=f"unified_categories_{refresh_count}"
            )
            
            # Process allocation changes only (simplified)
            if not edited_df.equals(display_df):
                changes_made = False
                
                # Check allocation changes for individual categories
                # We need to match edited rows back to original df by finding the same category
                for idx, row in edited_df.iterrows():
                    # Find matching row in original df by Category name and Master Category
                    matching_original = None
                    for orig_idx, orig_row in df.iterrows():
                        if (orig_row['Category'] == row['Category'] and 
                            orig_row['Master_Category_Assignment'] == row['Master_Category_Assignment'] and
                            orig_row['Type'] == 'category'):
                            matching_original = orig_row
                            break
                    
                    if matching_original is not None:
                        category_id = matching_original['ID']
                        original_allocation = matching_original['This_Month_Allocation']
                        new_allocation = row['This_Month_Allocation']
                        
                        if original_allocation != new_allocation:
                            try:
                                new_amount = int(new_allocation)
                                
                                if allocate_to_category(category_id, current_month, new_amount):
                                    st.success(f"✅ Set {row['Category'].strip()} allocation to {format_sats(new_amount)}")
                                    changes_made = True
                                else:
                                    st.error(f"❌ Failed to allocate to {row['Category'].strip()}")
                            except (ValueError, TypeError) as e:
                                st.error(f"❌ Invalid allocation amount: {e}")
                
                if changes_made:
                    # Force refresh of the data editor by updating its key
                    if 'data_editor_refresh_count' not in st.session_state:
                        st.session_state.data_editor_refresh_count = 0
                    st.session_state.data_editor_refresh_count += 1
                    st.rerun()
            
            # Simple help
            st.info("💡 Use the **Category Controls** panel above to expand/collapse master categories and sort your budget. Note: Clicking column headers will break the hierarchy view - use the controls above instead.")
            
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



    # === TAB 2: ACCOUNTS ===
    with tab2:
        mobile_responsive_header("🏦 Account Management", 3)
        
        # Account Summary Metrics
        tracked_accounts = get_tracked_accounts()
        untracked_accounts = get_untracked_accounts()
        
        tracked_total = get_total_account_balance(tracked_only=True)
        untracked_total = get_total_account_balance(tracked_only=False) - tracked_total
        total_all_accounts = tracked_total + untracked_total
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🟢 Tracked Accounts",
                value=format_sats(tracked_total),
                help="On-budget accounts that affect your spending plan"
            )
        
        with col2:
            st.metric(
                label="🔵 Untracked Accounts",
                value=format_sats(untracked_total),
                help="Off-budget accounts (long-term savings, investments)"
            )
        
        with col3:
            st.metric(
                label="💰 Total Net Worth",
                value=format_sats(total_all_accounts),
                help="Combined balance across all accounts"
            )
        
        st.markdown("---")
        
        # Show unaccounted income warning
        unaccounted = get_unaccounted_income(current_month)
        if unaccounted > 0:
            st.warning(f"⚠️ **{format_sats(unaccounted)} income not tied to accounts**")
            st.info("💡 Some income transactions aren't linked to accounts. Go to Transactions tab to edit them and select an account.")
            
            # Show which transactions are unaccounted
            with st.expander("🔍 View Unaccounted Transactions", expanded=False):
                unaccounted_transactions = []
                for trans in st.session_state.user_data['transactions']:
                    if (trans['type'] == 'income' and 
                        ('account_id' not in trans or not trans['account_id']) and
                        trans['date'].startswith(current_month)):
                        unaccounted_transactions.append(trans)
                
                if unaccounted_transactions:
                    for trans in unaccounted_transactions:
                        st.write(f"• {trans['date']}: **{format_sats(trans['amount'])}** - {trans['description']}")
                else:
                    st.write("No unaccounted transactions this month.")
        
        # Add New Account (mobile-responsive)
        with st.expander("➕ Add New Account", expanded=False):
            with st.form("add_account_form"):
                if is_mobile_layout():
                    # Mobile: Stack vertically for better form usability
                    account_name = st.text_input("Account Name", placeholder="e.g., Checking, Bitcoin Savings")
                    
                    # Enhanced account type selection with icons
                    account_type_options = [
                        "checking",
                        "savings", 
                        "investment",
                        "credit",
                        "loan",
                        "cold_storage",
                        "lightning_node", 
                        "hot_wallet",
                        "other"
                    ]
                    
                    # Create display options with icons
                    account_type_display = []
                    for acc_type in account_type_options:
                        icon = get_account_type_icon(acc_type)
                        account_type_display.append(f"{icon} {acc_type.title()}")
                    
                    selected_type_display = st.selectbox(
                        "Account Type", 
                        account_type_display
                    )
                    
                    # Extract the actual type from selection
                    account_type = selected_type_display.split(" ", 1)[1].lower()
                    
                    initial_balance = st.text_input(
                        "Initial Balance", 
                        placeholder="50000",
                        help="Enter current account balance in satoshis"
                    )
                    
                    # Real-time balance validation
                    if initial_balance:
                        is_valid, message, preview = validate_amount_input(initial_balance)
                        if is_valid:
                            st.success(f"{message}: {preview}")
                        else:
                            st.error(message)
                    
                    is_tracked = st.checkbox(
                        "Tracked Account", 
                        value=True,
                        help="Tracked = affects budget planning | Untracked = long-term savings"
                    )
                else:
                    # Desktop: Side by side
                    col1, col2 = st.columns(2)
                
                with col1:
                    account_name = st.text_input("Account Name", placeholder="e.g., Checking, Bitcoin Savings")
                    
                    # Enhanced account type selection with icons
                    account_type_options = [
                        "checking",
                        "savings", 
                        "investment",
                        "credit",
                        "loan",
                        "cold_storage",
                        "lightning_node", 
                        "hot_wallet",
                        "other"
                    ]
                    
                    # Create display options with icons
                    account_type_display = []
                    for acc_type in account_type_options:
                        icon = get_account_type_icon(acc_type)
                        account_type_display.append(f"{icon} {acc_type.title()}")
                    
                    selected_type_display = st.selectbox(
                        "Account Type", 
                        account_type_display
                    )
                    
                    # Extract the actual type from selection
                    account_type = selected_type_display.split(" ", 1)[1].lower()
                
                with col2:
                    initial_balance = st.text_input(
                        "Initial Balance", 
                        placeholder="50000",
                        help="Enter current account balance in satoshis"
                    )
                    
                    # Real-time balance validation
                    if initial_balance:
                        is_valid, message, preview = validate_amount_input(initial_balance)
                        if is_valid:
                            st.success(f"{message}: {preview}")
                        else:
                            st.error(message)
                    
                    is_tracked = st.checkbox(
                        "Tracked Account", 
                        value=True,
                        help="Tracked = affects budget planning | Untracked = long-term savings"
                    )
                
                submit_button_width = is_mobile_layout()
                if st.form_submit_button("Add Account", use_container_width=submit_button_width):
                    if account_name and initial_balance:
                        # Show loading state
                        loading_placeholder = st.empty()
                        loading_placeholder.info("⏳ Creating account...")
                        
                        try:
                            balance_sats = parse_amount_input(initial_balance)
                            if add_account(account_name, balance_sats, is_tracked, account_type):
                                loading_placeholder.empty()
                                account_status = "tracked" if is_tracked else "untracked"
                                show_bitcoin_toast(f"Added {account_status} account: {account_name}", "success")
                                st.rerun()
                            else:
                                loading_placeholder.empty()
                                show_bitcoin_toast("Account name already exists", "warning")
                        except ValueError as e:
                            loading_placeholder.empty()
                            show_bitcoin_toast(f"Invalid balance: {str(e)}", "error")
                    else:
                        show_bitcoin_toast("Please fill in all required fields", "warning")
        
        # Enhanced Account Lists with Visual Improvements (mobile-responsive)
        if is_mobile_layout():
            # Mobile: Stack account lists vertically
            st.markdown("#### 🟢 Tracked Accounts (On-Budget)")
            if tracked_accounts:
                for i, account in enumerate(tracked_accounts):
                    # Get visual indicators
                    type_icon = get_account_type_icon(account['account_type'])
                    balance_text, health_status, health_color = format_account_balance_with_health(account['balance'])
                    
                    # Mobile-friendly account display
                    account_info_col, balance_col = st.columns([3, 2])
                    with account_info_col:
                        st.markdown(f"**{type_icon} {account['name']}**")
                        st.caption(f"{account['account_type'].replace('_', ' ').title()} • {health_status}")
                    with balance_col:
                        st.text(balance_text)  # Use st.text instead of markdown for normal sizing
                    
                    # Action buttons in 2x2 grid for mobile (more compact)
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("📊 View", help="View Details", key=f"mobile_view_tracked_{account['id']}", use_container_width=True):
                            st.session_state.selected_account_id = account['id']
                            st.session_state.selected_account_name = account['name']
                            st.rerun()
                        if st.button("🗑️ Delete", help="Delete Account", key=f"mobile_delete_tracked_{account['id']}", use_container_width=True):
                            if delete_account(account['id']):
                                show_bitcoin_toast(f"Deleted account: {account['name']}", "success")
                                st.rerun()
                            else:
                                show_bitcoin_toast("Cannot delete account with transactions", "warning")
                    with btn_col2:
                        if st.button("✏️ Edit", help="Edit Account", key=f"mobile_edit_tracked_{account['id']}", use_container_width=True):
                            st.session_state[f'edit_account_{account["id"]}'] = True
                            st.rerun()
                        st.write("")  # Empty space to align with delete button
                    st.markdown("---")
            else:
                st.info("No tracked accounts yet. Add one above!")
            
            st.markdown("#### 🔵 Untracked Accounts (Off-Budget)")
            if untracked_accounts:
                for i, account in enumerate(untracked_accounts):
                    # Get visual indicators
                    type_icon = get_account_type_icon(account['account_type'])
                    balance_text, health_status, health_color = format_account_balance_with_health(account['balance'])
                    
                    # Mobile-friendly account display
                    account_info_col, balance_col = st.columns([3, 2])
                    with account_info_col:
                        st.markdown(f"**{type_icon} {account['name']}**")
                        st.caption(f"{account['account_type'].replace('_', ' ').title()} • {health_status}")
                    with balance_col:
                        st.text(balance_text)  # Use st.text instead of markdown for normal sizing
                    
                    # Action buttons in 2x2 grid for mobile (more compact)
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("📊 View", help="View Details", key=f"mobile_view_untracked_{account['id']}", use_container_width=True):
                            st.session_state.selected_account_id = account['id']
                            st.session_state.selected_account_name = account['name']
                            st.rerun()
                        if st.button("🗑️ Delete", help="Delete Account", key=f"mobile_delete_untracked_{account['id']}", use_container_width=True):
                            if delete_account(account['id']):
                                show_bitcoin_toast(f"Deleted account: {account['name']}", "success")
                                st.rerun()
                            else:
                                show_bitcoin_toast("Cannot delete account with transactions", "warning")
                    with btn_col2:
                        if st.button("✏️ Edit", help="Edit Account", key=f"mobile_edit_untracked_{account['id']}", use_container_width=True):
                            st.session_state[f'edit_account_{account["id"]}'] = True
                            st.rerun()
                        st.write("")  # Empty space to align with delete button
                    st.markdown("---")
            else:
                st.info("No untracked accounts yet. Add one above!")
        else:
            # Desktop: Side by side
            col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🟢 Tracked Accounts (On-Budget)")
            if tracked_accounts:
                for i, account in enumerate(tracked_accounts):
                    # Get visual indicators
                    type_icon = get_account_type_icon(account['account_type'])
                    balance_text, health_status, health_color = format_account_balance_with_health(account['balance'])
                    
                    # Streamlined account display
                    account_col1, account_col2, account_col3 = st.columns([4, 2, 1])
                    
                    with account_col1:
                        st.markdown(f"**{type_icon} {account['name']}**")
                        st.caption(f"{account['account_type'].replace('_', ' ').title()} • {health_status}")
                    
                    with account_col2:
                        st.markdown(f"**{balance_text}**")
                    
                    with account_col3:
                        # Action buttons in a row
                        if st.button("📊 View", help="View Details", key=f"view_tracked_{account['id']}"):
                            st.session_state.selected_account_id = account['id']
                            st.session_state.selected_account_name = account['name']
                            st.rerun()
                        
                        if st.button("✏️ Edit", help="Edit Account", key=f"edit_tracked_{account['id']}"):
                            st.session_state[f'edit_account_{account["id"]}'] = True
                            st.rerun()
                        
                        if st.button("🗑️ Delete", help="Delete Account", key=f"delete_tracked_{account['id']}"):
                            if delete_account(account['id']):
                                show_bitcoin_toast(f"Deleted account: {account['name']}", "success")
                                st.rerun()
                            else:
                                show_bitcoin_toast("Cannot delete account with transactions", "warning")
                    

            else:
                st.info("No tracked accounts yet. Add one above!")
        
        with col2:
            st.markdown("#### 🔵 Untracked Accounts (Off-Budget)")
            if untracked_accounts:
                for i, account in enumerate(untracked_accounts):
                    # Get visual indicators
                    type_icon = get_account_type_icon(account['account_type'])
                    balance_text, health_status, health_color = format_account_balance_with_health(account['balance'])
                    
                    # Streamlined account display
                    account_col1, account_col2, account_col3 = st.columns([4, 2, 1])
                    
                    with account_col1:
                        st.markdown(f"**{type_icon} {account['name']}**")
                        st.caption(f"{account['account_type'].replace('_', ' ').title()} • {health_status}")
                    
                    with account_col2:
                        st.markdown(f"**{balance_text}**")
                    
                    with account_col3:
                        # Action buttons in a row
                        if st.button("📊 View", help="View Details", key=f"view_untracked_{account['id']}"):
                            st.session_state.selected_account_id = account['id']
                            st.session_state.selected_account_name = account['name']
                            st.rerun()
                        
                        if st.button("✏️ Edit", help="Edit Account", key=f"edit_untracked_{account['id']}"):
                            st.session_state[f'edit_account_{account["id"]}'] = True
                            st.rerun()
                        
                        if st.button("🗑️ Delete", help="Delete Account", key=f"delete_untracked_{account['id']}"):
                            if delete_account(account['id']):
                                show_bitcoin_toast(f"Deleted account: {account['name']}", "success")
                                st.rerun()
                            else:
                                show_bitcoin_toast("Cannot delete account with transactions", "warning")
                    

            else:
                st.info("No untracked accounts yet. Add one above!")
        
        # Edit Account Forms (Full Width)
        all_accounts = get_accounts()
        for account in all_accounts:
            if st.session_state.get(f'edit_account_{account["id"]}', False):
                st.markdown("---")
                current_icon = get_account_type_icon(account['account_type'])
                st.markdown(f"### ✏️ Edit Account: {current_icon} {account['name']}")
                
                with st.form(f"edit_account_form_{account['id']}"):
                    # Enhanced layout with account type selection
                    col1, col2, col3 = st.columns([2, 2, 2])
                    
                    with col1:
                        st.markdown("**💰 Balance**")
                        new_balance = st.text_input(
                            "New Balance (satoshis)",
                            value=str(account['balance']),
                            help="Enter new account balance in satoshis"
                        )
                        
                        # Real-time balance validation
                        if new_balance:
                            is_valid, message, preview = validate_amount_input(new_balance)
                            if is_valid:
                                st.success(f"{message}: {preview}")
                            else:
                                st.error(message)
                        
                        st.caption(f"Current: {format_sats(account['balance'])}")
                    
                    with col2:
                        st.markdown("**🏷️ Account Type**")
                        account_types = [
                            ('checking', '🏦 Checking'),
                            ('savings', '💰 Savings'),
                            ('investment', '📈 Investment'),
                            ('credit', '💳 Credit'),
                            ('loan', '🏠 Loan'),
                            ('cold_storage', '🧊 Cold Storage'),
                            ('lightning_node', '⚡ Lightning Node'),
                            ('hot_wallet', '🔥 Hot Wallet'),
                            ('other', '📱 Other')
                        ]
                        
                        # Find current selection index
                        current_index = 0
                        for i, (type_key, _) in enumerate(account_types):
                            if type_key == account['account_type']:
                                current_index = i
                                break
                        
                        new_type = st.selectbox(
                            "Account Type",
                            options=[type_key for type_key, _ in account_types],
                            format_func=lambda x: next(display for type_key, display in account_types if type_key == x),
                            index=current_index,
                            help="Select the type of account"
                        )
                        
                        current_type_display = next(display for type_key, display in account_types if type_key == account['account_type'])
                        st.caption(f"Current: {current_type_display}")
                    
                    with col3:
                        st.markdown("**🎯 Actions**")
                        
                        # Show what will change
                        changes = []
                        if new_balance and new_balance != str(account['balance']):
                            try:
                                new_sats = parse_amount_input(new_balance)
                                if new_sats != account['balance']:
                                    changes.append("Balance")
                            except:
                                pass
                        
                        if new_type != account['account_type']:
                            changes.append("Type")
                        
                        if changes:
                            st.info(f"Will update: {', '.join(changes)}")
                        else:
                            st.info("No changes detected")
                        
                        if st.form_submit_button("💾 Save Changes", use_container_width=True):
                            try:
                                balance_sats = parse_amount_input(new_balance)
                                if update_account(account['id'], 
                                                new_balance=balance_sats, 
                                                new_type=new_type):
                                    updates = []
                                    if balance_sats != account['balance']:
                                        updates.append(f"balance to {format_sats(balance_sats)}")
                                    if new_type != account['account_type']:
                                        new_type_display = next(display for type_key, display in account_types if type_key == new_type)
                                        updates.append(f"type to {new_type_display}")
                                    
                                    if updates:
                                        st.success(f"✅ Updated {', '.join(updates)}!")
                                    else:
                                        st.info("No changes were made")
                                    
                                    del st.session_state[f'edit_account_{account["id"]}']
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update account")
                            except ValueError as e:
                                st.error(f"❌ {str(e)}")
                        
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            del st.session_state[f'edit_account_{account["id"]}']
                            st.rerun()
        
        # Enhanced Account Transfers
        st.markdown("#### 💸 Transfer Between Accounts")
        all_accounts = get_accounts()
        if len(all_accounts) >= 2:
            with st.form("transfer_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Enhanced account selection with icons and balances
                    from_account_options = []
                    for acc in all_accounts:
                        icon = get_account_type_icon(acc['account_type'])
                        balance_display = format_sats(acc['balance'])
                        from_account_options.append(f"{icon} {acc['name']} ({balance_display})")
                    
                    selected_from = st.selectbox(
                        "From Account",
                        from_account_options
                    )
                    
                    # Extract account name
                    from_account = selected_from.split(" ", 1)[1].split(" (")[0]
                
                with col2:
                    # Enhanced account selection with icons and balances
                    to_account_options = []
                    for acc in all_accounts:
                        icon = get_account_type_icon(acc['account_type'])
                        balance_display = format_sats(acc['balance'])
                        to_account_options.append(f"{icon} {acc['name']} ({balance_display})")
                    
                    selected_to = st.selectbox(
                        "To Account",
                        to_account_options
                    )
                    
                    # Extract account name
                    to_account = selected_to.split(" ", 1)[1].split(" (")[0]
                
                with col3:
                    transfer_amount = st.text_input(
                        "Amount",
                        placeholder="25000"
                    )
                    
                    # Real-time transfer amount validation
                    if transfer_amount:
                        is_valid, message, preview = validate_amount_input(transfer_amount)
                        if is_valid:
                            st.success(f"{message}: {preview}")
                        else:
                            st.error(message)
                
                if st.form_submit_button("Transfer"):
                    if from_account != to_account and transfer_amount:
                        try:
                            amount_sats = parse_amount_input(transfer_amount)
                            
                            # Get account IDs
                            from_id = next(acc['id'] for acc in all_accounts if acc['name'] == from_account)
                            to_id = next(acc['id'] for acc in all_accounts if acc['name'] == to_account)
                            
                            if transfer_between_accounts(from_id, to_id, amount_sats):
                                st.success(f"✅ Transferred {format_sats(amount_sats)} from {from_account} to {to_account}")
                                st.rerun()
                            else:
                                st.error("❌ Transfer failed - insufficient funds")
                        except ValueError as e:
                            st.error(f"❌ {str(e)}")
                    else:
                        st.error("❌ Please select different accounts and enter amount")
        else:
            st.info("Add at least 2 accounts to enable transfers")
        
        # Account Transaction View
        if hasattr(st.session_state, 'selected_account_id') and st.session_state.selected_account_id:
            st.markdown("---")
            st.markdown(f"### 📊 Transactions for {st.session_state.selected_account_name}")
            
            # Get all transactions for this account
            account_transactions = []
            for trans in st.session_state.user_data['transactions']:
                if trans.get('account_id') == st.session_state.selected_account_id:
                    category_name = None
                    if trans['category_id']:
                        for cat in st.session_state.user_data['categories']:
                            if cat['id'] == trans['category_id']:
                                category_name = cat['name']
                                break
                    
                    account_transactions.append({
                        'Date': trans['date'],
                        'Description': trans['description'],
                        'Amount': f"+{format_sats(trans['amount'])}" if trans['type'] == 'income' else f"-{format_sats(trans['amount'])}",
                        'Category': category_name if trans['type'] == 'expense' else 'Income',
                        'Type': trans['type'].title()
                    })
            
            if account_transactions:
                # Sort by date (newest first)
                account_transactions.sort(key=lambda x: x['Date'], reverse=True)
                
                df_account = pd.DataFrame(account_transactions)
                st.dataframe(df_account, use_container_width=True, hide_index=True)
                
                # Account transaction summary
                income_total = sum(trans['amount'] for trans in st.session_state.user_data['transactions'] 
                                 if trans.get('account_id') == st.session_state.selected_account_id and trans['type'] == 'income')
                expense_total = sum(trans['amount'] for trans in st.session_state.user_data['transactions'] 
                                  if trans.get('account_id') == st.session_state.selected_account_id and trans['type'] == 'expense')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Income", format_sats(income_total))
                with col2:
                    st.metric("Total Expenses", format_sats(expense_total))
                with col3:
                    st.metric("Net Activity", format_sats(income_total - expense_total))
            else:
                st.info(f"No transactions found for {st.session_state.selected_account_name}")
            
            if st.button("← Back to Accounts", key="back_to_accounts"):
                if hasattr(st.session_state, 'selected_account_id'):
                    delattr(st.session_state, 'selected_account_id')
                if hasattr(st.session_state, 'selected_account_name'):
                    delattr(st.session_state, 'selected_account_name')
                st.rerun()

    # === TAB 3: TRANSACTIONS (Combined transaction entry + recent transactions) ===
    with tab3:
        mobile_responsive_header("💳 Enter Transaction", 3)
        
        # Transaction type selection outside the form so it updates dynamically
        transaction_type = st.selectbox(
            "Transaction Type",
            options=["Income", "Expense"],
            help="Select whether this is income or an expense"
        )
        
        # Dynamic form based on transaction type (mobile-responsive)
        if transaction_type == "Income":
            with st.form("add_income_form"):
                if is_mobile_layout():
                    # Mobile: Stack vertically
                    transaction_date = st.date_input(
                        "Date",
                        value=datetime.now().date(),
                        help="Date of transaction"
                    )
                    
                    transaction_amount = st.text_input(
                        "Amount",
                        placeholder="1,000,000",
                        help="Enter amount in satoshis"
                    )
                    
                    # Real-time amount validation
                    if transaction_amount:
                        is_valid, message, preview = validate_amount_input(transaction_amount)
                        if is_valid:
                            st.success(f"{message}: {preview}")
                        else:
                            st.error(message)
                    
                    transaction_description = st.text_input(
                        "Description",
                        placeholder="Salary, freelance, etc.",
                        help="Brief description of income source"
                    )
                    
                    # Account selection for income
                    accounts = get_accounts()
                    account_options = ['None (no account)'] + [f"{acc['name']}" for acc in accounts]
                    selected_account = st.selectbox(
                        "Deposit to Account",
                        options=account_options,
                        help="Select which account receives this income"
                    )
                else:
                    # Desktop: Side by side
                    col1, col2 = st.columns(2)
                
                with col1:
                    transaction_date = st.date_input(
                        "Date",
                        value=datetime.now().date(),
                        help="Date of transaction"
                    )
                    
                    transaction_amount = st.text_input(
                        "Amount",
                        placeholder="1,000,000",
                        help="Enter amount in satoshis"
                    )
                    
                    # Real-time amount validation
                    if transaction_amount:
                        is_valid, message, preview = validate_amount_input(transaction_amount)
                        if is_valid:
                            st.success(f"{message}: {preview}")
                        else:
                            st.error(message)
                
                with col2:
                    transaction_description = st.text_input(
                        "Description",
                        placeholder="Salary, freelance, etc.",
                        help="Brief description of income source"
                    )
                    
                    # Account selection for income
                    accounts = get_accounts()
                    account_options = ['None (no account)'] + [f"{acc['name']}" for acc in accounts]
                    selected_account = st.selectbox(
                        "Deposit to Account",
                        options=account_options,
                        help="Select which account receives this income"
                    )
                
                # Income submit button
                submitted = st.form_submit_button("💰 Add Income", use_container_width=True, type="primary")
                
                if submitted:
                    if transaction_amount and transaction_description:
                        # Show loading state
                        loading_placeholder = st.empty()
                        loading_placeholder.info("⏳ Adding income...")
                        
                        try:
                            amount_sats = parse_amount_input(transaction_amount)
                            
                            # Get account ID if selected
                            account_id = None
                            if selected_account != 'None (no account)':
                                for acc in accounts:
                                    if acc['name'] == selected_account:
                                        account_id = acc['id']
                                        break
                            
                            # Clear loading state
                            loading_placeholder.empty()
                            
                            if add_income(amount_sats, transaction_description, str(transaction_date), account_id):
                                show_bitcoin_toast(f"Added income: {format_sats(amount_sats)} - {transaction_description}", "success")
                                st.rerun()
                            else:
                                show_bitcoin_toast("Failed to add income. Please try again.", "error")
                        except ValueError as e:
                            loading_placeholder.empty()
                            show_bitcoin_toast(f"Invalid amount: {str(e)}", "error")
                    else:
                        show_bitcoin_toast("Please fill in all required fields", "warning")
        
        else:  # Expense
            categories = get_categories()
            if categories:
                with st.form("add_expense_form"):
                    if is_mobile_layout():
                        # Mobile: Stack vertically
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
                        
                        transaction_amount = st.text_input(
                            "Amount",
                            placeholder="50000",
                            help="Enter amount in satoshis"
                        )
                        
                        # Real-time amount validation
                        if transaction_amount:
                            is_valid, message, preview = validate_amount_input(transaction_amount)
                            if is_valid:
                                st.success(f"{message}: {preview}")
                            else:
                                st.error(message)
                        
                        transaction_description = st.text_input(
                            "Description",
                            placeholder="Coffee, groceries, etc.",
                            help="Brief description of expense"
                        )
                        
                        # Account selection for expense
                        accounts = get_accounts()
                        account_options = ['None (no account)'] + [f"{acc['name']}" for acc in accounts]
                        selected_account = st.selectbox(
                            "Pay from Account",
                            options=account_options,
                            help="Select which account this expense is paid from"
                        )
                    else:
                        # Desktop: Side by side
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
                            placeholder="50000",
                            help="Enter amount in satoshis"
                        )
                        
                        # Real-time amount validation
                        if transaction_amount:
                            is_valid, message, preview = validate_amount_input(transaction_amount)
                            if is_valid:
                                st.success(f"{message}: {preview}")
                            else:
                                st.error(message)
                        
                        transaction_description = st.text_input(
                            "Description",
                            placeholder="Coffee, groceries, etc.",
                            help="Brief description of expense"
                        )
                    
                    # Account selection for expense (full width)
                    accounts = get_accounts()
                    account_options = ['None (no account)'] + [f"{acc['name']}" for acc in accounts]
                    selected_account = st.selectbox(
                        "Pay from Account",
                        options=account_options,
                        help="Select which account this expense is paid from"
                    )
                    
                    # Expense submit button
                    submitted = st.form_submit_button("💸 Add Expense", use_container_width=True, type="primary")
                    
                    if submitted:
                        if transaction_amount and transaction_description:
                            # Show loading state
                            loading_placeholder = st.empty()
                            loading_placeholder.info("⏳ Adding expense...")
                            
                            try:
                                amount_sats = parse_amount_input(transaction_amount)
                                
                                # Find category ID
                                category_id = None
                                for cat in categories:
                                    if cat['name'] == transaction_category:
                                        category_id = cat['id']
                                        break
                                
                                # Get account ID if selected
                                account_id = None
                                if selected_account != 'None (no account)':
                                    for acc in accounts:
                                        if acc['name'] == selected_account:
                                            account_id = acc['id']
                                            break
                                
                                # Clear loading state
                                loading_placeholder.empty()
                                
                                if category_id:
                                    if add_expense(amount_sats, transaction_description, category_id, str(transaction_date), account_id):
                                        show_bitcoin_toast(f"Added expense: {format_sats(amount_sats)} - {transaction_description}", "success")
                                        st.rerun()
                                    else:
                                        show_bitcoin_toast("Failed to add expense. Please try again.", "error")
                            except ValueError as e:
                                loading_placeholder.empty()
                                show_bitcoin_toast(f"Invalid amount: {str(e)}", "error")
                        else:
                            show_bitcoin_toast("Please fill in all required fields", "warning")
            else:
                st.warning("⚠️ Add categories first before recording expenses.")
                st.info("👆 Go to the Categories tab to add your first spending category.")

        # Add separator between transaction entry and recent transactions
        st.markdown("---")
        
        # All transactions section (moved below transaction entry)
        mobile_responsive_header("📋 All Transactions", 3)
        
        transactions = get_all_transactions()  # Get ALL transactions for editing
        
        if transactions:
            # Get all categories for dropdown options
            all_categories = get_categories()
            category_options = ['Income'] + [cat['name'] for cat in all_categories]
            
            # Convert to dataframe with proper data types for editing
            trans_data = []
            all_accounts = get_accounts()
            
            for trans in transactions:
                trans_id, date_str, desc, amount, trans_type, category = trans
                
                # Determine category for display
                if trans_type == 'income':
                    category_display = "Income"
                else:
                    category_display = category or "Unknown"
                
                # Find account name for this transaction
                account_name = "No Account"
                transaction_data = next((t for t in st.session_state.user_data['transactions'] if t['id'] == trans_id), None)
                if transaction_data and transaction_data.get('account_id'):
                    account = next((acc for acc in all_accounts if acc['id'] == transaction_data['account_id']), None)
                    if account:
                        account_name = account['name']
                
                trans_data.append({
                    'ID': trans_id,
                    'Date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                    'Description': desc,
                    'Amount': amount,  # Store as raw number for editing
                    'Category': category_display,
                    'Account': account_name,
                    'Type': trans_type,  # Keep track of original type
                    'Original_Category_ID': trans[0] if trans_type == 'expense' else None  # For reference
                })
            
            df = pd.DataFrame(trans_data)
            
            # Display editable transactions table
            account_options = ['No Account'] + [acc['name'] for acc in all_accounts]
            
            # Mobile-responsive transaction table configuration
            if is_mobile_layout():
                # Mobile: Tighten description column, use shorter labels
                transaction_column_config = {
                    "ID": None,  # Hide ID column
                    "Type": None,  # Hide type column
                    "Original_Category_ID": None,  # Hide original category ID
                    "Date": st.column_config.DateColumn(
                        "Date",
                        help="Edit date",
                        format="MM-DD",  # Shorter date format for mobile
                        width="small"
                    ),
                    "Description": st.column_config.TextColumn(
                        "Description",
                        help="Edit description",
                        width="medium"  # Tighter width for mobile
                    ),
                    "Amount": st.column_config.NumberColumn(
                        "Amount",  # Shorter label
                        help="Edit amount in sats",
                        min_value=1,
                        step=1,
                        format="%d",
                        width="small"
                    ),
                    "Category": st.column_config.SelectboxColumn(
                        "Category",
                        help="Change category",
                        options=category_options,
                        width="small"
                    ),
                    "Account": st.column_config.SelectboxColumn(
                        "Account",
                        help="Change account",
                        options=account_options,
                        width="small"
                    )
                }
            else:
                # Desktop: Keep full layout
                transaction_column_config = {
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
                    ),
                    "Account": st.column_config.SelectboxColumn(
                        "Account",
                        help="Click to change transaction account",
                        options=account_options
                    )
                }
            
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                column_config=transaction_column_config,
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
                    account_changed = row['Account'] != original_row['Account']
                    
                    if date_changed or desc_changed or amount_changed or category_changed or account_changed:
                        # Determine if this is income or expense based on category
                        new_category = row['Category']
                        new_date = str(row['Date'])
                        new_description = row['Description']
                        new_amount = int(row['Amount'])
                        new_account = row['Account']
                        
                        # Find account ID
                        account_id = None
                        if new_account != 'No Account':
                            for acc in all_accounts:
                                if acc['name'] == new_account:
                                    account_id = acc['id']
                                    break
                        
                        if new_category == 'Income':
                            # Income transaction
                            if update_transaction(transaction_id, new_date, new_description, new_amount, account_id=account_id):
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
                                if update_transaction(transaction_id, new_date, new_description, new_amount, category_id, account_id):
                                    st.success(f"✅ Updated expense: {new_description}")
                                    changes_made = True
                                else:
                                    st.error(f"❌ Failed to update expense: {new_description}")
                            else:
                                st.error(f"❌ Invalid category: {new_category}")
                
                if changes_made:
                    # Force refresh of the data editor by updating its key
                    if 'data_editor_refresh_count' not in st.session_state:
                        st.session_state.data_editor_refresh_count = 0
                    st.session_state.data_editor_refresh_count += 1
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
        
        # Mobile Layout Toggle
        st.markdown("### 📱 Display Settings")
        
        current_mobile = st.session_state.get('mobile_mode', False)
        mobile_toggle = st.toggle(
            "📱 Mobile-Friendly Layout", 
            value=current_mobile,
            help="Optimize layout for mobile devices (stacks columns vertically)"
        )
        
        # Update mobile mode if changed
        if mobile_toggle != current_mobile:
            st.session_state.mobile_mode = mobile_toggle
            st.rerun()
        
        st.markdown("---")
        
        # Navigation with helpful descriptions
        st.markdown("### 🚀 Navigation")
        
        if st.button("📖 Tutorial & Examples", use_container_width=True, help="See examples and learn how Bitcoin budgeting works"):
            st.session_state.page = 'landing'
            st.rerun()
        
        if st.button("🏠 Main Budget", use_container_width=True, help="Manage income, expenses, categories, and accounts"):
            st.session_state.page = 'main'
            st.rerun()
        
        if st.button("📊 Analytics & Reports", use_container_width=True, help="View spending patterns, net worth projections, and opportunity cost analysis"):
            st.session_state.page = 'reports'
            st.rerun()
        
        # Simple contextual tip for first-time users
        if st.session_state.get('first_visit', True):
            st.markdown("---")
            st.markdown("### 💡 Next Step")
            
            # Simple, clear guidance
            accounts = get_accounts()
            categories = get_categories()
            transactions = st.session_state.user_data['transactions']
            has_income = any(t['type'] == 'income' for t in transactions)
            
            if len(accounts) == 0:
                st.info("**Start:** Go to Tutorial & Examples to learn the basics")
            elif len(categories) == 0:
                st.info("**Create:** Add spending categories in the main app")
            elif not has_income:
                st.info("**Add Income:** Record Bitcoin income to begin budgeting")
            else:
                st.info("**Allocate:** Assign your income to spending categories")
        
        st.markdown("---")
        
        # Data Management Section
        st.markdown("### 💾 Data Management")
        st.warning("⚠️ **IMPORTANT**: Your data will be LOST when you close this browser tab! Export regularly to save your work.")
        
        # Export functionality
        st.markdown("#### 📤 Export Budget")
        export_data = export_budget_data()
        if export_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bitcoin_budget_{timestamp}.json"
            
            st.download_button(
                label="💾 Download Budget",
                data=export_data,
                file_name=filename,
                mime="application/json",
                use_container_width=True,
                help="Save your budget data to a file"
            )
        
        # Import functionality
        st.markdown("#### 📥 Import Budget")
        uploaded_file = st.file_uploader(
            "Choose a budget file",
            type=['json'],
            help="Upload a previously exported budget file",
            key="budget_import"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                json_data = uploaded_file.read().decode('utf-8')
                
                # Show import button
                if st.button("📥 Import Budget", use_container_width=True, type="primary"):
                    success, message = import_budget_data(json_data)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                        
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        # Reset data options
        st.markdown("#### 🔄 Reset Data")
        
        # Reset to demo data
        if st.button("🔄 Reset to Demo Budget", use_container_width=True, type="secondary", help="Load realistic example budget with income, expenses, and categories"):
            st.session_state.user_data = get_demo_data()
            st.success("✅ Reset to demo data")
            st.rerun()
        
        # Fresh start
        if st.button("🆕 Fresh Start (Empty)", use_container_width=True, type="secondary", help="Start completely fresh with no data"):
            st.session_state.user_data = get_fresh_data()
            st.success("✅ Fresh start - all data cleared")
            st.rerun()

def main():
    """Main application entry point"""
    # Initialize session state
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
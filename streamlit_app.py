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

# Add meta tags for better social media previews
st.markdown("""
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
    """Get default demo data structure"""
    current_month = get_current_month()
    
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
    
    demo_transactions = [
        {
            'id': 1,
            'date': current_month + '-01',
            'description': 'Monthly Salary',
            'amount': 100000,  # 100k sats
            'type': 'income',
            'category_id': None,
            'account_id': 1
        }
    ]
    
    demo_allocations = [
        {'id': 1, 'category_id': 1, 'month': current_month, 'amount': 50000},
        {'id': 2, 'category_id': 2, 'month': current_month, 'amount': 30000},
        {'id': 3, 'category_id': 3, 'month': current_month, 'amount': 20000}
    ]
    
    demo_accounts = [
        {
            'id': 1,
            'name': 'Checking Account',
            'balance': 100000,
            'is_tracked': True,
            'account_type': 'checking'
        },
        {
            'id': 2,
            'name': 'Bitcoin Savings',
            'balance': 500000,
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
        'next_transaction_id': 2,
        'next_category_id': 4,
        'next_master_category_id': 4,
        'next_allocation_id': 4,
        'next_account_id': 3
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
        
        # Calculate example: 1M sats + 250k/month for 20 years
        initial_sats = 1_000_000
        monthly_dca_sats = 250_000
        years = 20
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
        initial_sats = 1_000_000
        monthly_dca_sats = 250_000
        total_sats = 61_000_000
        current_usd_value = 1000
        total_invested_usd = 150000
        inflation_adjusted_purchasing_power = 780000
        purchasing_power_multiplier = 7.8
        calculations_ready = False
    
    # Show Net Worth Future Value example with custom styling
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f7931a 0%, #ff6b35 100%); 
             padding: 1rem 2rem; border-radius: 10px; margin: 1rem 0 1.5rem 0;">
            <h3 style="color: white; text-align: center; margin: 0; font-size: 1.3rem;">
                🚀 Example: Net Worth Future Value - DCA'ing 250k sats/month for 20 Years
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
                <div style="color: #8b5cf6; font-size: 0.8rem; margin-bottom: 0.3rem;">🎯 Future Value (Real)</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">${inflation_adjusted_purchasing_power:,.0f}</div>
                <div style="color: #10b981; font-size: 0.8rem;">↗ After 8% inflation</div>
            </div>
        """, unsafe_allow_html=True)
    
    with nw_col4:
        st.markdown(f"""
            <div style="background: #1f2937; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="color: #ef4444; font-size: 0.8rem; margin-bottom: 0.3rem;">💎 Final Stack</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.3rem;">{format_sats(total_sats)}</div>
                <div style="color: #10b981; font-size: 0.8rem;">↗ {purchasing_power_multiplier:.1f}x purchasing power</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Create side-by-side charts for Net Worth example (only if calculations are ready)
    if calculations_ready:
        nw_chart_col1, nw_chart_col2 = st.columns(2)
        
        # Left column: Stack Growth Over Time
        with nw_chart_col1:
            st.markdown("#### 📊 Stack Growth Over 20 Years")
            
            try:
                # Calculate milestone data points
                milestones = [0, 5, 10, 15, 20]
                stack_values = []
                for year in milestones:
                    milestone_sats = initial_sats + (monthly_dca_sats * 12 * year)
                    milestone_days = current_days + (year * 365.25)
                    milestone_btc_price = 1.0117e-17 * (milestone_days ** 5.82)
                    milestone_value = (milestone_sats / 100_000_000) * milestone_btc_price
                    stack_values.append(milestone_value)
                
                fig_growth = go.Figure(data=[
                    go.Scatter(
                        x=milestones,
                        y=stack_values,
                        mode='lines+markers',
                        line=dict(color='#f7931a', width=4),
                        marker=dict(size=10, color='#ff6b35'),
                        fill='tonexty' if len(milestones) > 1 else None,
                        fillcolor='rgba(247, 147, 26, 0.1)'
                    )
                ])
                
                fig_growth.update_layout(
                    title='',
                    xaxis=dict(
                        title='Years',
                        tickfont=dict(color='white', size=9),
                        gridcolor='rgba(255,255,255,0.1)',
                        title_font=dict(color='white', size=10)
                    ),
                    yaxis=dict(
                        title='Stack Value (USD)',
                        tickfont=dict(color='white', size=9),
                        gridcolor='rgba(255,255,255,0.1)',
                        title_font=dict(color='white', size=10)
                    ),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=280,
                    showlegend=False
                )
                
                st.plotly_chart(fig_growth, use_container_width=True)
            except Exception:
                st.markdown("📊 *Chart loading...*")
        
        # Right column: Stack Size Visualization
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
                    textinfo='percent+label',
                    textfont_size=10,
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
                <h4 style="color: #f7931a; margin-bottom: 1rem;">📊 Interactive Charts Available</h4>
                <p style="color: #e2e8f0; margin: 0;">
                    View stack growth projections and composition charts when you enter the app
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Add inspirational message for Net Worth example
    st.markdown(f"""
        <div style="background: #0f172a; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #f7931a;">
            <h4 style="color: #f7931a; margin: 0 0 0.5rem 0;">🎯 The Power of Consistent Stacking</h4>
            <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">
                Starting with just <strong>{format_sats(initial_sats)}</strong> and consistently adding <strong>{format_sats(monthly_dca_sats)}</strong> per month, 
                your Bitcoin stack could grow to <strong>{format_sats(total_sats)}</strong> with <strong>{purchasing_power_multiplier:.1f}x</strong> the purchasing power in 20 years. 
                That's the magic of time, scarcity, and disciplined accumulation! 🚀
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🎯 Available to Assign",
            value=format_sats(available_to_assign),
            delta=None,
            help="Current unallocated balance (consistent across all months)"
        )
    
    with col2:
        # Check if over budget (category balances > tracked balance)
        if total_category_balances > tracked_balance:
            st.metric(
                label="📋 In Categories",
                value=format_sats(total_category_balances),
                delta="⚠️ Over Budget",
                delta_color="inverse",
                help="Current total money in category envelopes (exceeds account balance)"
            )
        else:
            st.metric(
                label="📋 In Categories",
                value=format_sats(total_category_balances),
                delta=f"Viewing {current_month}: {format_sats(current_month_allocated)}",
                help="Current total money in category envelopes (consistent across all months)"
            )
    
    with col3:
        st.metric(
            label="🏦 Account Balance",
            value=format_sats(tracked_balance),
            delta=f"Total: {format_sats(total_balance)}",
            help="Balance in tracked accounts (affects budget)"
        )

    st.markdown("---")

    # === MAIN FUNCTIONALITY TABS ===
    tab1, tab2, tab3 = st.tabs(["📁 Categories", "🏦 Accounts", "💳 Transactions"])
    
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
                    'Current_Balance': 0,  # Will be calculated
                    'This_Month_Allocation': 0,  # Will be calculated
                    'Spent': 0,      # Will be calculated
                    'Status': '📊 Total'
                })
                
                # Add individual categories under this master category
                for cat in categories_in_group:
                    # In account-based budgeting, we care about current balance, not monthly allocations
                    current_balance = get_category_balance(cat['id'], current_month)
                    current_month_allocation = get_category_allocated(cat['id'], current_month)
                    spent = get_category_spent(cat['id'], current_month)
                    
                    master_allocated += current_balance
                    master_spent += spent
                    master_balance += current_balance
                    
                    # Get master category options for reassignment
                    master_options_for_cat = ['Uncategorized'] + [mc['name'] for mc in master_categories]
                    current_master = cat['master_category_name'] or 'Uncategorized'
                    
                    table_data.append({
                        'ID': cat['id'],
                        'Type': 'category',
                        'Category': f"    {cat['name']}", # Indent to show hierarchy
                        'Master_Category_Assignment': current_master,
                        'Current_Balance': current_balance,
                        'This_Month_Allocation': current_month_allocation,  # Show current month's allocation
                        'Spent': spent,
                        'Status': '✅ Good' if current_balance >= 0 else '⚠️ Overspent'
                    })
                
                # Update master category totals in the header row
                master_month_allocation = sum(get_category_allocated(cat['id'], current_month) for cat in categories_in_group)
                for row in table_data:
                    if row['ID'] == f"master_{master_name}":
                        row['Current_Balance'] = master_allocated
                        row['This_Month_Allocation'] = master_month_allocation
                        row['Spent'] = master_spent
                        row['Status'] = '📊 Total' if master_balance >= 0 else '⚠️ Over'
                        break
                
                # Add to grand totals
                grand_allocated += master_allocated
                grand_spent += master_spent
                grand_balance += master_balance
            
            # Add grand total row
            grand_month_allocation = get_total_allocated(current_month)
            table_data.append({
                'ID': 'grand_total',
                'Type': 'grand_total',
                'Category': '📊 GRAND TOTAL',
                'Master_Category_Assignment': 'Grand Total',
                'Current_Balance': grand_allocated,
                'This_Month_Allocation': grand_month_allocation,
                'Spent': grand_spent,
                'Status': '🎯 Total' if grand_balance >= 0 else '⚠️ Over'
            })
            
            # Create DataFrame with consistent data types
            df = pd.DataFrame(table_data)
            
            # Ensure all numeric columns are properly typed as integers
            numeric_columns = ['Current_Balance', 'This_Month_Allocation', 'Spent']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
            
            # Display editable table
            refresh_count = st.session_state.get('data_editor_refresh_count', 0)
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
                        width="large",
                        disabled=True  # Disable category name editing for now to focus on allocations
                    ),
                    "Master_Category_Assignment": st.column_config.SelectboxColumn(
                        "Master Category",
                        help="Click dropdown to reassign category to different master category",
                        options=['Uncategorized'] + [mc['name'] for mc in master_categories],
                        disabled=True  # Disable for now to focus on allocations
                    ),
                    "Current_Balance": st.column_config.NumberColumn(
                        "Current Balance (sats)",
                        help="Current money in this category envelope",
                        disabled=True,
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
                        disabled=True,
                        format="%d"
                    ),
                    "Status": st.column_config.TextColumn("Status", disabled=True)
                },
                key=f"unified_categories_{refresh_count}",
                disabled=["Type", "Category", "Master_Category_Assignment", "Current_Balance", "Spent", "Status"]
            )
            
            # Process changes with simplified logic focusing only on allocations
            if not edited_df.equals(df):
                changes_made = False
                
                # Only check allocation changes for individual categories
                for idx, row in edited_df.iterrows():
                    if row['Type'] == 'category':  # Only process individual categories
                        category_id = row['ID']
                        original_allocation = df.iloc[idx]['This_Month_Allocation']
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
        st.markdown("### 🏦 Account Management")
        
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
        
        # Add New Account
        with st.expander("➕ Add New Account", expanded=False):
            with st.form("add_account_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    account_name = st.text_input("Account Name", placeholder="e.g., Checking, Bitcoin Savings")
                    account_type = st.selectbox(
                        "Account Type", 
                        ["checking", "savings", "investment", "credit", "other"]
                    )
                
                with col2:
                    initial_balance = st.text_input(
                        "Initial Balance", 
                        placeholder="50000 or 0.0005 BTC",
                        help="Enter current account balance"
                    )
                    is_tracked = st.checkbox(
                        "Tracked Account", 
                        value=True,
                        help="Tracked = affects budget planning | Untracked = long-term savings"
                    )
                
                if st.form_submit_button("Add Account"):
                    if account_name and initial_balance:
                        try:
                            balance_sats = parse_amount_input(initial_balance)
                            if add_account(account_name, balance_sats, is_tracked, account_type):
                                st.success(f"✅ Added account: {account_name}")
                                st.rerun()
                            else:
                                st.error("❌ Account name already exists")
                        except ValueError:
                            st.error("❌ Invalid balance format")
                    else:
                        st.error("❌ Please fill in all required fields")
        
        # Account Lists
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🟢 Tracked Accounts (On-Budget)")
            if tracked_accounts:
                for account in tracked_accounts:
                    with st.container():
                        account_col1, account_col2, account_col3 = st.columns([3, 2, 1])
                        
                        with account_col1:
                            st.write(f"**{account['name']}** ({account['account_type']})")
                        
                        with account_col2:
                            st.write(format_sats(account['balance']))
                        
                        with account_col3:
                            if st.button("🗑️", key=f"delete_tracked_{account['id']}", help="Delete account"):
                                if delete_account(account['id']):
                                    st.success(f"Deleted {account['name']}")
                                    st.rerun()
                                else:
                                    st.error("Cannot delete account with transactions")
                        
                        st.markdown("---")
            else:
                st.info("No tracked accounts yet. Add one above!")
        
        with col2:
            st.markdown("#### 🔵 Untracked Accounts (Off-Budget)")
            if untracked_accounts:
                for account in untracked_accounts:
                    with st.container():
                        account_col1, account_col2, account_col3 = st.columns([3, 2, 1])
                        
                        with account_col1:
                            st.write(f"**{account['name']}** ({account['account_type']})")
                        
                        with account_col2:
                            st.write(format_sats(account['balance']))
                        
                        with account_col3:
                            if st.button("🗑️", key=f"delete_untracked_{account['id']}", help="Delete account"):
                                if delete_account(account['id']):
                                    st.success(f"Deleted {account['name']}")
                                    st.rerun()
                                else:
                                    st.error("Cannot delete account with transactions")
                        
                        st.markdown("---")
            else:
                st.info("No untracked accounts yet. Add one above!")
        
        # Account Transfers
        st.markdown("#### 💸 Transfer Between Accounts")
        all_accounts = get_accounts()
        if len(all_accounts) >= 2:
            with st.form("transfer_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    from_account = st.selectbox(
                        "From Account",
                        [acc['name'] for acc in all_accounts]
                    )
                
                with col2:
                    to_account = st.selectbox(
                        "To Account",
                        [acc['name'] for acc in all_accounts]
                    )
                
                with col3:
                    transfer_amount = st.text_input(
                        "Amount",
                        placeholder="25000 or 0.00025 BTC"
                    )
                
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
                        except ValueError:
                            st.error("❌ Invalid amount format")
                    else:
                        st.error("❌ Please select different accounts and enter amount")
        else:
            st.info("Add at least 2 accounts to enable transfers")

    # === TAB 3: TRANSACTIONS (Combined transaction entry + recent transactions) ===
    with tab3:
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
                        try:
                            amount_sats = parse_amount_input(transaction_amount)
                            
                            # Get account ID if selected
                            account_id = None
                            if selected_account != 'None (no account)':
                                for acc in accounts:
                                    if acc['name'] == selected_account:
                                        account_id = acc['id']
                                        break
                            
                            if add_income(amount_sats, transaction_description, str(transaction_date), account_id):
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
                                
                                if category_id:
                                    if add_expense(amount_sats, transaction_description, category_id, str(transaction_date), account_id):
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
        
        # Reset to demo data
        st.markdown("#### 🔄 Reset Data")
        if st.button("🗑️ Reset to Demo", use_container_width=True, type="secondary"):
            if st.session_state.get('confirm_reset', False):
                st.session_state.user_data = get_demo_data()
                st.session_state.confirm_reset = False
                st.success("✅ Reset to demo data")
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ Click again to confirm reset")
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
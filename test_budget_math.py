#!/usr/bin/env python3
"""
Comprehensive Test Suite for Bitcoin Budget Math

This will test all the core budget calculations to ensure proper YNAB behavior.
"""

import sqlite3
import os
from datetime import datetime
import sys

# Import functions from our main app
sys.path.append('.')
from bitcoin_budget import *

def setup_test_database():
    """Create a clean test database"""
    if os.path.exists('test_budget.db'):
        os.remove('test_budget.db')
    
    # Override the database connection for testing
    global get_db_connection
    original_get_db_connection = get_db_connection
    
    def test_get_db_connection():
        return sqlite3.connect('test_budget.db')
    
    get_db_connection = test_get_db_connection
    init_database()
    return original_get_db_connection

def cleanup_test_database(original_get_db_connection):
    """Clean up test database and restore original connection"""
    global get_db_connection
    get_db_connection = original_get_db_connection
    if os.path.exists('test_budget.db'):
        os.remove('test_budget.db')

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print('='*60)

def print_month_summary(month, description=""):
    """Print complete month summary for debugging"""
    print(f"\n📅 MONTH: {month} {description}")
    print("-" * 40)
    
    # Basic totals
    income = get_total_income(month)
    allocated = get_total_allocated_direct(month)
    rollover = get_rollover_amount(month)
    available = get_available_to_assign(month)
    
    print(f"💰 Income (current month): {format_sats(income)}")
    print(f"🔄 Rollover: {format_sats(rollover)}")
    print(f"📊 Total Allocated: {format_sats(allocated)}")
    print(f"✨ Available to Assign: {format_sats(available)}")
    
    # Category details
    categories = get_categories()
    if categories:
        print(f"\n📁 CATEGORY DETAILS:")
        for cat in categories:
            allocated_cat = get_category_allocated_direct(cat['id'], month)
            spent_cat = get_category_spent(cat['id'], month)
            balance_cat = allocated_cat - spent_cat
            rollover_cat = get_category_rollover_balance(cat['id'], month)
            
            print(f"  {cat['name']}:")
            print(f"    Allocated: {format_sats(allocated_cat)}")
            print(f"    Spent: {format_sats(spent_cat)}")
            print(f"    Balance: {format_sats(balance_cat)}")
            print(f"    Rollover from prev: {format_sats(rollover_cat)}")
    
    # Verify math
    expected_available = income + rollover - allocated
    math_check = "✅" if available == expected_available else "❌"
    print(f"\n🧮 MATH CHECK {math_check}")
    print(f"   Expected Available: {income} + {rollover} - {allocated} = {expected_available}")
    print(f"   Actual Available: {available}")
    if available != expected_available:
        print(f"   ❌ DIFFERENCE: {available - expected_available}")

def test_basic_single_month():
    """Test basic single month budget math"""
    print_test_header("Basic Single Month Budget")
    
    # Add categories
    add_category("Groceries")
    add_category("Rent")
    
    # Add income
    add_income(100000, "Salary", "2025-06-01")
    
    # Allocate some money
    categories = get_categories()
    groceries_id = next(cat['id'] for cat in categories if cat['name'] == 'Groceries')
    rent_id = next(cat['id'] for cat in categories if cat['name'] == 'Rent')
    
    allocate_to_category(groceries_id, "2025-06", 30000)
    allocate_to_category(rent_id, "2025-06", 50000)
    
    # Spend some money
    add_expense(20000, "Food shopping", groceries_id, "2025-06-15")
    add_expense(50000, "Monthly rent", rent_id, "2025-06-15")
    
    print_month_summary("2025-06", "(Basic test month)")
    
    # Expected results:
    # Income: 100,000
    # Allocated: 80,000 (30k + 50k)
    # Available: 20,000 (100k - 80k)
    # Groceries balance: 10,000 (30k - 20k)
    # Rent balance: 0 (50k - 50k)

def test_rollover_scenario():
    """Test the rollover scenario that's causing issues"""
    print_test_header("Rollover Scenario")
    
    print("Setting up June data...")
    
    # Clear any existing allocations for July to test fresh
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM allocations WHERE month = '2025-07'")
    conn.commit()
    conn.close()
    
    print_month_summary("2025-06", "(June - base month)")
    print_month_summary("2025-07", "(July - should show rollover)")
    
    # Let's manually check what the rollover calculation is doing
    print(f"\n🔍 DETAILED ROLLOVER ANALYSIS:")
    
    # June totals
    june_income = get_total_income("2025-06")
    june_allocated = get_total_allocated_direct("2025-06")
    june_unallocated = june_income - june_allocated
    
    print(f"June income: {format_sats(june_income)}")
    print(f"June allocated: {format_sats(june_allocated)}")
    print(f"June unallocated: {format_sats(june_unallocated)}")
    
    # Category balances from June
    categories = get_categories()
    total_june_balances = 0
    for cat in categories:
        june_allocated_cat = get_category_allocated_direct(cat['id'], "2025-06")
        june_spent_cat = get_category_spent(cat['id'], "2025-06")
        june_balance_cat = june_allocated_cat - june_spent_cat
        total_june_balances += max(0, june_balance_cat)
        print(f"{cat['name']} June balance: {format_sats(june_balance_cat)}")
    
    print(f"Total positive June balances: {format_sats(total_june_balances)}")
    
    # What should happen in July:
    print(f"\n💡 WHAT SHOULD HAPPEN IN JULY:")
    print(f"Option A (Category rollover): Categories should show their June balances")
    print(f"Option B (Available rollover): Available should be {format_sats(june_unallocated + total_june_balances)}")

def test_edge_cases():
    """Test edge cases that might break the math"""
    print_test_header("Edge Cases")
    
    # Test month with no income
    print_month_summary("2025-08", "(August - no income month)")
    
    # Test overspending scenario
    print("Creating overspending scenario...")
    categories = get_categories()
    groceries_id = next(cat['id'] for cat in categories if cat['name'] == 'Groceries')
    
    # Try to spend more than allocated (in June, Groceries had 30k allocated, 20k spent = 10k balance)
    add_expense(15000, "Overspending test", groceries_id, "2025-06-30")
    
    print_month_summary("2025-06", "(June - after overspending)")

def run_all_tests():
    """Run the complete test suite"""
    print("🚀 BITCOIN BUDGET MATH TEST SUITE")
    print("=" * 60)
    
    original_get_db_connection = setup_test_database()
    
    try:
        test_basic_single_month()
        test_rollover_scenario()
        test_edge_cases()
        
        print(f"\n{'='*60}")
        print("🏁 ALL TESTS COMPLETED")
        print("="*60)
        print("Review the output above to identify math issues.")
        print("Look for ❌ symbols indicating calculation problems.")
        
    finally:
        cleanup_test_database(original_get_db_connection)

if __name__ == "__main__":
    run_all_tests() 
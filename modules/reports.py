#!/usr/bin/env python3
"""
Bitcoin Budget - Reports Page
All reporting functionality converted to Streamlit with Plotly charts
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import calendar

# Import functions from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_user_data():
    """Get user data from session state"""
    return st.session_state.user_data

def format_sats(satoshis):
    """Format satoshis for display"""
    return f"{satoshis:,} sats"

def get_current_month():
    """Return current month as 'YYYY-MM'"""
    return datetime.now().strftime('%Y-%m')

def parse_amount_input(text):
    """Parse user input to satoshis"""
    text = text.strip().replace(',', '')
    if text.lower().endswith(' btc'):
        btc_amount = float(text[:-4])
        return int(btc_amount * 100_000_000)
    else:
        return int(text)

def get_spending_breakdown(start_date, end_date):
    """Get spending breakdown by category for a given date range"""
    user_data = get_user_data()
    
    # Group expenses by category
    category_spending = {}
    
    for transaction in user_data['transactions']:
        if (transaction['type'] == 'expense' and 
            start_date <= transaction['date'] <= end_date):
            
            # Find category name
            category_name = "Unknown"
            if transaction['category_id']:
                for category in user_data['categories']:
                    if category['id'] == transaction['category_id']:
                        category_name = category['name']
                        break
            
            if category_name not in category_spending:
                category_spending[category_name] = 0
            category_spending[category_name] += transaction['amount']
    
    # Convert to breakdown format
    breakdown = []
    total_spent = sum(category_spending.values())
    
    for category_name, amount in category_spending.items():
        if amount > 0:
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            breakdown.append({
                'category': category_name,
                'amount': amount,
                'percentage': percentage
            })
    
    # Sort by amount (highest first)
    breakdown.sort(key=lambda x: x['amount'], reverse=True)
    
    return breakdown, total_spent

def get_net_worth_data(start_date, end_date):
    """Get monthly income vs expenses data with account-based net worth analysis"""
    user_data = get_user_data()
    
    monthly_data = {}
    all_months = set()
    
    for transaction in user_data['transactions']:
        if start_date <= transaction['date'] <= end_date:
            # Extract year-month from date
            month = transaction['date'][:7]  # 'YYYY-MM'
            all_months.add(month)
            
            if month not in monthly_data:
                monthly_data[month] = {'income': 0, 'expenses': 0}
            
            if transaction['type'] == 'income':
                monthly_data[month]['income'] += transaction['amount']
            elif transaction['type'] == 'expense':
                monthly_data[month]['expenses'] += transaction['amount']
    
    # Fill in missing months with zero values
    for month in all_months:
        if month not in monthly_data:
            monthly_data[month] = {'income': 0, 'expenses': 0}
    
    # Convert to sorted list and calculate net worth progression
    months = sorted(all_months)
    net_worth_data = []
    
    # Calculate current actual net worth from account balances
    current_net_worth = 0
    for account in user_data['accounts']:
        current_net_worth += account['balance']
    
    # If we have multiple months, show progression
    if len(months) > 1:
        cumulative_net_worth = 0
        for i, month in enumerate(months):
            data = monthly_data.get(month, {'income': 0, 'expenses': 0})
            monthly_net = data['income'] - data['expenses']
            cumulative_net_worth += monthly_net
            
            # For the most recent month, use actual account balance
            if i == len(months) - 1:
                actual_net_worth = current_net_worth
            else:
                actual_net_worth = cumulative_net_worth
            
            net_worth_data.append({
                'month': month,
                'income': data['income'],
                'expenses': data['expenses'],
                'monthly_net': monthly_net,
                'cumulative_net_worth': actual_net_worth
            })
    else:
        # Single month or no historical data - show current account balance
        if months:
            month = months[0]
            data = monthly_data.get(month, {'income': 0, 'expenses': 0})
            net_worth_data.append({
                'month': month,
                'income': data['income'],
                'expenses': data['expenses'],
                'monthly_net': data['income'] - data['expenses'],
                'cumulative_net_worth': current_net_worth
            })
        else:
            # No transaction data in range - show current state
            current_month = get_current_month()
            net_worth_data.append({
                'month': current_month,
                'income': 0,
                'expenses': 0,
                'monthly_net': 0,
                'cumulative_net_worth': current_net_worth
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
        start_year, start_month = year, month
        for _ in range(2):
            start_month -= 1
            if start_month == 0:
                start_month = 12
                start_year -= 1
        
        start_date = f"{start_year}-{start_month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        return start_date, end_date
    
    elif period_type == "last_6_months":
        start_year, start_month = year, month
        for _ in range(5):
            start_month -= 1
            if start_month == 0:
                start_month = 12
                start_year -= 1
        
        start_date = f"{start_year}-{start_month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        return start_date, end_date
    
    elif period_type == "last_12_months":
        start_year, start_month = year, month
        for _ in range(11):
            start_month -= 1
            if start_month == 0:
                start_month = 12
                start_year -= 1
        
        start_date = f"{start_year}-{start_month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        return start_date, end_date
    
    else:
        return get_date_range_for_period(base_month, "current_month")

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

def get_expense_transactions(limit=50):
    """Get recent expense transactions for lifecycle cost analysis"""
    user_data = get_user_data()
    
    # Filter expense transactions
    expense_transactions = [
        t for t in user_data['transactions'] 
        if t['type'] == 'expense'
    ]
    
    # Sort by date (most recent first)
    sorted_transactions = sorted(
        expense_transactions, 
        key=lambda x: x['date'], 
        reverse=True
    )[:limit]
    
    # Format for compatibility with existing code
    transactions = []
    for transaction in sorted_transactions:
        category_name = "Unknown"
        if transaction['category_id']:
            for category in user_data['categories']:
                if category['id'] == transaction['category_id']:
                    category_name = category['name']
                    break
        
        transactions.append((
            transaction['id'],
            transaction['date'],
            transaction['description'],
            transaction['amount'],
            category_name
        ))
    
    return transactions

def show():
    """Main reports page"""
    st.title("📊 Bitcoin Budget Reports")
    
    # Report type selector
    report_type = st.selectbox(
        "Choose Report Type",
        ["📊 Spending Breakdown", "📈 Net Worth Analysis", "🚀 Net Worth Future Value", "🔮 Future Purchasing Power", "⏳ Lifecycle Cost Analysis"],
        index=0
    )
    
    if report_type == "📊 Spending Breakdown":
        spending_breakdown_report()
    elif report_type == "📈 Net Worth Analysis":
        net_worth_report()
    elif report_type == "🚀 Net Worth Future Value":
        net_worth_future_value_report()
    elif report_type == "🔮 Future Purchasing Power":
        future_purchasing_power_report()
    elif report_type == "⏳ Lifecycle Cost Analysis":
        lifecycle_cost_report()

def spending_breakdown_report():
    """Spending breakdown report with pie chart"""
    st.markdown("## 📊 Spending Breakdown Analysis")
    st.markdown("*Analyze your spending patterns by category*")
    
    current_month = st.session_state.current_month
    
    # Time period selection
    st.markdown("### ⏰ Time Period")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Current Month", use_container_width=True):
            period_type = "current_month"
            st.session_state.spending_period = period_type
    
    with col2:
        if st.button("Last 3 Months", use_container_width=True):
            period_type = "last_3_months"
            st.session_state.spending_period = period_type
    
    with col3:
        if st.button("Last 6 Months", use_container_width=True):
            period_type = "last_6_months"
            st.session_state.spending_period = period_type
    
    with col4:
        if st.button("Last 12 Months", use_container_width=True):
            period_type = "last_12_months"
            st.session_state.spending_period = period_type
    
    # Initialize default period
    if 'spending_period' not in st.session_state:
        st.session_state.spending_period = "current_month"
    
    # Get date range
    start_date, end_date = get_date_range_for_period(current_month, st.session_state.spending_period)
    
    # Display current period
    period_descriptions = {
        "current_month": f"Current Month: {current_month}",
        "last_3_months": f"Last 3 Months: {start_date} to {end_date}",
        "last_6_months": f"Last 6 Months: {start_date} to {end_date}",
        "last_12_months": f"Last 12 Months: {start_date} to {end_date}"
    }
    
    st.info(f"📅 **{period_descriptions[st.session_state.spending_period]}**")
    
    # Get spending data
    breakdown, total_spent = get_spending_breakdown(start_date, end_date)
    
    if breakdown:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create pie chart
            df = pd.DataFrame(breakdown)
            
            fig = px.pie(
                df, 
                values='amount', 
                names='category',
                title=f'Spending Breakdown - Total: {format_sats(total_spent)}',
                hover_data=['percentage'],
                labels={'amount': 'Amount (sats)', 'percentage': 'Percentage'}
            )
            
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>' +
                             'Amount: %{customdata[0]:.1f}%<br>' +
                             'Value: %{value:,} sats<extra></extra>'
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Display breakdown table
            st.markdown("### 📋 Category Details")
            
            table_data = []
            for item in breakdown:
                table_data.append({
                    'Category': item['category'],
                    'Amount': format_sats(item['amount']),
                    'Percentage': f"{item['percentage']:.1f}%"
                })
            
            df_table = pd.DataFrame(table_data)
            st.dataframe(df_table, use_container_width=True, hide_index=True)
            
            # Summary metrics
            st.markdown("### 📊 Summary")
            st.metric("Total Spending", format_sats(total_spent))
            st.metric("Categories", len(breakdown))
            
            if breakdown:
                top_category = max(breakdown, key=lambda x: x['amount'])
                st.metric("Top Category", f"{top_category['category']}")
    else:
        st.info("No spending data found for the selected period.")

def net_worth_report():
    """Net worth analysis report with bar charts"""
    st.markdown("## 📈 Net Worth Analysis")
    st.markdown("*Track your income vs expenses over time*")
    
    current_month = st.session_state.current_month
    
    # Time period selection
    st.markdown("### ⏰ Time Period")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Current Month", use_container_width=True, key="nw_current"):
            st.session_state.networth_period = "current_month"
    
    with col2:
        if st.button("Last 3 Months", use_container_width=True, key="nw_3m"):
            st.session_state.networth_period = "last_3_months"
    
    with col3:
        if st.button("Last 6 Months", use_container_width=True, key="nw_6m"):
            st.session_state.networth_period = "last_6_months"
    
    with col4:
        if st.button("Last 12 Months", use_container_width=True, key="nw_12m"):
            st.session_state.networth_period = "last_12_months"
    
    # Initialize default period
    if 'networth_period' not in st.session_state:
        st.session_state.networth_period = "last_6_months"
    
    # Get date range
    start_date, end_date = get_date_range_for_period(current_month, st.session_state.networth_period)
    
    # Display current period
    period_descriptions = {
        "current_month": f"Current Month: {current_month}",
        "last_3_months": f"Last 3 Months: {start_date} to {end_date}",
        "last_6_months": f"Last 6 Months: {start_date} to {end_date}",
        "last_12_months": f"Last 12 Months: {start_date} to {end_date}"
    }
    
    st.info(f"📅 **{period_descriptions[st.session_state.networth_period]}**")
    
    # Add spacing
    st.markdown("---")
    
    # Get net worth data
    net_worth_data = get_net_worth_data(start_date, end_date)
    
    if net_worth_data:
        # Create the chart
        months = [item['month'] for item in net_worth_data]
        income = [item['income'] for item in net_worth_data]
        expenses = [item['expenses'] for item in net_worth_data]
        cumulative = [item['cumulative_net_worth'] for item in net_worth_data]
        
        # Create subplots with increased height and spacing
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Monthly Income vs Expenses', 'Cumulative Net Worth'),
            vertical_spacing=0.25,  # Increased spacing significantly for more room
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Income and expenses bars
        fig.add_trace(
            go.Bar(x=months, y=income, name='Income', marker_color='#2E8B57', opacity=0.8),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=months, y=expenses, name='Expenses', marker_color='#DC143C', opacity=0.8),
            row=1, col=1
        )
        
        # Cumulative net worth line
        fig.add_trace(
            go.Scatter(x=months, y=cumulative, mode='lines+markers', 
                      name='Cumulative Net Worth', line=dict(color='#4169E1', width=3),
                      marker=dict(size=8)),
            row=2, col=1
        )
        
        # Update layout with increased height and better spacing
        fig.update_layout(
            height=900,  # Increased from 800 to accommodate more spacing
            title_text="Net Worth Analysis",
            showlegend=True,
            title_font_size=16,
            margin=dict(t=100, b=100, l=80, r=80)  # Increased top/bottom margins
        )
        
        # Format y-axes with better formatting and spacing
        fig.update_yaxes(
            title_text="Amount (sats)", 
            row=1, col=1, 
            title_font_size=14,
            title_standoff=20  # Add space between axis and title
        )
        fig.update_yaxes(
            title_text="Cumulative Net Worth (sats)", 
            row=2, col=1, 
            title_font_size=14,
            title_standoff=20  # Add space between axis and title
        )
        fig.update_xaxes(
            title_text="Month", 
            row=2, col=1, 
            title_font_size=14,
            title_standoff=20  # Add space between axis and title
        )
        
        # Update subplot title formatting for better spacing
        fig.update_annotations(font_size=16, font_color="white")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add spacing before summary
        st.markdown("---")
        st.markdown("### 📊 Summary Metrics")
        
        # Summary metrics with more spacing
        col1, col2, col3, col4 = st.columns(4)
        
        total_income = sum(income)
        total_expenses = sum(expenses)
        final_net_worth = cumulative[-1] if cumulative else 0
        avg_monthly_net = (total_income - total_expenses) / len(months) if months else 0
        
        with col1:
            st.metric("Total Income", format_sats(total_income))
        
        with col2:
            st.metric("Total Expenses", format_sats(total_expenses))
        
        with col3:
            st.metric("Current Net Worth", format_sats(final_net_worth))
        
        with col4:
            st.metric("Avg Monthly Net", format_sats(int(avg_monthly_net)))
        
        # Account breakdown
        st.markdown("### 🏦 Account Breakdown")
        user_data = get_user_data()
        
        account_data = []
        tracked_total = 0
        untracked_total = 0
        
        for account in user_data['accounts']:
            account_data.append({
                'Account': account['name'],
                'Type': 'Tracked' if account['is_tracked'] else 'Untracked',
                'Balance': format_sats(account['balance'])
            })
            
            if account['is_tracked']:
                tracked_total += account['balance']
            else:
                untracked_total += account['balance']
        
        if account_data:
            df_accounts = pd.DataFrame(account_data)
            st.dataframe(df_accounts, use_container_width=True, hide_index=True)
            
            # Account summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tracked Accounts", format_sats(tracked_total))
            with col2:
                st.metric("Untracked Accounts", format_sats(untracked_total))
            with col3:
                st.metric("Total Balance", format_sats(tracked_total + untracked_total))
        else:
            st.info("No accounts configured. Add accounts to see detailed breakdown.")
            
    else:
        st.info("No financial data found for the selected period.")

def net_worth_future_value_report():
    """Net worth future value analysis - show the power of HODLing Bitcoin"""
    st.markdown("## 🚀 Net Worth Future Value Analysis")
    st.markdown("*Discover the future purchasing power of your Bitcoin stack*")
    
    user_data = get_user_data()
    
    # Calculate current net worth
    current_net_worth_sats = sum(account['balance'] for account in user_data['accounts'])
    
    if current_net_worth_sats <= 0:
        st.warning("💡 **Add some Bitcoin to your accounts to see your future purchasing power!**")
        st.info("Go to the Accounts tab to add your Bitcoin holdings and see how they could grow over time.")
        return
    
    # Settings section
    st.markdown("### ⚙️ Analysis Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        # Inflation rate
        inflation_rate = st.slider(
            "Annual Inflation Rate:",
            min_value=0.0,
            max_value=15.0,
            value=8.0,
            step=0.5,
            format="%.1f%%",
            help="Expected annual debasement of fiat currency"
        ) / 100.0
        
        # Monthly DCA option
        monthly_dca_sats = st.number_input(
            "Additional Monthly Stacking (sats):",
            min_value=0,
            value=0,
            step=10000,
            help="How many sats you plan to stack each month"
        )
    
    with col2:
        # Current net worth display
        st.markdown("### 💎 Current Bitcoin Stack")
        today = datetime.now()
        current_days = get_days_since_genesis(today)
        current_btc_price = calculate_btc_fair_value(current_days)
        current_usd_value = (current_net_worth_sats / 100_000_000) * current_btc_price
        
        st.metric("Net Worth", format_sats(current_net_worth_sats))
        st.metric("Current USD Value", f"${current_usd_value:,.2f}")
        st.metric("Bitcoin Price (Power Law)", f"${current_btc_price:,.0f}")
    
    # Time horizons
    time_horizons = [5, 10, 15, 20]
    
    # Calculate projections
    projections = []
    for years in time_horizons:
        # Calculate future Bitcoin price
        future_date = today + timedelta(days=years * 365.25)
        future_days = get_days_since_genesis(future_date)
        future_btc_price = calculate_btc_fair_value(future_days)
        
        # Calculate total sats (current + DCA)
        total_dca_sats = monthly_dca_sats * 12 * years
        total_sats = current_net_worth_sats + total_dca_sats
        
        # Calculate future values
        future_usd_value = (total_sats / 100_000_000) * future_btc_price
        inflation_adjusted_purchasing_power = future_usd_value / ((1 + inflation_rate) ** years)
        
        # Calculate gains
        bitcoin_gain = ((future_btc_price / current_btc_price) - 1) * 100
        real_purchasing_power_multiplier = inflation_adjusted_purchasing_power / current_usd_value
        
        projections.append({
            'Years': years,
            'Total Sats': total_sats,
            'Bitcoin Price': future_btc_price,
            'Future USD Value': future_usd_value,
            'Real Purchasing Power': inflation_adjusted_purchasing_power,
            'Bitcoin Gain %': bitcoin_gain,
            'Purchasing Power Multiplier': real_purchasing_power_multiplier
        })
    
    # === MAIN VISUALIZATION ===
    st.markdown("---")
    st.markdown("### 🎯 Future Value Projections")
    
    # Create dramatic visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "🚀 Bitcoin Price Growth (Power Law)",
            "💰 Your Stack Value Growth", 
            "📈 Real Purchasing Power Growth",
            "🎯 Purchasing Power Multiplier"
        ),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    years = [p['Years'] for p in projections]
    
    # 1. Bitcoin price growth
    current_price_line = [current_btc_price] * len(years)
    future_prices = [p['Bitcoin Price'] for p in projections]
    
    fig.add_trace(
        go.Scatter(x=years, y=current_price_line, mode='lines', 
                  name='Current Price', line=dict(color='gray', dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=years, y=future_prices, mode='lines+markers',
                  name='Future Price', line=dict(color='#FF6B35', width=4),
                  marker=dict(size=10)),
        row=1, col=1
    )
    
    # 2. Stack value growth
    current_value_bars = [current_usd_value] * len(years)
    future_values = [p['Future USD Value'] for p in projections]
    
    fig.add_trace(
        go.Bar(x=years, y=current_value_bars, name='Current Value',
               marker_color='lightgray', opacity=0.6),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=years, y=future_values, name='Future Value',
               marker_color='#2E8B57'),
        row=1, col=2
    )
    
    # 3. Real purchasing power
    real_power = [p['Real Purchasing Power'] for p in projections]
    fig.add_trace(
        go.Bar(x=years, y=real_power, name='Real Purchasing Power',
               marker_color='#4169E1'),
        row=2, col=1
    )
    
    # 4. Purchasing power multiplier
    multipliers = [p['Purchasing Power Multiplier'] for p in projections]
    fig.add_trace(
        go.Bar(x=years, y=multipliers, name='Power Multiplier',
               marker_color='#9370DB', showlegend=False),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="🚀 The Power of HODLing Bitcoin",
        title_font_size=20,
        showlegend=True,
        title_x=0.5
    )
    
    # Format axes
    fig.update_yaxes(title_text="Bitcoin Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="USD Value", row=1, col=2)
    fig.update_yaxes(title_text="Real Purchasing Power (USD)", row=2, col=1)
    fig.update_yaxes(title_text="Multiplier", row=2, col=2)
    fig.update_xaxes(title_text="Years", row=2, col=1)
    fig.update_xaxes(title_text="Years", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # === DETAILED PROJECTIONS TABLE ===
    st.markdown("---")
    st.markdown("### 📊 Detailed Projections")
    
    # Format data for display
    display_data = []
    for p in projections:
        display_data.append({
            'Time Horizon': f"{p['Years']} years",
            'Total Stack': format_sats(p['Total Sats']),
            'Bitcoin Price': f"${p['Bitcoin Price']:,.0f}",
            'Stack Value': f"${p['Future USD Value']:,.0f}",
            'Real Purchasing Power': f"${p['Real Purchasing Power']:,.0f}",
            'BTC Gain': f"+{p['Bitcoin Gain %']:.0f}%",
            'Power Multiplier': f"{p['Purchasing Power Multiplier']:.1f}x"
        })
    
    df_projections = pd.DataFrame(display_data)
    st.dataframe(df_projections, use_container_width=True, hide_index=True)
    
    # === MOTIVATIONAL INSIGHTS ===
    st.markdown("---")
    st.markdown("### 💡 Key Insights")
    
    # Pick the 10-year projection for highlights
    ten_year = next((p for p in projections if p['Years'] == 10), projections[1] if len(projections) > 1 else projections[0])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Bitcoin Price (10Y)",
            f"${ten_year['Bitcoin Price']:,.0f}",
            delta=f"+{ten_year['Bitcoin Gain %']:.0f}%"
        )
    
    with col2:
        st.metric(
            "Your Stack Value (10Y)",
            f"${ten_year['Future USD Value']:,.0f}",
            delta=f"${ten_year['Future USD Value'] - current_usd_value:,.0f}"
        )
    
    with col3:
        st.metric(
            "Real Purchasing Power (10Y)",
            f"${ten_year['Real Purchasing Power']:,.0f}",
            delta=f"{ten_year['Purchasing Power Multiplier']:.1f}x current"
        )
    
    with col4:
        if monthly_dca_sats > 0:
            total_dca_usd = (monthly_dca_sats * 12 * 10 / 100_000_000) * current_btc_price
            st.metric(
                "DCA Investment (10Y)",
                f"${total_dca_usd:,.0f}",
                delta=f"{format_sats(monthly_dca_sats * 12 * 10)}"
            )
        else:
            st.metric(
                "Start DCA?",
                "Add monthly stacking",
                delta="Compound growth!"
            )
    
    # === MOTIVATIONAL MESSAGE ===
    st.markdown("---")
    
    # Create inspiring message based on the projections
    twenty_year = projections[-1]  # Last projection (20 years)
    
    st.markdown(f"""
    ### 🎯 The Power of Time and Patience
    
    **Your current {format_sats(current_net_worth_sats)} could become:**
    
    - 💎 **Real purchasing power of ${twenty_year['Real Purchasing Power']:,.0f}** in 20 years
    - 🚀 **That's {twenty_year['Purchasing Power Multiplier']:.1f}x your current purchasing power!**
    - 📈 **Bitcoin price could reach ${twenty_year['Bitcoin Price']:,.0f}** (Power Law projection)
    
    **Key Takeaways:**
    - ⏰ **Time is your greatest ally** - Bitcoin's scarcity + time = wealth preservation
    - 🔒 **HODLing beats timing** - Stay humble and stack sats
    - 📈 **DCA amplifies growth** - Regular stacking compounds exponentially
    - 💪 **Your future self will thank you** - Every sat counts in the long run
    
    *"The best time to plant a tree was 20 years ago. The second best time is now."*
    """)
    
    # Add DCA encouragement if not already doing it
    if monthly_dca_sats == 0:
        st.info("""
        💡 **Pro Tip:** Try adding even 10,000 sats/month to see how DCA accelerates your wealth building!
        Small consistent investments can have massive long-term impact.
        """)

def future_purchasing_power_report():
    """Future purchasing power analysis"""
    st.markdown("## 🔮 Future Purchasing Power Analysis")
    st.markdown("*Analyze how Bitcoin appreciation affects your spending needs*")
    
    current_month = st.session_state.current_month
    
    # Settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Analysis Settings")
        
        # Budget period selection
        budget_period = st.selectbox(
            "Base Budget Period:",
            ["current_month", "last_3_months", "last_6_months", "last_12_months"],
            index=0,
            format_func=lambda x: {
                "current_month": "Current Month",
                "last_3_months": "Last 3 Months",
                "last_6_months": "Last 6 Months", 
                "last_12_months": "Last 12 Months"
            }[x]
        )
        
        # Inflation rate
        inflation_rate = st.slider(
            "Annual Inflation Rate:",
            min_value=0.0,
            max_value=15.0,
            value=8.0,
            step=0.5,
            format="%.1f%%"
        ) / 100.0
        
        # Time horizons
        years_options = [1, 2, 5, 10]
        selected_years = st.multiselect(
            "Time Horizons (years):",
            years_options,
            default=[1, 2, 5, 10]
        )
    
    with col2:
        st.markdown("### 📊 Current Budget Base")
        
        # Get base budget using the same logic as Spending Breakdown
        start_date, end_date = get_date_range_for_period(current_month, budget_period)
        breakdown, total_spending = get_spending_breakdown(start_date, end_date)
        
        period_desc = {
            "current_month": f"Current month spending",
            "last_3_months": f"Average monthly spending (last 3 months)",
            "last_6_months": f"Average monthly spending (last 6 months)",
            "last_12_months": f"Average monthly spending (last 12 months)"
        }
        
        # For multi-month periods, convert to monthly averages for projections
        monthly_total_spending = total_spending
        monthly_breakdown = breakdown[:]  # Copy the breakdown list
        
        if budget_period != "current_month":
            months_count = {"last_3_months": 3, "last_6_months": 6, "last_12_months": 12}[budget_period]
            monthly_total_spending = total_spending / months_count
            
            # Adjust breakdown categories proportionally for monthly average
            monthly_breakdown = []
            for item in breakdown:
                monthly_breakdown.append({
                    'category': item['category'],
                    'amount': item['amount'] / months_count,
                    'percentage': item['percentage']  # Percentage stays the same
                })
        
        st.info(f"📅 {period_desc[budget_period]}")
        st.metric("Base Monthly Budget", format_sats(int(monthly_total_spending)))
        
        # Show current tracked account balance for context
        user_data = get_user_data()
        tracked_balance = sum(account['balance'] for account in user_data['accounts'] if account['is_tracked'])
        months_of_runway = int(tracked_balance / monthly_total_spending) if monthly_total_spending > 0 else 0
        
        st.metric("Tracked Account Balance", format_sats(tracked_balance))
        if months_of_runway > 0:
            st.metric("Months of Runway", f"{months_of_runway} months")
    
    if monthly_total_spending > 0 and selected_years:
        # Calculate projections using monthly averages
        projections = []
        today = datetime.now()
        current_days = get_days_since_genesis(today)
        current_btc_price = calculate_btc_fair_value(current_days)
        
        for years in selected_years:
            future_budget, reduction_percentage = calculate_future_purchasing_power(
                monthly_total_spending, years, inflation_rate
            )
            
            # Calculate future Bitcoin price
            future_date = today + timedelta(days=years * 365.25)
            future_days = get_days_since_genesis(future_date)
            future_btc_price = calculate_btc_fair_value(future_days)
            btc_gain = ((future_btc_price / current_btc_price) - 1) * 100
            
            projections.append({
                'Years': years,
                'Current Budget': format_sats(int(monthly_total_spending)),
                'Future Budget': format_sats(int(future_budget)),
                'Reduction': f"-{reduction_percentage:.1f}%",
                'BTC Price': f"${future_btc_price:,.0f}",
                'BTC Gain': f"+{btc_gain:.1f}%"
            })
        
        # === VISUALIZATION FIRST (moved above table) ===
        # Create visualization using the monthly breakdown
        if monthly_breakdown:
            st.markdown("---")
            st.markdown("### 🥧 Spending Comparison: Current vs Future")
            
            # Create comparison for 5-year projection
            five_year_data = next((p for p in projections if p['Years'] == 5), projections[0] if projections else None)
            
            if five_year_data:
                years_ahead = five_year_data['Years']
                future_budget, _ = calculate_future_purchasing_power(monthly_total_spending, years_ahead, inflation_rate)
                
                # Create side-by-side pie charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Current spending pie (using monthly breakdown)
                    df_current = pd.DataFrame(monthly_breakdown)
                    fig1 = px.pie(
                        df_current,
                        values='amount',
                        names='category',
                        title=f'Current Monthly Spending\n{format_sats(int(monthly_total_spending))}'
                    )
                    fig1.update_layout(height=500)  # Increased height
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Future spending pie with Bitcoin Vibes
                    future_categories = []
                    future_amounts = []
                    
                    # Scale down current categories proportionally
                    scale_factor = future_budget / monthly_total_spending
                    for item in monthly_breakdown:
                        future_categories.append(item['category'])
                        future_amounts.append(item['amount'] * scale_factor)
                    
                    # Add Bitcoin Vibes category for the savings
                    bitcoin_vibes_amount = monthly_total_spending - future_budget
                    if bitcoin_vibes_amount > 0:
                        future_categories.append("🚀 Bitcoin Vibes")
                        future_amounts.append(bitcoin_vibes_amount)
                    
                    df_future = pd.DataFrame({
                        'category': future_categories,
                        'amount': future_amounts
                    })
                    
                    fig2 = px.pie(
                        df_future,
                        values='amount',
                        names='category',
                        title=f'Future Monthly Spending ({years_ahead} years)\nSame purchasing power: {format_sats(int(future_budget))}'
                    )
                    fig2.update_layout(height=500)  # Increased height
                    st.plotly_chart(fig2, use_container_width=True)
        
        # === PROJECTIONS TABLE (moved below visualization) ===
        st.markdown("---")
        st.markdown("### 📈 Future Purchasing Power Projections")
        df = pd.DataFrame(projections)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    else:
        if monthly_total_spending <= 0:
            st.warning("No spending data found for the selected period.")
        if not selected_years:
            st.warning("Please select at least one time horizon.")

def lifecycle_cost_report():
    """Lifecycle cost analysis for individual transactions"""
    st.markdown("## ⏳ Lifecycle Cost Analysis")
    st.markdown("*Analyze the opportunity cost of individual purchases*")
    
    # Get expense transactions
    transactions = get_expense_transactions(100)
    
    if not transactions:
        st.warning("No expense transactions found. Add some expenses first!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🛍️ Select Transaction")
        
        # Create transaction options
        transaction_options = []
        transaction_data = {}
        
        for trans in transactions:
            trans_id, date_str, desc, amount, category = trans
            option = f"{date_str} | {desc} | {format_sats(amount)} | {category}"
            transaction_options.append(option)
            transaction_data[option] = {
                'id': trans_id,
                'date': date_str,
                'description': desc,
                'amount': amount,
                'category': category
            }
        
        selected_option = st.selectbox(
            "Choose an expense to analyze:",
            transaction_options,
            index=0
        )
        
        selected_transaction = transaction_data[selected_option]
    
    with col2:
        st.markdown("### ⚙️ Analysis Settings")
        
        years_ahead = st.radio(
            "Time Horizon:",
            options=[1, 2, 5, 10],
            index=2,  # Default to 5 years
            help="How far into the future to project"
        )
        
        inflation_rate = st.slider(
            "Annual Inflation Rate:",
            min_value=0.0,
            max_value=15.0,
            value=8.0,
            step=0.5,
            format="%.1f%%",
            help="Expected annual inflation rate"
        ) / 100.0
    
    st.markdown("---")
    
    # Calculate opportunity cost
    amount_sats = selected_transaction['amount']
    today = datetime.now()
    future_date = today + timedelta(days=years_ahead * 365.25)
    
    current_days = get_days_since_genesis(today)
    future_days = get_days_since_genesis(future_date)
    
    current_btc_price = calculate_btc_fair_value(current_days)
    future_btc_price = calculate_btc_fair_value(future_days)
    
    # Calculate USD values of the SAME amount of sats
    current_usd_value = (amount_sats / 100_000_000) * current_btc_price
    future_usd_value = (amount_sats / 100_000_000) * future_btc_price
    
    # Calculate inflation-adjusted value
    inflation_multiplier = (1 + inflation_rate) ** years_ahead
    inflation_adjusted_value = current_usd_value * inflation_multiplier
    
    # Calculate metrics
    bitcoin_gain_percentage = ((future_btc_price / current_btc_price) - 1) * 100
    opportunity_cost_usd = future_usd_value - current_usd_value
    real_purchasing_power_gain = future_usd_value / inflation_adjusted_value
    
    # Key insights metrics
    st.markdown("### 💡 Key Insights")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💸 Amount Spent",
            value=format_sats(amount_sats),
            delta=f"${current_usd_value:,.2f}"
        )
    
    with col2:
        st.metric(
            label="🚀 Future Value",
            value=f"${future_usd_value:,.2f}",
            delta=f"+{bitcoin_gain_percentage:.1f}%"
        )
    
    with col3:
        st.metric(
            label="💔 Opportunity Cost",
            value=f"${opportunity_cost_usd:,.2f}",
            delta=f"-{opportunity_cost_usd/current_usd_value*100:.1f}%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="📈 Purchasing Power",
            value=f"{real_purchasing_power_gain:.1f}x",
            delta="vs inflation"
        )
    
    # Interactive charts
    st.markdown("### 📊 Visual Analysis")
    
    tab1, tab2, tab3 = st.tabs(["💰 Value Comparison", "📈 Bitcoin Price", "🥧 Opportunity Cost"])
    
    with tab1:
        # Value comparison charts
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Bitcoin Amount (Unchanged)", "USD Value Comparison"),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Bitcoin amount (stays the same)
        fig.add_trace(
            go.Bar(
                x=["Amount Spent", f"Same Amount in {years_ahead} Years"],
                y=[amount_sats/1000, amount_sats/1000],
                name="Bitcoin Amount (K sats)",
                marker_color=["#DC143C", "#2E8B57"],
                showlegend=False
            ),
            row=1, col=1
        )
        
        # USD value comparison
        fig.add_trace(
            go.Bar(
                x=["Purchase Value", f"Future BTC Value", "Purchase + Inflation"],
                y=[current_usd_value, future_usd_value, inflation_adjusted_value],
                name="USD Value",
                marker_color=["#DC143C", "#2E8B57", "#FFD700"],
                showlegend=False
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=500,
            title_text=f"Analysis: {selected_transaction['description']}"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Bitcoin price progression
        years_range = list(range(years_ahead + 1))
        price_progression = []
        for year in years_range:
            future_days_year = get_days_since_genesis(today + timedelta(days=year * 365.25))
            price = calculate_btc_fair_value(future_days_year)
            price_progression.append(price)
        
        fig = px.line(
            x=years_range,
            y=price_progression,
            title=f"Bitcoin Price Projection ({years_ahead} Years)",
            labels={"x": "Years Ahead", "y": "Bitcoin Price (USD)"},
            markers=True
        )
        
        fig.update_traces(line_color="#FF8C00", line=dict(width=3), marker=dict(size=8))
        fig.update_layout(height=500)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Opportunity cost pie chart
        if opportunity_cost_usd > 0:
            pie_data = pd.DataFrame({
                'Category': ['Purchase Value', 'Opportunity Cost'],
                'Value': [current_usd_value, opportunity_cost_usd]
            })
            
            fig = px.pie(
                pie_data,
                values='Value',
                names='Category',
                title=f"Total Opportunity Cost: ${opportunity_cost_usd:,.0f}",
                color_discrete_sequence=['#DC143C', '#32CD32']
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No opportunity cost in this scenario (rare!)")
    
    # Detailed analysis
    with st.expander("📝 Detailed Analysis", expanded=True):
        st.markdown(f"""
        **🛍️ Purchase Details:**
        - **Item:** {selected_transaction['description']}
        - **Category:** {selected_transaction['category']}
        - **Date:** {selected_transaction['date']}
        - **Amount Spent:** {format_sats(amount_sats)}
        
        **📈 Opportunity Cost Analysis ({years_ahead} year{'s' if years_ahead > 1 else ''}):**
        
        - **Current Bitcoin Price:** ${current_btc_price:,.0f}
        - **Future Bitcoin Price:** ${future_btc_price:,.0f} (Power Law Projection)
        - **Bitcoin Price Appreciation:** +{bitcoin_gain_percentage:.1f}%
        
        **💸 What You Spent:**
        - **Bitcoin Amount:** {format_sats(amount_sats)}
        - **USD Value (then):** ${current_usd_value:,.2f}
        
        **🚀 What Those Same {format_sats(amount_sats)} Would Be Worth:**
        - **Bitcoin Amount:** {format_sats(amount_sats)} (same amount!)
        - **Future USD Value:** ${future_usd_value:,.2f}
        
        **💔 Opportunity Cost:**
        - **Foregone USD Appreciation:** ${opportunity_cost_usd:,.2f}
        - **Your {format_sats(amount_sats)} would have grown {bitcoin_gain_percentage:.1f}% in USD terms**
        
        **📊 Inflation Comparison:**
        - **Your Purchase + Inflation:** ${inflation_adjusted_value:,.2f}
        - **Same Bitcoin USD Value:** ${future_usd_value:,.2f}
        - **Real Purchasing Power Gain:** {real_purchasing_power_gain:.1f}x
        
        **🎯 Bottom Line:**
        Instead of buying "{selected_transaction['description']}" for {format_sats(amount_sats)}, 
        if you had held that Bitcoin for {years_ahead} year{'s' if years_ahead > 1 else ''}, those same 
        {format_sats(amount_sats)} would be worth **${opportunity_cost_usd:,.2f} MORE** in USD terms 
        (even after accounting for {inflation_rate*100:.0f}% annual inflation).
        
        This represents a **{real_purchasing_power_gain:.1f}x improvement in purchasing power!**
        """) 
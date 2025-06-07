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
    """Get current month from session state"""
    return st.session_state.current_month

def parse_amount_input(text):
    """Parse user input to satoshis"""
    if not text:
        return 0
    # Remove commas and spaces
    text = text.replace(',', '').replace(' ', '').lower()
    if 'btc' in text:
        btc_amount = float(text.replace('btc', ''))
        return int(btc_amount * 100_000_000)
    return int(float(text))

def get_spending_breakdown(start_date, end_date):
    """Get spending breakdown by category for date range"""
    user_data = get_user_data()
    
    # Filter transactions by date range and type
    category_spending = {}
    total_spent = 0
    
    for transaction in user_data['transactions']:
        if (transaction['type'] == 'expense' and 
            start_date <= transaction['date'] <= end_date):
            
            category_id = transaction['category_id']
            amount = transaction['amount']
            
            # Find category name
            category_name = 'Unknown'
            for category in user_data['categories']:
                if category['id'] == category_id:
                    category_name = category['name']
                    break
            
            if category_name not in category_spending:
                category_spending[category_name] = 0
            category_spending[category_name] += amount
            total_spent += amount
    
    # Convert to list format with percentages
    breakdown = []
    for category, amount in category_spending.items():
        percentage = (amount / total_spent * 100) if total_spent > 0 else 0
        breakdown.append({
            'category': category,
            'amount': amount,
            'percentage': percentage
        })
    
    # Sort by amount descending
    breakdown.sort(key=lambda x: x['amount'], reverse=True)
    
    return breakdown, total_spent

def get_net_worth_data(start_date, end_date):
    """Get net worth data for date range"""
    user_data = get_user_data()
    
    # Group transactions by month
    monthly_data = {}
    
    for transaction in user_data['transactions']:
        if start_date <= transaction['date'] <= end_date:
            # Extract year-month
            date_parts = transaction['date'].split('-')
            month_key = f"{date_parts[0]}-{date_parts[1]}"
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {'income': 0, 'expenses': 0}
            
            if transaction['type'] == 'income':
                monthly_data[month_key]['income'] += transaction['amount']
            elif transaction['type'] == 'expense':
                monthly_data[month_key]['expenses'] += transaction['amount']
    
    # Convert to list and calculate cumulative
    net_worth_data = []
    cumulative_net_worth = 0
    
    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        monthly_net = data['income'] - data['expenses']
        cumulative_net_worth += monthly_net
        
        net_worth_data.append({
            'month': month,
            'income': data['income'],
            'expenses': data['expenses'],
            'net_worth': monthly_net,
            'cumulative_net_worth': cumulative_net_worth
        })
    
    return net_worth_data

def get_date_range_for_period(base_month, period_type):
    """Get start and end dates for a period"""
    # Parse base month (format: "2024-12")
    year, month = map(int, base_month.split('-'))
    
    if period_type == "current_month":
        start_date = f"{year:04d}-{month:02d}-01"
        # Get last day of month
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    
    elif period_type == "last_3_months":
        # Go back 3 months from base month
        start_month = month - 2
        start_year = year
        if start_month <= 0:
            start_month += 12
            start_year -= 1
        start_date = f"{start_year:04d}-{start_month:02d}-01"
        
        # End at last day of base month
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    
    elif period_type == "last_6_months":
        # Go back 6 months from base month
        start_month = month - 5
        start_year = year
        if start_month <= 0:
            start_month += 12
            start_year -= 1
        start_date = f"{start_year:04d}-{start_month:02d}-01"
        
        # End at last day of base month
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    
    elif period_type == "last_12_months":
        # Go back 12 months from base month
        start_month = month - 11
        start_year = year
        if start_month <= 0:
            start_month += 12
            start_year -= 1
        start_date = f"{start_year:04d}-{start_month:02d}-01"
        
        # End at last day of base month
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    
    return start_date, end_date

# === BITCOIN POWER LAW FUNCTIONS ===

def calculate_btc_fair_value(days_since_genesis):
    """Calculate Bitcoin fair value using Power Law"""
    return 1.0117e-17 * (days_since_genesis ** 5.82)

def get_days_since_genesis(target_date):
    """Calculate days since Bitcoin genesis block"""
    genesis_date = datetime(2009, 1, 3)
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d')
    return (target_date - genesis_date).days

def calculate_future_purchasing_power(current_budget_sats, years_ahead, inflation_rate=0.08):
    """Calculate future purchasing power considering Bitcoin appreciation vs inflation"""
    # Get current Bitcoin price
    today = datetime.now()
    current_days = get_days_since_genesis(today)
    current_btc_price = calculate_btc_fair_value(current_days)
    
    # Get future Bitcoin price
    future_date = today + timedelta(days=years_ahead * 365.25)
    future_days = get_days_since_genesis(future_date)
    future_btc_price = calculate_btc_fair_value(future_days)
    
    # Calculate Bitcoin appreciation
    btc_appreciation = future_btc_price / current_btc_price
    
    # Calculate inflation impact
    inflation_multiplier = (1 + inflation_rate) ** years_ahead
    
    # Net effect: Bitcoin appreciation vs inflation
    net_multiplier = btc_appreciation / inflation_multiplier
    
    # Future budget needed (in sats) for same purchasing power
    future_budget_sats = current_budget_sats / net_multiplier
    
    # Calculate reduction percentage
    reduction_percentage = ((current_budget_sats - future_budget_sats) / current_budget_sats) * 100
    
    return future_budget_sats, reduction_percentage

def get_expense_transactions(limit=50):
    """Get recent expense transactions"""
    user_data = get_user_data()
    
    # Filter and sort expense transactions
    expenses = []
    for transaction in user_data['transactions']:
        if transaction['type'] == 'expense':
            # Find category name
            category_name = 'Unknown'
            for category in user_data['categories']:
                if category['id'] == transaction['category_id']:
                    category_name = category['name']
                    break
            
            expenses.append((
                transaction['id'],
                transaction['date'],
                transaction['description'],
                transaction['account_id'],
                transaction['amount'],
                category_name
            ))
    
    # Sort by date descending (most recent first)
    expenses.sort(key=lambda x: x[1], reverse=True)
    
    return expenses[:limit]

# === MAIN REPORTS INTERFACE ===

def show():
    """Main reports page with consolidated report structure"""
    st.title("📊 Bitcoin Budget Reports")
    
    # Check if specific report type is set in session state (for cross-report navigation)
    if 'report_type' in st.session_state:
        if st.session_state.report_type == 'spending_analysis':
            default_index = 0
        elif st.session_state.report_type == 'net_worth_retirement':
            default_index = 1
        elif st.session_state.report_type == 'lifecycle_cost':
            default_index = 2
        else:
            default_index = 0
        # Clear the session state after using it
        del st.session_state.report_type
    else:
        default_index = 0
    
    # Consolidated report selector
    report_type = st.selectbox(
        "Choose Report Type",
        ["🛒 Spending Analysis", "🚀 Net Worth & Retirement Planning", "⏳ Lifecycle Cost Analysis"],
        index=default_index,
        help="Streamlined reports combining related analyses"
    )
    
    if report_type == "🛒 Spending Analysis":
        spending_analysis_report()
    elif report_type == "🚀 Net Worth & Retirement Planning":
        net_worth_retirement_report()
    elif report_type == "⏳ Lifecycle Cost Analysis":
        lifecycle_cost_report()

def spending_analysis_report():
    """Comprehensive spending analysis combining breakdown and future purchasing power"""
    st.markdown("## 🛒 Spending Analysis")
    st.markdown("*Analyze your spending patterns and understand their future impact*")
    
    current_month = st.session_state.current_month
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["📊 Spending Breakdown", "🔮 Future Purchasing Power"])
    
    with tab1:
        spending_breakdown_analysis()
    
    with tab2:
        future_purchasing_power_analysis()

def spending_breakdown_analysis():
    """Spending breakdown analysis component"""
    st.markdown("### 📊 Spending Breakdown by Category")
    
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

def future_purchasing_power_analysis():
    """Future purchasing power analysis component"""
    st.markdown("### 🔮 Future Cost of Your Spending")
    
    user_data = get_user_data()
    
    # Get recent expense transactions for analysis
    recent_expenses = get_expense_transactions(50)
    
    if not recent_expenses:
        st.warning("💡 **Add some expenses to see their future purchasing power impact!**")
        st.info("Record a few transactions in your budget to see how your current spending will affect your future Bitcoin purchasing power.")
        return
    
    # Settings
    col1, col2 = st.columns(2)
    
    with col1:
        inflation_rate = st.slider(
            "Annual Inflation Rate:",
            min_value=0.0,
            max_value=15.0,
            value=8.0,
            step=0.5,
            format="%.1f%%"
        ) / 100.0
    
    with col2:
        years_ahead = st.slider(
            "Years into Future:",
            min_value=1,
            max_value=20,
            value=10,
            step=1
        )
    
    # Prepare data for charts and analysis
    expense_analysis = []
    chart_data = []
    
    for expense in recent_expenses[:10]:  # Top 10 recent expenses
        current_amount = expense[4]  # amount in sats
        future_cost, reduction_percentage = calculate_future_purchasing_power(current_amount, years_ahead, inflation_rate)
        
        expense_analysis.append({
            'Date': expense[1],
            'Description': expense[2],
            'Category': expense[5] or 'Unknown',
            'Current Cost': format_sats(current_amount),
            'Future Equivalent': format_sats(int(future_cost)),
            'Inflation Impact': f"{((future_cost/current_amount - 1) * 100):.1f}%"
        })
        
        # Data for charts
        chart_data.append({
            'description': expense[2][:15] + '...' if len(expense[2]) > 15 else expense[2],
            'current': current_amount / 100_000_000,  # Convert to BTC equivalent for USD
            'future': future_cost / 100_000_000,
            'category': expense[5] or 'Unknown'
        })
    
    # CHARTS FIRST - Main visualization
    st.markdown("### 📊 Future Cost Impact Visualization")
    
    if chart_data:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Current vs Future Cost Comparison (Bar Chart)
            descriptions = [item['description'] for item in chart_data]
            current_values = [item['current'] for item in chart_data]
            future_values = [item['future'] for item in chart_data]
            
            fig_bar = go.Figure(data=[
                go.Bar(name='Current Cost', x=descriptions, y=current_values, marker_color='lightblue'),
                go.Bar(name=f'Cost in {years_ahead} Years', x=descriptions, y=future_values, marker_color='orange')
            ])
            
            fig_bar.update_layout(
                title='Current vs Future Purchasing Power',
                xaxis_title='Recent Purchases',
                yaxis_title='Cost (USD Equivalent)',
                barmode='group',
                height=400,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_chart2:
            # Category Impact Pie Chart
            category_impact = {}
            for item in chart_data:
                category = item['category']
                impact = item['future'] - item['current']
                if category in category_impact:
                    category_impact[category] += impact
                else:
                    category_impact[category] = impact
            
            fig_pie = px.pie(
                values=list(category_impact.values()),
                names=list(category_impact.keys()),
                title=f'Future Cost Impact by Category ({years_ahead} Years)',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Summary insights
    total_current = sum(expense[4] for expense in recent_expenses[:10])
    total_future = sum(calculate_future_purchasing_power(expense[4], years_ahead, inflation_rate)[0] 
                      for expense in recent_expenses[:10])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Total", format_sats(total_current))
    
    with col2:
        st.metric("Future Equivalent", format_sats(int(total_future)))
    
    with col3:
        impact = ((total_future/total_current - 1) * 100) if total_current > 0 else 0
        st.metric("Inflation Impact", f"+{impact:.1f}%")
    
    # TABLE AS SUPPORTING CAST
    st.markdown("### 📋 Detailed Analysis")
    df_analysis = pd.DataFrame(expense_analysis)
    st.dataframe(df_analysis, use_container_width=True, hide_index=True)

def net_worth_retirement_report():
    """Comprehensive net worth and retirement planning analysis"""
    st.markdown("## 🚀 Net Worth & Retirement Planning")
    st.markdown("*Track your wealth growth and plan your Bitcoin-based retirement*")
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["💰 Future Value Analysis", "🏖️ Retirement Planning"])
    
    with tab1:
        net_worth_future_value_analysis()
    
    with tab2:
        retire_on_bitcoin_analysis()

def retire_on_bitcoin_analysis():
    """Retire on Bitcoin analysis component"""
    st.markdown("### 🏖️ Bitcoin Retirement Planning")
    
    # User input controls
    col1, col2 = st.columns(2)
    
    with col1:
        annual_expenses = st.number_input(
            "Annual Retirement Expenses (USD):",
            min_value=10000,
            max_value=1000000,
            value=100000,
            step=5000,
            help="How much do you need per year in retirement?"
        )
        
        retirement_years = st.slider(
            "Years in Retirement:",
            min_value=10,
            max_value=50,
            value=50,
            step=5,
            help="Maximum retirement duration (50 years recommended)"
        )
        
    with col2:
        inflation_rate = st.slider(
            "Annual Inflation Rate:",
            min_value=0.0,
            max_value=15.0,
            value=8.0,
            step=0.5,
            format="%.1f%%",
            help="Expected annual inflation rate"
        ) / 100.0
        
        use_floor_price = st.checkbox(
            "Use Conservative Floor Price",
            value=False,
            help="Use 42% of Power Law Fair Price for extra safety margin"
        )
    
    # Calculate retirement BTC requirements
    start_year = 2025
    end_year = 2040
    years = list(range(start_year, end_year + 1))
    
    retirement_data = []
    
    for year in years:
        # Calculate minimum BTC needed to retire in this year
        min_btc_needed = calculate_minimum_btc_for_retirement(year, annual_expenses, inflation_rate, retirement_years, use_floor_price)
        
        # Get Bitcoin price for this retirement year
        target_date = datetime(year, 1, 1)
        days_since_genesis = get_days_since_genesis(target_date)
        btc_price_usd = calculate_btc_fair_value(days_since_genesis)
        
        retirement_data.append({
            'year': year,
            'btc_price': btc_price_usd,
            'btc_needed': min_btc_needed
        })
    
    # Create interactive chart
    df = pd.DataFrame(retirement_data)
    
    # Main chart: BTC needed over time
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['btc_needed'],
        mode='lines+markers',
        name='BTC Needed for Retirement',
        line=dict(color='#FF8C00', width=4),
        marker=dict(size=8, color='#FF8C00'),
        hovertemplate='<b>Year: %{x}</b><br>' +
                     'BTC Needed: %{y:.2f}<br>' +
                     '<extra></extra>'
    ))
    
    model_name = "Floor Price (42%)" if use_floor_price else "Fair Price"
    fig.update_layout(
        title=f'Minimum Bitcoin Stack for {retirement_years}-Year Retirement - {model_name} Model',
        xaxis_title='Retirement Start Year',
        yaxis_title='Minimum Bitcoin (BTC) Stack Needed',
        height=500,
        showlegend=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.markdown("### 💡 Key Retirement Milestones")
    
    btc_2025 = df[df['year'] == 2025]['btc_needed'].iloc[0]
    btc_2030 = df[df['year'] == 2030]['btc_needed'].iloc[0]
    btc_2035 = df[df['year'] == 2035]['btc_needed'].iloc[0]
    btc_2040 = df[df['year'] == 2040]['btc_needed'].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏁 2025 Minimum Stack",
            value=f"{btc_2025:.2f} BTC",
            delta=f"{retirement_years} years max"
        )
    
    with col2:
        st.metric(
            label="📅 2030 Minimum Stack",
            value=f"{btc_2030:.2f} BTC",
            delta=f"{((btc_2030/btc_2025-1)*100):+.1f}% vs 2025"
        )
    
    with col3:
        st.metric(
            label="🔮 2035 Minimum Stack",
            value=f"{btc_2035:.2f} BTC",
            delta=f"{((btc_2035/btc_2025-1)*100):+.1f}% vs 2025"
        )
    
    with col4:
        st.metric(
            label="🚀 2040 Minimum Stack",
            value=f"{btc_2040:.2f} BTC",
            delta=f"{((btc_2040/btc_2025-1)*100):+.1f}% vs 2025"
        )
    
    # Model assumptions and details
    st.markdown("---")
    st.markdown("### 🔬 Model Assumptions & Details")
    
    with st.expander("📊 Bitcoin Power Law Model"):
        st.markdown("""
        **Price Projection Model:**
        - **Base Model**: Bitcoin Power Law Fair Value = 1.0117e-17 × (days since genesis)^5.82
        - **Conservative Model**: 42% of Fair Value (optional safety margin)
        - **Genesis Date**: January 3, 2009 (Bitcoin's first block)
        
        **Retirement Calculation:**
        - **Spend-down Strategy**: Sell Bitcoin each year to cover inflation-adjusted expenses
        - **Time Horizon**: Up to 50 years of retirement spending
        - **Inflation Adjustment**: Annual expenses increase by selected inflation rate
        - **Precision**: Binary search algorithm for optimal BTC requirement (±0.001 BTC)
        """)
    
    with st.expander("⚖️ Risk Considerations"):
        st.markdown("""
        **Conservative Factors:**
        - Use 42% floor price for extra safety margin
        - Plan for higher inflation rates (8%+ recommended)
        - Consider longer retirement periods (50 years max)
        
        **Risks Not Modeled:**
        - Bitcoin volatility during retirement
        - Regulatory changes affecting Bitcoin
        - Personal health or emergency expenses
        - Technology risks (lost keys, etc.)
        """)
    
    # Cross-reference with future value analysis
    st.info("""
    💡 **Compare with your actual stack**: Switch to the **Future Value Analysis** tab above to see:
    - Your current Bitcoin holdings and projected growth
    - When you could retire based on your stacking rate
    - Personalized retirement readiness timeline
    """)

def net_worth_future_value_analysis():
    """Net worth future value analysis component"""
    st.markdown("### 💰 Future Value of Your Bitcoin Stack")
    
    user_data = get_user_data()
    
    # Calculate current Bitcoin holdings from all accounts
    total_bitcoin_sats = 0
    tracked_bitcoin_sats = 0
    
    for account in user_data['accounts']:
        total_bitcoin_sats += account['balance']
        if account['is_tracked']:
            tracked_bitcoin_sats += account['balance']
    
    current_btc = total_bitcoin_sats / 100_000_000  # Convert to BTC
    
    # User controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Analysis Settings")
        
        # Monthly stacking rate
        monthly_stacking_sats = st.number_input(
            "Monthly Bitcoin Stacking (sats):",
            min_value=0,
            max_value=100_000_000,
            value=500_000,
            step=50_000,
            help="How many sats do you stack per month?"
        )
        
        # Time horizon
        years_ahead = st.slider(
            "Years into Future:",
            min_value=1,
            max_value=20,
            value=10,
            step=1
        )
        
        # Price model
        use_conservative = st.checkbox(
            "Use Conservative Price Model",
            value=False,
            help="Use 42% of Power Law Fair Price for conservative estimates"
        )
    
    with col2:
        st.markdown("### 📊 Current Holdings")
        
        # Current Bitcoin price
        today = datetime.now()
        current_days = get_days_since_genesis(today)
        current_btc_price = calculate_btc_fair_value(current_days)
        
        current_usd_value = current_btc * current_btc_price
        
        st.metric("Current Bitcoin Stack", f"{current_btc:.4f} BTC")
        st.metric("Current USD Value", f"${current_usd_value:,.0f}")
        st.metric("Monthly Stacking", format_sats(monthly_stacking_sats))
        
        # Show tracked vs total
        if tracked_bitcoin_sats != total_bitcoin_sats:
            tracked_btc = tracked_bitcoin_sats / 100_000_000
            st.metric("Tracked Accounts Only", f"{tracked_btc:.4f} BTC")
    
    # Calculate future projections
    projections = []
    chart_years = []
    chart_btc_stack = []
    chart_usd_value = []
    chart_btc_price = []
    
    for year in range(1, years_ahead + 1):
        # Future date
        future_date = today + timedelta(days=year * 365.25)
        future_days = get_days_since_genesis(future_date)
        
        # Future Bitcoin price
        future_btc_price = calculate_btc_fair_value(future_days)
        if use_conservative:
            future_btc_price *= 0.42
        
        # Future Bitcoin stack (current + monthly stacking)
        months_stacking = year * 12
        future_sats = total_bitcoin_sats + (monthly_stacking_sats * months_stacking)
        future_btc = future_sats / 100_000_000
        
        # Future USD value
        future_usd_value = future_btc * future_btc_price
        
        # Growth metrics
        btc_growth = ((future_btc / current_btc) - 1) * 100 if current_btc > 0 else 0
        usd_growth = ((future_usd_value / current_usd_value) - 1) * 100 if current_usd_value > 0 else 0
        
        projections.append({
            'Year': year,
            'Bitcoin Stack': f"{future_btc:.4f} BTC",
            'USD Value': f"${future_usd_value:,.0f}",
            'BTC Growth': f"+{btc_growth:.1f}%",
            'USD Growth': f"+{usd_growth:.1f}%"
        })
        
        # Data for charts
        chart_years.append(year)
        chart_btc_stack.append(future_btc)
        chart_usd_value.append(future_usd_value)
        chart_btc_price.append(future_btc_price)
    
    # THE 4 BEAUTIFUL CHARTS - MAIN STARS
    st.markdown("---")
    st.markdown("### 📈 Future Value Analysis - The Beautiful Charts")
    
    # Create 2x2 subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Bitcoin Stack Growth', 'USD Value Growth', 'Bitcoin Price Projection', 'Stack Value Multipliers'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Chart 1: Bitcoin Stack Growth
    fig.add_trace(
        go.Scatter(x=chart_years, y=chart_btc_stack, mode='lines+markers',
                  name='Bitcoin Stack', line=dict(color='#FF8C00', width=3)),
        row=1, col=1
    )
    
    # Chart 2: USD Value Growth
    fig.add_trace(
        go.Scatter(x=chart_years, y=chart_usd_value, mode='lines+markers',
                  name='USD Value', line=dict(color='#32CD32', width=3)),
        row=1, col=2
    )
    
    # Chart 3: Bitcoin Price Projection
    fig.add_trace(
        go.Scatter(x=chart_years, y=chart_btc_price, mode='lines+markers',
                  name='BTC Price', line=dict(color='#DC143C', width=3)),
        row=2, col=1
    )
    
    # Chart 4: Stack Value Multipliers
    multipliers = [val / current_usd_value if current_usd_value > 0 else 1 for val in chart_usd_value]
    fig.add_trace(
        go.Scatter(x=chart_years, y=multipliers, mode='lines+markers',
                  name='Value Multiplier', line=dict(color='#9370DB', width=3)),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Bitcoin Stack Future Value Analysis",
        height=600,
        showlegend=False
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Years", row=1, col=1)
    fig.update_xaxes(title_text="Years", row=1, col=2)
    fig.update_xaxes(title_text="Years", row=2, col=1)
    fig.update_xaxes(title_text="Years", row=2, col=2)
    
    fig.update_yaxes(title_text="Bitcoin (BTC)", row=1, col=1)
    fig.update_yaxes(title_text="USD Value", row=1, col=2)
    fig.update_yaxes(title_text="Price (USD)", row=2, col=1)
    fig.update_yaxes(title_text="Multiplier", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # === BITCOIN RETIREMENT ANALYSIS ===
    st.markdown("---")
    st.markdown("### 🏖️ Bitcoin Retirement Analysis")
    
    # Retirement parameters
    col1, col2 = st.columns(2)
    
    with col1:
        retirement_expenses = st.number_input(
            "Annual Retirement Expenses (USD):",
            min_value=10000,
            max_value=500000,
            value=100000,
            step=5000
        )
        
    with col2:
        retirement_inflation = st.slider(
            "Retirement Inflation Rate:",
            min_value=0.0,
            max_value=12.0,
            value=8.0,
            step=0.5,
            format="%.1f%%"
        ) / 100.0
    
    # Calculate when user can retire
    retirement_data = []
    user_can_retire_year = None
    
    for year in range(2025, 2041):
        # User's projected Bitcoin stack for this year
        years_from_now = year - today.year
        if years_from_now > 0:
            months_stacking = years_from_now * 12
            user_future_sats = total_bitcoin_sats + (monthly_stacking_sats * months_stacking)
            user_future_btc = user_future_sats / 100_000_000
        else:
            user_future_btc = current_btc
        
        # Minimum BTC needed for retirement in this year
        min_btc_needed = calculate_minimum_btc_for_retirement(
            year, retirement_expenses, retirement_inflation, 50, use_conservative
        )
        
        retirement_data.append({
            'year': year,
            'user_btc': user_future_btc,
            'min_btc_needed': min_btc_needed,
            'can_retire': user_future_btc >= min_btc_needed
        })
        
        # Find first year user can retire
        if user_can_retire_year is None and user_future_btc >= min_btc_needed:
            user_can_retire_year = year
    
    # Create retirement readiness chart
    df_retirement = pd.DataFrame(retirement_data)
    
    fig = go.Figure()
    
    # User's Bitcoin stack projection
    fig.add_trace(go.Scatter(
        x=df_retirement['year'],
        y=df_retirement['user_btc'],
        mode='lines+markers',
        name='Your Bitcoin Stack',
        line=dict(color='#FF8C00', width=3),
        marker=dict(size=6)
    ))
    
    # Minimum BTC needed for retirement
    fig.add_trace(go.Scatter(
        x=df_retirement['year'],
        y=df_retirement['min_btc_needed'],
        mode='lines+markers',
        name='Min BTC for Retirement',
        line=dict(color='#DC143C', width=3, dash='dash'),
        marker=dict(size=6)
    ))
    
    # Add retirement readiness line
    if user_can_retire_year:
        fig.add_vline(
            x=user_can_retire_year,
            line_width=3,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Can Retire: {user_can_retire_year}"
        )
    
    model_name = "Conservative" if use_conservative else "Fair Price"
    fig.update_layout(
        title=f'Bitcoin Retirement Readiness - {model_name} Model',
        xaxis_title='Year',
        yaxis_title='Bitcoin (BTC)',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key retirement metrics
    st.markdown("### 💡 Retirement Readiness Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if user_can_retire_year:
            st.metric(
                label="🎯 Can Retire In",
                value=f"{user_can_retire_year}",
                delta=f"{user_can_retire_year - today.year} years"
            )
        else:
            st.metric(
                label="🎯 Can Retire In",
                value="After 2040",
                delta="Need more stacking"
            )
    
    with col2:
        st.metric(
            label="🪙 Current Bitcoin Stack",
            value=f"{current_btc:.3f} BTC",
            delta=f"${current_usd_value:,.0f}"
        )
    
    with col3:
        # Calculate required monthly stacking for 2030 retirement
        btc_needed_2030 = calculate_minimum_btc_for_retirement(
            2030, retirement_expenses, retirement_inflation, 50, use_conservative
        )
        years_to_2030 = 2030 - today.year
        months_to_2030 = years_to_2030 * 12
        
        if months_to_2030 > 0:
            btc_gap = max(0, btc_needed_2030 - current_btc)
            sats_gap = btc_gap * 100_000_000
            required_monthly_sats = sats_gap / months_to_2030
            
            if required_monthly_sats <= monthly_stacking_sats:
                st.metric(
                    label="🎯 2030 Retirement Goal",
                    value="On Track! 🎉",
                    delta=f"Need {format_sats(int(required_monthly_sats))}/month"
                )
            else:
                st.metric(
                    label="🎯 2030 Retirement Goal",
                    value=format_sats(int(required_monthly_sats)),
                    delta="per month needed"
                )
        else:
            st.metric(
                label="🎯 2030 Retirement Goal",
                value="Already 2030+",
                delta="Update timeline"
            )
    
    with col4:
        # Show results for current stacking rate
        current_rate_retirement = user_can_retire_year if user_can_retire_year else "After 2040"
        st.metric(
            label=f"📊 Current Rate Results",
            value=f"{current_rate_retirement}",
            delta=f"{format_sats(monthly_stacking_sats)}/month"
        )
    
    # Cross-reference explanation
    st.info("""
    💡 **Want more detailed retirement planning?** Switch to the **Retirement Planning** tab above for comprehensive analysis including:
    - Year-by-year BTC requirements for different retirement years
    - Conservative vs fair price model options
    - Supporting charts for price projections and inflation impact
    """)
    
    # TABLE AS SUPPORTING CAST - moved here after the main charts and analysis
    st.markdown("---")
    st.markdown("### 📊 Future Value Projections Table")
    df = pd.DataFrame(projections)
    st.dataframe(df, use_container_width=True, hide_index=True)

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
        st.markdown("### 🔍 Select Transaction to Analyze")
        
        # Create transaction options for selectbox
        transaction_options = []
        for i, tx in enumerate(transactions[:20]):  # Limit to 20 most recent
            date, description, category, amount = tx[1], tx[2], tx[5], tx[4]
            option_text = f"{date} - {description} - {format_sats(amount)} ({category})"
            transaction_options.append((i, option_text, tx))
        
        if transaction_options:
            selected_idx = st.selectbox(
                "Choose a transaction:",
                range(len(transaction_options)),
                format_func=lambda x: transaction_options[x][1]
            )
            
            selected_transaction = transaction_options[selected_idx][2]
            
            # Transaction details
            st.markdown("### 📋 Transaction Details")
            tx_date, tx_desc, tx_category, tx_amount = selected_transaction[1], selected_transaction[2], selected_transaction[5], selected_transaction[4]
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Date", tx_date)
                st.metric("Amount", format_sats(tx_amount))
            with col_b:
                st.metric("Description", tx_desc)
                st.metric("Category", tx_category)
    
    with col2:
        st.markdown("### ⚙️ Analysis Settings")
        
        # Time horizons for analysis
        time_horizons = st.multiselect(
            "Time Horizons (years):",
            [1, 2, 5, 10, 15, 20],
            default=[5, 10, 20]
        )
        
        # Bitcoin price model
        use_conservative_model = st.checkbox(
            "Conservative Model",
            value=False,
            help="Use 42% of Power Law Fair Price"
        )
    
    if transaction_options and time_horizons:
        selected_transaction = transaction_options[selected_idx][2]
        tx_amount = selected_transaction[4]
        tx_date = selected_transaction[1]
        
        # Calculate opportunity cost
        st.markdown("---")
        st.markdown("### 💰 Opportunity Cost Analysis")
        
        # Get Bitcoin price at transaction date
        tx_datetime = datetime.strptime(tx_date, '%Y-%m-%d')
        tx_days = get_days_since_genesis(tx_datetime)
        tx_btc_price = calculate_btc_fair_value(tx_days)
        
        # How much Bitcoin could have been bought (proper conversion)
        tx_amount_usd = (tx_amount / 100_000_000) * tx_btc_price  # Convert sats to USD at purchase time
        btc_could_have_bought = tx_amount_usd / tx_btc_price  # USD amount divided by BTC price
        
        st.metric("Bitcoin Equivalent at Purchase", f"{btc_could_have_bought:.6f} BTC")
        st.metric("Bitcoin Price at Purchase", f"${tx_btc_price:,.0f}")
        st.metric("USD Amount at Purchase", f"${tx_amount_usd:,.2f}")
        
        # Calculate future values
        opportunity_data = []
        
        for years in time_horizons:
            # Future date
            future_date = tx_datetime + timedelta(days=years * 365.25)
            future_days = get_days_since_genesis(future_date)
            future_btc_price = calculate_btc_fair_value(future_days)
            
            if use_conservative_model:
                future_btc_price *= 0.42
            
            # Future value if had bought Bitcoin instead
            future_value = btc_could_have_bought * future_btc_price
            
            # Opportunity cost (future value minus original USD amount)
            opportunity_cost = future_value - tx_amount_usd
            
            opportunity_data.append({
                'Years': years,
                'Future BTC Price': f"${future_btc_price:,.0f}",
                'Future Value': f"${future_value:,.0f}",
                'Opportunity Cost': f"${opportunity_cost:,.0f}",
                'Multiple': f"{future_value / tx_amount_usd:.1f}x" if tx_amount_usd > 0 else "N/A"
            })
        
        # CHART FIRST - Main visualization
        st.markdown("### 📊 Opportunity Cost Visualization")
        
        years = [item['Years'] for item in opportunity_data]
        future_values = [float(item['Future Value'].replace('$', '').replace(',', '')) for item in opportunity_data]
        original_value = tx_amount_usd
        
        fig = go.Figure()
        
        # Future value line
        fig.add_trace(go.Scatter(
            x=years,
            y=future_values,
            mode='lines+markers',
            name='Future Value if Bought Bitcoin',
            line=dict(color='#FF8C00', width=3),
            marker=dict(size=8)
        ))
        
        # Original purchase line
        fig.add_hline(
            y=original_value,
            line_width=2,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Original Purchase: ${original_value:,.0f}"
        )
        
        model_name = "Conservative" if use_conservative_model else "Fair Price"
        fig.update_layout(
            title=f'Opportunity Cost Analysis - {model_name} Model',
            xaxis_title='Years After Purchase',
            yaxis_title='Value (USD)',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        if opportunity_data:
            max_opportunity = max(opportunity_data, key=lambda x: float(x['Opportunity Cost'].replace('$', '').replace(',', '')))
            
            st.markdown("### 💡 Key Insights")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Biggest Opportunity Cost", max_opportunity['Opportunity Cost'])
            
            with col2:
                st.metric("Time Horizon", f"{max_opportunity['Years']} years")
            
            with col3:
                st.metric("Value Multiple", max_opportunity['Multiple'])
        
        # TABLE AS SUPPORTING CAST - moved here after the chart
        st.markdown("### 📋 Detailed Opportunity Cost Analysis")
        df_opportunity = pd.DataFrame(opportunity_data)
        st.dataframe(df_opportunity, use_container_width=True, hide_index=True)

def calculate_minimum_btc_for_retirement(retirement_year, annual_expenses, inflation_rate, retirement_years, use_floor_price=False):
    """Calculate minimum BTC needed for retirement using binary search"""
    
    # Binary search bounds
    min_btc = 0.01  # Start with 0.01 BTC
    max_btc = 100.0  # Max 100 BTC should be more than enough
    tolerance = 0.001  # 0.001 BTC precision
    
    # Binary search to find minimum BTC needed
    for _ in range(100):  # Max 100 iterations
        test_btc = (min_btc + max_btc) / 2
        
        # Simulate spending down this BTC stack
        remaining_btc = test_btc
        
        for year_offset in range(retirement_years):
            current_year = retirement_year + year_offset
            
            # Get Bitcoin price for this year
            target_date = datetime(current_year, 1, 1)
            days_since_genesis = get_days_since_genesis(target_date)
            btc_fair_price = calculate_btc_fair_value(days_since_genesis)
            btc_price = btc_fair_price * 0.42 if use_floor_price else btc_fair_price
            
            # Calculate inflation-adjusted expenses for this year
            inflated_expenses = annual_expenses * ((1 + inflation_rate) ** year_offset)
            
            # Calculate BTC needed to sell for this year's expenses
            btc_to_sell = inflated_expenses / btc_price
            
            # Subtract from remaining BTC
            remaining_btc -= btc_to_sell
            
            # If we run out of Bitcoin, this amount is not enough
            if remaining_btc < 0:
                break
        
        # Check if we found the right amount
        if abs(max_btc - min_btc) < tolerance:
            break
        
        # Adjust search range based on result
        if remaining_btc < 0:
            min_btc = test_btc  # Need more BTC
        else:
            max_btc = test_btc  # This amount works, try less
    
    return max_btc
# Bitcoin Budget - Streamlit Web Application Architecture

## Philosophy: Excel-Level Simplicity in the Browser

This is a **modern, web-based budgeting application** for Bitcoin users with advanced opportunity cost analysis. No over-engineering, no complex patterns, just straightforward envelope budgeting with powerful Bitcoin-specific insights delivered through an interactive web interface.

**Core Principle: If you can do it in Excel, it should be simple in code - now accessible from any browser.**

## Technology Stack

- **Language**: Python 3.8+
- **Web Framework**: Streamlit (interactive web UI)
- **Charts**: Plotly (interactive visualizations with hover details)
- **Data Handling**: Pandas (DataFrames for display and analysis)
- **Database**: SQLite (single file database)
- **Deployment**: Streamlit Cloud, Heroku, or self-hosted
- **Total Code**: ~1,630 lines across 2 main files
- **Interface**: Responsive web UI with sidebar navigation

## Why This Stack?

### Python + Streamlit
- ✅ **Modern**: Clean, responsive web interface
- ✅ **Interactive**: Real-time updates and form validation
- ✅ **Mobile-friendly**: Works on phones, tablets, and desktops
- ✅ **Simple**: No HTML/CSS/JavaScript required
- ✅ **Fast development**: Working prototype in hours
- ✅ **Easy deployment**: One-click deploy to cloud platforms

### Plotly Charts
- ✅ **Interactive**: Zoom, pan, hover details built-in
- ✅ **Professional**: Publication-quality visualizations
- ✅ **Responsive**: Charts adapt to screen size
- ✅ **No configuration**: Works out-of-the-box with Streamlit

### SQLite (Unchanged)
- ✅ **Zero configuration**: Just a file
- ✅ **Reliable**: Used by millions of apps
- ✅ **Portable**: Copy file = backup entire budget
- ✅ **Fast**: More than sufficient for personal budgets

### Clean Architecture
- ✅ **Organized**: Main app + reports module structure
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Testable**: Functions can be tested independently
- ✅ **Extensible**: Easy to add new features

## Database Schema (3 Tables, That's It)

```sql
-- Transactions: Income and expenses
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,              -- '2025-06-03'
    description TEXT NOT NULL,
    amount INTEGER NOT NULL,         -- satoshis (always positive)
    category_id INTEGER,             -- NULL for income
    type TEXT NOT NULL,              -- 'income' or 'expense'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Categories: Spending envelopes
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,       -- 'Groceries', 'Rent', etc.
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Allocations: Monthly budget assignments
CREATE TABLE allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    month TEXT NOT NULL,             -- '2025-06'
    amount INTEGER NOT NULL,         -- satoshis allocated to category
    UNIQUE(category_id, month),
    FOREIGN KEY(category_id) REFERENCES categories(id)
);
```

## Core Logic (Simple Functions)

### Budget Math
```python
def get_total_income(month=None):
    """Get total income for a month (or all time if None)"""
    return sum(amount for transactions where type='income')

def get_available_to_assign(month):
    """Unallocated income for the month"""
    total_income = get_total_income(month)
    total_allocated = sum(allocations for month)
    return total_income - total_allocated

def get_category_balance(category_id, month):
    """Available balance in category envelope"""
    allocated = get_allocation(category_id, month)
    spent = sum(expenses for category in month)
    previous_balance = get_category_balance(category_id, previous_month)
    return previous_balance + allocated - spent
```

### Bitcoin Units
```python
def sats_to_btc(satoshis):
    """Convert satoshis to BTC display"""
    return satoshis / 100_000_000

def btc_to_sats(btc):
    """Convert BTC to satoshis"""
    return int(btc * 100_000_000)

def format_sats(satoshis):
    """Display satoshis with commas"""
    return f"{satoshis:,} sats"
```

### Advanced Analytics & Reports
```python
def get_spending_breakdown(start_date, end_date):
    """Get spending by category for interactive pie chart"""
    return breakdown_data, total_spent

def get_net_worth_data(start_date, end_date):
    """Get monthly income vs expenses for interactive bar chart"""
    return monthly_data_with_cumulative_net_worth

def calculate_btc_fair_value(days_since_genesis):
    """Bitcoin power law: 1.0117e-17 * days^5.82"""
    return power_law_price

def calculate_future_purchasing_power(current_budget, years, inflation_rate):
    """Analyze future spending needs vs Bitcoin appreciation"""
    return future_budget_sats, reduction_percentage

def get_expense_transactions(limit=50):
    """Get expense transactions for lifecycle cost analysis"""
    return transactions_for_opportunity_cost_analysis
```

### Interactive Visualization Functions
```python
def create_spending_pie_chart(breakdown_data):
    """Create interactive pie chart with hover details"""
    fig = px.pie(df, values='amount', names='category', 
                 title='Spending Breakdown')
    return fig

def create_net_worth_charts(net_worth_data):
    """Create dual-chart visualization with subplots"""
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=('Monthly Flow', 'Cumulative'))
    return fig

def create_lifecycle_analysis_dashboard(transaction_data):
    """Create 4-chart opportunity cost analysis"""
    return comprehensive_plotly_dashboard
```

## File Structure

```
bitcoin_budget/
├── streamlit_app.py           # Main application (758 lines)
├── pages/
│   ├── __init__.py           # Package initialization
│   └── reports.py            # All reports functionality (886 lines)
├── budget.db                 # SQLite database (created automatically)
├── requirements_streamlit.txt # Dependencies: streamlit, plotly, pandas
├── README.md                 # Usage instructions
└── ARCHITECTURE.md           # This technical documentation
```

## Web Interface Layout

### Main Application (Responsive Web Layout)
```
┌─────────────────────────────────────────────────────────────────┐
│ ₿ Bitcoin Budget - June 2025                                   │
├─────────────────────────────────────────────────────────────────┤
│ ║ Sidebar Navigation         │ Main Content Area               │
│ ║ 📅 June 2025              │                                 │
│ ║ 📊 Reports                │ [Total Income] [Available]      │
│ ║ ⚙️ Settings              │ [Allocated] [Expenses]          │
│ ║                          │                                 │
│ ║                          │ ┌─ Add Income ─┐                │
│ ║                          │ │ Amount: _____ │                │
│ ║                          │ │ Desc: _______ │                │
│ ║                          │ │ [Add Income]  │                │
│ ║                          │ └─────────────────┘              │
│ ║                          │                                 │
│ ║                          │ ┌─ Categories ─┐                 │
│ ║                          │ │ Groceries: 50K│                │
│ ║                          │ │ [Allocate] [💸]│                │
│ ║                          │ └─────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Reports Interface (Full-Screen Interactive)
```
┌─────────────────────────────────────────────────────────────────┐
│ 📊 Bitcoin Budget Reports                                      │
├─────────────────────────────────────────────────────────────────┤
│ Report Type: [📊 Spending Breakdown ▼]                        │
│                                                                 │
│ ⏰ Time Period: [Current Month] [3 Months] [6 Months] [12 Mon] │
│                                                                 │
│ ┌─────────────────────────┐ ┌─────────────────────────────────┐ │
│ │     INTERACTIVE         │ │        CATEGORY                 │ │
│ │      PIE CHART          │ │        DETAILS                  │ │
│ │   (hover for details)   │ │                                 │ │
│ │                         │ │ • Groceries: 45%                │ │
│ │     🥧 Plotly           │ │ • Rent: 30%                     │ │
│ │   Visualization         │ │ • Transport: 15%                │ │
│ │                         │ │ • Other: 10%                    │ │
│ └─────────────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Streamlit-Specific Architecture

### Session State Management
```python
def initialize_session_state():
    """Initialize app state on first load"""
    if 'current_month' not in st.session_state:
        st.session_state.current_month = get_current_month()
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = None
```

### Form Handling with Validation
```python
def add_income_form():
    """Income entry form with real-time validation"""
    with st.form("add_income_form", clear_on_submit=True):
        amount = st.text_input("Amount", placeholder="1000000 or 0.01 BTC")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Income")
        
        if submitted and amount and description:
            try:
                amount_sats = parse_amount_input(amount)
                if add_income(amount_sats, description, date.today()):
                    st.success("Income added successfully!")
                    st.rerun()
            except ValueError:
                st.error("Invalid amount format")
```

### Interactive Data Display
```python
def display_categories():
    """Show categories with interactive controls"""
    categories = get_all_categories()
    
    for category in categories:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            balance = get_category_balance(category['id'], current_month)
            st.metric(category['name'], format_sats(balance))
        
        with col2:
            if st.button("💰", key=f"allocate_{category['id']}"):
                st.session_state.allocate_category = category['id']
        
        with col3:
            if st.button("💸", key=f"expense_{category['id']}"):
                st.session_state.expense_category = category['id']
```

## Reports Module Architecture

### Four Interactive Report Types

1. **📊 Spending Breakdown**: Interactive pie charts with time period selection
2. **📈 Net Worth Analysis**: Dual-chart visualization (monthly flow + cumulative)
3. **🔮 Future Purchasing Power**: Bitcoin appreciation vs inflation modeling
4. **⏳ Lifecycle Cost Analysis**: Individual transaction opportunity cost analysis

### Plotly Integration
```python
def create_interactive_pie_chart(breakdown_data):
    """Create responsive pie chart with hover details"""
    fig = px.pie(
        df, values='amount', names='category',
        title='Spending Breakdown',
        hover_data=['percentage']
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: %{value:,} sats<extra></extra>'
    )
    
    return fig
```

### Advanced Bitcoin Analytics
```python
def bitcoin_power_law_analysis():
    """Calculate Bitcoin fair value using power law model"""
    current_days = get_days_since_genesis(datetime.now())
    fair_value = 1.0117e-17 * (current_days ** 5.82)
    return fair_value

def opportunity_cost_dashboard(transaction_id, years_ahead):
    """Create 4-chart opportunity cost analysis"""
    # Chart 1: Bitcoin amount comparison
    # Chart 2: USD value comparison  
    # Chart 3: Bitcoin price progression
    # Chart 4: Opportunity cost breakdown
    return plotly_dashboard_with_insights
```

## Deployment Options

### Development
```bash
streamlit run streamlit_app.py
```

### Production Deployment
- **Streamlit Cloud**: One-click deployment from GitHub
- **Heroku**: Web app hosting with custom domain
- **Self-hosted**: Docker container or VPS deployment
- **Local network**: Share on home network

## Performance Characteristics

- **Database**: SQLite handles thousands of transactions easily
- **Charts**: Plotly renders interactively in browser
- **Responsiveness**: Real-time updates with st.rerun()
- **Memory**: Efficient pandas operations for data display
- **Load Time**: Fast startup with Streamlit caching

## Security & Privacy

- **Local data**: SQLite database stays on your machine
- **No cloud storage**: Unless you choose cloud deployment
- **No tracking**: Pure financial calculations
- **Open source**: All code is readable and auditable

## Success Metrics

✅ **Modern Web Interface**: Accessible from any browser  
✅ **Mobile Responsive**: Works on phones and tablets  
✅ **Interactive Charts**: Hover details, zoom, pan functionality  
✅ **Real-time Validation**: Immediate feedback on form inputs  
✅ **Advanced Analytics**: Bitcoin opportunity cost analysis  
✅ **Easy Deployment**: One-click to Streamlit Cloud  
✅ **All YNAB Features**: Complete envelope budgeting system  
✅ **Professional UI**: Clean, intuitive interface design  

## Migration Benefits

**From Desktop to Web:**
- 🌐 **Universal Access**: Use from any device with a browser
- 📱 **Mobile Friendly**: Full functionality on phones/tablets  
- ☁️ **Easy Sharing**: Deploy to cloud for multi-device access
- 📊 **Better Charts**: Interactive Plotly vs static matplotlib
- 🔄 **Live Updates**: Real-time interface updates
- 🎯 **Modern UX**: Streamlit's professional interface components

**Maintained Simplicity:**
- 🎯 **Same Core Logic**: All budget math functions unchanged
- 🗄️ **Same Database**: 100% compatible with existing data
- 🛠️ **Simple Deployment**: `streamlit run` for development
- 📝 **Readable Code**: Still under 2000 lines total

Remember: **Simple is better than complex. Web-native is better than desktop porting. Interactive is better than static.** 
# Bitcoin Budget - Streamlit Web Application

A modern, privacy-focused envelope budgeting application for Bitcoin users with advanced opportunity cost analysis.

🌐 **Live Demo**: [https://bitcoinbudget.streamlit.app/](https://bitcoinbudget.streamlit.app/)

## What It Does

- Track Bitcoin income and expenses in satoshis
- Create spending categories with master category organization
- Allocate income to categories monthly with rollover tracking
- View transaction history with editing capabilities
- **Privacy-First Design**: Each user has isolated session data
- **Professional Web Interface**: Modern, responsive design with interactive charts
- **Advanced Analytics**: Visual reports with Plotly charts and opportunity cost analysis
- **Bitcoin Economics**: Built-in power law projections and inflation comparisons

## Why This Architecture?

### 🔒 **Privacy & Security**
- **Session-Based Storage**: Each user's data is completely isolated
- **No Shared Database**: Your financial data is never mixed with other users
- **Browser-Only Persistence**: Data exists only during your session
- **Zero Installation**: No downloads, accounts, or personal information required

### 🌐 **Modern Web Experience**
- **Instant Access**: Works immediately in any browser
- **Mobile Friendly**: Responsive design for phones and tablets
- **Interactive Charts**: Professional Plotly visualizations with hover details
- **Real-time Updates**: Instant feedback and form validation
- **Professional Dashboard**: Tabbed interface with metric cards and data tables

### ⚡ **Performance & Reliability**
- **Streamlit Cloud Hosting**: Fast, reliable infrastructure
- **No Database Setup**: Session state eliminates database complexity
- **Auto-Deploy**: Updates pushed automatically from GitHub
- **Global CDN**: Fast loading worldwide

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Charts**: Plotly (interactive visualizations)
- **Data**: Pandas + Session State (no database required)
- **Hosting**: Streamlit Cloud
- **Deployment**: GitHub integration with auto-deploy

## Quick Start

### 🚀 **Try It Now**
1. Visit [https://bitcoinbudget.streamlit.app/](https://bitcoinbudget.streamlit.app/)
2. App loads with demo data (100k sats income, sample categories)
3. Start by clicking "🚀 Get Started" on the landing page
4. Add your own income/expenses to see it in action

### 💻 **Run Locally**
```bash
# Clone the repository
git clone https://github.com/nostrgamer/BitcoinBudget.git
cd BitcoinBudget

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

The application will open at `http://localhost:8501`

## Features

### 🏦 **Core Envelope Budgeting**
- ✅ **Smart Income Entry**: Add Bitcoin income with flexible sats/BTC input
- ✅ **Category Management**: Create master categories (Fixed, Variable, Savings) and subcategories
- ✅ **Intelligent Allocation**: Allocate income with availability checking and rollover
- ✅ **Real-time Balances**: Live category balances with overspending alerts
- ✅ **Month Navigation**: Navigate between months with preserved data
- ✅ **Transaction Management**: Edit, delete, and categorize all transactions

### ₿ **Bitcoin-Native Features**
- ✅ **Satoshi Precision**: All calculations in satoshis (no floating point errors)
- ✅ **Flexible Input**: Support "1000000", "1,000,000", or "0.01 BTC" formats
- ✅ **Clear Display**: Shows as "1,000,000 sats" with comma formatting
- ✅ **Bitcoin Power Law**: Built-in fair value calculations for projections

### 📊 **Advanced Analytics & Reports**

#### 📊 Spending Breakdown
- **Interactive Pie Charts**: Category spending with hover details and percentages
- **Time Period Selection**: Current month, 3/6/12 months back
- **Category Tables**: Detailed breakdowns with amounts and percentages
- **Summary Metrics**: Total spending, category count, top spending category

#### 📈 Net Worth Analysis
- **Dual Chart Display**: Income vs expenses + cumulative net worth
- **Interactive Plotly Charts**: Zoom, pan, hover for detailed information
- **Financial Metrics**: Income, expenses, net worth, monthly averages
- **Trend Analysis**: Track financial progress across multiple months

#### 🔮 Future Purchasing Power
- **Bitcoin Power Law Modeling**: Project future Bitcoin prices using historical data
- **Inflation Comparison**: Compare Bitcoin appreciation vs traditional inflation
- **Budget Projections**: Show how spending power increases over time
- **Visual Analysis**: Side-by-side current vs future budget comparisons
- **Multiple Horizons**: 1, 2, 5, 10-year purchasing power projections

#### ⏳ Lifecycle Cost Analysis
- **Transaction Selection**: Analyze any historical expense transaction
- **Configurable Settings**: Adjust time horizon (1-10 years) and inflation rate
- **4-Chart Dashboard**:
  - Bitcoin Amount Comparison (amounts remain constant)
  - USD Value Analysis (purchase vs future value vs inflation)
  - Bitcoin Price Projection (power law trend with markers)
  - Opportunity Cost Breakdown (visual impact analysis)
- **Comprehensive Analysis**: Detailed explanations with bottom-line impact
- **Key Insights**: Amount spent, future value, opportunity cost, purchasing power multiplier

## How It Works

### 🏗️ **Session-Based Architecture**
```python
# Each user gets isolated data in browser session
st.session_state.user_data = {
    'transactions': [],      # User's income/expenses
    'categories': [],        # User's spending categories
    'master_categories': [], # User's category groups
    'allocations': [],       # User's budget allocations
}
```

### 📱 **Modern Web Interface**
```
┌─────────────────────────────────────────────────────────────────┐
│ ₿ Bitcoin Budget - 2025-06                                      │
├─────────────────────────────────────────────────────────────────┤
│ 💰 Budget Summary (Real-time metrics)                          │
│ [Total Income] [Rollover] [Allocated] [Available to Assign]     │
├─────────────────────────────────────────────────────────────────┤
│ [📁 Categories] [💳 Transactions] (Interactive tabs)           │
│ Modern forms with validation and editable data tables          │
├─────────────────────────────────────────────────────────────────┤
│ Sidebar: Month Navigation + Reports + How to Use               │
└─────────────────────────────────────────────────────────────────┘
```

### 🔬 **Bitcoin Economics Integration**
```python
# Bitcoin Power Law for future value projections
def calculate_btc_fair_value(days_since_genesis):
    return 1.0117e-17 * (days_since_genesis ** 5.82)

# Opportunity cost analysis with interactive charts
def analyze_lifecycle_cost(amount_sats, years_ahead):
    current_value = amount_sats / 100_000_000 * current_btc_price
    future_value = amount_sats / 100_000_000 * future_btc_price
    opportunity_cost = future_value - current_value
    return opportunity_cost
```

## Privacy & Data Protection

### 🔒 **Your Data is Safe**
- **Session Isolation**: Each browser session has completely separate data
- **No User Accounts**: No registration, login, or personal information required
- **No Data Persistence**: Your data doesn't survive browser sessions (by design)
- **No Analytics Tracking**: We don't track your usage or financial information
- **No Server Storage**: Your budget data never touches our servers

### 🛡️ **Security Benefits**
- **Cannot Access Other Users**: Technical impossibility due to session isolation
- **No Data Breaches**: No database to breach, no persistent storage
- **No Identity Exposure**: Use completely anonymously
- **Local Processing**: All calculations happen in your browser

## Example Workflows

### 🚀 **First Time User**
1. Visit [bitcoinbudget.streamlit.app](https://bitcoinbudget.streamlit.app/)
2. Read the landing page explanation with real opportunity cost example
3. Click "🚀 Start Budgeting Now" 
4. App loads with demo data: 100k sats income, 3 categories, sample allocations
5. Try adding your own transactions to see how it works

### 📊 **Daily Budget Management**
1. **Add Income**: Use the Income tab with date picker and amount validation
2. **Allocate Budget**: Assign income to categories with smart availability checking
3. **Track Expenses**: Record spending with category selection and descriptions
4. **Monitor Balances**: Real-time category balances with overspending warnings
5. **View Reports**: Analyze spending patterns and opportunity costs

### 🔍 **Advanced Analysis**
1. **Spending Breakdown**: See which categories consume the most Bitcoin
2. **Net Worth Tracking**: Monitor income vs expenses over multiple months
3. **Future Projections**: Understand how current spending affects future wealth
4. **Lifecycle Analysis**: Analyze specific purchases' long-term opportunity cost

## Deployment & Architecture

### 🌐 **Live Production**
- **URL**: [https://bitcoinbudget.streamlit.app/](https://bitcoinbudget.streamlit.app/)
- **Hosting**: Streamlit Cloud (free tier)
- **Auto-Deploy**: Connected to GitHub for automatic updates
- **Global CDN**: Fast loading worldwide
- **99.9% Uptime**: Reliable infrastructure

### 💻 **Local Development**
```bash
# Requirements
pip install streamlit>=1.28.0 pandas>=1.5.0 plotly>=5.15.0

# Run locally
streamlit run streamlit_app.py
```

### 📁 **File Structure**
```
streamlit_app.py           # Main application (1,750 lines)
modules/
  ├── __init__.py         # Package initialization
  └── reports.py          # All reports functionality (900+ lines)
requirements.txt          # Production dependencies
README.md                # This documentation
```

### 🔄 **Development Workflow**
1. **Code Changes**: Update code in GitHub repository
2. **Auto-Deploy**: Streamlit Cloud automatically detects changes
3. **Live Updates**: New version deployed within minutes
4. **Zero Downtime**: Seamless updates for all users

## Why Session-Based Storage?

### ✅ **Advantages**
- **Maximum Privacy**: No shared database, no data leaks possible
- **Zero Setup**: No database configuration or management
- **Fast Performance**: All data in memory, instant operations
- **Simple Architecture**: Eliminates database complexity and security concerns
- **Demo Friendly**: Perfect for trying the app without commitment

### ⚠️ **Considerations**
- **Session Only**: Data lost when browser/tab closes (by design for privacy)
- **Demo Purpose**: Best for exploring features and short-term budgeting
- **No Backup**: Users responsible for any data they want to preserve
- **Fresh Start**: Each visit starts clean (good for privacy, neutral for persistence)

## Technical Details

### 🔧 **Core Functions** (Unchanged Logic)
```python
def get_available_to_assign(month):
    """Calculate unallocated income for the month"""
    income = get_total_income(month) 
    allocated = get_total_allocated(month)
    rollover = get_rollover_amount(month)
    return income + rollover - allocated

def get_category_balance(category_id, month):
    """Get current balance for category envelope"""
    allocated = get_category_allocated(category_id, month)
    spent = get_category_spent(category_id, month) 
    rollover = get_category_rollover_balance(category_id, month)
    return allocated + rollover - spent
```

### 📊 **Analytics Functions**
```python
def calculate_future_purchasing_power(sats, years, inflation=0.08):
    """Project future purchasing power using Bitcoin power law"""
    current_days = get_days_since_genesis(datetime.now())
    future_days = get_days_since_genesis(datetime.now() + timedelta(days=years*365))
    
    current_price = calculate_btc_fair_value(current_days)
    future_price = calculate_btc_fair_value(future_days)
    
    current_value = sats / 100_000_000 * current_price
    future_value = sats / 100_000_000 * future_price
    
    return future_value / current_value  # Purchasing power multiplier
```

## Contributing

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes
5. **Test** locally with `streamlit run streamlit_app.py`
6. **Submit** a pull request

Changes are automatically deployed to the live app when merged to main branch.

## License

MIT License - Use freely for personal or commercial purposes.

---

**🌐 Try it now**: [https://bitcoinbudget.streamlit.app/](https://bitcoinbudget.streamlit.app/)

**Built for Bitcoiners who want to understand the true cost of their spending decisions in a Bitcoin world.**
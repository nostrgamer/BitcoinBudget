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
- ✅ **Account Management**: Tracked accounts (on-budget) and untracked accounts (savings/long-term)
- ✅ **Smart Income Entry**: Add Bitcoin income with flexible sats/BTC input and account selection
- ✅ **Category Management**: Create master categories (Fixed, Variable, Savings) and subcategories
- ✅ **Intelligent Allocation**: Allocate income with availability checking and rollover
- ✅ **Real-time Balances**: Live category balances with overspending alerts and account tracking
- ✅ **Month Navigation**: Navigate between months with preserved data
- ✅ **Transaction Management**: Edit, delete, and categorize all transactions with account tracking
- ✅ **Account Transfers**: Move funds between different Bitcoin accounts

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
- **Account-Based Net Worth**: Real net worth using actual account balances
- **Dual Chart Display**: Income vs expenses + cumulative net worth progression
- **Account Breakdown**: Detailed view of tracked vs untracked accounts
- **Interactive Plotly Charts**: Zoom, pan, hover for detailed information
- **Financial Metrics**: Current net worth, income, expenses, monthly averages
- **Trend Analysis**: Track financial progress across multiple months

#### 🚀 Net Worth Future Value
- **Personal Stack Projections**: Show future value of your actual Bitcoin holdings
- **DCA Modeling**: Optional Dollar Cost Averaging scenario analysis
- **20-Year Horizons**: Project 5, 10, 15, 20-year growth scenarios
- **4-Panel Dashboard**: Bitcoin price growth, stack value, purchasing power, multipliers
- **Motivational Insights**: Encouraging analysis to incentivize HODLing and stacking
- **Account Integration**: Uses your real account balances for projections

#### 🔮 Future Purchasing Power
- **Bitcoin Power Law Modeling**: Project future Bitcoin prices using historical data
- **Inflation Comparison**: Compare Bitcoin appreciation vs traditional inflation
- **Budget Projections**: Show how spending power increases over time
- **Visual Analysis**: Side-by-side current vs future budget comparisons
- **Multiple Horizons**: 1, 2, 5, 10-year purchasing power projections
- **Runway Analysis**: Shows months of financial runway with current spending

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
    'accounts': [],          # User's Bitcoin accounts (tracked/untracked)
    'transactions': [],      # User's income/expenses with account tracking
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
│ 💰 Budget Summary (Account-based metrics)                      │
│ [Tracked Balance] [In Categories] [Available to Assign]        │
├─────────────────────────────────────────────────────────────────┤
│ [🏦 Accounts] [📁 Categories] [💳 Transactions] (Tabs)         │
│ Modern forms with validation and editable data tables          │
├─────────────────────────────────────────────────────────────────┤
│ Sidebar: Month Navigation + Reports (5 types) + How to Use     │
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
2. See compelling examples on landing page:
   - **Net Worth Future Value**: 1M sats + 250k/month DCA over 20 years
   - **Opportunity Cost Analysis**: $250 dinner becomes $3,914 opportunity cost
3. Click "🚀 Get Started" to see the app with demo data
4. App loads with demo accounts (Checking + Bitcoin Savings) and sample allocations
5. Try adding your own transactions and explore the different tabs

### 📊 **Daily Budget Management**
1. **Manage Accounts**: Set up your tracked (on-budget) and untracked (savings) accounts
2. **Add Income**: Use the Income tab with date picker, amount validation, and account selection
3. **Allocate Budget**: Assign income to categories with smart availability checking
4. **Track Expenses**: Record spending with category and account selection
5. **Monitor Balances**: Real-time category and account balances with overspending warnings
6. **Transfer Funds**: Move money between accounts as needed
7. **View Reports**: Analyze spending patterns, net worth, and future projections

### 🔍 **Advanced Analysis**
1. **Spending Breakdown**: See which categories consume the most Bitcoin
2. **Net Worth Tracking**: Monitor account balances and income vs expenses over time
3. **Net Worth Future Value**: Visualize your Bitcoin stack growth over 5-20 years with DCA modeling
4. **Future Purchasing Power**: Understand how current spending affects future wealth
5. **Lifecycle Analysis**: Analyze specific purchases' long-term opportunity cost

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

## Database Integration Roadmap

### 🗄️ **Current Limitation**: Session-Only Storage
The current app uses session-based storage which provides maximum privacy but doesn't persist data between browser sessions. We're implementing a hybrid solution that maintains privacy while adding data persistence and portability.

### 🎯 **Hybrid Storage Solution**: localStorage + File Import/Export

#### **Phase 1: localStorage Persistence** 
- ⏳ Replace SQLite with browser localStorage for automatic session persistence
- ⏳ Data automatically saves as user works (no data loss during sessions)
- ⏳ Browser restart recovery - budgets persist until user clears browser data
- ⏳ Same privacy benefits - data never leaves user's device

#### **Phase 2: JSON Export/Import** ✅ **COMPLETED**
- ✅ Export budget data as JSON file for backup/sharing
- ✅ Import previously exported budgets on any device/browser
- ✅ Move data between devices while maintaining complete user control
- ✅ True self-custody of financial data (Bitcoin ethos)
- ✅ Data Management UI integrated in sidebar
- ✅ Reset to demo data functionality with confirmation

#### **Phase 3: YNAB CSV Import** 
- ✅ Import YNAB budget exports (CSV format) for easy migration
- ✅ Automatic mapping: YNAB accounts → Bitcoin accounts, categories → categories
- ✅ Convert USD amounts to satoshis using user-specified or current BTC rate
- ✅ Massive user acquisition opportunity (millions of existing YNAB users)

#### **Phase 4: Enhanced Export Formats**
- ✅ CSV export for analysis/spreadsheets
- ✅ YNAB-compatible CSV export (for users who want to go back)
- ✅ Multiple format support for different use cases

### 💡 **Benefits of New Storage System**
- **Seamless UX**: No data loss, works like native app
- **Data Ownership**: Users control their own budget files
- **Privacy-First**: No server-side storage, encryption options
- **YNAB Migration**: Easy path from YNAB subscription to Bitcoin budgeting
- **Backup Strategy**: Users choose their own data redundancy approach
- **Device Portability**: Use budget on multiple devices with file sync

### 🔄 **Implementation Status**
- **Current Branch**: `1-database-integration-that-allows-local-and-csv-formats`
- **Phase 1**: ⏳ Planned - localStorage integration (deferred)
- **Phase 2**: ✅ **COMPLETED** - JSON import/export with data management UI
- **Phase 3**: 🚧 In Progress - YNAB CSV import  
- **Phase 4**: ⏳ Planned - Additional export formats

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
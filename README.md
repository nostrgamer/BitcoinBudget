# Bitcoin Budget - Streamlit Web Application

A modern, privacy-focused envelope budgeting application for Bitcoin users with advanced opportunity cost analysis and Bitcoin retirement planning.

🌐 **Live Demo**: [https://bitcoinbudget.streamlit.app/](https://bitcoinbudget.streamlit.app/)

## What It Does

- Track Bitcoin income and expenses in satoshis with account-based budgeting
- Create spending categories with master category organization and visual hierarchy
- Allocate income to categories monthly with rollover tracking and smart automation
- View transaction history with full editing capabilities
- **Privacy-First Design**: Each user has isolated session data with JSON export/import
- **Professional Web Interface**: Modern, responsive design with interactive Plotly charts
- **Bitcoin Retirement Planning**: Advanced analytics with Power Law projections and retirement scenarios
- **Bitcoin Economics**: Built-in opportunity cost analysis showing the true cost of spending decisions

## Why This Architecture?

### 🔒 **Privacy & Security**
- **Session-Based Storage**: Each user's data is completely isolated in browser memory
- **No Shared Database**: Your financial data is never mixed with other users
- **JSON Export/Import**: Full data ownership with file-based backup system
- **Zero Installation**: No downloads, accounts, or personal information required
- **Self-Custody**: Following Bitcoin principles of personal data ownership

### 🌐 **Modern Web Experience**
- **Instant Access**: Works immediately in any browser, mobile-friendly
- **Interactive Charts**: Professional Plotly visualizations with proper visual hierarchy
- **Real-time Updates**: Instant feedback, form validation, and smart automation
- **Professional Dashboard**: Tabbed interface with account management and consolidated reports
- **Bitcoin-Native UI**: Satoshi-only input, tree-style category hierarchy, context-aware actions

### ⚡ **Performance & Reliability**
- **Streamlit Cloud Hosting**: Fast, reliable infrastructure with auto-deploy
- **No Database Setup**: Session state eliminates database complexity
- **Global CDN**: Fast loading worldwide with 99.9% uptime

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Charts**: Plotly (interactive visualizations with proper chart-first hierarchy)
- **Data**: Pandas + Session State (privacy-focused, no database)
- **Hosting**: Streamlit Cloud with GitHub auto-deploy
- **Storage**: Session-based with JSON export/import for data portability

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
- ✅ **Enhanced Account Management**: Tracked accounts (on-budget) and untracked accounts (savings/long-term)
  - **9 Account Types**: 🏦 Checking, 💰 Savings, 📈 Investment, 💳 Credit, 🏠 Loan, 🧊 Cold Storage, ⚡ Lightning Node, 🔥 Hot Wallet, 📱 Other
  - **Full-Width Edit Forms**: Professional account editing with balance and type changes
  - **Streamlined Actions**: Clean button layout with 📊 View, ✏️ Edit, 🗑️ Delete options
  - **Real-time Validation**: Enhanced input validation with immediate feedback
- ✅ **Smart Transaction Entry**: Enhanced forms with real-time validation and sats-only standard (rejecting BIP 178)
  - **Live Amount Preview**: See formatted satoshi amounts as you type
  - **Enhanced Validation**: Clear error messages and positive feedback for valid amounts
  - **Account Integration**: All transactions linked to specific Bitcoin accounts
- ✅ **Category Management**: Create master categories (Fixed, Variable, Savings) and subcategories with visual hierarchy
- ✅ **Professional Category Display**: Tree-style visual hierarchy with 📂 master categories and ├─ subcategories
- ✅ **Intelligent Allocation**: Allocate income with availability checking and rollover
- ✅ **Budget Health Dashboard**: Visual progress bars, color-coded status, and allocation percentage tracking
- ✅ **Quick Action Buttons**: Context-aware automation (Auto-Fix over-allocation, Distribute Evenly, To Bitcoin Stack)
- ✅ **Real-time Balances**: Live category balances with 🟢🔴⚪ status indicators and account tracking
- ✅ **Month Navigation**: Navigate between months with preserved data
- ✅ **Transaction Management**: Edit, delete, and categorize all transactions with account tracking
- ✅ **Account Transfers**: Move funds between different Bitcoin accounts

### ₿ **Bitcoin-Native Features**
- ✅ **Satoshi Precision**: All calculations in satoshis (no floating point errors)
- ✅ **Sats-Only Standard**: Enhanced validation that formally rejects BIP 178 (no BTC decimal input)
- ✅ **Professional Display**: Shows as "1,000,000 sats" with comma formatting
- ✅ **Bitcoin-Specific Account Types**: Cold storage, lightning nodes, hot wallets
- ✅ **Bitcoin Power Law Integration**: Fair value calculations for all projections
- ✅ **Opportunity Cost Focus**: Shows true cost of spending in Bitcoin appreciation terms

### 🎨 **Enhanced UI/UX Features** - **VISUAL HIERARCHY PERFECTED**
- ✅ **Charts-First Design**: Interactive visualizations prominently displayed, tables as supporting information
- ✅ **Professional Visual Hierarchy**: Proper text sizing with charts as the stars
- ✅ **Tree-Style Category Display**: 📂 master categories with ├─ └─ subcategory indicators
- ✅ **Smart Status Indicators**: 🟢 Good, ⚪ Empty/Zero, 🔴 Overspent with color coding
- ✅ **Context-Aware Actions**: Quick buttons that adapt to budget situation
- ✅ **Bitcoin Vibes Emphasis**: Orange visualization showing Bitcoin's purchasing power dominance
- ✅ **Custom Analysis Toggle**: Override net worth for scenario planning
- ✅ **Streamlined Navigation**: Consolidated reports with logical flow

### 📊 **Advanced Analytics & Reports** - **CONSOLIDATED TO 3 POWERFUL REPORTS**

The app now features **3 comprehensive reports** with proper visual hierarchy (charts first, tables supporting):

#### 1. 📊 **Spending Analysis & Future Purchasing Power**
- **Bitcoin Vibes Visualization**: Side-by-side pie charts showing current spending vs future cost with Bitcoin appreciation
- **Massive Orange "Bitcoin Vibes" Slice**: Shows the 93.7% savings from Bitcoin outpacing inflation (feature, not bug!)
- **Time Period Selection**: Current month, 3/6/12 months analysis
- **Interactive Charts**: Category spending with hover details and proper chart prominence
- **Summary Metrics**: Total spending, top categories, Bitcoin appreciation effects

#### 2. 🚀 **Net Worth & Bitcoin Retirement Planning**
- **4 Beautiful Charts**: Bitcoin stack growth, USD value, price projections, multipliers in 2x2 layout
- **Comprehensive Bitcoin Retirement Analysis**: 
  - Calculate minimum BTC needed for retirement using realistic spend-down strategy
  - Two price models: Fair Price (Power Law) and Super Conservative Floor Price (42% of fair price)
  - Interactive parameters: annual expenses, inflation rate, retirement duration
  - Early retirement insight: Starting in 2025 needs significantly less BTC than waiting
- **Custom Stack Analysis**: Toggle to override current net worth for scenario planning
- **Real Account Integration**: Uses actual tracked account balances for projections
- **Motivational Insights**: Encouraging analysis to incentivize Bitcoin accumulation
- **20-Year Projections**: Complete lifecycle analysis with retirement timeline

#### 3. 💰 **Lifecycle Cost Analysis**
- **Visual-First Layout**: Charts prominently displayed above supporting text
- **Dual Chart System**: 
  - Left: Donut chart showing Purchase Value vs Opportunity Cost
  - Right: Bar chart with Purchase Value, Future BTC Value, and Purchase + Inflation comparison
- **Transaction Selection**: Analyze any historical expense for opportunity cost
- **Time Horizon Control**: 1-10 year analysis with single slider (simplified from conservative model)
- **4-Column Metrics**: Clean layout showing key financial impact numbers
- **Bitcoin Power Law Integration**: Realistic price projections with mathematical accuracy

#### 📚 **Tutorial & Examples** - **UPDATED WITH REALISTIC DATA**
- **Honest Bitcoin Retirement Scenarios**: 10M sats starting stack, 1M sats monthly DCA
- **Realistic Timeline**: 15-20 year retirement planning with proper mathematical intersection
- **Visual Retirement Analysis**: Charts showing where Bitcoin accumulation meets retirement needs
- **Clean Pie Charts**: Removed hard-to-read text, maintained percentages and legend clarity

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
│ Sidebar: Month Navigation + Reports (6 types) + How to Use     │
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

### 🔒 **Your Data is Safe (But Temporary)**
- **Session Isolation**: Each browser session has completely separate data
- **No User Accounts**: No registration, login, or personal information required
- **⚠️ No Auto-Save**: Your data doesn't survive browser sessions - EXPORT TO SAVE
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
2. See realistic Bitcoin retirement examples on landing page:
   - **Net Worth Future Value**: 10M sats + 1M/month DCA showing honest 15-20 year timeline
   - **Opportunity Cost Analysis**: Purchases showing true Bitcoin opportunity cost
3. Click "🚀 Get Started" to see the app with enhanced demo data
4. App loads with realistic demo accounts and sample transactions
5. Explore the 3 consolidated reports to understand Bitcoin's purchasing power advantage

### 📊 **Daily Budget Management**
1. **Account Management**: Set up tracked (on-budget) and untracked (savings) Bitcoin accounts
2. **Smart Income Entry**: Enhanced forms with real-time validation and account selection
3. **Category Allocation**: Assign income with visual hierarchy and availability checking
4. **Expense Tracking**: Record spending with professional category tree display
5. **Real-time Monitoring**: Live balances with color-coded status and smart automation
6. **Data Ownership**: Export your budget as JSON before closing browser

### 🔍 **Advanced Bitcoin Analysis**
1. **Spending Analysis**: See your "Bitcoin Vibes" - how Bitcoin appreciation dwarfs traditional costs
2. **Retirement Planning**: Calculate minimum BTC needed for retirement with realistic timelines
3. **Opportunity Cost**: Analyze specific purchases to understand their true Bitcoin cost
4. **Future Projections**: Visualize your Bitcoin stack growth over 5-20 years
5. **Custom Scenarios**: Toggle different stack amounts to explore retirement possibilities

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
streamlit_app.py           # Main application (~2400 lines)
modules/
  ├── __init__.py         # Package initialization  
  └── reports.py          # 3 consolidated reports (~1000 lines)
requirements.txt          # Production dependencies
README.md                # Complete documentation
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

### ⚠️ **Important: Data Storage**
- **⚠️ SESSION ONLY**: Your data will be LOST when you close the browser tab
- **💾 MANUAL SAVE REQUIRED**: Data is NOT automatically saved - you must export manually
- **📥 Export Before Closing**: Always export your budget before closing the browser
- **📤 Import to Restore**: Upload your exported JSON file to restore your budget
- **🔒 Privacy Benefit**: No server storage means maximum privacy and security

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

## Data Management

### 📁 **JSON Export/Import**
The app includes simple file-based data management for users who want to backup or move their budget data:

- **📥 Export**: Download your complete budget as a timestamped JSON file
- **📤 Import**: Upload a previously exported JSON file to restore your data
- **🔄 Reset**: Clear all data and start fresh with demo data
- **🔒 Privacy**: All operations happen locally in your browser

### 💾 **How to Use Data Management**
1. **⚠️ IMPORTANT**: Your data exists ONLY while your browser tab is open
2. **💾 Export to Save**: Click "💾 Download Budget" in the sidebar before closing browser
3. **📤 Import to Restore**: Use "📥 Import Budget" to upload your saved JSON file
4. **🔄 Cross-Device**: Export from one device, import on another to continue your budget
5. **📅 Regular Backups**: Export your budget regularly to avoid losing work

### 🛡️ **Data Ownership**
Following Bitcoin's self-custody principles:
- **You Own Your Data**: Complete control over your financial information
- **No Server Storage**: Your data never leaves your device
- **File-Based Backup**: Simple, transparent backup using standard JSON format
- **Privacy by Design**: No accounts, no tracking, no data sharing

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

**Built for Bitcoiners who want to understand the true opportunity cost of spending decisions and plan realistic Bitcoin retirement scenarios.**
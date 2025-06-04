# Bitcoin Budget - Streamlit Web Application

A modern, web-based envelope budgeting application for Bitcoin users with advanced opportunity cost analysis.

## What It Does

- Track Bitcoin income and expenses in satoshis
- Create spending categories (groceries, rent, etc.)
- Allocate income to categories monthly
- Track category balances with rollover
- View transaction history
- **Professional Web Interface**: Modern, responsive design with interactive charts
- **Advanced Analytics**: Visual reports with Plotly charts
- **Opportunity Cost Analysis**: Analyze individual purchase impact on Bitcoin wealth

## Why Streamlit?

- **Modern Web UI** - Clean, responsive interface accessible from any browser
- **Interactive Charts** - Professional Plotly visualizations with hover details
- **No Installation** - Runs in browser, access from any device
- **Real-time Updates** - Instant feedback and form validation
- **Mobile Friendly** - Responsive design works on tablets and phones
- **Professional Dashboard** - Tabbed interface with metric cards and data tables

## Requirements

- Python 3.8+
- Streamlit
- Plotly (for interactive charts)
- Pandas (for data handling)
- SQLite (built into Python)

## Installation & Usage

### Install Dependencies
```bash
pip install -r requirements_streamlit.txt
```

### Run the Application
```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Build for Production
Deploy to Streamlit Cloud, Heroku, or any Python hosting platform:
- Single SQLite database file
- All business logic in `streamlit_app.py`
- Reports in `pages/reports.py`

## Features

### Core Envelope Budgeting
- ✅ **Modern Web Forms**: Add income/expenses with date pickers and validation
- ✅ **Category Management**: Create and manage spending categories
- ✅ **Smart Allocation**: Allocate income to categories with availability checking
- ✅ **Balance Tracking**: Real-time category balances with rollover
- ✅ **Month Navigation**: Previous/next month controls in sidebar
- ✅ **Transaction Management**: View, select, and delete transactions

### Bitcoin-Specific Features
- ✅ **Satoshi Precision**: All amounts in satoshis (no floating point errors)
- ✅ **Flexible Input**: Support "1000" or "0.001 BTC" formats
- ✅ **Clear Display**: Shows as "1,000,000 sats" with proper formatting
- ✅ **Bitcoin Economics**: Built-in Bitcoin power law calculations

### Professional Web Interface
- ✅ **Responsive Layout**: Works on desktop, tablet, and mobile
- ✅ **Interactive Metrics**: Key budget stats with visual indicators
- ✅ **Tabbed Organization**: Clean separation of income, categories, expenses, transactions
- ✅ **Data Tables**: Sortable, searchable transaction and category tables
- ✅ **Form Validation**: Real-time error checking and user feedback
- ✅ **Sidebar Navigation**: Month controls and page navigation

### Advanced Analytics & Reports

#### 📊 Spending Breakdown
- **Interactive Pie Charts**: Category spending with hover details
- **Time Period Selection**: Current month, 3/6/12 months
- **Summary Tables**: Category breakdowns with percentages
- **Visual Metrics**: Total spending, top categories, spending patterns

#### 📈 Net Worth Analysis
- **Dual Chart Display**: Monthly income vs expenses + cumulative trend
- **Interactive Plotly Charts**: Zoom, pan, hover for details
- **Summary Metrics**: Total income, expenses, net worth, averages
- **Time Series**: Track financial progress over multiple months

#### 🔮 Future Purchasing Power
- **Bitcoin Power Law Modeling**: Project future Bitcoin prices
- **Inflation Analysis**: Compare Bitcoin vs traditional inflation
- **Budget Projections**: Show how spending needs decrease over time
- **Visual Comparisons**: Side-by-side pie charts of current vs future budgets
- **Multiple Time Horizons**: 1, 2, 5, 10-year projections

#### ⏳ Lifecycle Cost Analysis
- **Transaction Selection**: Dropdown with all expense transactions
- **Interactive Settings**: Time horizon and inflation rate controls
- **4-Chart Dashboard**:
  - Bitcoin Amount Comparison (unchanged amounts)
  - USD Value Analysis (purchase vs future value vs inflation)
  - Bitcoin Price Projection (power law trend line)
  - Opportunity Cost Breakdown (pie chart)
- **Detailed Analysis**: Comprehensive text breakdown with bottom-line impact
- **Key Metrics**: Amount spent, future value, opportunity cost, purchasing power gain

## How It Works

### Modern Web Architecture
```python
# Streamlit page structure
streamlit_app.py     # Main application with navigation
pages/reports.py     # All reporting functionality
pages/__init__.py    # Package initialization
```

### Database (3 Tables - Unchanged)
```sql
transactions - all income/expenses with dates
categories   - spending envelopes (groceries, rent, etc.)
allocations  - monthly budget assignments
```

### Core Logic (Same Business Rules)
```python
# Simple functions, web-enabled
def get_available_to_assign(month):
    income = get_total_income(month)
    allocated = get_total_allocated(month)
    return income - allocated

def get_category_balance(category_id, month):
    allocated = get_category_allocated(category_id, month)
    spent = get_category_spent(category_id, month)
    return allocated - spent
```

### Economic Analysis (Enhanced Visualization)
```python
# Bitcoin Power Law with interactive charts
def calculate_btc_fair_value(days_since_genesis):
    return 1.0117e-17 * (days_since_genesis ** 5.82)

# Plotly charts for opportunity cost
fig = px.pie(opportunity_data, values='amount', names='category',
             title='Opportunity Cost Analysis')
st.plotly_chart(fig, use_container_width=True)
```

### Streamlit Interface Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ ₿ Bitcoin Budget - June 2025                                    │
├─────────────────────────────────────────────────────────────────┤
│ 💰 Budget Summary                                               │
│ [Total Income] [Rollover] [Allocated] [Available to Assign]     │
├─────────────────────────────────────────────────────────────────┤
│ [💰 Add Income] [📁 Categories] [💸 Expenses] [📋 Transactions] │
│ Modern forms with validation and interactive tables             │
├─────────────────────────────────────────────────────────────────┤
│ Sidebar: Month Navigation + Reports Access                     │
└─────────────────────────────────────────────────────────────────┘
```

## Example Workflow

1. **Access Application**: Open browser to `http://localhost:8501`
2. **Add Income**: Use the modern form with date picker and amount validation
3. **Create Categories**: Expandable form for quick category creation
4. **Allocate Budget**: Smart form showing available amounts and preventing over-allocation
5. **Add Expenses**: Category dropdown with real-time validation
6. **View Analytics**: Click "📊 Reports" in sidebar for advanced analysis
7. **Interactive Charts**: Hover, zoom, and interact with all visualizations
8. **Mobile Access**: Use from phone/tablet with responsive design

## Advanced Reports Examples

### Lifecycle Cost Analysis Workflow
1. **Select Transaction**: Choose expense from searchable dropdown
2. **Configure Analysis**: Set time horizon (1-10 years) and inflation rate
3. **View Key Metrics**: See opportunity cost in easy-to-understand cards
4. **Interactive Charts**: 
   - Bitcoin Amount: Shows amounts stay the same
   - USD Comparison: Purchase vs future value vs inflation
   - Price Projection: Bitcoin power law trend with markers
   - Opportunity Cost: Visual breakdown of foregone gains
5. **Detailed Analysis**: Comprehensive text explanation with bottom line

### Example Analysis Output
```
💸 Amount Spent: 50,000 sats ($49.13)
🚀 Future Value: $231.07 (+370.3%)
💔 Opportunity Cost: $181.94 (-370.3%)
📈 Purchasing Power: 5.8x vs inflation

Bottom Line: That coffee for 50,000 sats would be worth 
$181.94 MORE in 5 years - representing a 5.8x improvement 
in purchasing power!
```

## File Structure

```
streamlit_app.py           # Main application (~750 lines)
pages/
  ├── __init__.py         # Package initialization
  └── reports.py          # All reports functionality (~870 lines)
requirements_streamlit.txt # Dependencies (streamlit, plotly, pandas)
budget.db                 # SQLite database (auto-created)
README.md                 # This file
ARCHITECTURE.md           # Technical details
```

## Migration from Tkinter Version

The Streamlit version maintains **100% compatibility** with existing Tkinter databases:
- Same SQLite schema
- Same business logic
- Same data integrity
- Enhanced user experience

Simply install dependencies and run `streamlit run streamlit_app.py` to upgrade your existing budget data to the modern web interface.

## Deployment Options

- **Local Development**: `streamlit run streamlit_app.py`
- **Streamlit Cloud**: Free hosting with GitHub integration
- **Heroku**: Production deployment with custom domain
- **Docker**: Container deployment for any cloud provider
- **Self-hosted**: Run on your own server with reverse proxy
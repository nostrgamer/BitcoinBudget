# Bitcoin Budget

A privacy-focused Bitcoin budgeting application with envelope budgeting methodology and advanced analytics.

🌐 **Live Demo**: [https://bitcoinbudget.streamlit.app/](https://bitcoinbudget.streamlit.app/)

## Overview

Bitcoin Budget is a web-based financial management tool designed for Bitcoin users who want to understand the true opportunity cost of their spending decisions. Built with Python and Streamlit, it provides envelope budgeting capabilities with session-based privacy and comprehensive Bitcoin analytics.

## Key Features

- **Account-Based Budgeting**: Track income, expenses, and transfers across multiple Bitcoin accounts
- **Category Management**: Hierarchical spending categories with allocation tracking
- **Opportunity Cost Analysis**: Visualize the Bitcoin appreciation impact of spending decisions  
- **Retirement Planning**: Calculate Bitcoin retirement scenarios using Power Law projections
- **Privacy-First**: Session-based storage with JSON export/import for data portability
- **Mobile Responsive**: Optimized layouts for both desktop and mobile devices

## Technology Stack

- **Framework**: Streamlit (Python)
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **Hosting**: Streamlit Cloud
- **Storage**: Browser session state with file export/import

## Quick Start

### Online Demo
Visit [bitcoinbudget.streamlit.app](https://bitcoinbudget.streamlit.app/) to try the application immediately with sample data.

### Local Installation
```bash
git clone https://github.com/nostrgamer/BitcoinBudget.git
cd BitcoinBudget
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Core Functionality

### Budget Management
- **Account Types**: Support for 9 Bitcoin account types including cold storage, Lightning nodes, and traditional accounts
- **Transaction Tracking**: Record income and expenses with account association
- **Category Allocation**: Distribute funds across spending categories with rollover support
- **Balance Monitoring**: Real-time category balances with visual status indicators

### Analytics & Reports

**1. Spending Analysis**  
Compare current spending patterns with future purchasing power, accounting for Bitcoin appreciation.

**2. Retirement Planning**  
Calculate minimum Bitcoin requirements for retirement using conservative and fair-value price models.

**3. Lifecycle Cost Analysis**  
Analyze opportunity cost of individual purchases over configurable time horizons.

### Mobile Optimization
- Responsive column layouts that adapt to screen size
- Touch-friendly interface elements
- Optimized chart positioning and legend placement
- User-controlled layout toggle between desktop and mobile modes

## Architecture

### Privacy Model
- **Session Isolation**: Each user's data exists only in their browser session
- **No Persistent Storage**: Data is not saved on servers
- **Export/Import**: Users control data backup through JSON files
- **Zero Personal Information**: No accounts or registration required

### Data Structure
```python
user_data = {
    'accounts': [],          # Bitcoin accounts with balances
    'transactions': [],      # Income/expense records
    'categories': [],        # Spending categories
    'allocations': []        # Budget allocations
}
```

## Development

### File Structure
```
streamlit_app.py           # Main application (~2400 lines)
modules/
  └── reports.py          # Analytics and reporting (~1000 lines)
requirements.txt          # Dependencies
README.md                # Documentation
```

### Key Principles
- Satoshi-precision arithmetic (no floating-point errors)
- Bitcoin Power Law integration for price projections
- Session-based privacy architecture
- Mobile-first responsive design

## Data Management

**Export**: Download complete budget data as timestamped JSON file  
**Import**: Restore data from previously exported JSON file  
**Reset**: Clear all data and restart with sample data  

**Important**: Data exists only during browser session. Export before closing to preserve work.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test locally with `streamlit run streamlit_app.py`
4. Submit a pull request

Changes are automatically deployed when merged to main branch.

## License

MIT License

---

**Try it now**: [bitcoinbudget.streamlit.app](https://bitcoinbudget.streamlit.app/)
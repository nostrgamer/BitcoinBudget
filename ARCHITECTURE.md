# Bitcoin Budget Desktop - Architecture Documentation

## Overview

Bitcoin Budget Desktop is a simple envelope budgeting application for Bitcoin users. The application follows Clean Architecture principles with manual transaction entry, focusing on the core budgeting methodology without unnecessary complexity.

## Architecture Principles

### Clean Architecture
The application is structured in layers with clear dependency rules:
- **Dependencies point inward only**
- **Core domain has no external dependencies**
- **Infrastructure implements domain contracts**
- **UI depends only on application layer**

### Envelope Budgeting
- **Monthly budget periods** with category allocations
- **Rollover logic** for unspent funds
- **Manual transaction entry** for privacy and control
- **Available to assign** tracking for unallocated funds

### MVVM Pattern
- **Model**: Domain entities and DTOs
- **View**: WPF views and controls
- **ViewModel**: Presentation logic and data binding

## Technology Stack

### Core Technologies
- **.NET 8**: Latest LTS framework
- **WPF**: Desktop UI framework with rich data binding
- **Entity Framework Core**: ORM with SQLite provider
- **SQLite**: Embedded database for local storage

### Supporting Libraries
- **xUnit**: Testing framework
- **FluentAssertions**: Readable test assertions
- **MediatR**: CQRS pattern implementation

## Project Structure

```
BitcoinBudget.Desktop/
├── src/
│   ├── BitcoinBudget.Core/              # Domain Layer
│   │   ├── Entities/
│   │   │   ├── Budget.cs               # Root aggregate
│   │   │   ├── Category.cs             # Spending envelope
│   │   │   ├── Transaction.cs          # Bitcoin transaction
│   │   │   ├── BudgetPeriod.cs        # Monthly budget cycle
│   │   │   └── CategoryAllocation.cs   # Budget allocation
│   │   ├── ValueObjects/
│   │   │   ├── SatoshiAmount.cs       # Immutable Bitcoin amount
│   │   │   └── TransactionType.cs     # Transaction classification
│   │   ├── Interfaces/
│   │   │   └── Repositories/          # Data access contracts
│   │   └── Exceptions/
│   │       ├── DomainException.cs
│   │       └── InsufficientFundsException.cs
│   ├── BitcoinBudget.Application/       # Application Layer
│   │   ├── Commands/
│   │   │   ├── Categories/            # Category operations
│   │   │   ├── Transactions/          # Transaction operations
│   │   │   └── Budget/                # Budget operations
│   │   ├── Queries/
│   │   │   ├── Categories/            # Category queries
│   │   │   ├── Transactions/          # Transaction queries
│   │   │   └── Reports/               # Budget reports
│   │   ├── Handlers/
│   │   │   ├── CommandHandlers/       # Command implementations
│   │   │   └── QueryHandlers/         # Query implementations
│   │   └── DTOs/
│   │       ├── CategoryDto.cs
│   │       ├── TransactionDto.cs
│   │       └── BudgetSummaryDto.cs
│   ├── BitcoinBudget.Infrastructure/    # Infrastructure Layer
│   │   ├── Data/
│   │   │   ├── BudgetDbContext.cs     # EF Core context
│   │   │   ├── Configurations/        # Entity configurations
│   │   │   ├── Repositories/          # Repository implementations
│   │   │   └── Migrations/            # Database migrations
│   │   └── Configuration/
│   │       └── DatabaseConfiguration.cs
│   ├── BitcoinBudget.Presentation/      # Presentation Layer
│   │   ├── ViewModels/
│   │   │   ├── MainWindowViewModel.cs
│   │   │   ├── CategoriesViewModel.cs
│   │   │   ├── TransactionsViewModel.cs
│   │   │   └── BudgetViewModel.cs
│   │   ├── Views/
│   │   │   ├── MainWindow.xaml
│   │   │   ├── CategoriesView.xaml
│   │   │   ├── TransactionsView.xaml
│   │   │   └── BudgetView.xaml
│   │   └── Converters/
│   │       ├── SatoshiToStringConverter.cs
│   │       └── BooleanToVisibilityConverter.cs
│   └── Tests/
│       ├── BitcoinBudget.Core.Tests/
│       ├── BitcoinBudget.Application.Tests/
│       ├── BitcoinBudget.Infrastructure.Tests/
│       └── BitcoinBudget.Presentation.Tests/
```

## Domain Model

### Core Entities

#### Budget (Aggregate Root)
- **Purpose**: Central aggregate containing all budget data
- **Properties**: Id, Name, CreatedDate
- **Relationships**: Categories, BudgetPeriods, Transactions

#### Category
- **Purpose**: Spending envelopes for budget organization
- **Properties**: Id, Name, Description, Color
- **Business Rules**: Category names must be unique

#### Transaction
- **Purpose**: Records Bitcoin movements
- **Properties**: Id, Amount, Date, Description, CategoryId, TransactionType
- **Business Rules**: Must reference valid category, amount validation

#### BudgetPeriod
- **Purpose**: Monthly budget cycles
- **Properties**: Id, Year, Month, StartDate, EndDate, IsClosed, ClosedDate
- **Business Rules**: No overlapping periods
- **Phase 3 Enhancements**: Rollover calculations, period transitions, overspending detection

#### CategoryAllocation
- **Purpose**: Budget assignments to categories
- **Properties**: Id, Amount, CategoryId, BudgetPeriodId, RolloverAmount, NewAllocation, CreatedDate, LastModified
- **Business Rules**: Total allocations cannot exceed available funds
- **Phase 3 Enhancements**: Rollover tracking, allocation analysis, audit fields

### Value Objects

#### SatoshiAmount
- **Purpose**: Immutable Bitcoin amount representation
- **Properties**: Value (long)
- **Operations**: Add, Subtract, Multiply, Divide
- **Validation**: Non-negative values, proper arithmetic

#### TransactionType
- **Purpose**: Classification of transactions
- **Values**: Income, Expense, Transfer
- **Business Rules**: Determines transaction behavior

## Database Design

### Simple Schema

```sql
CREATE TABLE Budgets (
    Id INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    CreatedDate TEXT NOT NULL
);

CREATE TABLE Categories (
    Id INTEGER PRIMARY KEY,
    BudgetId INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Description TEXT,
    Color TEXT,
    FOREIGN KEY (BudgetId) REFERENCES Budgets(Id),
    UNIQUE(BudgetId, Name)
);

CREATE TABLE BudgetPeriods (
    Id INTEGER PRIMARY KEY,
    BudgetId INTEGER NOT NULL,
    Year INTEGER NOT NULL,
    Month INTEGER NOT NULL,
    StartDate TEXT NOT NULL,
    EndDate TEXT NOT NULL,
    IsClosed INTEGER NOT NULL DEFAULT 0,
    ClosedDate TEXT,
    FOREIGN KEY (BudgetId) REFERENCES Budgets(Id),
    UNIQUE(BudgetId, Year, Month)
);

CREATE TABLE Transactions (
    Id INTEGER PRIMARY KEY,
    BudgetId INTEGER NOT NULL,
    CategoryId INTEGER NOT NULL,
    Amount INTEGER NOT NULL,
    Date TEXT NOT NULL,
    Description TEXT,
    TransactionType INTEGER NOT NULL,
    FOREIGN KEY (BudgetId) REFERENCES Budgets(Id),
    FOREIGN KEY (CategoryId) REFERENCES Categories(Id)
);

CREATE TABLE CategoryAllocations (
    Id INTEGER PRIMARY KEY,
    BudgetPeriodId INTEGER NOT NULL,
    CategoryId INTEGER NOT NULL,
    Amount INTEGER NOT NULL,
    RolloverAmount INTEGER NOT NULL DEFAULT 0,
    NewAllocation INTEGER NOT NULL DEFAULT 0,
    CreatedDate TEXT NOT NULL,
    LastModified TEXT NOT NULL,
    FOREIGN KEY (BudgetPeriodId) REFERENCES BudgetPeriods(Id),
    FOREIGN KEY (CategoryId) REFERENCES Categories(Id),
    UNIQUE(BudgetPeriodId, CategoryId)
);
```

## Core Features

### 1. Category Management
- Create, edit, delete spending categories
- Assign colors for visual organization
- Track category balances

### 2. Budget Allocation
- Assign available sats to categories monthly
- Track "Available to Assign" amount
- Validate allocations don't exceed available funds

### 3. Transaction Entry
- Manual entry of Bitcoin transactions
- Assign transactions to categories
- Support income, expense, and transfer types

### 4. Monthly Budget Periods
- Automatic monthly period creation
- Rollover unspent funds to next month
- Track overspending in categories

### 5. Budget Reporting
- Category balance summaries
- Monthly spending reports
- Available funds tracking

## Development Phases

### Phase 1: Core Foundation ✅ COMPLETE (2-3 weeks)
- Basic domain entities and value objects
- SQLite database with EF Core
- Simple WPF UI for categories and transactions
- Basic budget allocation

### Phase 2: Enhanced Allocation System ✅ COMPLETE (2-3 weeks)
- Full budget allocation workflow
- Available to Assign calculation
- Budget period management
- Enhanced UI for allocations

### Phase 3: Core Monthly Logic ✅ COMPLETE - Backend Only (1-2 weeks)
- Monthly budget periods with rollover
- Rollover logic and calculations
- Enhanced transaction categorization
- Month transition automation
- **Note**: UI updates not yet implemented

### Phase 4: UI for Monthly Features (NEXT - 1-2 weeks)
- Rollover summary displays
- Month transition interface
- Overspending indicators
- Enhanced budget period navigation
- Monthly rollover reports

### Phase 5: UI Polish (Future - 1-2 weeks)
- Improved user interface design
- Advanced data validation and error handling
- Export/import functionality

This simplified architecture focuses on delivering a functional envelope budgeting system without unnecessary complexity, allowing for rapid development and easy maintenance. 
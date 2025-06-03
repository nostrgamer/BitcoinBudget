# Bitcoin Budget Desktop

A simple envelope budgeting desktop application for Bitcoin users with manual transaction entry. Built with C# and .NET 8, following Clean Architecture principles.

![.NET](https://img.shields.io/badge/.NET-8.0-purple)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

## 🎯 Project Overview

**Core Principle: Start Simple, Build Incrementally**

This application implements envelope budgeting specifically designed for Bitcoin users who prefer manual transaction entry over automatic bank connections. Each spending category acts as an "envelope" where you allocate satoshis for specific purposes.

## 🚀 Features

### Phase 1 - Core Features ✅
- **Categories**: Spending envelopes (groceries, rent, savings, etc.)
- **Budget Allocation**: Assign sats to categories monthly
- **Transactions**: Manual entry of Bitcoin movements
- **Monthly Periods**: Budget cycles with rollover logic
- **Balance Tracking**: Available funds and category balances
- **Comprehensive Diagnostics**: Built-in system validation

### Phase 2 - Budget Management ✅
- **Income Management**: Add and track Bitcoin income
- **Expense Tracking**: Record spending against categories
- **Real-time Calculations**: Live updates of available funds
- **Data Persistence**: SQLite database with Entity Framework
- **Delete Operations**: Safe deletion with data integrity
- **Budget Reset**: Complete data reset with safety features

### Phase 3 - Monthly System 🚧
- **Month-to-Month Transitions**: Automatic new period creation
- **Rollover Logic**: Carry unspent funds to next month
- **Overspending Handling**: Track and manage category overruns
- **Historical Navigation**: View past/future months

## 🛠️ Technology Stack

- **Framework**: .NET 8 with WPF
- **Database**: SQLite with Entity Framework Core
- **Architecture**: Clean Architecture + MVVM
- **Testing**: xUnit with FluentAssertions
- **Logging**: Serilog with file logging

## 🏗️ Architecture

### Clean Architecture Layers
```
BitcoinOnBudgetDesktop/
├── src/
│   ├── Core/                    # Domain layer
│   │   ├── Entities/           # Domain entities
│   │   ├── ValueObjects/       # Value objects (SatoshiAmount, etc.)
│   │   ├── Interfaces/         # Domain contracts
│   │   └── Exceptions/         # Domain exceptions
│   ├── Application/            # Application layer
│   │   ├── Commands/          # CQRS commands
│   │   ├── Queries/           # CQRS queries
│   │   ├── Handlers/          # Command/Query handlers
│   │   └── DTOs/              # Data transfer objects
│   ├── Infrastructure/         # Infrastructure layer
│   │   ├── Data/              # EF Core, repositories
│   │   └── Configuration/     # App configuration
│   ├── Presentation/           # Presentation layer (WPF)
│   │   ├── ViewModels/        # MVVM view models
│   │   ├── Views/             # WPF views/windows
│   │   └── Converters/        # UI data converters
│   └── Tests/
│       ├── Core.Tests/        # Domain tests
│       ├── Application.Tests/ # Application tests
│       ├── Infrastructure.Tests/ # Infrastructure tests
│       └── Presentation.Tests/ # UI tests
```

### Key Patterns
- **CQRS**: Command Query Responsibility Segregation
- **Repository Pattern**: Data access abstraction
- **MVVM**: Model-View-ViewModel for WPF
- **Value Objects**: Bitcoin-safe `SatoshiAmount` calculations
- **Domain-Driven Design**: Rich domain models with business logic

## 🔗 Bitcoin-Specific Features

- **SatoshiAmount Value Object**: Immutable, validated Bitcoin amounts
- **No Floating Point**: All calculations use `long` integers (satoshis)
- **Manual Entry**: No automatic bank connections or API dependencies
- **Privacy-First**: All data stored locally in SQLite

## 🚀 Getting Started

### Prerequisites
- .NET 8 SDK
- Windows 10/11
- Visual Studio 2022 or VS Code

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/nostrgamer/BitcoinBudgetDesktop.git
   cd BitcoinBudgetDesktop
   ```

2. Build the solution:
   ```bash
   dotnet build
   ```

3. Run the application:
   ```bash
   dotnet run --project src/BitcoinOnBudgetDesktop.Presentation
   ```

### First Run
1. The application will automatically create a SQLite database
2. Built-in diagnostics will validate system functionality
3. Start by adding income and creating categories
4. Allocate satoshis to categories and begin tracking expenses

## 📊 Usage

### Envelope Budgeting Workflow
1. **Add Income**: Record Bitcoin received
2. **Create Categories**: Define spending envelopes (rent, groceries, etc.)
3. **Allocate Funds**: Assign satoshis to each category
4. **Record Expenses**: Log spending against specific categories
5. **Monitor Balances**: Track remaining funds in each envelope

### Key Concepts
- **Available to Assign**: Unallocated sats ready for budget assignment
- **Rollover**: Unspent category funds carry to next month
- **Overspending**: Track when category spending exceeds allocation
- **Monthly Reset**: New budget period with fresh allocations

## 🔧 Development

### Running Tests
```bash
dotnet test
```

### Building for Release
```bash
dotnet publish -c Release -r win-x64 --self-contained
```

### Development Philosophy
- Start with the simplest working version
- Add one feature at a time
- Test core domain logic, be pragmatic with simple CRUD
- UI function over form initially
- Avoid premature optimization

## 📝 Coding Standards

### C# Guidelines
- Use PascalCase for public members, camelCase for private fields
- Prefix private fields with underscore: `_fieldName`
- Maximum line length: 120 characters
- Use nullable reference types consistently

### Bitcoin-Specific Rules
- Always use `SatoshiAmount` value object for Bitcoin amounts
- Never use `decimal` or `double` for Bitcoin calculations
- All Bitcoin amounts stored as `long` (satoshis)
- Use domain validation for Bitcoin-specific business rules

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Bitcoin community for inspiration
- Clean Architecture principles by Robert C. Martin
- Envelope budgeting methodology
- .NET and WPF communities

## 📞 Support

- Create an [Issue](https://github.com/nostrgamer/BitcoinBudgetDesktop/issues) for bug reports
- Start a [Discussion](https://github.com/nostrgamer/BitcoinBudgetDesktop/discussions) for questions
- Check the [Wiki](https://github.com/nostrgamer/BitcoinBudgetDesktop/wiki) for documentation

---

**"Be your own bank with your own budget."** 🟠⚡ 
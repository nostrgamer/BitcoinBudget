using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Commands.Budget;

/// <summary>
/// Command to delete all data for a budget (reset budget).
/// This includes all transactions, category allocations, categories, and budget periods.
/// </summary>
public record DeleteBudgetDataCommand(int BudgetId) : IRequest<DeleteBudgetDataResult>;

public record DeleteBudgetDataResult(
    bool Success,
    string? ErrorMessage = null,
    int TransactionsDeleted = 0,
    int CategoriesDeleted = 0,
    int AllocationsDeleted = 0,
    int BudgetPeriodsDeleted = 0
); 
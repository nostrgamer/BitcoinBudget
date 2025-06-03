using BitcoinOnBudgetDesktop.Core.ValueObjects;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Commands.Budget;

/// <summary>
/// Command to add an expense transaction to a specific category.
/// This reduces the available balance in that category's envelope.
/// </summary>
public record AddExpenseCommand(
    int BudgetId,
    int CategoryId,
    SatoshiAmount Amount,
    string Description,
    DateTime? Date = null) : IRequest<AddExpenseResult>;

public record AddExpenseResult(
    bool Success,
    int? TransactionId = null,
    string? ErrorMessage = null
); 
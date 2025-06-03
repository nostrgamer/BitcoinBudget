using BitcoinOnBudgetDesktop.Core.ValueObjects;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Commands.Budget;

/// <summary>
/// Command to add income to the budget, increasing available funds.
/// </summary>
public record AddIncomeCommand(
    int BudgetId,
    SatoshiAmount Amount,
    string Description,
    DateTime? Date = null
) : IRequest<AddIncomeResult>;

public record AddIncomeResult(
    bool Success,
    int? TransactionId = null,
    string? ErrorMessage = null
); 
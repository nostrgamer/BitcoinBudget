using BitcoinOnBudgetDesktop.Core.ValueObjects;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Commands.Budget;

/// <summary>
/// Command to allocate satoshis to a category for a specific budget period.
/// </summary>
public record AllocateToCategoryCommand(
    int BudgetPeriodId,
    int CategoryId,
    SatoshiAmount Amount
) : IRequest<AllocateToCategoryResult>;

public record AllocateToCategoryResult(
    bool Success,
    string? ErrorMessage = null
); 
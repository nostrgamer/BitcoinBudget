using MediatR;
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.Commands.Budget;

/// <summary>
/// Command to transition from current month to next month with automatic rollover calculations.
/// </summary>
public record TransitionToNextMonthCommand(
    int BudgetId,
    bool ClosePreviousPeriod = true,
    Dictionary<int, SatoshiAmount>? CategoryNewAllocations = null
) : IRequest<TransitionToNextMonthResult>;

public record TransitionToNextMonthResult(
    bool Success,
    int? NewBudgetPeriodId = null,
    Dictionary<int, SatoshiAmount>? RolloverAmounts = null,
    SatoshiAmount TotalRollover = default,
    string? ErrorMessage = null
); 
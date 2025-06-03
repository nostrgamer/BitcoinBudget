using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Commands.Budget;

/// <summary>
/// Command to create a new monthly budget period.
/// </summary>
public record CreateBudgetPeriodCommand(
    int BudgetId,
    int Year,
    int Month
) : IRequest<CreateBudgetPeriodResult>;

public record CreateBudgetPeriodResult(
    bool Success,
    int? BudgetPeriodId = null,
    string? ErrorMessage = null
); 
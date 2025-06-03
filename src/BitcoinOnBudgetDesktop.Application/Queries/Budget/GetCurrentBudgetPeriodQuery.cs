using BitcoinOnBudgetDesktop.Application.DTOs;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Queries.Budget;

/// <summary>
/// Query to get the current budget period for a budget (current month/year).
/// </summary>
public record GetCurrentBudgetPeriodQuery(
    int BudgetId
) : IRequest<BudgetPeriodDto?>; 
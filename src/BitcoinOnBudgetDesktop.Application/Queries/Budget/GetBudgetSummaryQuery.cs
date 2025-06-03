using BitcoinOnBudgetDesktop.Application.DTOs;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Queries.Budget;

/// <summary>
/// Query to get a complete budget summary with categories, allocations, and available amounts.
/// </summary>
public record GetBudgetSummaryQuery(
    int BudgetId,
    int BudgetPeriodId
) : IRequest<BudgetSummaryDto?>; 
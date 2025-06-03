using MediatR;
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.Queries.Budget;

/// <summary>
/// Query to get rollover summary information for a budget period.
/// </summary>
public record GetRolloverSummaryQuery(
    int BudgetId,
    int? TargetYear = null,
    int? TargetMonth = null
) : IRequest<RolloverSummaryDto?>;

/// <summary>
/// DTO containing rollover information for categories and overall summary.
/// </summary>
public record RolloverSummaryDto(
    int BudgetPeriodId,
    int Year,
    int Month,
    string PeriodDisplayName,
    bool IsClosed,
    Dictionary<int, CategoryRolloverDto> CategoryRollovers,
    SatoshiAmount TotalRolloverAvailable,
    SatoshiAmount TotalOverspent,
    int CategoriesWithRollover,
    int CategoriesOverspent
);

/// <summary>
/// DTO for individual category rollover information.
/// </summary>
public record CategoryRolloverDto(
    int CategoryId,
    string CategoryName,
    SatoshiAmount AllocatedAmount,
    SatoshiAmount SpentAmount,
    SatoshiAmount RolloverAmount,
    SatoshiAmount OverspentAmount,
    bool HasRollover,
    bool IsOverspent
); 
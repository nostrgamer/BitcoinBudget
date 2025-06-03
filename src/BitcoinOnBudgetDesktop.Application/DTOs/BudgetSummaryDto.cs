using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.DTOs;

/// <summary>
/// Data transfer object for budget summary information.
/// </summary>
public record BudgetSummaryDto(
    int BudgetId,
    string BudgetName,
    SatoshiAmount TotalIncome,
    SatoshiAmount TotalAllocated,
    SatoshiAmount AvailableToAssign,
    IEnumerable<CategoryDto> Categories,
    string CurrentPeriod
); 
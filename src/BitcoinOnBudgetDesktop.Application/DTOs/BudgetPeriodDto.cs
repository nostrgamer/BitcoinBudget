using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.DTOs;

/// <summary>
/// Data transfer object for budget period information.
/// </summary>
public record BudgetPeriodDto(
    int Id,
    int BudgetId,
    int Year,
    int Month,
    DateTime StartDate,
    DateTime EndDate,
    SatoshiAmount TotalAllocated,
    string DisplayName,
    IEnumerable<CategoryAllocationDto> CategoryAllocations
); 
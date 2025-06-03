using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.DTOs;

/// <summary>
/// Data transfer object for category allocation information.
/// </summary>
public record CategoryAllocationDto(
    int Id,
    int CategoryId,
    string CategoryName,
    SatoshiAmount Amount
); 
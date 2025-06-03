using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.DTOs;

/// <summary>
/// Data transfer object for category information.
/// </summary>
public record CategoryDto(
    int Id,
    string Name,
    string? Description,
    string? Color,
    SatoshiAmount AllocatedAmount,
    SatoshiAmount SpentAmount,
    SatoshiAmount RemainingAmount
)
{
    public override string ToString() => Name;
}; 
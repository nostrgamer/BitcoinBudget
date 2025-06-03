using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.DTOs;

/// <summary>
/// Data transfer object for category information with rollover tracking.
/// </summary>
public record CategoryDto(
    int Id,
    string Name,
    string? Description,
    string? Color,
    SatoshiAmount AllocatedAmount,
    SatoshiAmount RolloverAmount,
    SatoshiAmount NewAllocation,
    SatoshiAmount SpentAmount,
    SatoshiAmount RemainingAmount,
    bool HasRollover,
    decimal RolloverPercentage
)
{
    public override string ToString() => Name;

    /// <summary>
    /// Gets a formatted display of rollover information.
    /// </summary>
    public string RolloverDisplay => HasRollover 
        ? $"{RolloverAmount} (rollover) + {NewAllocation} (new) = {AllocatedAmount} total"
        : $"{AllocatedAmount} (new allocation)";

    /// <summary>
    /// Indicates if this category is overspent.
    /// </summary>
    public bool IsOverspent => RemainingAmount.Value < 0;

    /// <summary>
    /// Gets the overspent amount (positive value if overspent, zero otherwise).
    /// </summary>
    public SatoshiAmount OverspentAmount => IsOverspent 
        ? new SatoshiAmount(-RemainingAmount.Value) 
        : SatoshiAmount.Zero;
}; 
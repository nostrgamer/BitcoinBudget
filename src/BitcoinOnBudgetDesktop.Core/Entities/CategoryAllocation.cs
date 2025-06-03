using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Core.Entities;

/// <summary>
/// Represents the allocation of funds to a category for a specific budget period,
/// including rollover tracking from previous periods.
/// </summary>
public class CategoryAllocation
{
    public int Id { get; private set; }
    public int BudgetPeriodId { get; private set; }
    public int CategoryId { get; private set; }
    public SatoshiAmount Amount { get; private set; }
    public SatoshiAmount RolloverAmount { get; private set; }
    public SatoshiAmount NewAllocation { get; private set; }
    public DateTime CreatedDate { get; private set; }
    public DateTime? LastModified { get; private set; }

    // Navigation properties
    public BudgetPeriod BudgetPeriod { get; private set; } = null!;
    public Category Category { get; private set; } = null!;

    // Private constructor for EF Core
    private CategoryAllocation() { }

    public CategoryAllocation(int budgetPeriodId, int categoryId, SatoshiAmount amount)
    {
        if (amount.Value < 0)
            throw new ArgumentException("Allocation amount cannot be negative", nameof(amount));

        BudgetPeriodId = budgetPeriodId;
        CategoryId = categoryId;
        Amount = amount;
        RolloverAmount = SatoshiAmount.Zero;
        NewAllocation = amount;
        CreatedDate = DateTime.UtcNow;
    }

    /// <summary>
    /// Creates a category allocation with rollover from previous period.
    /// </summary>
    public CategoryAllocation(int budgetPeriodId, int categoryId, SatoshiAmount rolloverAmount, SatoshiAmount newAllocation)
    {
        if (rolloverAmount.Value < 0)
            throw new ArgumentException("Rollover amount cannot be negative", nameof(rolloverAmount));
        
        if (newAllocation.Value < 0)
            throw new ArgumentException("New allocation amount cannot be negative", nameof(newAllocation));

        BudgetPeriodId = budgetPeriodId;
        CategoryId = categoryId;
        RolloverAmount = rolloverAmount;
        NewAllocation = newAllocation;
        Amount = new SatoshiAmount(rolloverAmount.Value + newAllocation.Value);
        CreatedDate = DateTime.UtcNow;
    }

    public void UpdateAmount(SatoshiAmount amount)
    {
        if (amount.Value < 0)
            throw new ArgumentException("Allocation amount cannot be negative", nameof(amount));

        Amount = amount;
        // When updating total amount, preserve rollover and adjust new allocation
        NewAllocation = new SatoshiAmount(Math.Max(0, amount.Value - RolloverAmount.Value));
        LastModified = DateTime.UtcNow;
    }

    /// <summary>
    /// Updates the allocation by specifying rollover and new allocation separately.
    /// </summary>
    public void UpdateAllocation(SatoshiAmount rolloverAmount, SatoshiAmount newAllocation)
    {
        if (rolloverAmount.Value < 0)
            throw new ArgumentException("Rollover amount cannot be negative", nameof(rolloverAmount));
        
        if (newAllocation.Value < 0)
            throw new ArgumentException("New allocation amount cannot be negative", nameof(newAllocation));

        RolloverAmount = rolloverAmount;
        NewAllocation = newAllocation;
        Amount = new SatoshiAmount(rolloverAmount.Value + newAllocation.Value);
        LastModified = DateTime.UtcNow;
    }

    /// <summary>
    /// Gets the percentage of total allocation that came from rollover.
    /// </summary>
    public decimal GetRolloverPercentage()
    {
        if (Amount.Value == 0)
            return 0;

        return (decimal)RolloverAmount.Value / Amount.Value * 100;
    }

    /// <summary>
    /// Checks if this allocation includes rollover funds.
    /// </summary>
    public bool HasRollover()
    {
        return RolloverAmount.Value > 0;
    }

    /// <summary>
    /// Gets a breakdown of the allocation sources.
    /// </summary>
    public (SatoshiAmount Rollover, SatoshiAmount Fresh) GetAllocationBreakdown()
    {
        return (RolloverAmount, NewAllocation);
    }
} 
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Core.Entities;

/// <summary>
/// Represents the allocation of funds to a category for a specific budget period.
/// </summary>
public class CategoryAllocation
{
    public int Id { get; private set; }
    public int BudgetPeriodId { get; private set; }
    public int CategoryId { get; private set; }
    public SatoshiAmount Amount { get; private set; }

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
    }

    public void UpdateAmount(SatoshiAmount amount)
    {
        if (amount.Value < 0)
            throw new ArgumentException("Allocation amount cannot be negative", nameof(amount));

        Amount = amount;
    }
} 
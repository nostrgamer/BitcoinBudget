using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Core.Entities;

/// <summary>
/// Represents a spending envelope/category in the budget system.
/// Categories organize transactions and track allocated vs spent amounts.
/// </summary>
public class Category
{
    public int Id { get; private set; }
    public int BudgetId { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public string? Description { get; private set; }
    public string? Color { get; private set; }

    // Navigation properties
    public Budget Budget { get; private set; } = null!;
    public ICollection<Transaction> Transactions { get; private set; } = new List<Transaction>();
    public ICollection<CategoryAllocation> Allocations { get; private set; } = new List<CategoryAllocation>();

    // Private constructor for EF Core
    private Category() { }

    public Category(int budgetId, string name, string? description = null, string? color = null)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Category name cannot be empty", nameof(name));

        BudgetId = budgetId;
        Name = name.Trim();
        Description = description?.Trim();
        Color = color?.Trim();
    }

    public void UpdateDetails(string name, string? description = null, string? color = null)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Category name cannot be empty", nameof(name));

        Name = name.Trim();
        Description = description?.Trim();
        Color = color?.Trim();
    }

    /// <summary>
    /// Calculates the total amount allocated to this category for a specific budget period.
    /// </summary>
    public SatoshiAmount GetAllocatedAmount(int budgetPeriodId)
    {
        var allocation = Allocations.FirstOrDefault(a => a.BudgetPeriodId == budgetPeriodId);
        return allocation?.Amount ?? SatoshiAmount.Zero;
    }

    /// <summary>
    /// Calculates the total amount spent from this category for a specific budget period.
    /// </summary>
    public SatoshiAmount GetSpentAmount(int budgetPeriodId, DateTime periodStart, DateTime periodEnd)
    {
        var spentAmount = Transactions
            .Where(t => t.TransactionType == TransactionType.Expense 
                       && t.Date >= periodStart 
                       && t.Date <= periodEnd)
            .Sum(t => t.Amount.Value);

        return new SatoshiAmount(spentAmount);
    }

    /// <summary>
    /// Calculates the remaining balance for this category in a specific budget period.
    /// </summary>
    public SatoshiAmount GetRemainingBalance(int budgetPeriodId, DateTime periodStart, DateTime periodEnd)
    {
        var allocated = GetAllocatedAmount(budgetPeriodId);
        var spent = GetSpentAmount(budgetPeriodId, periodStart, periodEnd);
        
        return allocated - spent;
    }

    /// <summary>
    /// Checks if this category is overspent for a specific budget period.
    /// </summary>
    public bool IsOverspent(int budgetPeriodId, DateTime periodStart, DateTime periodEnd)
    {
        var remaining = GetRemainingBalance(budgetPeriodId, periodStart, periodEnd);
        return remaining.Value < 0;
    }
} 
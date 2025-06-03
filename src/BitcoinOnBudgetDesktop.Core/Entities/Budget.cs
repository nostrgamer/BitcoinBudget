using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Core.Entities;

/// <summary>
/// Aggregate root representing a complete budget with categories, transactions, and periods.
/// </summary>
public class Budget
{
    public int Id { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public DateTime CreatedDate { get; private set; }

    // Navigation properties
    public ICollection<Category> Categories { get; private set; } = new List<Category>();
    public ICollection<Transaction> Transactions { get; private set; } = new List<Transaction>();
    public ICollection<BudgetPeriod> BudgetPeriods { get; private set; } = new List<BudgetPeriod>();

    // Private constructor for EF Core
    private Budget() { }

    public Budget(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Budget name cannot be empty", nameof(name));

        Name = name.Trim();
        CreatedDate = DateTime.UtcNow;
    }

    public void UpdateName(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Budget name cannot be empty", nameof(name));

        Name = name.Trim();
    }

    /// <summary>
    /// Calculates the total available funds to assign to categories.
    /// This is total income minus already allocated amounts.
    /// </summary>
    public SatoshiAmount GetAvailableToAssign(int budgetPeriodId)
    {
        var totalIncome = Transactions
            .Where(t => t.TransactionType == TransactionType.Income)
            .Sum(t => t.Amount.Value);

        var totalAllocated = BudgetPeriods
            .Where(bp => bp.Id == budgetPeriodId)
            .SelectMany(bp => bp.CategoryAllocations)
            .Sum(ca => ca.Amount.Value);

        var availableAmount = totalIncome - totalAllocated;
        return new SatoshiAmount(Math.Max(0, availableAmount));
    }

    /// <summary>
    /// Gets the current budget period (current month).
    /// </summary>
    public BudgetPeriod? GetCurrentBudgetPeriod()
    {
        var now = DateTime.UtcNow;
        return BudgetPeriods.FirstOrDefault(bp => bp.Year == now.Year && bp.Month == now.Month);
    }

    /// <summary>
    /// Creates a new budget period for the specified month/year.
    /// </summary>
    public BudgetPeriod CreateBudgetPeriod(int year, int month)
    {
        // Check if period already exists
        var existingPeriod = BudgetPeriods.FirstOrDefault(bp => bp.Year == year && bp.Month == month);
        if (existingPeriod != null)
            throw new InvalidOperationException($"Budget period for {year}-{month:D2} already exists");

        var budgetPeriod = new BudgetPeriod(Id, year, month);
        BudgetPeriods.Add(budgetPeriod);
        return budgetPeriod;
    }
} 
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Core.Entities;

/// <summary>
/// Represents a monthly budget period with category allocations.
/// </summary>
public class BudgetPeriod
{
    public int Id { get; private set; }
    public int BudgetId { get; private set; }
    public int Year { get; private set; }
    public int Month { get; private set; }
    public DateTime StartDate { get; private set; }
    public DateTime EndDate { get; private set; }

    // Navigation properties
    public Budget Budget { get; private set; } = null!;
    public ICollection<CategoryAllocation> CategoryAllocations { get; private set; } = new List<CategoryAllocation>();

    // Private constructor for EF Core
    private BudgetPeriod() { }

    public BudgetPeriod(int budgetId, int year, int month)
    {
        if (year < 2000 || year > 3000)
            throw new ArgumentOutOfRangeException(nameof(year), "Year must be between 2000 and 3000");
        
        if (month < 1 || month > 12)
            throw new ArgumentOutOfRangeException(nameof(month), "Month must be between 1 and 12");

        BudgetId = budgetId;
        Year = year;
        Month = month;
        StartDate = new DateTime(year, month, 1);
        EndDate = StartDate.AddMonths(1).AddDays(-1);
    }

    /// <summary>
    /// Allocates an amount to a specific category for this budget period.
    /// </summary>
    public void AllocateToCategory(int categoryId, SatoshiAmount amount)
    {
        var existingAllocation = CategoryAllocations.FirstOrDefault(ca => ca.CategoryId == categoryId);
        
        if (existingAllocation != null)
        {
            existingAllocation.UpdateAmount(amount);
        }
        else
        {
            var allocation = new CategoryAllocation(Id, categoryId, amount);
            CategoryAllocations.Add(allocation);
        }
    }

    /// <summary>
    /// Gets the total amount allocated across all categories for this period.
    /// </summary>
    public SatoshiAmount GetTotalAllocated()
    {
        var total = CategoryAllocations.Sum(ca => ca.Amount.Value);
        return new SatoshiAmount(total);
    }

    /// <summary>
    /// Checks if this period contains the specified date.
    /// </summary>
    public bool ContainsDate(DateTime date)
    {
        return date >= StartDate && date <= EndDate;
    }

    /// <summary>
    /// Gets a display name for this budget period.
    /// </summary>
    public string GetDisplayName()
    {
        return $"{Year}-{Month:D2}";
    }
} 
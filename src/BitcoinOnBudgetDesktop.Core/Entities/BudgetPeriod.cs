using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Core.Entities;

/// <summary>
/// Represents a monthly budget period with category allocations and rollover logic.
/// </summary>
public class BudgetPeriod
{
    public int Id { get; private set; }
    public int BudgetId { get; private set; }
    public int Year { get; private set; }
    public int Month { get; private set; }
    public DateTime StartDate { get; private set; }
    public DateTime EndDate { get; private set; }
    public bool IsClosed { get; private set; }
    public DateTime? ClosedDate { get; private set; }

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
        IsClosed = false;
    }

    /// <summary>
    /// Allocates an amount to a specific category for this budget period.
    /// </summary>
    public void AllocateToCategory(int categoryId, SatoshiAmount amount)
    {
        if (IsClosed)
            throw new InvalidOperationException("Cannot allocate funds to a closed budget period");

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
    /// Adds rollover funds to a category allocation (from previous period's unspent amount).
    /// </summary>
    public void AddRolloverToCategory(int categoryId, SatoshiAmount rolloverAmount, SatoshiAmount newAllocation)
    {
        if (IsClosed)
            throw new InvalidOperationException("Cannot add rollover to a closed budget period");

        if (rolloverAmount.Value < 0)
            throw new ArgumentException("Rollover amount cannot be negative", nameof(rolloverAmount));

        var totalAmount = new SatoshiAmount(rolloverAmount.Value + newAllocation.Value);
        AllocateToCategory(categoryId, totalAmount);
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
    /// Calculates rollover amount for a specific category based on allocated vs spent.
    /// </summary>
    public SatoshiAmount CalculateCategoryRollover(int categoryId, SatoshiAmount spentAmount)
    {
        var allocation = CategoryAllocations.FirstOrDefault(ca => ca.CategoryId == categoryId);
        if (allocation == null)
            return SatoshiAmount.Zero;

        var remainingAmount = allocation.Amount.Value - spentAmount.Value;
        
        // Only positive amounts roll over; overspending is handled separately
        return new SatoshiAmount(Math.Max(0, remainingAmount));
    }

    /// <summary>
    /// Calculates overspending amount for a specific category.
    /// </summary>
    public SatoshiAmount CalculateCategoryOverspending(int categoryId, SatoshiAmount spentAmount)
    {
        var allocation = CategoryAllocations.FirstOrDefault(ca => ca.CategoryId == categoryId);
        if (allocation == null)
            return SatoshiAmount.Zero;

        var overspentAmount = spentAmount.Value - allocation.Amount.Value;
        
        // Only negative balances count as overspending
        return new SatoshiAmount(Math.Max(0, overspentAmount));
    }

    /// <summary>
    /// Gets all category rollover amounts for transitioning to the next period.
    /// </summary>
    public Dictionary<int, SatoshiAmount> CalculateAllCategoryRollovers(Dictionary<int, SatoshiAmount> categorySpending)
    {
        var rollovers = new Dictionary<int, SatoshiAmount>();
        
        foreach (var allocation in CategoryAllocations)
        {
            var spentAmount = categorySpending.GetValueOrDefault(allocation.CategoryId, SatoshiAmount.Zero);
            var rollover = CalculateCategoryRollover(allocation.CategoryId, spentAmount);
            
            if (rollover.Value > 0)
            {
                rollovers[allocation.CategoryId] = rollover;
            }
        }
        
        return rollovers;
    }

    /// <summary>
    /// Closes this budget period, preventing further modifications.
    /// </summary>
    public void ClosePeriod()
    {
        if (IsClosed)
            throw new InvalidOperationException("Budget period is already closed");

        IsClosed = true;
        ClosedDate = DateTime.UtcNow;
    }

    /// <summary>
    /// Reopens a closed budget period (use with caution).
    /// </summary>
    public void ReopenPeriod()
    {
        if (!IsClosed)
            throw new InvalidOperationException("Budget period is not closed");

        IsClosed = false;
        ClosedDate = null;
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

    /// <summary>
    /// Gets the next month's year and month values.
    /// </summary>
    public (int Year, int Month) GetNextPeriod()
    {
        if (Month == 12)
            return (Year + 1, 1);
        
        return (Year, Month + 1);
    }

    /// <summary>
    /// Gets the previous month's year and month values.
    /// </summary>
    public (int Year, int Month) GetPreviousPeriod()
    {
        if (Month == 1)
            return (Year - 1, 12);
        
        return (Year, Month - 1);
    }

    /// <summary>
    /// Checks if this is the current month period.
    /// </summary>
    public bool IsCurrentMonth()
    {
        var now = DateTime.Now;
        return Year == now.Year && Month == now.Month;
    }
} 
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Core.Entities;

/// <summary>
/// Represents a Bitcoin transaction in the budgeting system.
/// Records the movement of sats with category assignment for envelope budgeting.
/// </summary>
public class Transaction
{
    public int Id { get; private set; }
    public int BudgetId { get; private set; }
    public int CategoryId { get; private set; }
    public SatoshiAmount Amount { get; private set; }
    public DateTime Date { get; private set; }
    public string? Description { get; private set; }
    public TransactionType TransactionType { get; private set; }

    // Navigation properties
    public Budget Budget { get; private set; } = null!;
    public Category Category { get; private set; } = null!;

    // Private constructor for EF Core
    private Transaction() { }

    public Transaction(
        int budgetId, 
        int categoryId, 
        SatoshiAmount amount, 
        DateTime date, 
        TransactionType transactionType,
        string? description = null)
    {
        if (amount.Value <= 0)
            throw new ArgumentException("Transaction amount must be positive", nameof(amount));

        BudgetId = budgetId;
        CategoryId = categoryId;
        Amount = amount;
        Date = date;
        TransactionType = transactionType;
        Description = description?.Trim();
    }

    public void UpdateDetails(
        SatoshiAmount amount, 
        DateTime date, 
        TransactionType transactionType,
        string? description = null)
    {
        if (amount.Value <= 0)
            throw new ArgumentException("Transaction amount must be positive", nameof(amount));

        Amount = amount;
        Date = date;
        TransactionType = transactionType;
        Description = description?.Trim();
    }

    public void UpdateCategory(int categoryId)
    {
        CategoryId = categoryId;
    }

    /// <summary>
    /// Gets the effective amount for budget calculations.
    /// Income adds to available funds, expenses reduce category balance.
    /// </summary>
    public SatoshiAmount GetEffectiveAmount()
    {
        return TransactionType switch
        {
            TransactionType.Income => Amount,
            TransactionType.Expense => Amount,
            TransactionType.Transfer => Amount,
            _ => throw new InvalidOperationException($"Unknown transaction type: {TransactionType}")
        };
    }

    /// <summary>
    /// Determines if this transaction affects the category balance.
    /// </summary>
    public bool AffectsCategoryBalance()
    {
        return TransactionType == TransactionType.Expense || TransactionType == TransactionType.Transfer;
    }

    /// <summary>
    /// Determines if this transaction affects the total available funds.
    /// </summary>
    public bool AffectsAvailableFunds()
    {
        return TransactionType == TransactionType.Income;
    }
} 
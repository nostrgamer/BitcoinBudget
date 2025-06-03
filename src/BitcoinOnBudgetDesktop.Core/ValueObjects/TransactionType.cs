namespace BitcoinOnBudgetDesktop.Core.ValueObjects;

/// <summary>
/// Represents the different types of transactions in the budgeting system.
/// </summary>
public enum TransactionType
{
    /// <summary>
    /// Money coming into the budget (salary, freelance, etc.)
    /// </summary>
    Income = 1,
    
    /// <summary>
    /// Money spent from a category (groceries, rent, etc.)
    /// </summary>
    Expense = 2,
    
    /// <summary>
    /// Money moved between categories without affecting total budget
    /// </summary>
    Transfer = 3
} 
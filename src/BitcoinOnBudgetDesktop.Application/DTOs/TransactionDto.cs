using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.DTOs;

/// <summary>
/// Data transfer object for Transaction entity.
/// </summary>
public class TransactionDto
{
    public int Id { get; set; }
    public int BudgetId { get; set; }
    public int CategoryId { get; set; }
    public string CategoryName { get; set; } = string.Empty;
    public SatoshiAmount Amount { get; set; } = new(0);
    public DateTime Date { get; set; }
    public string? Description { get; set; }
    public TransactionType TransactionType { get; set; }
    public string TransactionTypeDisplay => TransactionType.ToString();
    public string AmountDisplay => Amount.ToString();
    public string DateDisplay => Date.ToString("MMM dd, yyyy");
} 
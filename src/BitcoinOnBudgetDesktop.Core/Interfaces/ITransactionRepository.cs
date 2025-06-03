using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Core.Interfaces;

/// <summary>
/// Repository interface for Transaction entity operations.
/// </summary>
public interface ITransactionRepository
{
    Task<Transaction> AddAsync(Transaction transaction);
    Task<Transaction?> GetByIdAsync(int id);
    Task<IEnumerable<Transaction>> GetByBudgetIdAsync(int budgetId);
    Task<IEnumerable<Transaction>> GetByCategoryIdAsync(int categoryId);
    Task<IEnumerable<Transaction>> GetByBudgetAndCategoryAsync(int budgetId, int categoryId);
    Task<IEnumerable<Transaction>> GetByTransactionTypeAsync(int budgetId, TransactionType transactionType);
    Task<IEnumerable<Transaction>> GetByDateRangeAsync(int budgetId, DateTime startDate, DateTime endDate);
    Task UpdateAsync(Transaction transaction);
    Task DeleteAsync(Transaction transaction);
    Task<SatoshiAmount> GetTotalIncomeAsync(int budgetId);
    Task<SatoshiAmount> GetTotalExpensesAsync(int budgetId);
    Task<SatoshiAmount> GetCategoryExpensesAsync(int budgetId, int categoryId);
    Task<SatoshiAmount> GetCategoryExpensesAsync(int budgetId, int categoryId, DateTime startDate, DateTime endDate);
    Task<int> DeleteByBudgetIdAsync(int budgetId);
} 
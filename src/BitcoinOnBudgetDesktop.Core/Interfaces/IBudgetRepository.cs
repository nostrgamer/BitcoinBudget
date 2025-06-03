using BitcoinOnBudgetDesktop.Core.Entities;

namespace BitcoinOnBudgetDesktop.Core.Interfaces;

/// <summary>
/// Repository interface for Budget aggregate operations.
/// </summary>
public interface IBudgetRepository
{
    Task<Budget?> GetByIdAsync(int id);
    Task<Budget?> GetByIdWithCategoriesAsync(int id);
    Task<Budget?> GetByIdWithPeriodsAsync(int id);
    Task<Budget> AddAsync(Budget budget);
    Task UpdateAsync(Budget budget);
    Task DeleteAsync(Budget budget);
    Task<IEnumerable<Budget>> GetAllAsync();
} 
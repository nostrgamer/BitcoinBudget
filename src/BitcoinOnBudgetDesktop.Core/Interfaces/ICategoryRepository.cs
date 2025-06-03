using BitcoinOnBudgetDesktop.Core.Entities;

namespace BitcoinOnBudgetDesktop.Core.Interfaces;

/// <summary>
/// Repository interface for Category operations.
/// </summary>
public interface ICategoryRepository
{
    Task<Category?> GetByIdAsync(int id);
    Task<Category> AddAsync(Category category);
    Task UpdateAsync(Category category);
    Task DeleteAsync(Category category);
    Task<IEnumerable<Category>> GetByBudgetIdAsync(int budgetId);
} 
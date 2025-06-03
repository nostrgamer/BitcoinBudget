using BitcoinOnBudgetDesktop.Core.Entities;

namespace BitcoinOnBudgetDesktop.Core.Interfaces;

/// <summary>
/// Repository interface for BudgetPeriod operations.
/// </summary>
public interface IBudgetPeriodRepository
{
    Task<BudgetPeriod?> GetByIdAsync(int id);
    Task<BudgetPeriod?> GetByBudgetAndDateAsync(int budgetId, int year, int month);
    Task<BudgetPeriod> AddAsync(BudgetPeriod budgetPeriod);
    Task UpdateAsync(BudgetPeriod budgetPeriod);
    Task DeleteAsync(BudgetPeriod budgetPeriod);
    Task<IEnumerable<BudgetPeriod>> GetByBudgetIdAsync(int budgetId);
} 
using BitcoinOnBudgetDesktop.Core.Entities;

namespace BitcoinOnBudgetDesktop.Core.Interfaces;

/// <summary>
/// Repository interface for BudgetPeriod entities.
/// </summary>
public interface IBudgetPeriodRepository
{
    Task<BudgetPeriod?> GetByIdAsync(int id);
    Task<BudgetPeriod> AddAsync(BudgetPeriod budgetPeriod);
    Task UpdateAsync(BudgetPeriod budgetPeriod);
    Task DeleteAsync(BudgetPeriod budgetPeriod);
    Task<IEnumerable<BudgetPeriod>> GetByBudgetIdAsync(int budgetId);
    Task<BudgetPeriod?> GetByMonthAsync(int budgetId, int year, int month);
    Task<BudgetPeriod?> GetCurrentOrCreateAsync(int budgetId);
    Task<int> DeleteByBudgetIdAsync(int budgetId);
} 
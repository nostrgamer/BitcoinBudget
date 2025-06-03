using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace BitcoinOnBudgetDesktop.Infrastructure.Data.Repositories;

public class BudgetPeriodRepository : IBudgetPeriodRepository
{
    private readonly BudgetDbContext _context;

    public BudgetPeriodRepository(BudgetDbContext context)
    {
        _context = context;
    }

    public async Task<BudgetPeriod?> GetByIdAsync(int id)
    {
        return await _context.BudgetPeriods
            .Include(bp => bp.CategoryAllocations)
                .ThenInclude(ca => ca.Category)
            .FirstOrDefaultAsync(bp => bp.Id == id);
    }

    public async Task<BudgetPeriod?> GetByBudgetAndDateAsync(int budgetId, int year, int month)
    {
        return await _context.BudgetPeriods
            .Include(bp => bp.CategoryAllocations)
                .ThenInclude(ca => ca.Category)
            .FirstOrDefaultAsync(bp => bp.BudgetId == budgetId && bp.Year == year && bp.Month == month);
    }

    public async Task<BudgetPeriod> AddAsync(BudgetPeriod budgetPeriod)
    {
        _context.BudgetPeriods.Add(budgetPeriod);
        await _context.SaveChangesAsync();
        return budgetPeriod;
    }

    public async Task UpdateAsync(BudgetPeriod budgetPeriod)
    {
        _context.BudgetPeriods.Update(budgetPeriod);
        await _context.SaveChangesAsync();
    }

    public async Task DeleteAsync(BudgetPeriod budgetPeriod)
    {
        _context.BudgetPeriods.Remove(budgetPeriod);
        await _context.SaveChangesAsync();
    }

    public async Task<IEnumerable<BudgetPeriod>> GetByBudgetIdAsync(int budgetId)
    {
        return await _context.BudgetPeriods
            .Include(bp => bp.CategoryAllocations)
                .ThenInclude(ca => ca.Category)
            .Where(bp => bp.BudgetId == budgetId)
            .OrderByDescending(bp => bp.Year)
            .ThenByDescending(bp => bp.Month)
            .ToListAsync();
    }
} 
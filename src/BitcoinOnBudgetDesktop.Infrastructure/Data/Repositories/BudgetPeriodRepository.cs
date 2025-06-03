using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace BitcoinOnBudgetDesktop.Infrastructure.Data.Repositories;

/// <summary>
/// Repository implementation for BudgetPeriod entities.
/// </summary>
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

    public async Task<BudgetPeriod?> GetByMonthAsync(int budgetId, int year, int month)
    {
        return await _context.BudgetPeriods
            .Include(bp => bp.CategoryAllocations)
                .ThenInclude(ca => ca.Category)
            .FirstOrDefaultAsync(bp => bp.BudgetId == budgetId && bp.Year == year && bp.Month == month);
    }

    public async Task<BudgetPeriod?> GetCurrentOrCreateAsync(int budgetId)
    {
        var currentDate = DateTime.Now;
        var currentYear = currentDate.Year;
        var currentMonth = currentDate.Month;

        // Try to get existing period
        var existingPeriod = await GetByMonthAsync(budgetId, currentYear, currentMonth);
        if (existingPeriod != null)
        {
            return existingPeriod;
        }

        // Create new period if it doesn't exist
        var newPeriod = new BudgetPeriod(budgetId, currentYear, currentMonth);
        return await AddAsync(newPeriod);
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

    public async Task<int> DeleteByBudgetIdAsync(int budgetId)
    {
        var budgetPeriods = await _context.BudgetPeriods
            .Where(bp => bp.BudgetId == budgetId)
            .ToListAsync();

        _context.BudgetPeriods.RemoveRange(budgetPeriods);
        await _context.SaveChangesAsync();
        
        return budgetPeriods.Count;
    }
} 
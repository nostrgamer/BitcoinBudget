using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace BitcoinOnBudgetDesktop.Infrastructure.Data.Repositories;

public class BudgetRepository : IBudgetRepository
{
    private readonly BudgetDbContext _context;

    public BudgetRepository(BudgetDbContext context)
    {
        _context = context;
    }

    public async Task<Budget> AddAsync(Budget budget)
    {
        _context.Budgets.Add(budget);
        await _context.SaveChangesAsync();
        return budget;
    }

    public async Task<Budget?> GetByIdAsync(int id)
    {
        return await _context.Budgets.FindAsync(id);
    }

    public async Task<Budget?> GetByIdWithCategoriesAsync(int id)
    {
        return await _context.Budgets
            .Include(b => b.Categories)
            .FirstOrDefaultAsync(b => b.Id == id);
    }

    public async Task<Budget?> GetByIdWithPeriodsAsync(int id)
    {
        return await _context.Budgets
            .Include(b => b.BudgetPeriods)
                .ThenInclude(bp => bp.CategoryAllocations)
            .Include(b => b.Transactions)
            .FirstOrDefaultAsync(b => b.Id == id);
    }

    public async Task<IEnumerable<Budget>> GetAllAsync()
    {
        return await _context.Budgets.ToListAsync();
    }

    public async Task UpdateAsync(Budget budget)
    {
        _context.Budgets.Update(budget);
        await _context.SaveChangesAsync();
    }

    public async Task DeleteAsync(Budget budget)
    {
        _context.Budgets.Remove(budget);
        await _context.SaveChangesAsync();
    }
} 
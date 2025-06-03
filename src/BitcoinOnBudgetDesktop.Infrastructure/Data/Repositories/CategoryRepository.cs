using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace BitcoinOnBudgetDesktop.Infrastructure.Data.Repositories;

public class CategoryRepository : ICategoryRepository
{
    private readonly BudgetDbContext _context;

    public CategoryRepository(BudgetDbContext context)
    {
        _context = context;
    }

    public async Task<Category> AddAsync(Category category)
    {
        _context.Categories.Add(category);
        await _context.SaveChangesAsync();
        return category;
    }

    public async Task<Category?> GetByIdAsync(int id)
    {
        return await _context.Categories.FindAsync(id);
    }

    public async Task<IEnumerable<Category>> GetByBudgetIdAsync(int budgetId)
    {
        return await _context.Categories
            .Where(c => c.BudgetId == budgetId)
            .ToListAsync();
    }

    public async Task UpdateAsync(Category category)
    {
        _context.Categories.Update(category);
        await _context.SaveChangesAsync();
    }

    public async Task DeleteAsync(Category category)
    {
        _context.Categories.Remove(category);
        await _context.SaveChangesAsync();
    }
} 
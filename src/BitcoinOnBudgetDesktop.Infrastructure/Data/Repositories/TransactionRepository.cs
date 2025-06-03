using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Core.ValueObjects;
using Microsoft.EntityFrameworkCore;

namespace BitcoinOnBudgetDesktop.Infrastructure.Data.Repositories;

public class TransactionRepository : ITransactionRepository
{
    private readonly BudgetDbContext _context;

    public TransactionRepository(BudgetDbContext context)
    {
        _context = context;
    }

    public async Task<Transaction> AddAsync(Transaction transaction)
    {
        _context.Transactions.Add(transaction);
        await _context.SaveChangesAsync();
        return transaction;
    }

    public async Task<Transaction?> GetByIdAsync(int id)
    {
        return await _context.Transactions
            .Include(t => t.Budget)
            .Include(t => t.Category)
            .FirstOrDefaultAsync(t => t.Id == id);
    }

    public async Task<IEnumerable<Transaction>> GetByBudgetIdAsync(int budgetId)
    {
        return await _context.Transactions
            .Include(t => t.Category)
            .Where(t => t.BudgetId == budgetId)
            .OrderByDescending(t => t.Date)
            .ToListAsync();
    }

    public async Task<IEnumerable<Transaction>> GetByCategoryIdAsync(int categoryId)
    {
        return await _context.Transactions
            .Include(t => t.Budget)
            .Include(t => t.Category)
            .Where(t => t.CategoryId == categoryId)
            .OrderByDescending(t => t.Date)
            .ToListAsync();
    }

    public async Task<IEnumerable<Transaction>> GetByBudgetAndCategoryAsync(int budgetId, int categoryId)
    {
        return await _context.Transactions
            .Include(t => t.Category)
            .Where(t => t.BudgetId == budgetId && t.CategoryId == categoryId)
            .OrderByDescending(t => t.Date)
            .ToListAsync();
    }

    public async Task<IEnumerable<Transaction>> GetByTransactionTypeAsync(int budgetId, TransactionType transactionType)
    {
        return await _context.Transactions
            .Include(t => t.Category)
            .Where(t => t.BudgetId == budgetId && t.TransactionType == transactionType)
            .OrderByDescending(t => t.Date)
            .ToListAsync();
    }

    public async Task<IEnumerable<Transaction>> GetByDateRangeAsync(int budgetId, DateTime startDate, DateTime endDate)
    {
        return await _context.Transactions
            .Include(t => t.Category)
            .Where(t => t.BudgetId == budgetId && t.Date >= startDate && t.Date <= endDate)
            .OrderByDescending(t => t.Date)
            .ToListAsync();
    }

    public async Task UpdateAsync(Transaction transaction)
    {
        _context.Transactions.Update(transaction);
        await _context.SaveChangesAsync();
    }

    public async Task DeleteAsync(Transaction transaction)
    {
        _context.Transactions.Remove(transaction);
        await _context.SaveChangesAsync();
    }

    public async Task<SatoshiAmount> GetTotalIncomeAsync(int budgetId)
    {
        var transactions = await _context.Transactions
            .Where(t => t.BudgetId == budgetId && t.TransactionType == TransactionType.Income)
            .ToListAsync();
        
        var total = transactions.Sum(t => t.Amount.Value);
        return new SatoshiAmount(total);
    }

    public async Task<SatoshiAmount> GetTotalExpensesAsync(int budgetId)
    {
        var transactions = await _context.Transactions
            .Where(t => t.BudgetId == budgetId && t.TransactionType == TransactionType.Expense)
            .ToListAsync();
        
        var total = transactions.Sum(t => t.Amount.Value);
        return new SatoshiAmount(total);
    }

    public async Task<SatoshiAmount> GetCategoryExpensesAsync(int budgetId, int categoryId)
    {
        var transactions = await _context.Transactions
            .Where(t => t.BudgetId == budgetId && 
                       t.CategoryId == categoryId && 
                       t.TransactionType == TransactionType.Expense)
            .ToListAsync();
        
        var total = transactions.Sum(t => t.Amount.Value);
        return new SatoshiAmount(total);
    }
} 
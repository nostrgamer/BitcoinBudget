using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handles the deletion of all budget data (budget reset).
/// Deletes data in the correct order to avoid foreign key constraint violations.
/// </summary>
public class DeleteBudgetDataCommandHandler : IRequestHandler<DeleteBudgetDataCommand, DeleteBudgetDataResult>
{
    private readonly ITransactionRepository _transactionRepository;
    private readonly ICategoryRepository _categoryRepository;
    private readonly IBudgetPeriodRepository _budgetPeriodRepository;

    public DeleteBudgetDataCommandHandler(
        ITransactionRepository transactionRepository,
        ICategoryRepository categoryRepository,
        IBudgetPeriodRepository budgetPeriodRepository)
    {
        _transactionRepository = transactionRepository;
        _categoryRepository = categoryRepository;
        _budgetPeriodRepository = budgetPeriodRepository;
    }

    public async Task<DeleteBudgetDataResult> Handle(DeleteBudgetDataCommand request, CancellationToken cancellationToken)
    {
        try
        {
            int transactionsDeleted = 0;
            int categoriesDeleted = 0;
            int allocationsDeleted = 0;
            int budgetPeriodsDeleted = 0;

            // Step 1: Delete all transactions for this budget
            // (Transactions reference categories, so delete them first)
            var transactions = await _transactionRepository.GetByBudgetIdAsync(request.BudgetId);
            foreach (var transaction in transactions)
            {
                await _transactionRepository.DeleteAsync(transaction);
                transactionsDeleted++;
            }

            // Step 2: Get all budget periods for this budget and delete their allocations
            var budgetPeriods = await _budgetPeriodRepository.GetByBudgetIdAsync(request.BudgetId);
            foreach (var budgetPeriod in budgetPeriods)
            {
                // Count allocations in this budget period
                allocationsDeleted += budgetPeriod.CategoryAllocations.Count;
                
                // Delete the budget period (this will cascade delete allocations due to EF configuration)
                await _budgetPeriodRepository.DeleteAsync(budgetPeriod);
                budgetPeriodsDeleted++;
            }

            // Step 3: Delete all categories for this budget
            // (Now safe since transactions and allocations are gone)
            var categories = await _categoryRepository.GetByBudgetIdAsync(request.BudgetId);
            foreach (var category in categories)
            {
                await _categoryRepository.DeleteAsync(category);
                categoriesDeleted++;
            }

            // NOTE: We intentionally preserve the Budget entity itself during reset
            // This ensures Budget ID 1 continues to exist for the application to function

            return new DeleteBudgetDataResult(
                Success: true,
                TransactionsDeleted: transactionsDeleted,
                CategoriesDeleted: categoriesDeleted,
                AllocationsDeleted: allocationsDeleted,
                BudgetPeriodsDeleted: budgetPeriodsDeleted
            );
        }
        catch (Exception ex)
        {
            return new DeleteBudgetDataResult(
                Success: false,
                ErrorMessage: $"Failed to delete budget data: {ex.Message}"
            );
        }
    }
} 
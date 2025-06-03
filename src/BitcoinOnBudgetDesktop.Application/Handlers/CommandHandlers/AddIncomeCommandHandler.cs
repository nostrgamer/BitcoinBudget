using MediatR;
using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handler for adding income transactions.
/// </summary>
public class AddIncomeCommandHandler : IRequestHandler<AddIncomeCommand, AddIncomeResult>
{
    private readonly IBudgetRepository _budgetRepository;
    private readonly ICategoryRepository _categoryRepository;

    public AddIncomeCommandHandler(
        IBudgetRepository budgetRepository,
        ICategoryRepository categoryRepository)
    {
        _budgetRepository = budgetRepository;
        _categoryRepository = categoryRepository;
    }

    public async Task<AddIncomeResult> Handle(AddIncomeCommand request, CancellationToken cancellationToken)
    {
        try
        {
            // Validate amount
            if (request.Amount.Value <= 0)
            {
                return new AddIncomeResult(
                    Success: false,
                    ErrorMessage: "Income amount must be positive"
                );
            }

            // Get budget
            var budget = await _budgetRepository.GetByIdAsync(request.BudgetId);
            if (budget == null)
            {
                return new AddIncomeResult(
                    Success: false,
                    ErrorMessage: "Budget not found"
                );
            }

            // For income transactions, we need a category. Let's get or create an "Income" category
            var categories = await _categoryRepository.GetByBudgetIdAsync(request.BudgetId);
            var incomeCategory = categories.FirstOrDefault(c => c.Name.Equals("Income", StringComparison.OrdinalIgnoreCase));
            
            if (incomeCategory == null)
            {
                // Create the Income category
                incomeCategory = new Category(request.BudgetId, "Income", "Income and salary transactions");
                incomeCategory = await _categoryRepository.AddAsync(incomeCategory);
            }

            // Create the income transaction
            var transaction = new Transaction(
                budgetId: request.BudgetId,
                categoryId: incomeCategory.Id,
                amount: request.Amount,
                date: request.Date ?? DateTime.UtcNow,
                transactionType: TransactionType.Income,
                description: request.Description
            );

            // Note: We would need a transaction repository for this
            // For now, we'll add it directly to the budget entity
            budget.Transactions.Add(transaction);
            await _budgetRepository.UpdateAsync(budget);

            return new AddIncomeResult(
                Success: true,
                TransactionId: transaction.Id
            );
        }
        catch (Exception ex)
        {
            return new AddIncomeResult(
                Success: false,
                ErrorMessage: ex.Message
            );
        }
    }
} 
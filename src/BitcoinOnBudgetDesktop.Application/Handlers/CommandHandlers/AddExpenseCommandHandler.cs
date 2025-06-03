using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Core.ValueObjects;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handles the addition of expense transactions to reduce category balances.
/// </summary>
public class AddExpenseCommandHandler : IRequestHandler<AddExpenseCommand, AddExpenseResult>
{
    private readonly ITransactionRepository _transactionRepository;
    private readonly IBudgetRepository _budgetRepository;
    private readonly ICategoryRepository _categoryRepository;

    public AddExpenseCommandHandler(
        ITransactionRepository transactionRepository,
        IBudgetRepository budgetRepository,
        ICategoryRepository categoryRepository)
    {
        _transactionRepository = transactionRepository;
        _budgetRepository = budgetRepository;
        _categoryRepository = categoryRepository;
    }

    public async Task<AddExpenseResult> Handle(AddExpenseCommand request, CancellationToken cancellationToken)
    {
        try
        {
            // Validate budget exists
            var budget = await _budgetRepository.GetByIdAsync(request.BudgetId);
            if (budget == null)
            {
                return new AddExpenseResult(
                    Success: false,
                    ErrorMessage: $"Budget with ID {request.BudgetId} not found"
                );
            }

            // Validate category exists and belongs to budget
            var category = await _categoryRepository.GetByIdAsync(request.CategoryId);
            if (category == null)
            {
                return new AddExpenseResult(
                    Success: false,
                    ErrorMessage: $"Category with ID {request.CategoryId} not found"
                );
            }

            if (category.BudgetId != request.BudgetId)
            {
                return new AddExpenseResult(
                    Success: false,
                    ErrorMessage: "Category does not belong to the specified budget"
                );
            }

            // Validate amount
            if (request.Amount.Value <= 0)
            {
                return new AddExpenseResult(
                    Success: false,
                    ErrorMessage: "Expense amount must be greater than zero"
                );
            }

            // Create transaction (using current time if no date specified)
            var transactionDate = request.Date ?? DateTime.Now;
            
            var transaction = new Transaction(
                budgetId: request.BudgetId,
                categoryId: request.CategoryId,
                amount: request.Amount,
                date: transactionDate,
                transactionType: TransactionType.Expense,
                description: request.Description
            );

            // Save transaction
            await _transactionRepository.AddAsync(transaction);

            return new AddExpenseResult(
                Success: true,
                TransactionId: transaction.Id
            );
        }
        catch (Exception ex)
        {
            return new AddExpenseResult(
                Success: false,
                ErrorMessage: $"Failed to add expense transaction: {ex.Message}"
            );
        }
    }
} 
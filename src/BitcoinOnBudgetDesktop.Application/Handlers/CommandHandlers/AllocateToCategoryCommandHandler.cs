using MediatR;
using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handler for allocating funds to categories.
/// </summary>
public class AllocateToCategoryCommandHandler : IRequestHandler<AllocateToCategoryCommand, AllocateToCategoryResult>
{
    private readonly IBudgetPeriodRepository _budgetPeriodRepository;
    private readonly ICategoryRepository _categoryRepository;
    private readonly ITransactionRepository _transactionRepository;

    public AllocateToCategoryCommandHandler(
        IBudgetPeriodRepository budgetPeriodRepository,
        ICategoryRepository categoryRepository,
        ITransactionRepository transactionRepository)
    {
        _budgetPeriodRepository = budgetPeriodRepository;
        _categoryRepository = categoryRepository;
        _transactionRepository = transactionRepository;
    }

    public async Task<AllocateToCategoryResult> Handle(AllocateToCategoryCommand request, CancellationToken cancellationToken)
    {
        try
        {
            // Validate amount
            if (request.Amount.Value < 0)
            {
                return new AllocateToCategoryResult(
                    Success: false,
                    ErrorMessage: "Allocation amount cannot be negative"
                );
            }

            // Get the budget period
            var budgetPeriod = await _budgetPeriodRepository.GetByIdAsync(request.BudgetPeriodId);
            if (budgetPeriod == null)
            {
                return new AllocateToCategoryResult(
                    Success: false,
                    ErrorMessage: "Budget period not found"
                );
            }

            // Validate category exists and belongs to the same budget
            var category = await _categoryRepository.GetByIdAsync(request.CategoryId);
            if (category == null)
            {
                return new AllocateToCategoryResult(
                    Success: false,
                    ErrorMessage: "Category not found"
                );
            }

            if (category.BudgetId != budgetPeriod.BudgetId)
            {
                return new AllocateToCategoryResult(
                    Success: false,
                    ErrorMessage: "Category does not belong to the budget period's budget"
                );
            }

            // Calculate available amount using repository methods for accuracy
            var totalIncome = await _transactionRepository.GetTotalIncomeAsync(budgetPeriod.BudgetId);
            var currentAllocated = budgetPeriod.GetTotalAllocated();
            var availableToAssign = new SatoshiAmount(Math.Max(0, totalIncome.Value - currentAllocated.Value));
            
            // Get existing allocation for this category to handle updates
            var existingAllocation = budgetPeriod.CategoryAllocations
                .FirstOrDefault(ca => ca.CategoryId == request.CategoryId);
            var existingAmount = existingAllocation?.Amount.Value ?? 0;
            
            // Calculate what the new total would be after this allocation
            var newTotalAllocated = currentAllocated.Value - existingAmount + request.Amount.Value;
            var wouldExceedAvailable = newTotalAllocated > totalIncome.Value;

            if (wouldExceedAvailable)
            {
                return new AllocateToCategoryResult(
                    Success: false,
                    ErrorMessage: $"Allocation would exceed available funds. Available: {availableToAssign.Value + existingAmount:N0} sats, Total Income: {totalIncome.Value:N0} sats"
                );
            }

            // Perform the allocation using the domain method
            budgetPeriod.AllocateToCategory(request.CategoryId, request.Amount);

            // Save changes
            await _budgetPeriodRepository.UpdateAsync(budgetPeriod);

            return new AllocateToCategoryResult(
                Success: true
            );
        }
        catch (Exception ex)
        {
            return new AllocateToCategoryResult(
                Success: false,
                ErrorMessage: ex.Message
            );
        }
    }
} 
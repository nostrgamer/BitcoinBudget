using MediatR;
using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handler for transitioning between months with automatic rollover calculations.
/// </summary>
public class TransitionToNextMonthCommandHandler : IRequestHandler<TransitionToNextMonthCommand, TransitionToNextMonthResult>
{
    private readonly IBudgetPeriodRepository _budgetPeriodRepository;
    private readonly ICategoryRepository _categoryRepository;
    private readonly ITransactionRepository _transactionRepository;
    private readonly IBudgetRepository _budgetRepository;

    public TransitionToNextMonthCommandHandler(
        IBudgetPeriodRepository budgetPeriodRepository,
        ICategoryRepository categoryRepository,
        ITransactionRepository transactionRepository,
        IBudgetRepository budgetRepository)
    {
        _budgetPeriodRepository = budgetPeriodRepository;
        _categoryRepository = categoryRepository;
        _transactionRepository = transactionRepository;
        _budgetRepository = budgetRepository;
    }

    public async Task<TransitionToNextMonthResult> Handle(TransitionToNextMonthCommand request, CancellationToken cancellationToken)
    {
        try
        {
            // Validate budget exists
            var budget = await _budgetRepository.GetByIdAsync(request.BudgetId);
            if (budget == null)
            {
                return new TransitionToNextMonthResult(
                    Success: false,
                    ErrorMessage: "Budget not found"
                );
            }

            // Get current month's budget period
            var currentDate = DateTime.Now;
            var currentPeriod = await _budgetPeriodRepository.GetByMonthAsync(
                request.BudgetId, currentDate.Year, currentDate.Month);

            if (currentPeriod == null)
            {
                return new TransitionToNextMonthResult(
                    Success: false,
                    ErrorMessage: "Current budget period not found"
                );
            }

            // Get next month's year and month
            var (nextYear, nextMonth) = currentPeriod.GetNextPeriod();

            // Check if next month period already exists
            var existingNextPeriod = await _budgetPeriodRepository.GetByMonthAsync(
                request.BudgetId, nextYear, nextMonth);

            if (existingNextPeriod != null)
            {
                return new TransitionToNextMonthResult(
                    Success: false,
                    ErrorMessage: $"Budget period for {nextYear}-{nextMonth:D2} already exists"
                );
            }

            // Calculate spending for each category in current period
            var categories = await _categoryRepository.GetByBudgetIdAsync(request.BudgetId);
            var categorySpending = new Dictionary<int, SatoshiAmount>();

            foreach (var category in categories)
            {
                var spentAmount = await _transactionRepository.GetCategoryExpensesAsync(
                    request.BudgetId, category.Id, currentPeriod.StartDate, currentPeriod.EndDate);
                categorySpending[category.Id] = spentAmount;
            }

            // Calculate rollover amounts
            var rolloverAmounts = currentPeriod.CalculateAllCategoryRollovers(categorySpending);
            var totalRollover = new SatoshiAmount(rolloverAmounts.Values.Sum(r => r.Value));

            // Create new budget period for next month
            var newPeriod = new BudgetPeriod(request.BudgetId, nextYear, nextMonth);
            newPeriod = await _budgetPeriodRepository.AddAsync(newPeriod);

            // Apply rollover allocations to new period
            foreach (var category in categories)
            {
                var rolloverAmount = rolloverAmounts.GetValueOrDefault(category.Id, SatoshiAmount.Zero);
                var newAllocation = request.CategoryNewAllocations?.GetValueOrDefault(category.Id, SatoshiAmount.Zero) 
                                  ?? SatoshiAmount.Zero;

                // Only create allocation if there's rollover or new allocation
                if (rolloverAmount.Value > 0 || newAllocation.Value > 0)
                {
                    newPeriod.AddRolloverToCategory(category.Id, rolloverAmount, newAllocation);
                }
            }

            // Save the updated period with allocations
            await _budgetPeriodRepository.UpdateAsync(newPeriod);

            // Close previous period if requested
            if (request.ClosePreviousPeriod)
            {
                currentPeriod.ClosePeriod();
                await _budgetPeriodRepository.UpdateAsync(currentPeriod);
            }

            return new TransitionToNextMonthResult(
                Success: true,
                NewBudgetPeriodId: newPeriod.Id,
                RolloverAmounts: rolloverAmounts,
                TotalRollover: totalRollover
            );
        }
        catch (Exception ex)
        {
            return new TransitionToNextMonthResult(
                Success: false,
                ErrorMessage: ex.Message
            );
        }
    }
} 
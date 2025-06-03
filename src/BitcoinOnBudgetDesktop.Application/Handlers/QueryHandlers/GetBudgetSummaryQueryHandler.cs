using MediatR;
using BitcoinOnBudgetDesktop.Application.DTOs;
using BitcoinOnBudgetDesktop.Application.Queries.Budget;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Application.Handlers.QueryHandlers;

/// <summary>
/// Handler for getting complete budget summary information.
/// </summary>
public class GetBudgetSummaryQueryHandler : IRequestHandler<GetBudgetSummaryQuery, BudgetSummaryDto?>
{
    private readonly IBudgetRepository _budgetRepository;
    private readonly IBudgetPeriodRepository _budgetPeriodRepository;
    private readonly ICategoryRepository _categoryRepository;
    private readonly ITransactionRepository _transactionRepository;

    public GetBudgetSummaryQueryHandler(
        IBudgetRepository budgetRepository,
        IBudgetPeriodRepository budgetPeriodRepository,
        ICategoryRepository categoryRepository,
        ITransactionRepository transactionRepository)
    {
        _budgetRepository = budgetRepository;
        _budgetPeriodRepository = budgetPeriodRepository;
        _categoryRepository = categoryRepository;
        _transactionRepository = transactionRepository;
    }

    public async Task<BudgetSummaryDto?> Handle(GetBudgetSummaryQuery request, CancellationToken cancellationToken)
    {
        // Get budget to verify it exists
        var budget = await _budgetRepository.GetByIdAsync(request.BudgetId);
        if (budget == null)
            return null;

        // Get the specific budget period
        var budgetPeriod = await _budgetPeriodRepository.GetByIdAsync(request.BudgetPeriodId);
        if (budgetPeriod == null)
            return null;

        // Get categories for this budget
        var categories = await _categoryRepository.GetByBudgetIdAsync(request.BudgetId);

        // Calculate totals using TransactionRepository for accuracy
        var totalIncome = await _transactionRepository.GetTotalIncomeAsync(request.BudgetId);
        var totalExpenses = await _transactionRepository.GetTotalExpensesAsync(request.BudgetId);
        
        var totalAllocated = budgetPeriod.GetTotalAllocated();
        
        // Calculate available to assign directly from repository data
        var availableToAssign = new SatoshiAmount(Math.Max(0, totalIncome.Value - totalAllocated.Value));

        // Convert categories to DTOs with accurate spending data
        var categoryDtos = new List<CategoryDto>();
        foreach (var category in categories)
        {
            var allocatedAmount = category.GetAllocatedAmount(request.BudgetPeriodId);
            var spentAmount = await _transactionRepository.GetCategoryExpensesAsync(request.BudgetId, category.Id);
            var remainingAmount = new SatoshiAmount(Math.Max(0, allocatedAmount.Value - spentAmount.Value));

            categoryDtos.Add(new CategoryDto(
                Id: category.Id,
                Name: category.Name,
                Description: category.Description,
                Color: category.Color,
                AllocatedAmount: allocatedAmount,
                RolloverAmount: SatoshiAmount.Zero,
                NewAllocation: allocatedAmount,
                SpentAmount: spentAmount,
                RemainingAmount: remainingAmount,
                HasRollover: false,
                RolloverPercentage: 0
            ));
        }

        return new BudgetSummaryDto(
            BudgetId: budget.Id,
            BudgetName: budget.Name,
            TotalIncome: totalIncome,
            TotalAllocated: totalAllocated,
            AvailableToAssign: availableToAssign,
            Categories: categoryDtos,
            CurrentPeriod: budgetPeriod.GetDisplayName()
        );
    }
} 
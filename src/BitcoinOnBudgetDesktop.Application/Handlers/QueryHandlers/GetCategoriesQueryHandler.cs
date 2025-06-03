using BitcoinOnBudgetDesktop.Application.DTOs;
using BitcoinOnBudgetDesktop.Application.Queries.Categories;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Core.ValueObjects;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Handlers.QueryHandlers;

/// <summary>
/// Handler for retrieving categories for a specific budget.
/// </summary>
public class GetCategoriesQueryHandler : IRequestHandler<GetCategoriesQuery, IEnumerable<CategoryDto>>
{
    private readonly ICategoryRepository _categoryRepository;
    private readonly IBudgetRepository _budgetRepository;

    public GetCategoriesQueryHandler(ICategoryRepository categoryRepository, IBudgetRepository budgetRepository)
    {
        _categoryRepository = categoryRepository;
        _budgetRepository = budgetRepository;
    }

    public async Task<IEnumerable<CategoryDto>> Handle(GetCategoriesQuery request, CancellationToken cancellationToken)
    {
        var categories = await _categoryRepository.GetByBudgetIdAsync(request.BudgetId);
        
        // For now, we'll get the current month's budget period
        // This is simplified - in a full implementation you'd specify which period
        var currentDate = DateTime.Now;
        var currentPeriodStart = new DateTime(currentDate.Year, currentDate.Month, 1);
        var currentPeriodEnd = currentPeriodStart.AddMonths(1).AddDays(-1);
        
        return categories.Select(category => 
        {
            // Calculate amounts using the Category methods
            // For simplicity, we'll use budget period ID 1 for now
            var allocatedAmount = category.GetAllocatedAmount(1);
            var spentAmount = category.GetSpentAmount(1, currentPeriodStart, currentPeriodEnd);
            var remainingAmount = category.GetRemainingBalance(1, currentPeriodStart, currentPeriodEnd);
            
            return new CategoryDto(
                Id: category.Id,
                Name: category.Name,
                Description: category.Description,
                Color: category.Color,
                AllocatedAmount: allocatedAmount,
                RolloverAmount: SatoshiAmount.Zero, // TODO: Calculate actual rollover from allocation
                NewAllocation: allocatedAmount, // TODO: Split allocation into rollover vs new
                SpentAmount: spentAmount,
                RemainingAmount: remainingAmount,
                HasRollover: false, // TODO: Check if allocation has rollover
                RolloverPercentage: 0 // TODO: Calculate rollover percentage
            );
        });
    }
} 
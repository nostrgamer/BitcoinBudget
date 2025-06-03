using MediatR;
using BitcoinOnBudgetDesktop.Application.DTOs;
using BitcoinOnBudgetDesktop.Application.Queries.Budget;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Core.Entities;

namespace BitcoinOnBudgetDesktop.Application.Handlers.QueryHandlers;

/// <summary>
/// Handler for getting the current budget period (auto-creates if needed).
/// </summary>
public class GetCurrentBudgetPeriodQueryHandler : IRequestHandler<GetCurrentBudgetPeriodQuery, BudgetPeriodDto?>
{
    private readonly IBudgetPeriodRepository _budgetPeriodRepository;
    private readonly IBudgetRepository _budgetRepository;

    public GetCurrentBudgetPeriodQueryHandler(
        IBudgetPeriodRepository budgetPeriodRepository,
        IBudgetRepository budgetRepository)
    {
        _budgetPeriodRepository = budgetPeriodRepository;
        _budgetRepository = budgetRepository;
    }

    public async Task<BudgetPeriodDto?> Handle(GetCurrentBudgetPeriodQuery request, CancellationToken cancellationToken)
    {
        // Verify budget exists, auto-create if needed (especially for Budget ID 1)
        var budget = await _budgetRepository.GetByIdAsync(request.BudgetId);
        if (budget == null && request.BudgetId == 1)
        {
            // Auto-create default budget for ID 1 to ensure system resilience
            budget = new Budget("My Bitcoin Budget");
            budget = await _budgetRepository.AddAsync(budget);
        }
        else if (budget == null)
        {
            // For non-default budgets, just return null
            return null;
        }

        var now = DateTime.UtcNow;
        var currentYear = now.Year;
        var currentMonth = now.Month;

        // Try to find existing budget period for current month
        var existingPeriod = await _budgetPeriodRepository.GetByMonthAsync(
            request.BudgetId, currentYear, currentMonth);

        // Auto-create if doesn't exist
        if (existingPeriod == null)
        {
            existingPeriod = new BudgetPeriod(request.BudgetId, currentYear, currentMonth);
            existingPeriod = await _budgetPeriodRepository.AddAsync(existingPeriod);
        }

        // Convert to DTO
        return new BudgetPeriodDto(
            Id: existingPeriod.Id,
            BudgetId: existingPeriod.BudgetId,
            Year: existingPeriod.Year,
            Month: existingPeriod.Month,
            StartDate: existingPeriod.StartDate,
            EndDate: existingPeriod.EndDate,
            TotalAllocated: existingPeriod.GetTotalAllocated(),
            DisplayName: existingPeriod.GetDisplayName(),
            CategoryAllocations: existingPeriod.CategoryAllocations.Select(ca => 
                new CategoryAllocationDto(
                    Id: ca.Id,
                    CategoryId: ca.CategoryId,
                    CategoryName: ca.Category?.Name ?? "Unknown",
                    Amount: ca.Amount
                ))
        );
    }
} 
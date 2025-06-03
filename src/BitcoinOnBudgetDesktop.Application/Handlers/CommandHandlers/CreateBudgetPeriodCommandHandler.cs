using MediatR;
using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.Interfaces;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handler for creating new budget periods.
/// </summary>
public class CreateBudgetPeriodCommandHandler : IRequestHandler<CreateBudgetPeriodCommand, CreateBudgetPeriodResult>
{
    private readonly IBudgetPeriodRepository _budgetPeriodRepository;

    public CreateBudgetPeriodCommandHandler(IBudgetPeriodRepository budgetPeriodRepository)
    {
        _budgetPeriodRepository = budgetPeriodRepository;
    }

    public async Task<CreateBudgetPeriodResult> Handle(CreateBudgetPeriodCommand request, CancellationToken cancellationToken)
    {
        try
        {
            // Check if budget period already exists
            var existingPeriod = await _budgetPeriodRepository.GetByMonthAsync(
                request.BudgetId, request.Year, request.Month);

            if (existingPeriod != null)
            {
                return new CreateBudgetPeriodResult(
                    Success: false,
                    ErrorMessage: $"Budget period for {request.Year}-{request.Month:D2} already exists"
                );
            }

            var budgetPeriod = new BudgetPeriod(
                budgetId: request.BudgetId,
                year: request.Year,
                month: request.Month
            );

            var createdPeriod = await _budgetPeriodRepository.AddAsync(budgetPeriod);

            return new CreateBudgetPeriodResult(
                Success: true,
                BudgetPeriodId: createdPeriod.Id
            );
        }
        catch (Exception ex)
        {
            return new CreateBudgetPeriodResult(
                Success: false,
                ErrorMessage: ex.Message
            );
        }
    }
} 
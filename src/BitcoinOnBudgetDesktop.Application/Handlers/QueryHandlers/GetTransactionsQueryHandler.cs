using BitcoinOnBudgetDesktop.Application.DTOs;
using BitcoinOnBudgetDesktop.Application.Queries.Transactions;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Handlers.QueryHandlers;

/// <summary>
/// Handles queries for retrieving transactions.
/// </summary>
public class GetTransactionsQueryHandler : IRequestHandler<GetTransactionsQuery, IEnumerable<TransactionDto>>
{
    private readonly ITransactionRepository _transactionRepository;

    public GetTransactionsQueryHandler(ITransactionRepository transactionRepository)
    {
        _transactionRepository = transactionRepository;
    }

    public async Task<IEnumerable<TransactionDto>> Handle(GetTransactionsQuery request, CancellationToken cancellationToken)
    {
        var transactions = await _transactionRepository.GetByBudgetIdAsync(request.BudgetId);

        return transactions.Select(t => new TransactionDto
        {
            Id = t.Id,
            BudgetId = t.BudgetId,
            CategoryId = t.CategoryId,
            CategoryName = t.Category?.Name ?? "Unknown",
            Amount = t.Amount,
            Date = t.Date,
            Description = t.Description,
            TransactionType = t.TransactionType
        });
    }
} 
using BitcoinOnBudgetDesktop.Application.DTOs;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Queries.Transactions;

/// <summary>
/// Query to get transactions for a specific budget.
/// </summary>
public record GetTransactionsQuery(int BudgetId) : IRequest<IEnumerable<TransactionDto>>; 
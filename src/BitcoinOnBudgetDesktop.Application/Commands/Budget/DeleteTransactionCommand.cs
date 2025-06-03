using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Commands.Budget;

/// <summary>
/// Command to delete a transaction.
/// </summary>
public record DeleteTransactionCommand(int TransactionId) : IRequest<DeleteTransactionResult>;

public record DeleteTransactionResult(
    bool Success,
    string? ErrorMessage = null
); 
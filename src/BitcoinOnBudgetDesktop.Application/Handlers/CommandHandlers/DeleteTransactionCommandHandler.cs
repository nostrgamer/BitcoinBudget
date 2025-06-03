using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handles the deletion of transactions.
/// </summary>
public class DeleteTransactionCommandHandler : IRequestHandler<DeleteTransactionCommand, DeleteTransactionResult>
{
    private readonly ITransactionRepository _transactionRepository;

    public DeleteTransactionCommandHandler(ITransactionRepository transactionRepository)
    {
        _transactionRepository = transactionRepository;
    }

    public async Task<DeleteTransactionResult> Handle(DeleteTransactionCommand request, CancellationToken cancellationToken)
    {
        try
        {
            // Check if transaction exists
            var transaction = await _transactionRepository.GetByIdAsync(request.TransactionId);
            if (transaction == null)
            {
                return new DeleteTransactionResult(
                    Success: false,
                    ErrorMessage: $"Transaction with ID {request.TransactionId} not found"
                );
            }

            // Delete the transaction
            await _transactionRepository.DeleteAsync(transaction);

            return new DeleteTransactionResult(Success: true);
        }
        catch (Exception ex)
        {
            return new DeleteTransactionResult(
                Success: false,
                ErrorMessage: $"Failed to delete transaction: {ex.Message}"
            );
        }
    }
} 
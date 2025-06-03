using BitcoinOnBudgetDesktop.Application.Commands.Categories;
using BitcoinOnBudgetDesktop.Core.Interfaces;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handles the deletion of categories with proper validation.
/// </summary>
public class DeleteCategoryCommandHandler : IRequestHandler<DeleteCategoryCommand, DeleteCategoryResult>
{
    private readonly ICategoryRepository _categoryRepository;
    private readonly ITransactionRepository _transactionRepository;

    public DeleteCategoryCommandHandler(
        ICategoryRepository categoryRepository,
        ITransactionRepository transactionRepository)
    {
        _categoryRepository = categoryRepository;
        _transactionRepository = transactionRepository;
    }

    public async Task<DeleteCategoryResult> Handle(DeleteCategoryCommand request, CancellationToken cancellationToken)
    {
        try
        {
            // Check if category exists
            var category = await _categoryRepository.GetByIdAsync(request.CategoryId);
            if (category == null)
            {
                return new DeleteCategoryResult(
                    Success: false,
                    ErrorMessage: $"Category with ID {request.CategoryId} not found"
                );
            }

            // Check if category has transactions
            var transactions = await _transactionRepository.GetByCategoryIdAsync(request.CategoryId);
            if (transactions.Any())
            {
                return new DeleteCategoryResult(
                    Success: false,
                    ErrorMessage: $"Cannot delete category '{category.Name}' because it has {transactions.Count()} transaction(s). Delete the transactions first."
                );
            }

            // Check if category has allocations
            // Note: We could add a more sophisticated check here for allocations
            // For now, we'll allow deletion even if there are allocations, but we could enhance this

            // Delete the category
            await _categoryRepository.DeleteAsync(category);

            return new DeleteCategoryResult(Success: true);
        }
        catch (Exception ex)
        {
            return new DeleteCategoryResult(
                Success: false,
                ErrorMessage: $"Failed to delete category: {ex.Message}"
            );
        }
    }
} 
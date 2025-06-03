using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Commands.Categories;

/// <summary>
/// Command to delete a category.
/// </summary>
public record DeleteCategoryCommand(int CategoryId) : IRequest<DeleteCategoryResult>;

public record DeleteCategoryResult(
    bool Success,
    string? ErrorMessage = null
); 
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Commands.Categories;

/// <summary>
/// Command to create a new spending category.
/// </summary>
public record CreateCategoryCommand(
    int BudgetId,
    string Name,
    string? Description = null,
    string? Color = null
) : IRequest<CreateCategoryResult>;

public record CreateCategoryResult(
    bool Success,
    int? CategoryId = null,
    string? ErrorMessage = null
); 
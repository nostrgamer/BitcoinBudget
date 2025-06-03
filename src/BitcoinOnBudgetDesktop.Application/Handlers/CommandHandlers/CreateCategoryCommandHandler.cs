using MediatR;
using BitcoinOnBudgetDesktop.Application.Commands.Categories;
using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.Interfaces;

namespace BitcoinOnBudgetDesktop.Application.Handlers.CommandHandlers;

/// <summary>
/// Handler for creating new categories.
/// </summary>
public class CreateCategoryCommandHandler : IRequestHandler<CreateCategoryCommand, CreateCategoryResult>
{
    private readonly ICategoryRepository _categoryRepository;

    public CreateCategoryCommandHandler(ICategoryRepository categoryRepository)
    {
        _categoryRepository = categoryRepository;
    }

    public async Task<CreateCategoryResult> Handle(CreateCategoryCommand request, CancellationToken cancellationToken)
    {
        try
        {
            var category = new Category(
                budgetId: request.BudgetId,
                name: request.Name,
                description: request.Description,
                color: request.Color
            );

            var createdCategory = await _categoryRepository.AddAsync(category);

            return new CreateCategoryResult(
                Success: true,
                CategoryId: createdCategory.Id
            );
        }
        catch (Exception ex)
        {
            return new CreateCategoryResult(
                Success: false,
                ErrorMessage: ex.Message
            );
        }
    }
} 
using BitcoinOnBudgetDesktop.Application.DTOs;
using MediatR;

namespace BitcoinOnBudgetDesktop.Application.Queries.Categories;

/// <summary>
/// Query to retrieve all categories for a specific budget.
/// </summary>
public record GetCategoriesQuery(int BudgetId) : IRequest<IEnumerable<CategoryDto>>; 
using BitcoinOnBudgetDesktop.Core.Interfaces;
using BitcoinOnBudgetDesktop.Infrastructure.Data;
using BitcoinOnBudgetDesktop.Infrastructure.Data.Repositories;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace BitcoinOnBudgetDesktop.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, string connectionString)
    {
        // Add DbContext
        services.AddDbContext<BudgetDbContext>(options =>
            options.UseSqlite(connectionString));

        // Add repositories
        services.AddScoped<ICategoryRepository, CategoryRepository>();
        services.AddScoped<IBudgetRepository, BudgetRepository>();
        services.AddScoped<IBudgetPeriodRepository, BudgetPeriodRepository>();
        services.AddScoped<ITransactionRepository, TransactionRepository>();

        return services;
    }
} 
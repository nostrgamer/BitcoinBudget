using BitcoinOnBudgetDesktop.Application;
using BitcoinOnBudgetDesktop.Application.Commands.Categories;
using BitcoinOnBudgetDesktop.Application.Queries.Categories;
using BitcoinOnBudgetDesktop.Infrastructure;
using BitcoinOnBudgetDesktop.Infrastructure.Data;
using BitcoinOnBudgetDesktop.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using MediatR;
using System.IO;

namespace BitcoinOnBudgetDesktop.Presentation;

public class Program
{
    [STAThread]
    public static async Task Main(string[] args)
    {
        // Test our command pipeline first
        await TestCommandPipeline();
        
        // Then start WPF
        var app = new App();
        app.InitializeComponent();
        app.Run();
    }
    
    private static async Task TestCommandPipeline()
    {
        Console.WriteLine("Testing CQRS pipeline...");
        
        var host = CreateTestHost();
        await host.StartAsync();
        
        try
        {
            // Ensure database and default budget exist
            using var scope = host.Services.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<BudgetDbContext>();
            await context.Database.EnsureCreatedAsync();
            
            if (!await context.Budgets.AnyAsync())
            {
                var defaultBudget = new Budget("Test Budget");
                context.Budgets.Add(defaultBudget);
                await context.SaveChangesAsync();
                Console.WriteLine("Created default budget");
            }
            
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // Test querying categories
            Console.WriteLine("Querying existing categories...");
            var query = new GetCategoriesQuery(1);
            var existingCategories = await mediator.Send(query);
            Console.WriteLine($"Found {existingCategories.Count()} existing categories");
            
            // Test creating a category
            var command = new CreateCategoryCommand(1, "Groceries", "Food and household items");
            var result = await mediator.Send(command);
            
            if (result.Success)
            {
                Console.WriteLine($"Successfully created category with ID: {result.CategoryId}");
                
                // Query again to verify
                var updatedCategories = await mediator.Send(query);
                Console.WriteLine($"Now have {updatedCategories.Count()} categories total");
                
                foreach (var category in updatedCategories)
                {
                    Console.WriteLine($"- {category.Name}: {category.Description}");
                }
            }
            else
            {
                Console.WriteLine($"Failed to create category: {result.ErrorMessage}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
        }
        finally
        {
            await host.StopAsync();
        }
    }
    
    private static IHost CreateTestHost()
    {
        return Host.CreateDefaultBuilder()
            .ConfigureServices(services =>
            {
                var dataDirectory = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "BitcoinOnBudgetDesktop");
                
                Directory.CreateDirectory(dataDirectory);
                var connectionString = $"Data Source={Path.Combine(dataDirectory, "budget.db")}";

                services.AddApplication();
                services.AddInfrastructure(connectionString);
            })
            .Build();
    }
} 
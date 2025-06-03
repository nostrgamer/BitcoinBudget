using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using MediatR;
using BitcoinOnBudgetDesktop.Application.Commands.Categories;
using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Application.Queries.Categories;
using BitcoinOnBudgetDesktop.Application.Queries.Budget;
using BitcoinOnBudgetDesktop.Application.Queries.Transactions;
using BitcoinOnBudgetDesktop.Core.ValueObjects;
using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BitcoinOnBudgetDesktop.Presentation;

/// <summary>
/// Comprehensive diagnostic tool to validate all systems before normal operation.
/// This catches all issues upfront instead of debugging one at a time.
/// </summary>
public class DiagnosticTool
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<DiagnosticTool> _logger;
    private readonly List<string> _results = new();
    private int _testCount = 0;
    private int _passedCount = 0;

    public DiagnosticTool(IServiceProvider serviceProvider, ILogger<DiagnosticTool> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    public async Task<DiagnosticReport> RunFullDiagnosticAsync()
    {
        _logger.LogInformation("=== STARTING FULL DIAGNOSTIC ===");
        
        // Core tests
        await TestValueObjectsAsync();
        await TestDatabaseConnectionAsync();
        await TestEntityCreationAsync();
        
        // Application layer tests
        await TestCommandHandlersAsync();
        await TestQueryHandlersAsync();
        await TestMediatRPipelineAsync();
        
        // Infrastructure tests
        await TestRepositoriesAsync();
        await TestEntityFrameworkAsync();
        
        // Budget allocation system tests
        await TestBudgetAllocationSystemAsync();
        
        // Integration tests
        await TestFullWorkflowAsync();
        
        // Test 9: End-to-End Workflow Tests
        await TestEndToEndWorkflow();

        // Test 10: Budget Calculation Corner Cases (NEW - for debugging the current issues)
        await TestBudgetCalculationCornerCases();

        // Test 11: Budget Seeding and Default Budget Test
        await TestDefaultBudgetExists();
        
        // Test 12: Detailed Budget Reset and Recovery Test
        await TestBudgetResetAndRecovery();
        
        // Test 13: Step-by-Step Income and Allocation Test
        await TestStepByStepIncomeAndAllocation();
        
        // Test 14: Database State Verification Test
        await TestDatabaseStateVerification();
        
        // Test 15: AddIncomeCommand Deep Dive Test
        await TestAddIncomeCommandWorkflow();

        // Test 16: Comprehensive Allocation System Diagnostic
        await TestAllocationSystemComprehensiveAsync();

        var report = new DiagnosticReport
        {
            TotalTests = _testCount,
            PassedTests = _passedCount,
            FailedTests = _testCount - _passedCount,
            Results = _results.ToList(),
            Success = _passedCount == _testCount
        };
        
        _logger.LogInformation("=== DIAGNOSTIC COMPLETE: {Passed}/{Total} tests passed ===", 
            _passedCount, _testCount);
        
        return report;
    }

    private async Task TestValueObjectsAsync()
    {
        LogTest("Testing SatoshiAmount Value Object");
        
        try
        {
            // Test creation and validation
            var amount = new SatoshiAmount(100000);
            Assert(amount.Value == 100000, "SatoshiAmount creation");
            
            // Test addition
            var sum = amount + new SatoshiAmount(50000);
            Assert(sum.Value == 150000, "SatoshiAmount addition");
            
            // Test negative validation
            try
            {
                new SatoshiAmount(-1);
                Fail("Should reject negative amounts");
            }
            catch (ArgumentException)
            {
                Pass("Correctly rejects negative amounts");
            }
            
            Pass("SatoshiAmount value object works correctly");
            await Task.CompletedTask; // Make async
        }
        catch (Exception ex)
        {
            Fail($"SatoshiAmount test failed: {ex.Message}");
        }
    }

    private async Task TestDatabaseConnectionAsync()
    {
        LogTest("Testing Database Connection");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<BudgetDbContext>();
            
            await context.Database.EnsureCreatedAsync();
            var canConnect = await context.Database.CanConnectAsync();
            
            Assert(canConnect, "Database connection");
            Pass("Database connection successful");
        }
        catch (Exception ex)
        {
            Fail($"Database connection failed: {ex.Message}");
        }
    }

    private async Task TestEntityCreationAsync()
    {
        LogTest("Testing Entity Creation");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<BudgetDbContext>();
            
            // Test Budget creation
            var budget = new BitcoinOnBudgetDesktop.Core.Entities.Budget("Test Budget");
            context.Budgets.Add(budget);
            await context.SaveChangesAsync();
            
            Assert(budget.Id > 0, "Budget entity creation and persistence");
            
            // Test Category creation
            var category = new BitcoinOnBudgetDesktop.Core.Entities.Category(budget.Id, "Test Category");
            context.Categories.Add(category);
            await context.SaveChangesAsync();
            
            Assert(category.Id > 0, "Category entity creation and persistence");
            
            Pass("Entity creation and persistence works");
        }
        catch (Exception ex)
        {
            Fail($"Entity creation failed: {ex.Message}");
        }
    }

    private async Task TestCommandHandlersAsync()
    {
        LogTest("Testing Command Handlers");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // Use unique name to avoid constraint violations
            var uniqueName = $"DiagnosticTest-{DateTime.Now:yyyyMMdd-HHmmss-fff}";
            var command = new CreateCategoryCommand(1, uniqueName);
            var result = await mediator.Send(command);
            
            Assert(result.Success, "CreateCategoryCommand execution");
            Assert(result.CategoryId > 0, "Category ID returned from command");
            
            Pass("Command handlers working correctly");
        }
        catch (Exception ex)
        {
            Fail($"Command handler test failed: {ex.Message}");
        }
    }

    private async Task TestQueryHandlersAsync()
    {
        LogTest("Testing Query Handlers");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // Test GetCategoriesQuery
            var query = new GetCategoriesQuery(1);
            var categories = await mediator.Send(query);
            
            Assert(categories != null, "GetCategoriesQuery returns result");
            Assert(categories?.Any() == true, "Categories found in query result");
            
            Pass("Query handlers working correctly");
        }
        catch (Exception ex)
        {
            Fail($"Query handler test failed: {ex.Message}");
        }
    }

    private async Task TestMediatRPipelineAsync()
    {
        LogTest("Testing MediatR Pipeline");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            Assert(mediator != null, "MediatR mediator resolution");
            
            // Test that we can resolve handlers
            var handlers = scope.ServiceProvider.GetServices<IRequestHandler<CreateCategoryCommand, CreateCategoryResult>>();
            Assert(handlers.Any(), "Command handlers registered");
            
            var queryHandlers = scope.ServiceProvider.GetServices<IRequestHandler<GetCategoriesQuery, IEnumerable<BitcoinOnBudgetDesktop.Application.DTOs.CategoryDto>>>();
            Assert(queryHandlers.Any(), "Query handlers registered");
            
            Pass("MediatR pipeline configured correctly");
            await Task.CompletedTask; // Make async
        }
        catch (Exception ex)
        {
            Fail($"MediatR pipeline test failed: {ex.Message}");
        }
    }

    private async Task TestRepositoriesAsync()
    {
        LogTest("Testing Repository Pattern");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var categoryRepo = scope.ServiceProvider.GetRequiredService<BitcoinOnBudgetDesktop.Core.Interfaces.ICategoryRepository>();
            var budgetRepo = scope.ServiceProvider.GetRequiredService<BitcoinOnBudgetDesktop.Core.Interfaces.IBudgetRepository>();
            var budgetPeriodRepo = scope.ServiceProvider.GetRequiredService<BitcoinOnBudgetDesktop.Core.Interfaces.IBudgetPeriodRepository>();
            
            Assert(categoryRepo != null, "Category repository resolution");
            Assert(budgetRepo != null, "Budget repository resolution");
            Assert(budgetPeriodRepo != null, "BudgetPeriod repository resolution");
            
            // Test basic repository operations - use correct method name
            var categories = await categoryRepo.GetByBudgetIdAsync(1);
            Assert(categories != null, "Category repository query");
            
            Pass("Repository pattern working correctly");
        }
        catch (Exception ex)
        {
            Fail($"Repository test failed: {ex.Message}");
        }
    }

    private async Task TestEntityFrameworkAsync()
    {
        LogTest("Testing Entity Framework Configuration");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<BudgetDbContext>();
            
            // Test entity configurations
            var budgetEntity = context.Model.FindEntityType(typeof(BitcoinOnBudgetDesktop.Core.Entities.Budget));
            Assert(budgetEntity != null, "Budget entity configured");
            
            var categoryEntity = context.Model.FindEntityType(typeof(BitcoinOnBudgetDesktop.Core.Entities.Category));
            Assert(categoryEntity != null, "Category entity configured");
            
            // Test SatoshiAmount conversion in Transaction entity
            var transactionEntity = context.Model.FindEntityType(typeof(BitcoinOnBudgetDesktop.Core.Entities.Transaction));
            Assert(transactionEntity != null, "Transaction entity configured");
            
            var transactionProps = transactionEntity?.GetProperties();
            var amountProp = transactionProps?.FirstOrDefault(p => p.Name == "Amount");
            Assert(amountProp != null, "Transaction Amount SatoshiAmount conversion configured");
            
            // Test SatoshiAmount conversion in CategoryAllocation entity
            var allocationEntity = context.Model.FindEntityType(typeof(BitcoinOnBudgetDesktop.Core.Entities.CategoryAllocation));
            Assert(allocationEntity != null, "CategoryAllocation entity configured");
            
            var allocationProps = allocationEntity?.GetProperties();
            var allocationAmountProp = allocationProps?.FirstOrDefault(p => p.Name == "Amount");
            Assert(allocationAmountProp != null, "CategoryAllocation Amount SatoshiAmount conversion configured");
            
            // Test BudgetPeriod entity
            var budgetPeriodEntity = context.Model.FindEntityType(typeof(BitcoinOnBudgetDesktop.Core.Entities.BudgetPeriod));
            Assert(budgetPeriodEntity != null, "BudgetPeriod entity configured");
            
            Pass("Entity Framework configuration correct");
            await Task.CompletedTask; // Make async
        }
        catch (Exception ex)
        {
            Fail($"Entity Framework test failed: {ex.Message}");
        }
    }

    private async Task TestBudgetAllocationSystemAsync()
    {
        LogTest("Testing Budget Allocation System");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // Test GetCurrentBudgetPeriodQuery
            var currentPeriodQuery = new GetCurrentBudgetPeriodQuery(1);
            var currentPeriod = await mediator.Send(currentPeriodQuery);
            Assert(currentPeriod != null, "GetCurrentBudgetPeriodQuery returns result");
            Assert(currentPeriod?.Id > 0, "Current budget period has valid ID");
            
            // Add income first so we have funds to allocate
            var addIncomeCommand = new AddIncomeCommand(
                BudgetId: 1, // Use budget ID directly
                Amount: new SatoshiAmount(10000), // Add 10,000 sats income
                Description: "Test income for allocation"
            );
            var incomeResult = await mediator.Send(addIncomeCommand);
            Assert(incomeResult.Success, "Add income command executed successfully");
            
            // Test allocation command with small amount (half of income)
            var allocateCommand = new AllocateToCategoryCommand(
                BudgetPeriodId: currentPeriod!.Id,
                CategoryId: 1, // Assuming we have a category with ID 1
                Amount: new SatoshiAmount(5000) // Allocate 5,000 sats
            );
            
            var allocationResult = await mediator.Send(allocateCommand);
            Assert(allocationResult.Success, "Budget allocation command executed successfully");
            
            // Test budget summary query
            var summaryQuery = new GetBudgetSummaryQuery(1, currentPeriod.Id);
            var summary = await mediator.Send(summaryQuery);
            Assert(summary != null, "GetBudgetSummaryQuery returns result");
            
            Pass("Budget allocation system working correctly");
        }
        catch (Exception ex)
        {
            Fail($"Budget allocation system test failed: {ex.Message}");
        }
    }

    private async Task TestFullWorkflowAsync()
    {
        LogTest("Testing Full End-to-End Workflow");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // 1. Create a category with unique name
            var uniqueName = $"E2E-Test-{DateTime.Now:yyyyMMdd-HHmmss-fff}";
            var createCommand = new CreateCategoryCommand(1, uniqueName);
            var createResult = await mediator.Send(createCommand);
            Assert(createResult.Success, "End-to-end category creation");
            
            // 2. Query for categories
            var query = new GetCategoriesQuery(1);
            var categories = await mediator.Send(query);
            var testCategory = categories?.FirstOrDefault(c => c.Name == uniqueName);
            Assert(testCategory != null, "End-to-end category retrieval");
            
            // 3. Get current budget period
            var periodQuery = new GetCurrentBudgetPeriodQuery(1);
            var period = await mediator.Send(periodQuery);
            Assert(period != null, "End-to-end budget period retrieval");
            
            // 4. Add income to budget before allocation
            var addIncomeCommand = new AddIncomeCommand(
                BudgetId: 1, // Use budget ID directly
                Amount: new SatoshiAmount(20000), // Add 20,000 sats income
                Description: "E2E test income"
            );
            var incomeResult = await mediator.Send(addIncomeCommand);
            Assert(incomeResult.Success, "End-to-end income addition");
            
            // 5. Test allocation
            var allocationCommand = new AllocateToCategoryCommand(
                BudgetPeriodId: period!.Id,
                CategoryId: testCategory!.Id,
                Amount: new SatoshiAmount(8000) // Allocate 8,000 sats (less than income)
            );
            var allocationResult = await mediator.Send(allocationCommand);
            Assert(allocationResult.Success, "End-to-end budget allocation");
            
            Pass("Full end-to-end workflow successful");
        }
        catch (Exception ex)
        {
            Fail($"End-to-end workflow failed: {ex.Message}");
        }
    }

    private async Task TestEndToEndWorkflow()
    {
        var testName = "End-to-End Workflow";
        LogTest(testName);
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // 1. Create a category with unique name
            var uniqueName = $"E2E-Test-{DateTime.Now:yyyyMMdd-HHmmss-fff}";
            var createCommand = new CreateCategoryCommand(1, uniqueName);
            var createResult = await mediator.Send(createCommand);
            
            if (!createResult.Success)
            {
                Fail($"Category creation failed: {createResult.ErrorMessage}");
                return;
            }
            
            // 2. Query for categories
            var query = new GetCategoriesQuery(1);
            var categories = await mediator.Send(query);
            var testCategory = categories?.FirstOrDefault(c => c.Name == uniqueName);
            
            if (testCategory == null)
            {
                Fail("Category not found after creation");
                return;
            }
            
            // 3. Get current budget period
            var periodQuery = new GetCurrentBudgetPeriodQuery(1);
            var period = await mediator.Send(periodQuery);
            
            if (period == null)
            {
                Fail("Failed to get budget period");
                return;
            }
            
            // 4. Add income to budget before allocation
            var addIncomeCommand = new AddIncomeCommand(
                BudgetId: 1,
                Amount: new SatoshiAmount(20000),
                Description: "E2E test income"
            );
            var incomeResult = await mediator.Send(addIncomeCommand);
            
            if (!incomeResult.Success)
            {
                Fail($"Income addition failed: {incomeResult.ErrorMessage}");
                return;
            }
            
            // 5. Test allocation
            var allocationCommand = new AllocateToCategoryCommand(
                BudgetPeriodId: period.Id,
                CategoryId: testCategory.Id,
                Amount: new SatoshiAmount(8000)
            );
            var allocationResult = await mediator.Send(allocationCommand);
            
            if (!allocationResult.Success)
            {
                Fail($"Allocation failed: {allocationResult.ErrorMessage}");
                return;
            }
            
            Pass("End-to-end workflow completed successfully");
        }
        catch (Exception ex)
        {
            Fail($"Exception: {ex.Message}");
        }
    }

    private async Task TestBudgetCalculationCornerCases()
    {
        var testName = "Budget Calculation After Reset";
        LogTest(testName);
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // Step 1: Add income transaction
            var addIncomeCommand = new AddIncomeCommand(
                BudgetId: 1,
                Amount: new SatoshiAmount(5000000), // 5M sats like in the screenshot
                Description: "Test Freelance Income"
            );
            var incomeResult = await mediator.Send(addIncomeCommand);
            
            if (!incomeResult.Success)
            {
                Fail($"Failed to add income: {incomeResult.ErrorMessage}");
                return;
            }
            
            // Step 2: Get current budget period (should auto-create)
            var periodQuery = new GetCurrentBudgetPeriodQuery(1);
            var period = await mediator.Send(periodQuery);
            
            if (period == null)
            {
                Fail("Failed to get/create current budget period");
                return;
            }
            
            // Step 3: Get budget summary and check income calculation
            var summaryQuery = new GetBudgetSummaryQuery(1, period.Id);
            var summary = await mediator.Send(summaryQuery);
            
            if (summary == null)
            {
                Fail("Failed to get budget summary");
                return;
            }
            
            // Step 4: Verify income shows up correctly
            if (summary.TotalIncome.Value == 0)
            {
                Fail($"Income calculation failed - Total Income: {summary.TotalIncome.Value} sats " +
                     $"(expected: 5000000 sats). Available to Assign: {summary.AvailableToAssign.Value} sats");
                return;
            }
            
            // Step 5: Verify available to assign is correct
            if (summary.AvailableToAssign.Value == 0)
            {
                Fail($"Available to Assign calculation failed - Available: {summary.AvailableToAssign.Value} sats " +
                     $"(expected: 5000000 sats). Total Income: {summary.TotalIncome.Value} sats, " +
                     $"Total Allocated: {summary.TotalAllocated.Value} sats");
                return;
            }
            
            // Step 6: Try to create a category (reported as failing)
            var categoryName = $"Test-Reset-Category-{DateTime.Now:HHmmss}";
            var createCategoryCommand = new CreateCategoryCommand(1, categoryName);
            var categoryResult = await mediator.Send(createCategoryCommand);
            
            if (!categoryResult.Success)
            {
                Fail($"Category creation failed: {categoryResult.ErrorMessage}");
                return;
            }
            
            Pass($"Budget calculations working correctly - Income: {summary.TotalIncome.Value} sats, " +
                 $"Available: {summary.AvailableToAssign.Value} sats, Category created successfully");
        }
        catch (Exception ex)
        {
            Fail($"Test exception: {ex.Message}");
        }
    }

    private async Task TestDefaultBudgetExists()
    {
        var testName = "Budget Seeding and Default Budget Test";
        LogTest(testName);
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // Test GetCurrentBudgetPeriodQuery
            var currentPeriodQuery = new GetCurrentBudgetPeriodQuery(1);
            var currentPeriod = await mediator.Send(currentPeriodQuery);
            
            if (currentPeriod == null)
            {
                Fail("GetCurrentBudgetPeriodQuery returned null - Budget ID 1 may not exist");
                return;
            }
            
            if (currentPeriod.Id <= 0)
            {
                Fail("Current budget period has invalid ID");
                return;
            }
            
            // Test budget summary query
            var summaryQuery = new GetBudgetSummaryQuery(1, currentPeriod.Id);
            var summary = await mediator.Send(summaryQuery);
            
            if (summary == null)
            {
                Fail("GetBudgetSummaryQuery returned null");
                return;
            }
            
            Pass($"Budget seeding working - Budget: {summary.BudgetName}, Period: {summary.CurrentPeriod}");
        }
        catch (Exception ex)
        {
            Fail($"Test exception: {ex.Message}");
        }
    }

    private async Task TestBudgetResetAndRecovery()
    {
        var testName = "Detailed Budget Reset and Recovery Test";
        LogTest(testName);
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            var context = scope.ServiceProvider.GetRequiredService<BudgetDbContext>();
            
            // Step 1: Verify Budget ID 1 exists
            var budget = await context.Budgets.FindAsync(1);
            if (budget == null)
            {
                Fail("Budget ID 1 does not exist in database");
                return;
            }
            Pass($"Budget ID 1 exists: {budget.Name}");
            
            // Step 2: Reset all budget data first to simulate user scenario
            var resetCommand = new DeleteBudgetDataCommand(1);
            var resetResult = await mediator.Send(resetCommand);
            if (!resetResult.Success)
            {
                Fail($"Failed to reset budget data: {resetResult.ErrorMessage}");
                return;
            }
            Pass($"Budget reset successful - Deleted: {resetResult.TransactionsDeleted} transactions, {resetResult.CategoriesDeleted} categories");
            
            // Step 3: Verify Budget ID 1 still exists after reset
            budget = await context.Budgets.FindAsync(1);
            if (budget == null)
            {
                Fail("Budget ID 1 was deleted during reset - this is the core issue!");
                return;
            }
            Pass("Budget ID 1 preserved after reset");
            
            // Step 4: Add income transaction like user did
            var addIncomeCommand = new AddIncomeCommand(
                BudgetId: 1,
                Amount: new SatoshiAmount(5000000),
                Description: "Freelance Income"
            );
            var incomeResult = await mediator.Send(addIncomeCommand);
            if (!incomeResult.Success)
            {
                Fail($"Failed to add income after reset: {incomeResult.ErrorMessage}");
                return;
            }
            Pass("Income added successfully after reset");
            
            // Step 5: Check if transaction was actually created
            var transactions = await context.Transactions.Where(t => t.BudgetId == 1).ToListAsync();
            if (!transactions.Any())
            {
                Fail("Income transaction was not persisted to database");
                return;
            }
            Pass($"Found {transactions.Count} transaction(s) in database");
            
            // Step 6: Get current budget period
            var periodQuery = new GetCurrentBudgetPeriodQuery(1);
            var period = await mediator.Send(periodQuery);
            if (period == null)
            {
                Fail("Failed to get/create current budget period after reset");
                return;
            }
            Pass($"Current budget period: {period.DisplayName} (ID: {period.Id})");
            
            // Step 7: Get budget summary and verify calculations
            var summaryQuery = new GetBudgetSummaryQuery(1, period.Id);
            var summary = await mediator.Send(summaryQuery);
            if (summary == null)
            {
                Fail("Failed to get budget summary after reset");
                return;
            }
            
            Pass($"Budget Summary - Income: {summary.TotalIncome.Value} sats, " +
                 $"Allocated: {summary.TotalAllocated.Value} sats, " +
                 $"Available: {summary.AvailableToAssign.Value} sats");
            
            // Step 8: Verify income calculation is correct
            if (summary.TotalIncome.Value != 5000000)
            {
                Fail($"Income calculation incorrect - Expected: 5000000, Actual: {summary.TotalIncome.Value}");
                return;
            }
            
            // Step 9: Verify available to assign is correct
            if (summary.AvailableToAssign.Value != 5000000)
            {
                Fail($"Available to Assign incorrect - Expected: 5000000, Actual: {summary.AvailableToAssign.Value}");
                return;
            }
            
            Pass("All budget calculations correct after reset and income addition");
        }
        catch (Exception ex)
        {
            Fail($"Budget reset and recovery test failed: {ex.Message}\nStack Trace: {ex.StackTrace}");
        }
    }

    private async Task TestStepByStepIncomeAndAllocation()
    {
        var testName = "Step-by-Step Income Transaction Analysis";
        LogTest(testName);
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<BudgetDbContext>();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // Step 1: Direct database query for transactions
            var allTransactions = await context.Transactions
                .Include(t => t.Budget)
                .Include(t => t.Category)
                .Where(t => t.BudgetId == 1)
                .ToListAsync();
            
            Pass($"Found {allTransactions.Count} total transactions for Budget ID 1");
            
            var incomeTransactions = allTransactions.Where(t => t.TransactionType == TransactionType.Income).ToList();
            Pass($"Found {incomeTransactions.Count} income transactions");
            
            if (incomeTransactions.Any())
            {
                var totalIncome = incomeTransactions.Sum(t => t.Amount.Value);
                Pass($"Total income from direct DB query: {totalIncome} sats");
                
                foreach (var transaction in incomeTransactions)
                {
                    Pass($"Income Transaction: {transaction.Amount.Value} sats - {transaction.Description} (Category: {transaction.Category?.Name})");
                }
            }
            
            // Step 2: Repository method verification
            var repo = scope.ServiceProvider.GetRequiredService<BitcoinOnBudgetDesktop.Core.Interfaces.ITransactionRepository>();
            var repoIncome = await repo.GetTotalIncomeAsync(1);
            Pass($"Total income from repository method: {repoIncome.Value} sats");
            
            // Step 3: Test GetBudgetSummaryQuery calculation step by step
            var periodQuery = new GetCurrentBudgetPeriodQuery(1);
            var period = await mediator.Send(periodQuery);
            
            if (period != null)
            {
                var summaryQuery = new GetBudgetSummaryQuery(1, period.Id);
                var summary = await mediator.Send(summaryQuery);
                
                if (summary != null)
                {
                    Pass($"Summary Total Income: {summary.TotalIncome.Value} sats");
                    Pass($"Summary Available to Assign: {summary.AvailableToAssign.Value} sats");
                    Pass($"Summary Total Allocated: {summary.TotalAllocated.Value} sats");
                }
                else
                {
                    Fail("Budget summary returned null");
                }
            }
            else
            {
                Fail("Current budget period is null");
            }
            
            // Step 4: Test category creation
            var categoryName = $"Test-Category-{DateTime.Now:HHmmss}";
            var createCategoryCommand = new CreateCategoryCommand(1, categoryName);
            var categoryResult = await mediator.Send(createCategoryCommand);
            
            if (categoryResult.Success)
            {
                Pass($"Category '{categoryName}' created successfully with ID {categoryResult.CategoryId}");
            }
            else
            {
                Fail($"Category creation failed: {categoryResult.ErrorMessage}");
            }
        }
        catch (Exception ex)
        {
            Fail($"Step-by-step analysis failed: {ex.Message}\nStack Trace: {ex.StackTrace}");
        }
    }

    private async Task TestDatabaseStateVerification()
    {
        var testName = "Database State and Entity Verification";
        LogTest(testName);
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<BudgetDbContext>();
            
            // Check database connection
            var canConnect = await context.Database.CanConnectAsync();
            if (!canConnect)
            {
                Fail("Cannot connect to database");
                return;
            }
            Pass("Database connection successful");
            
            // Check if tables exist by trying to query them
            try
            {
                await context.Budgets.AnyAsync();
                Pass("Budgets table exists and is accessible");
            }
            catch (Exception ex)
            {
                Fail($"Budgets table issue: {ex.Message}");
            }
            
            try
            {
                await context.Transactions.AnyAsync();
                Pass("Transactions table exists and is accessible");
            }
            catch (Exception ex)
            {
                Fail($"Transactions table issue: {ex.Message}");
            }
            
            // Count records in each table
            var budgetCount = await context.Budgets.CountAsync();
            var categoryCount = await context.Categories.CountAsync();
            var transactionCount = await context.Transactions.CountAsync();
            var budgetPeriodCount = await context.BudgetPeriods.CountAsync();
            var allocationCount = await context.CategoryAllocations.CountAsync();
            
            Pass($"Record counts - Budgets: {budgetCount}, Categories: {categoryCount}, " +
                 $"Transactions: {transactionCount}, BudgetPeriods: {budgetPeriodCount}, Allocations: {allocationCount}");
            
            // Check Budget ID 1 specifically
            var defaultBudget = await context.Budgets.FindAsync(1);
            if (defaultBudget != null)
            {
                Pass($"Budget ID 1 exists: '{defaultBudget.Name}' created {defaultBudget.CreatedDate}");
            }
            else
            {
                Fail("Budget ID 1 does not exist - this is a critical issue!");
            }
            
            // Check for any orphaned data
            var orphanedTransactions = await context.Transactions
                .Where(t => !context.Budgets.Any(b => b.Id == t.BudgetId))
                .CountAsync();
            
            var orphanedCategories = await context.Categories
                .Where(c => !context.Budgets.Any(b => b.Id == c.BudgetId))
                .CountAsync();
            
            if (orphanedTransactions > 0 || orphanedCategories > 0)
            {
                Fail($"Found orphaned data - Transactions: {orphanedTransactions}, Categories: {orphanedCategories}");
            }
            else
            {
                Pass("No orphaned data found");
            }
        }
        catch (Exception ex)
        {
            Fail($"Database state verification failed: {ex.Message}");
        }
    }

    private async Task TestAddIncomeCommandWorkflow()
    {
        var testName = "AddIncomeCommand Deep Dive Test";
        LogTest(testName);
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            
            // Step 1: Add income transaction
            var addIncomeCommand = new AddIncomeCommand(
                BudgetId: 1,
                Amount: new SatoshiAmount(5000000), // 5M sats like in the screenshot
                Description: "Test Freelance Income"
            );
            var incomeResult = await mediator.Send(addIncomeCommand);
            
            if (!incomeResult.Success)
            {
                Fail($"Failed to add income: {incomeResult.ErrorMessage}");
                return;
            }
            
            // Step 2: Get current budget period (should auto-create)
            var periodQuery = new GetCurrentBudgetPeriodQuery(1);
            var period = await mediator.Send(periodQuery);
            
            if (period == null)
            {
                Fail("Failed to get/create current budget period");
                return;
            }
            
            // Step 3: Get budget summary and check income calculation
            var summaryQuery = new GetBudgetSummaryQuery(1, period.Id);
            var summary = await mediator.Send(summaryQuery);
            
            if (summary == null)
            {
                Fail("Failed to get budget summary");
                return;
            }
            
            // Step 4: Verify income shows up correctly
            if (summary.TotalIncome.Value == 0)
            {
                Fail($"Income calculation failed - Total Income: {summary.TotalIncome.Value} sats " +
                     $"(expected: 5000000 sats). Available to Assign: {summary.AvailableToAssign.Value} sats");
                return;
            }
            
            // Step 5: Verify available to assign is correct
            if (summary.AvailableToAssign.Value == 0)
            {
                Fail($"Available to Assign calculation failed - Available: {summary.AvailableToAssign.Value} sats " +
                     $"(expected: 5000000 sats). Total Income: {summary.TotalIncome.Value} sats, " +
                     $"Total Allocated: {summary.TotalAllocated.Value} sats");
                return;
            }
            
            Pass("AddIncomeCommand workflow completed successfully");
        }
        catch (Exception ex)
        {
            Fail($"Test exception: {ex.Message}");
        }
    }

    private async Task TestAllocationSystemComprehensiveAsync()
    {
        LogTest("COMPREHENSIVE ALLOCATION SYSTEM DIAGNOSTIC");
        
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
            var context = scope.ServiceProvider.GetRequiredService<BudgetDbContext>();
            
            _logger.LogInformation("=== ALLOCATION DEBUGGING: UI STATE vs DATABASE STATE ===");
            
            // Check what the UI thinks the current period is
            var debugCurrentPeriodQuery = new GetCurrentBudgetPeriodQuery(1);
            var uiCurrentPeriod = await mediator.Send(debugCurrentPeriodQuery);
            _logger.LogInformation($"🎯 UI Current Period: ID={uiCurrentPeriod?.Id}, {uiCurrentPeriod?.Year}-{uiCurrentPeriod?.Month:D2}");
            
            // Check what actually exists in the database
            var allPeriods = await context.BudgetPeriods.Where(bp => bp.BudgetId == 1).ToListAsync();
            _logger.LogInformation($"📊 Database Budget Periods for Budget ID 1:");
            foreach (var period in allPeriods)
            {
                _logger.LogInformation($"   - Period ID {period.Id}: {period.Year}-{period.Month:D2} ({period.StartDate:yyyy-MM-dd} to {period.EndDate:yyyy-MM-dd})");
            }
            
            // Try to load the period that the UI thinks is current
            if (uiCurrentPeriod != null)
            {
                var periodFromDb = await context.BudgetPeriods.FindAsync(uiCurrentPeriod.Id);
                if (periodFromDb == null)
                {
                    _logger.LogInformation($"❌ CRITICAL ISSUE: UI thinks current period is ID {uiCurrentPeriod.Id}, but this period doesn't exist in database!");
                }
                else
                {
                    _logger.LogInformation($"✅ UI current period ID {uiCurrentPeriod.Id} exists in database");
                }
            }

            // Check categories for allocation
            var debugCategories = await context.Categories.Where(c => c.BudgetId == 1).ToListAsync();
            _logger.LogInformation($"📋 Available Categories for Budget ID 1:");
            foreach (var cat in debugCategories)
            {
                _logger.LogInformation($"   - Category ID {cat.Id}: '{cat.Name}'");
            }
            
            // Test a simple allocation with logging
            if (uiCurrentPeriod != null && debugCategories.Any())
            {
                var debugTestCategory = debugCategories.First();
                _logger.LogInformation($"🧪 Testing allocation: 1000 sats to Category '{debugTestCategory.Name}' (ID: {debugTestCategory.Id})");
                _logger.LogInformation($"   - Budget Period ID: {uiCurrentPeriod.Id}");
                
                var debugAllocateCommand = new AllocateToCategoryCommand(
                    BudgetPeriodId: uiCurrentPeriod.Id,
                    CategoryId: debugTestCategory.Id,
                    Amount: new SatoshiAmount(1000)
                );
                
                var result = await mediator.Send(debugAllocateCommand);
                
                if (result.Success)
                {
                    _logger.LogInformation("✅ Test allocation succeeded!");
                }
                else
                {
                    _logger.LogInformation($"❌ Test allocation failed: {result.ErrorMessage}");
                    
                    // Additional debugging for failure
                    _logger.LogInformation("🔍 Detailed failure analysis:");
                    
                    // Check if budget period exists using repository
                    var budgetPeriodRepo = scope.ServiceProvider.GetRequiredService<BitcoinOnBudgetDesktop.Core.Interfaces.IBudgetPeriodRepository>();
                    var periodFromRepo = await budgetPeriodRepo.GetByIdAsync(uiCurrentPeriod.Id);
                    _logger.LogInformation($"   - Repository can find period ID {uiCurrentPeriod.Id}: {periodFromRepo != null}");
                    
                    // Check if category exists using repository
                    var categoryRepo = scope.ServiceProvider.GetRequiredService<BitcoinOnBudgetDesktop.Core.Interfaces.ICategoryRepository>();
                    var categoryFromRepo = await categoryRepo.GetByIdAsync(debugTestCategory.Id);
                    _logger.LogInformation($"   - Repository can find category ID {debugTestCategory.Id}: {categoryFromRepo != null}");
                    _logger.LogInformation($"   - Category belongs to budget 1: {categoryFromRepo?.BudgetId == 1}");
                }
            }

            _logger.LogInformation("=== PHASE 1: DATABASE STATE VERIFICATION ===");
            
            // Check if Budget ID 1 exists
            var budget = await context.Budgets.FindAsync(1);
            if (budget == null)
            {
                _logger.LogInformation("❌ Budget ID 1 does not exist - CRITICAL ISSUE");
                
                // Create it
                budget = new Budget("My Bitcoin Budget");
                context.Budgets.Add(budget);
                await context.SaveChangesAsync();
                _logger.LogInformation($"✅ Created Budget ID 1: '{budget.Name}' with actual ID: {budget.Id}");
            }
            else
            {
                _logger.LogInformation($"✅ Budget ID 1 exists: '{budget.Name}' created {budget.CreatedDate}");
            }
            
            // Check categories
            var categories = await context.Categories.Where(c => c.BudgetId == 1).ToListAsync();
            _logger.LogInformation($"📊 Found {categories.Count} categories for Budget ID 1");
            foreach (var cat in categories)
            {
                _logger.LogInformation($"   - Category {cat.Id}: '{cat.Name}'");
            }
            
            if (categories.Count == 0)
            {
                _logger.LogInformation("⚠️ No categories exist - this might cause allocation issues");
            }
            
            // Check transactions
            var transactions = await context.Transactions.Where(t => t.BudgetId == 1).ToListAsync();
            _logger.LogInformation($"💰 Found {transactions.Count} transactions for Budget ID 1");
            long totalIncome = 0;
            foreach (var txn in transactions.Where(t => t.TransactionType == TransactionType.Income))
            {
                totalIncome += txn.Amount.Value;
                _logger.LogInformation($"   - Income {txn.Id}: {txn.Amount.Value:N0} sats - '{txn.Description}'");
            }
            _logger.LogInformation($"💰 Total Income: {totalIncome:N0} sats");
            
            // Check budget periods
            var budgetPeriods = await context.BudgetPeriods.Where(bp => bp.BudgetId == 1).ToListAsync();
            _logger.LogInformation($"📅 Found {budgetPeriods.Count} budget periods for Budget ID 1");
            foreach (var bp in budgetPeriods)
            {
                _logger.LogInformation($"   - Period {bp.Id}: {bp.Year}-{bp.Month:D2}");
            }
            
            _logger.LogInformation("=== PHASE 2: QUERY HANDLER TESTING ===");
            
            // Test GetCurrentBudgetPeriodQuery
            _logger.LogInformation("🔍 Testing GetCurrentBudgetPeriodQuery...");
            var currentPeriodQuery = new GetCurrentBudgetPeriodQuery(1);
            var currentPeriod = await mediator.Send(currentPeriodQuery);
            
            if (currentPeriod == null)
            {
                _logger.LogInformation("❌ GetCurrentBudgetPeriodQuery returned null - CRITICAL ISSUE");
                Fail("Current budget period query failed");
                return;
            }
            else
            {
                _logger.LogInformation($"✅ Current Period: ID={currentPeriod.Id}, {currentPeriod.Year}-{currentPeriod.Month:D2}");
                _logger.LogInformation($"   - Total Allocated: {currentPeriod.TotalAllocated.Value:N0} sats");
                _logger.LogInformation($"   - Allocations Count: {currentPeriod.CategoryAllocations.Count()}");
            }
            
            // Test GetBudgetSummaryQuery  
            _logger.LogInformation("🔍 Testing GetBudgetSummaryQuery...");
            var summaryQuery = new GetBudgetSummaryQuery(1, currentPeriod.Id);
            var summary = await mediator.Send(summaryQuery);
            
            if (summary == null)
            {
                _logger.LogInformation("❌ GetBudgetSummaryQuery returned null - CRITICAL ISSUE");
                Fail("Budget summary query failed");
                return;
            }
            else
            {
                _logger.LogInformation($"✅ Budget Summary:");
                _logger.LogInformation($"   - Total Income: {summary.TotalIncome.Value:N0} sats");
                _logger.LogInformation($"   - Total Allocated: {summary.TotalAllocated.Value:N0} sats");
                _logger.LogInformation($"   - Available to Assign: {summary.AvailableToAssign.Value:N0} sats");
                _logger.LogInformation($"   - Categories: {summary.Categories.Count()}");
            }
            
            _logger.LogInformation("=== PHASE 3: CATEGORY CREATION TEST ===");
            
            // Ensure we have at least one category for allocation testing
            var testCategoryName = $"TestAllocation-{DateTime.Now:HHmmss}";
            _logger.LogInformation($"🏷️ Creating test category '{testCategoryName}'...");
            
            var createCategoryCommand = new CreateCategoryCommand(1, testCategoryName);
            var createResult = await mediator.Send(createCategoryCommand);
            
            if (!createResult.Success)
            {
                _logger.LogInformation($"❌ Failed to create test category: {createResult.ErrorMessage}");
                Fail("Category creation failed");
                return;
            }
            else
            {
                _logger.LogInformation($"✅ Created test category: {testCategoryName}");
            }
            
            // Get the created category
            var categoriesQuery = new GetCategoriesQuery(1);
            var allCategories = await mediator.Send(categoriesQuery);
            var testCategory = allCategories?.FirstOrDefault(c => c.Name == testCategoryName);
            
            if (testCategory == null)
            {
                _logger.LogInformation("❌ Could not find the test category we just created - CRITICAL ISSUE");
                Fail("Category retrieval failed");
                return;
            }
            else
            {
                _logger.LogInformation($"✅ Found test category: ID={testCategory.Id}, Name='{testCategory.Name}'");
            }
            
            _logger.LogInformation("=== PHASE 4: INCOME ADDITION TEST ===");
            
            // Add income if needed
            if (summary.TotalIncome.Value < 50000)
            {
                _logger.LogInformation("💰 Adding test income...");
                var addIncomeCommand = new AddIncomeCommand(
                    BudgetId: 1,
                    Amount: new SatoshiAmount(50000),
                    Description: "Diagnostic test income"
                );
                
                var incomeResult = await mediator.Send(addIncomeCommand);
                if (!incomeResult.Success)
                {
                    _logger.LogInformation($"❌ Failed to add income: {incomeResult.ErrorMessage}");
                    Fail("Income addition failed");
                    return;
                }
                else
                {
                    _logger.LogInformation("✅ Added 50,000 sats test income");
                }
                
                // Refresh summary
                summary = await mediator.Send(summaryQuery);
                _logger.LogInformation($"💰 Updated Total Income: {summary?.TotalIncome.Value:N0} sats");
                _logger.LogInformation($"💰 Updated Available to Assign: {summary?.AvailableToAssign.Value:N0} sats");
            }
            
            _logger.LogInformation("=== PHASE 5: ALLOCATION COMMAND TEST ===");
            
            // Test allocation with detailed logging
            var allocationAmount = 10000L;
            _logger.LogInformation($"🎯 Testing allocation of {allocationAmount:N0} sats to category '{testCategory.Name}' (ID: {testCategory.Id})...");
            _logger.LogInformation($"   - Budget Period ID: {currentPeriod.Id}");
            _logger.LogInformation($"   - Available before allocation: {summary?.AvailableToAssign.Value:N0} sats");
            
            var allocateCommand = new AllocateToCategoryCommand(
                BudgetPeriodId: currentPeriod.Id,
                CategoryId: testCategory.Id,
                Amount: new SatoshiAmount(allocationAmount)
            );
            
            var allocationResult = await mediator.Send(allocateCommand);
            
            if (!allocationResult.Success)
            {
                _logger.LogInformation($"❌ ALLOCATION FAILED: {allocationResult.ErrorMessage}");
                
                // Additional debugging for allocation failure
                _logger.LogInformation("🔍 DEBUGGING ALLOCATION FAILURE:");
                
                // Re-check budget period exists
                var debugBudgetPeriod = await context.BudgetPeriods.FindAsync(currentPeriod.Id);
                _logger.LogInformation($"   - Budget Period {currentPeriod.Id} exists: {debugBudgetPeriod != null}");
                
                // Re-check category exists  
                var debugCategory = await context.Categories.FindAsync(testCategory.Id);
                _logger.LogInformation($"   - Category {testCategory.Id} exists: {debugCategory != null}");
                _logger.LogInformation($"   - Category belongs to budget 1: {debugCategory?.BudgetId == 1}");
                
                // Check available funds calculation
                var debugIncome = await context.Transactions
                    .Where(t => t.BudgetId == 1 && t.TransactionType == TransactionType.Income)
                    .ToListAsync();
                var debugTotalIncome = debugIncome.Sum(t => t.Amount.Value);
                _logger.LogInformation($"   - Calculated total income: {debugTotalIncome:N0} sats");
                
                var debugAllocations = await context.CategoryAllocations
                    .Where(ca => ca.BudgetPeriod.BudgetId == 1)
                    .ToListAsync();
                var debugTotalAllocated = debugAllocations.Sum(a => a.Amount.Value);
                _logger.LogInformation($"   - Calculated total allocated: {debugTotalAllocated:N0} sats");
                _logger.LogInformation($"   - Calculated available: {debugTotalIncome - debugTotalAllocated:N0} sats");
                
                Fail($"Allocation failed: {allocationResult.ErrorMessage}");
                return;
            }
            else
            {
                _logger.LogInformation($"✅ ALLOCATION SUCCESSFUL: {allocationAmount:N0} sats allocated to '{testCategory.Name}'");
            }
            
            _logger.LogInformation("=== PHASE 6: POST-ALLOCATION VERIFICATION ===");
            
            // Verify allocation was saved
            var verifyPeriod = await mediator.Send(currentPeriodQuery);
            var verifyAllocation = verifyPeriod?.CategoryAllocations.FirstOrDefault(ca => ca.CategoryId == testCategory.Id);
            
            if (verifyAllocation == null)
            {
                _logger.LogInformation("❌ Allocation not found after successful command - DATA PERSISTENCE ISSUE");
                Fail("Allocation persistence failed");
                return;
            }
            else
            {
                _logger.LogInformation($"✅ Allocation verified: {verifyAllocation.Amount.Value:N0} sats to '{verifyAllocation.CategoryName}'");
            }
            
            // Verify budget summary reflects changes
            var finalSummary = await mediator.Send(summaryQuery);
            if (finalSummary != null)
            {
                _logger.LogInformation($"📊 Final Budget Summary:");
                _logger.LogInformation($"   - Total Income: {finalSummary.TotalIncome.Value:N0} sats");
                _logger.LogInformation($"   - Total Allocated: {finalSummary.TotalAllocated.Value:N0} sats");
                _logger.LogInformation($"   - Available to Assign: {finalSummary.AvailableToAssign.Value:N0} sats");
                
                var allocatedCategory = finalSummary.Categories.FirstOrDefault(c => c.Id == testCategory.Id);
                if (allocatedCategory != null)
                {
                    _logger.LogInformation($"   - Test Category Allocated: {allocatedCategory.AllocatedAmount.Value:N0} sats");
                }
            }
            
            _logger.LogInformation("=== PHASE 7: CLEANUP ===");
            
            // Clean up test category
            _logger.LogInformation("🧹 Cleaning up test data...");
            var deleteCommand = new DeleteCategoryCommand(testCategory.Id);
            var deleteResult = await mediator.Send(deleteCommand);
            
            if (deleteResult.Success)
            {
                _logger.LogInformation($"✅ Cleaned up test category '{testCategoryName}'");
            }
            else
            {
                _logger.LogInformation($"⚠️ Could not clean up test category: {deleteResult.ErrorMessage}");
            }
            
            Pass("COMPREHENSIVE ALLOCATION DIAGNOSTIC COMPLETED SUCCESSFULLY");
            _logger.LogInformation("🎉 All allocation system components are working correctly!");
            
        }
        catch (Exception ex)
        {
            _logger.LogInformation($"💥 DIAGNOSTIC EXCEPTION: {ex.Message}");
            _logger.LogInformation($"📍 Stack Trace: {ex.StackTrace}");
            Fail($"Comprehensive allocation diagnostic failed: {ex.Message}");
        }
    }

    private void LogTest(string testName)
    {
        _testCount++;
        _logger.LogInformation("Running test {TestNumber}: {TestName}", _testCount, testName);
    }

    private void Pass(string message)
    {
        _passedCount++;
        var result = $"✓ PASS: {message}";
        _results.Add(result);
        _logger.LogInformation(result);
    }

    private void Fail(string message)
    {
        var result = $"✗ FAIL: {message}";
        _results.Add(result);
        _logger.LogError(result);
    }

    private void Assert(bool condition, string testDescription)
    {
        if (condition)
        {
            Pass(testDescription);
        }
        else
        {
            Fail(testDescription);
        }
    }
}

public class DiagnosticReport
{
    public int TotalTests { get; set; }
    public int PassedTests { get; set; }
    public int FailedTests { get; set; }
    public List<string> Results { get; set; } = new();
    public bool Success { get; set; }
    
    public override string ToString()
    {
        var summary = $"Diagnostic Results: {PassedTests}/{TotalTests} tests passed\n\n";
        summary += string.Join("\n", Results);
        
        if (!Success)
        {
            summary += "\n\n⚠️  ISSUES FOUND - Check logs for details";
        }
        else
        {
            summary += "\n\n✅ ALL TESTS PASSED";
        }
        
        return summary;
    }
} 
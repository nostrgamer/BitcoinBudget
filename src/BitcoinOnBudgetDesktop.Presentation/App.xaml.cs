using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Serilog;
using BitcoinOnBudgetDesktop.Application;
using BitcoinOnBudgetDesktop.Infrastructure;
using BitcoinOnBudgetDesktop.Infrastructure.Data;
using BitcoinOnBudgetDesktop.Presentation.ViewModels;
using BitcoinOnBudgetDesktop.Core.Entities;
using Microsoft.EntityFrameworkCore;
using System.IO;

namespace BitcoinOnBudgetDesktop.Presentation;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : System.Windows.Application
{
    private IHost _host = null!;
    private ILogger<App>? _logger;

    private async void OnStartup(object sender, StartupEventArgs e)
    {
        try
        {
            // Set shutdown mode to prevent premature closure
            ShutdownMode = ShutdownMode.OnMainWindowClose;
            
            // Setup logging first
            SetupLogging();
            
            _host = CreateHostBuilder().Build();
            _logger = _host.Services.GetRequiredService<ILogger<App>>();
            
            _logger.LogInformation("=== APPLICATION STARTUP ===");
            _logger.LogInformation("Starting Bitcoin Budget Desktop...");

            // Create main window first but don't show it yet
            var mainWindow = _host.Services.GetRequiredService<MainWindow>();
            MainWindow = mainWindow; // Set as main window
            
            // Comprehensive startup validation
            await ValidateAndInitializeAsync();

            // Now show the main window
            mainWindow.Show();
            
            _logger.LogInformation("Application started successfully");
        }
        catch (Exception ex)
        {
            var logPath = GetLogFilePath();
            var errorMsg = $"STARTUP FAILED: {ex.GetType().Name}: {ex.Message}\n" +
                          $"StackTrace: {ex.StackTrace}\n" +
                          $"See full log at: {logPath}";
            
            MessageBox.Show(errorMsg, "Startup Error", MessageBoxButton.OK, MessageBoxImage.Error);
            
            if (_logger != null)
                _logger.LogCritical(ex, "Application startup failed");
            else
                File.AppendAllText(logPath, $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} CRITICAL: {errorMsg}\n");
            
            Shutdown(1);
        }
    }

    private async Task ValidateAndInitializeAsync()
    {
        _logger!.LogInformation("Starting validation and initialization...");
        
        // Run comprehensive diagnostic
        var diagnosticTool = _host.Services.GetRequiredService<DiagnosticTool>();
        var report = await diagnosticTool.RunFullDiagnosticAsync();
        
        if (!report.Success)
        {
            // Show diagnostic window instead of simple MessageBox
            var diagnosticWindow = new DiagnosticWindow(_host.Services);
            await diagnosticWindow.ShowDiagnosticAsync(report);
            
            // Check if user chose to continue
            if (!diagnosticWindow.ContinueRequested)
            {
                _logger.LogWarning("User chose to exit application");
                Shutdown(0);
                return;
            }
            
            _logger.LogWarning("User chose to continue despite {FailedTests} failed tests", report.FailedTests);
        }
        
        _logger.LogInformation("All validations passed!");

        // Ensure database is created and Budget ID 1 exists
        var context = _host.Services.GetRequiredService<BudgetDbContext>();
        await context.Database.EnsureCreatedAsync();
        
        // Ensure Budget ID 1 exists (our default budget)
        var defaultBudget = await context.Budgets.FindAsync(1);
        if (defaultBudget == null)
        {
            defaultBudget = new BitcoinOnBudgetDesktop.Core.Entities.Budget("My Bitcoin Budget");
            context.Budgets.Add(defaultBudget);
            await context.SaveChangesAsync();
            
            // Log the actual ID (should be 1 as first record)
            _logger.LogInformation("Default budget created with ID {BudgetId}", defaultBudget.Id);
        }
        else
        {
            _logger.LogInformation("Default budget already exists with ID 1");
        }

        _logger.LogInformation("Database initialization completed successfully");
    }

    private static void SetupLogging()
    {
        var logPath = GetLogFilePath();
        
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .WriteTo.File(logPath,
                outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss} [{Level:u3}] {SourceContext}: {Message:lj}{NewLine}{Exception}",
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 7)
            .CreateLogger();
            
        Console.WriteLine($"Logging to: {logPath}");
    }

    private static string GetLogFilePath()
    {
        var logDir = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "BitcoinOnBudgetDesktop", "Logs");
        Directory.CreateDirectory(logDir);
        return Path.Combine(logDir, "app-.log");
    }

    protected override async void OnExit(ExitEventArgs e)
    {
        _logger?.LogInformation("Application shutting down");
        
        if (_host != null)
        {
            await _host.StopAsync();
            _host.Dispose();
        }
        
        Log.CloseAndFlush();
        base.OnExit(e);
    }

    private static IHostBuilder CreateHostBuilder()
    {
        return Host.CreateDefaultBuilder()
            .UseSerilog()
            .ConfigureServices(services =>
            {
                // Get data directory for SQLite database
                var dataDirectory = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "BitcoinOnBudgetDesktop");
                
                Directory.CreateDirectory(dataDirectory);
                
                var connectionString = $"Data Source={Path.Combine(dataDirectory, "budget.db")}";

                // Register layers
                services.AddApplication();
                services.AddInfrastructure(connectionString);

                // Register ViewModels
                services.AddTransient<MainViewModel>();

                // Register WPF windows/views
                services.AddSingleton<MainWindow>();
                
                // Register diagnostic tool
                services.AddTransient<DiagnosticTool>();
            });
    }
}


using Microsoft.Extensions.DependencyInjection;
using System.Diagnostics;
using System.IO;
using System.Windows;

namespace BitcoinOnBudgetDesktop.Presentation;

public partial class DiagnosticWindow : Window
{
    private readonly IServiceProvider _serviceProvider;
    private DiagnosticReport? _lastReport;

    public bool ContinueRequested { get; private set; }

    public DiagnosticWindow(IServiceProvider serviceProvider)
    {
        InitializeComponent();
        _serviceProvider = serviceProvider;
    }

    public async Task ShowDiagnosticAsync(DiagnosticReport report)
    {
        _lastReport = report;
        
        // Set summary
        var summaryColor = report.Success ? "Green" : "Red";
        var summaryIcon = report.Success ? "✅" : "⚠️";
        SummaryText.Text = $"{summaryIcon} {report.PassedTests}/{report.TotalTests} tests passed";
        
        if (report.Success)
        {
            SummaryText.Foreground = System.Windows.Media.Brushes.Green;
            ContinueButton.Content = "Continue";
        }
        else
        {
            SummaryText.Foreground = System.Windows.Media.Brushes.Red;
            ContinueButton.Content = "Continue Anyway";
        }
        
        // Set detailed results
        ResultsText.Text = string.Join("\n", report.Results);
        
        // Show the window
        ShowDialog();
    }

    private async void RunAgainButton_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            RunAgainButton.IsEnabled = false;
            RunAgainButton.Content = "Running...";
            
            var diagnosticTool = _serviceProvider.GetRequiredService<DiagnosticTool>();
            var report = await diagnosticTool.RunFullDiagnosticAsync();
            
            await ShowDiagnosticAsync(report);
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Failed to run diagnostic: {ex.Message}", "Error", 
                MessageBoxButton.OK, MessageBoxImage.Error);
        }
        finally
        {
            RunAgainButton.IsEnabled = true;
            RunAgainButton.Content = "Run Again";
        }
    }

    private void ViewLogsButton_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            var logDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "BitcoinOnBudgetDesktop", "Logs");
                
            if (Directory.Exists(logDir))
            {
                Process.Start("explorer.exe", logDir);
            }
            else
            {
                MessageBox.Show("Log directory not found.", "Information", 
                    MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Failed to open logs: {ex.Message}", "Error", 
                MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private void ContinueButton_Click(object sender, RoutedEventArgs e)
    {
        ContinueRequested = true;
        Close();
    }

    private void ExitButton_Click(object sender, RoutedEventArgs e)
    {
        ContinueRequested = false;
        Close();
    }
} 
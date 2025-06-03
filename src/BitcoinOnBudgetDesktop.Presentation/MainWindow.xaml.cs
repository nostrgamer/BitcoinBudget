using BitcoinOnBudgetDesktop.Presentation.ViewModels;
using System.Windows;

namespace BitcoinOnBudgetDesktop.Presentation;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }
}
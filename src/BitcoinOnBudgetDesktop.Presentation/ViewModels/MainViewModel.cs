using BitcoinOnBudgetDesktop.Application.Commands.Budget;
using BitcoinOnBudgetDesktop.Application.Commands.Categories;
using BitcoinOnBudgetDesktop.Application.DTOs;
using BitcoinOnBudgetDesktop.Application.Queries.Categories;
using BitcoinOnBudgetDesktop.Application.Queries.Budget;
using BitcoinOnBudgetDesktop.Application.Queries.Transactions;
using BitcoinOnBudgetDesktop.Core.ValueObjects;
using MediatR;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace BitcoinOnBudgetDesktop.Presentation.ViewModels;

public class MainViewModel : INotifyPropertyChanged
{
    private readonly IMediator _mediator;
    private string _categoryName = string.Empty;
    private string _statusMessage = string.Empty;
    private string _allocationAmount = string.Empty;
    private string _incomeAmount = string.Empty;
    private string _incomeDescription = string.Empty;
    private string _expenseAmount = string.Empty;
    private string _expenseDescription = string.Empty;
    private CategoryDto? _selectedCategory;
    private CategoryDto? _selectedExpenseCategory;
    private CategoryDto? _selectedCategoryForDeletion;
    private TransactionDto? _selectedTransaction;
    private BudgetSummaryDto? _budgetSummary;
    private BudgetPeriodDto? _currentPeriod;
    private bool _resetBudgetConfirmation = false;
    private const int DefaultBudgetId = 1; // Using budget ID 1 for now

    public MainViewModel(IMediator mediator)
    {
        _mediator = mediator;
        Categories = new ObservableCollection<CategoryDto>();
        Transactions = new ObservableCollection<TransactionDto>();
        CreateCategoryCommand = new RelayCommand(async () => await CreateCategory(), () => !string.IsNullOrWhiteSpace(CategoryName));
        AllocateCommand = new RelayCommand(async () => await AllocateToCategory(), () => CanAllocate());
        AddIncomeCommand = new RelayCommand(async () => await AddIncome(), () => CanAddIncome());
        AddExpenseCommand = new RelayCommand(async () => await AddExpense(), () => CanAddExpense());
        DeleteCategoryCommand = new RelayCommand(async () => await DeleteCategory(), () => SelectedCategoryForDeletion != null);
        DeleteTransactionCommand = new RelayCommand(async () => await DeleteTransaction(), () => SelectedTransaction != null);
        ResetBudgetCommand = new RelayCommand(async () => await ResetBudget(), () => ResetBudgetConfirmation);
        RefreshCommand = new RelayCommand(async () => await RefreshData());
        
        // Load data on startup
        _ = Task.Run(InitializeData);
    }

    public ObservableCollection<CategoryDto> Categories { get; }
    public ObservableCollection<TransactionDto> Transactions { get; }

    public string CategoryName
    {
        get => _categoryName;
        set
        {
            _categoryName = value;
            OnPropertyChanged();
            ((RelayCommand)CreateCategoryCommand).RaiseCanExecuteChanged();
        }
    }

    public string AllocationAmount
    {
        get => _allocationAmount;
        set
        {
            _allocationAmount = value;
            OnPropertyChanged();
            ((RelayCommand)AllocateCommand).RaiseCanExecuteChanged();
        }
    }

    public string IncomeAmount
    {
        get => _incomeAmount;
        set
        {
            _incomeAmount = value;
            OnPropertyChanged();
            ((RelayCommand)AddIncomeCommand).RaiseCanExecuteChanged();
        }
    }

    public string IncomeDescription
    {
        get => _incomeDescription;
        set
        {
            _incomeDescription = value;
            OnPropertyChanged();
            ((RelayCommand)AddIncomeCommand).RaiseCanExecuteChanged();
        }
    }

    public string ExpenseAmount
    {
        get => _expenseAmount;
        set
        {
            _expenseAmount = value;
            OnPropertyChanged();
            ((RelayCommand)AddExpenseCommand).RaiseCanExecuteChanged();
        }
    }

    public string ExpenseDescription
    {
        get => _expenseDescription;
        set
        {
            _expenseDescription = value;
            OnPropertyChanged();
            ((RelayCommand)AddExpenseCommand).RaiseCanExecuteChanged();
        }
    }

    public CategoryDto? SelectedCategory
    {
        get => _selectedCategory;
        set
        {
            _selectedCategory = value;
            OnPropertyChanged();
            ((RelayCommand)AllocateCommand).RaiseCanExecuteChanged();
        }
    }

    public CategoryDto? SelectedExpenseCategory
    {
        get => _selectedExpenseCategory;
        set
        {
            _selectedExpenseCategory = value;
            OnPropertyChanged();
            ((RelayCommand)AddExpenseCommand).RaiseCanExecuteChanged();
        }
    }

    public CategoryDto? SelectedCategoryForDeletion
    {
        get => _selectedCategoryForDeletion;
        set
        {
            _selectedCategoryForDeletion = value;
            OnPropertyChanged();
            ((RelayCommand)DeleteCategoryCommand).RaiseCanExecuteChanged();
        }
    }

    public TransactionDto? SelectedTransaction
    {
        get => _selectedTransaction;
        set
        {
            _selectedTransaction = value;
            OnPropertyChanged();
            ((RelayCommand)DeleteTransactionCommand).RaiseCanExecuteChanged();
        }
    }

    public bool ResetBudgetConfirmation
    {
        get => _resetBudgetConfirmation;
        set
        {
            _resetBudgetConfirmation = value;
            OnPropertyChanged();
            ((RelayCommand)ResetBudgetCommand).RaiseCanExecuteChanged();
        }
    }

    public string StatusMessage
    {
        get => _statusMessage;
        set
        {
            _statusMessage = value;
            OnPropertyChanged();
        }
    }

    public BudgetSummaryDto? BudgetSummary
    {
        get => _budgetSummary;
        set
        {
            _budgetSummary = value;
            OnPropertyChanged();
            OnPropertyChanged(nameof(AvailableToAssignDisplay));
            OnPropertyChanged(nameof(TotalAllocatedDisplay));
            OnPropertyChanged(nameof(TotalIncomeDisplay));
            OnPropertyChanged(nameof(CurrentPeriodDisplay));
        }
    }

    public BudgetPeriodDto? CurrentPeriod
    {
        get => _currentPeriod;
        set
        {
            _currentPeriod = value;
            OnPropertyChanged();
            OnPropertyChanged(nameof(CurrentPeriodDisplay));
        }
    }

    public string AvailableToAssignDisplay => 
        BudgetSummary?.AvailableToAssign.ToString() ?? "0 sats";

    public string TotalAllocatedDisplay => 
        BudgetSummary?.TotalAllocated.ToString() ?? "0 sats";

    public string TotalIncomeDisplay => 
        BudgetSummary?.TotalIncome.ToString() ?? "0 sats";

    public string CurrentPeriodDisplay => 
        BudgetSummary?.CurrentPeriod ?? "Loading...";

    public ICommand CreateCategoryCommand { get; }
    public ICommand AllocateCommand { get; }
    public ICommand AddIncomeCommand { get; }
    public ICommand AddExpenseCommand { get; }
    public ICommand DeleteCategoryCommand { get; }
    public ICommand DeleteTransactionCommand { get; }
    public ICommand ResetBudgetCommand { get; }
    public ICommand RefreshCommand { get; }

    private bool CanAllocate()
    {
        return SelectedCategory != null && 
               !string.IsNullOrWhiteSpace(AllocationAmount) && 
               long.TryParse(AllocationAmount, out var amount) &&
               amount > 0 &&
               CurrentPeriod != null;
    }

    private bool CanAddIncome()
    {
        return !string.IsNullOrWhiteSpace(IncomeAmount) && 
               long.TryParse(IncomeAmount, out var amount) &&
               amount > 0 &&
               !string.IsNullOrWhiteSpace(IncomeDescription);
    }

    private bool CanAddExpense()
    {
        return !string.IsNullOrWhiteSpace(ExpenseAmount) && 
               long.TryParse(ExpenseAmount, out var amount) &&
               amount > 0 &&
               !string.IsNullOrWhiteSpace(ExpenseDescription) &&
               SelectedExpenseCategory != null;
    }

    private async Task InitializeData()
    {
        try
        {
            // First get or create current budget period
            await LoadCurrentPeriod();
            
            // Then load budget summary
            await LoadBudgetSummary();
            
            // Load categories
            await LoadCategories();
            
            // Load transactions
            await LoadTransactions();
            
            StatusMessage = "✅ Budget data loaded successfully";
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error loading data: {ex.Message}";
        }
    }

    private async Task LoadCurrentPeriod()
    {
        try
        {
            var query = new GetCurrentBudgetPeriodQuery(DefaultBudgetId);
            CurrentPeriod = await _mediator.Send(query);
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error loading budget period: {ex.Message}";
        }
    }

    private async Task LoadBudgetSummary()
    {
        try
        {
            if (CurrentPeriod == null) return;
            
            var query = new GetBudgetSummaryQuery(DefaultBudgetId, CurrentPeriod.Id);
            BudgetSummary = await _mediator.Send(query);
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error loading budget summary: {ex.Message}";
        }
    }

    private async Task LoadCategories()
    {
        try
        {
            // Categories with correct allocation amounts are already loaded in BudgetSummary
            // So we just copy them from there instead of making a separate query
            if (BudgetSummary?.Categories != null)
            {
                Categories.Clear();
                foreach (var category in BudgetSummary.Categories)
                {
                    Categories.Add(category);
                }
            }
            else
            {
                // Fallback: load basic categories if budget summary isn't available yet
                var query = new GetCategoriesQuery(DefaultBudgetId);
                var categories = await _mediator.Send(query);
                
                Categories.Clear();
                if (categories != null)
                {
                    foreach (var category in categories)
                    {
                        Categories.Add(category);
                    }
                }
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error loading categories: {ex.Message}";
        }
    }

    private async Task LoadTransactions()
    {
        try
        {
            var query = new GetTransactionsQuery(DefaultBudgetId);
            var transactions = await _mediator.Send(query);
            
            Transactions.Clear();
            if (transactions != null)
            {
                foreach (var transaction in transactions)
                {
                    Transactions.Add(transaction);
                }
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error loading transactions: {ex.Message}";
        }
    }

    private async Task CreateCategory()
    {
        try
        {
            StatusMessage = "Creating category...";
            
            var command = new CreateCategoryCommand(DefaultBudgetId, CategoryName);
            var result = await _mediator.Send(command);
            
            if (result.Success)
            {
                CategoryName = string.Empty;
                await RefreshData();
                StatusMessage = "✅ Category created successfully";
            }
            else
            {
                StatusMessage = $"❌ Failed to create category: {result.ErrorMessage}";
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error creating category: {ex.Message}";
        }
    }

    private async Task AddIncome()
    {
        try
        {
            if (!long.TryParse(IncomeAmount, out var amount) || amount <= 0)
            {
                StatusMessage = "❌ Please enter a valid income amount greater than 0";
                return;
            }

            StatusMessage = "Adding income...";

            var command = new AddIncomeCommand(
                BudgetId: DefaultBudgetId,
                Amount: new SatoshiAmount(amount),
                Description: IncomeDescription
            );

            var result = await _mediator.Send(command);

            if (result.Success)
            {
                IncomeAmount = string.Empty;
                IncomeDescription = string.Empty;
                await RefreshData();
                StatusMessage = $"✅ Added {amount:N0} sats income: {command.Description}";
            }
            else
            {
                StatusMessage = $"❌ Failed to add income: {result.ErrorMessage}";
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error adding income: {ex.Message}";
        }
    }

    private async Task AddExpense()
    {
        try
        {
            if (!long.TryParse(ExpenseAmount, out var amount) || amount <= 0)
            {
                StatusMessage = "❌ Please enter a valid expense amount greater than 0";
                return;
            }

            StatusMessage = "Adding expense...";

            var command = new AddExpenseCommand(
                BudgetId: DefaultBudgetId,
                Amount: new SatoshiAmount(amount),
                Description: ExpenseDescription,
                CategoryId: SelectedExpenseCategory!.Id
            );

            var result = await _mediator.Send(command);

            if (result.Success)
            {
                ExpenseAmount = string.Empty;
                ExpenseDescription = string.Empty;
                await RefreshData();
                StatusMessage = $"✅ Added {amount:N0} sats expense: {command.Description}";
            }
            else
            {
                StatusMessage = $"❌ Failed to add expense: {result.ErrorMessage}";
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error adding expense: {ex.Message}";
        }
    }

    private async Task AllocateToCategory()
    {
        try
        {
            if (SelectedCategory == null || CurrentPeriod == null) return;
            
            if (!long.TryParse(AllocationAmount, out var amount) || amount <= 0)
            {
                StatusMessage = "❌ Please enter a valid amount greater than 0";
                return;
            }

            StatusMessage = "Allocating funds...";

            var command = new AllocateToCategoryCommand(
                BudgetPeriodId: CurrentPeriod.Id,
                CategoryId: SelectedCategory.Id,
                Amount: new SatoshiAmount(amount)
            );

            var result = await _mediator.Send(command);

            if (result.Success)
            {
                AllocationAmount = string.Empty;
                StatusMessage = $"✅ Allocated {amount:N0} sats to {SelectedCategory.Name}";
                
                try
                {
                    await RefreshData();
                }
                catch (Exception refreshEx)
                {
                    // Don't let refresh errors override success message, just append a warning
                    StatusMessage = $"✅ Allocated {amount:N0} sats to {SelectedCategory.Name} (Warning: {refreshEx.Message})";
                }
            }
            else
            {
                StatusMessage = $"❌ Allocation failed: {result.ErrorMessage}";
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error allocating funds: {ex.Message}";
        }
    }

    private async Task DeleteCategory()
    {
        try
        {
            if (SelectedCategoryForDeletion == null) return;
            
            StatusMessage = "Deleting category...";

            var command = new DeleteCategoryCommand(SelectedCategoryForDeletion.Id);
            var result = await _mediator.Send(command);

            if (result.Success)
            {
                Categories.Remove(SelectedCategoryForDeletion);
                await RefreshData();
                StatusMessage = "✅ Category deleted successfully";
            }
            else
            {
                StatusMessage = $"❌ Failed to delete category: {result.ErrorMessage}";
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error deleting category: {ex.Message}";
        }
    }

    private async Task DeleteTransaction()
    {
        try
        {
            if (SelectedTransaction == null) return;
            
            StatusMessage = "Deleting transaction...";

            var command = new DeleteTransactionCommand(SelectedTransaction.Id);
            var result = await _mediator.Send(command);

            if (result.Success)
            {
                Transactions.Remove(SelectedTransaction);
                await RefreshData();
                StatusMessage = "✅ Transaction deleted successfully";
            }
            else
            {
                StatusMessage = $"❌ Failed to delete transaction: {result.ErrorMessage}";
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error deleting transaction: {ex.Message}";
        }
    }

    private async Task ResetBudget()
    {
        try
        {
            StatusMessage = "⚠️ RESETTING BUDGET - This will delete ALL data...";

            var command = new DeleteBudgetDataCommand(DefaultBudgetId);
            var result = await _mediator.Send(command);

            if (result.Success)
            {
                // Clear local collections
                Categories.Clear();
                Transactions.Clear();
                
                // Reset confirmation
                ResetBudgetConfirmation = false;
                
                // Refresh to show empty state
                await RefreshData();
                
                StatusMessage = $"✅ Budget reset complete! Deleted: {result.TransactionsDeleted} transactions, " +
                               $"{result.CategoriesDeleted} categories, {result.AllocationsDeleted} allocations, " +
                               $"{result.BudgetPeriodsDeleted} budget periods";
            }
            else
            {
                StatusMessage = $"❌ Failed to reset budget: {result.ErrorMessage}";
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error resetting budget: {ex.Message}";
        }
    }

    private async Task RefreshData()
    {
        try
        {
            StatusMessage = "Refreshing data...";
            await LoadCurrentPeriod();
            await LoadBudgetSummary();  // Load budget summary first
            await LoadCategories();     // Then load categories (which now uses data from budget summary)
            await LoadTransactions();
            StatusMessage = "✅ Data refreshed";
        }
        catch (Exception ex)
        {
            StatusMessage = $"❌ Error refreshing data: {ex.Message}";
        }
    }

    public event PropertyChangedEventHandler? PropertyChanged;

    protected virtual void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}

public class RelayCommand : ICommand
{
    private readonly Func<Task> _executeAsync;
    private readonly Func<bool> _canExecute;
    private bool _isExecuting;

    public RelayCommand(Func<Task> executeAsync, Func<bool>? canExecute = null)
    {
        _executeAsync = executeAsync ?? throw new ArgumentNullException(nameof(executeAsync));
        _canExecute = canExecute ?? (() => true);
    }

    public bool CanExecute(object? parameter)
    {
        return !_isExecuting && _canExecute();
    }

    public async void Execute(object? parameter)
    {
        if (!CanExecute(parameter)) return;

        try
        {
            _isExecuting = true;
            RaiseCanExecuteChanged();
            await _executeAsync();
        }
        finally
        {
            _isExecuting = false;
            RaiseCanExecuteChanged();
        }
    }

    public event EventHandler? CanExecuteChanged;

    public void RaiseCanExecuteChanged()
    {
        CanExecuteChanged?.Invoke(this, EventArgs.Empty);
    }
} 
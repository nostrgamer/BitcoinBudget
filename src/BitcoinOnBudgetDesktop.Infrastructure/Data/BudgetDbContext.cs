using Microsoft.EntityFrameworkCore;
using BitcoinOnBudgetDesktop.Core.Entities;
using BitcoinOnBudgetDesktop.Core.ValueObjects;

namespace BitcoinOnBudgetDesktop.Infrastructure.Data;

/// <summary>
/// Entity Framework DbContext for the Bitcoin budgeting system.
/// </summary>
public class BudgetDbContext : DbContext
{
    public DbSet<Budget> Budgets { get; set; }
    public DbSet<Category> Categories { get; set; }
    public DbSet<Transaction> Transactions { get; set; }
    public DbSet<BudgetPeriod> BudgetPeriods { get; set; }
    public DbSet<CategoryAllocation> CategoryAllocations { get; set; }

    public BudgetDbContext(DbContextOptions<BudgetDbContext> options) : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure Budget entity
        modelBuilder.Entity<Budget>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.CreatedDate).IsRequired();
        });

        // Configure Category entity
        modelBuilder.Entity<Category>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Description).HasMaxLength(500);
            entity.Property(e => e.Color).HasMaxLength(20);
            
            entity.HasOne(e => e.Budget)
                  .WithMany(b => b.Categories)
                  .HasForeignKey(e => e.BudgetId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasIndex(e => new { e.BudgetId, e.Name }).IsUnique();
        });

        // Configure Transaction entity with SatoshiAmount conversion
        modelBuilder.Entity<Transaction>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Description).HasMaxLength(500);
            entity.Property(e => e.Date).IsRequired();
            entity.Property(e => e.TransactionType).IsRequired();
            
            // Convert SatoshiAmount to long for storage
            entity.Property(e => e.Amount)
                  .HasConversion(
                      v => v.Value,
                      v => new SatoshiAmount(v))
                  .IsRequired();

            entity.HasOne(e => e.Budget)
                  .WithMany(b => b.Transactions)
                  .HasForeignKey(e => e.BudgetId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(e => e.Category)
                  .WithMany(c => c.Transactions)
                  .HasForeignKey(e => e.CategoryId)
                  .OnDelete(DeleteBehavior.Restrict);
        });

        // Configure BudgetPeriod entity
        modelBuilder.Entity<BudgetPeriod>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Year).IsRequired();
            entity.Property(e => e.Month).IsRequired();
            entity.Property(e => e.StartDate).IsRequired();
            entity.Property(e => e.EndDate).IsRequired();

            entity.HasOne(e => e.Budget)
                  .WithMany(b => b.BudgetPeriods)
                  .HasForeignKey(e => e.BudgetId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasIndex(e => new { e.BudgetId, e.Year, e.Month }).IsUnique();
        });

        // Configure CategoryAllocation entity with SatoshiAmount conversion
        modelBuilder.Entity<CategoryAllocation>(entity =>
        {
            entity.HasKey(e => e.Id);
            
            // Convert SatoshiAmount to long for storage
            entity.Property(e => e.Amount)
                  .HasConversion(
                      v => v.Value,
                      v => new SatoshiAmount(v))
                  .IsRequired();

            entity.HasOne(e => e.BudgetPeriod)
                  .WithMany(bp => bp.CategoryAllocations)
                  .HasForeignKey(e => e.BudgetPeriodId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(e => e.Category)
                  .WithMany(c => c.Allocations)
                  .HasForeignKey(e => e.CategoryId)
                  .OnDelete(DeleteBehavior.Restrict);

            entity.HasIndex(e => new { e.BudgetPeriodId, e.CategoryId }).IsUnique();
        });
    }
} 
using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BitcoinOnBudgetDesktop.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddRolloverFields : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Add new columns to BudgetPeriods table
            migrationBuilder.AddColumn<bool>(
                name: "IsClosed",
                table: "BudgetPeriods",
                type: "INTEGER",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<DateTime>(
                name: "ClosedDate",
                table: "BudgetPeriods",
                type: "TEXT",
                nullable: true);

            // Add new columns to CategoryAllocations table
            migrationBuilder.AddColumn<long>(
                name: "RolloverAmount",
                table: "CategoryAllocations",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0L);

            migrationBuilder.AddColumn<long>(
                name: "NewAllocation",
                table: "CategoryAllocations",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0L);

            migrationBuilder.AddColumn<DateTime>(
                name: "CreatedDate",
                table: "CategoryAllocations",
                type: "TEXT",
                nullable: false,
                defaultValue: new DateTime(2025, 6, 3, 0, 0, 0, 0, DateTimeKind.Utc));

            migrationBuilder.AddColumn<DateTime>(
                name: "LastModified",
                table: "CategoryAllocations",
                type: "TEXT",
                nullable: true);

            // Update existing CategoryAllocations to set NewAllocation = Amount (since they're all new allocations)
            migrationBuilder.Sql("UPDATE CategoryAllocations SET NewAllocation = Amount WHERE NewAllocation = 0");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Remove columns from BudgetPeriods table
            migrationBuilder.DropColumn(
                name: "IsClosed",
                table: "BudgetPeriods");

            migrationBuilder.DropColumn(
                name: "ClosedDate",
                table: "BudgetPeriods");

            // Remove columns from CategoryAllocations table
            migrationBuilder.DropColumn(
                name: "RolloverAmount",
                table: "CategoryAllocations");

            migrationBuilder.DropColumn(
                name: "NewAllocation",
                table: "CategoryAllocations");

            migrationBuilder.DropColumn(
                name: "CreatedDate",
                table: "CategoryAllocations");

            migrationBuilder.DropColumn(
                name: "LastModified",
                table: "CategoryAllocations");
        }
    }
} 
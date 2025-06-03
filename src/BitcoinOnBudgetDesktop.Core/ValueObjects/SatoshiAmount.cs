using System;

namespace BitcoinOnBudgetDesktop.Core.ValueObjects;

/// <summary>
/// Immutable value object representing Bitcoin amounts in satoshis.
/// Prevents floating-point arithmetic errors by working exclusively with whole numbers.
/// </summary>
public readonly struct SatoshiAmount : IEquatable<SatoshiAmount>, IComparable<SatoshiAmount>
{
    private const long SatoshisPerBitcoin = 100_000_000L;
    
    public long Value { get; }

    public SatoshiAmount(long satoshis)
    {
        if (satoshis < 0)
            throw new ArgumentOutOfRangeException(nameof(satoshis), "Satoshi amount cannot be negative");
            
        Value = satoshis;
    }

    /// <summary>
    /// Creates a SatoshiAmount from a Bitcoin decimal value (e.g., 0.00001 BTC)
    /// </summary>
    public static SatoshiAmount FromBitcoin(decimal bitcoin)
    {
        if (bitcoin < 0)
            throw new ArgumentOutOfRangeException(nameof(bitcoin), "Bitcoin amount cannot be negative");
            
        var satoshis = (long)(bitcoin * SatoshisPerBitcoin);
        return new SatoshiAmount(satoshis);
    }

    /// <summary>
    /// Converts satoshis to Bitcoin decimal representation
    /// </summary>
    public decimal ToBitcoin() => (decimal)Value / SatoshisPerBitcoin;

    // Arithmetic operations
    public static SatoshiAmount operator +(SatoshiAmount left, SatoshiAmount right)
    {
        checked
        {
            return new SatoshiAmount(left.Value + right.Value);
        }
    }

    public static SatoshiAmount operator -(SatoshiAmount left, SatoshiAmount right)
    {
        var result = left.Value - right.Value;
        if (result < 0)
            throw new InvalidOperationException("Subtraction would result in negative satoshis");
            
        return new SatoshiAmount(result);
    }

    public static SatoshiAmount operator *(SatoshiAmount amount, decimal multiplier)
    {
        if (multiplier < 0)
            throw new ArgumentOutOfRangeException(nameof(multiplier), "Multiplier cannot be negative");
            
        var result = (long)(amount.Value * multiplier);
        return new SatoshiAmount(result);
    }

    public static SatoshiAmount operator /(SatoshiAmount amount, decimal divisor)
    {
        if (divisor <= 0)
            throw new ArgumentOutOfRangeException(nameof(divisor), "Divisor must be positive");
            
        var result = (long)(amount.Value / divisor);
        return new SatoshiAmount(result);
    }

    // Comparison operations
    public static bool operator ==(SatoshiAmount left, SatoshiAmount right) => left.Value == right.Value;
    public static bool operator !=(SatoshiAmount left, SatoshiAmount right) => left.Value != right.Value;
    public static bool operator <(SatoshiAmount left, SatoshiAmount right) => left.Value < right.Value;
    public static bool operator <=(SatoshiAmount left, SatoshiAmount right) => left.Value <= right.Value;
    public static bool operator >(SatoshiAmount left, SatoshiAmount right) => left.Value > right.Value;
    public static bool operator >=(SatoshiAmount left, SatoshiAmount right) => left.Value >= right.Value;

    // IEquatable implementation
    public bool Equals(SatoshiAmount other) => Value == other.Value;
    public override bool Equals(object? obj) => obj is SatoshiAmount other && Equals(other);
    public override int GetHashCode() => Value.GetHashCode();

    // IComparable implementation
    public int CompareTo(SatoshiAmount other) => Value.CompareTo(other.Value);

    // String representation
    public override string ToString() => $"{Value:N0} sats";
    
    /// <summary>
    /// Formats the amount as Bitcoin with 8 decimal places
    /// </summary>
    public string ToBitcoinString() => $"{ToBitcoin():F8} BTC";

    // Static helpers
    public static SatoshiAmount Zero => new(0);
    public static SatoshiAmount OneBitcoin => new(SatoshisPerBitcoin);
} 
"""
Customer data models for the Transaction Risk Investigation Assistant.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from src.models.transaction import TransactionRecord


@dataclass
class CustomerBaseline:
    """
    Statistical baseline for a customer's normal behavior.
    Used for pattern break detection.
    """
    avg_transaction_amount: Decimal
    median_transaction_amount: Decimal
    avg_daily_transaction_count: float
    common_merchants: list[str]
    common_transaction_types: list[str]
    typical_hours: list[int]  # Hours when customer typically transacts
    
    def to_dict(self) -> dict:
        """Convert baseline to dictionary for JSON serialization."""
        return {
            'avg_transaction_amount': str(self.avg_transaction_amount),
            'median_transaction_amount': str(self.median_transaction_amount),
            'avg_daily_transaction_count': self.avg_daily_transaction_count,
            'common_merchants': self.common_merchants,
            'common_transaction_types': self.common_transaction_types,
            'typical_hours': self.typical_hours
        }
    
    @staticmethod
    def calculate_from_transactions(transactions: list[TransactionRecord]) -> Optional['CustomerBaseline']:
        """
        Calculate customer baseline statistics from transaction history.
        
        Args:
            transactions: List of transaction records to analyze
            
        Returns:
            CustomerBaseline with calculated statistics, or None if no transactions
        """
        if not transactions:
            return None
        
        amounts = [t.amount for t in transactions]
        
        # Calculate statistics
        avg_amount = sum(amounts) / len(amounts)
        sorted_amounts = sorted(amounts)
        median_amount = sorted_amounts[len(sorted_amounts) // 2]
        
        # Calculate daily transaction count
        date_counts = {}
        for t in transactions:
            date_key = t.timestamp.date()
            date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        avg_daily_count = sum(date_counts.values()) / len(date_counts) if date_counts else 0
        
        # Extract common merchants and types
        merchant_counts = {}
        type_counts = {}
        hour_counts = {}
        
        for t in transactions:
            merchant_counts[t.merchant] = merchant_counts.get(t.merchant, 0) + 1
            type_counts[t.transaction_type] = type_counts.get(t.transaction_type, 0) + 1
            hour_counts[t.timestamp.hour] = hour_counts.get(t.timestamp.hour, 0) + 1
        
        common_merchants = sorted(merchant_counts.keys(), key=lambda m: merchant_counts[m], reverse=True)[:5]
        common_types = sorted(type_counts.keys(), key=lambda t: type_counts[t], reverse=True)[:3]
        typical_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:8]
        
        return CustomerBaseline(
            avg_transaction_amount=avg_amount,
            median_transaction_amount=median_amount,
            avg_daily_transaction_count=avg_daily_count,
            common_merchants=common_merchants,
            common_transaction_types=common_types,
            typical_hours=typical_hours
        )


@dataclass
class CustomerProfile:
    """
    Represents a customer with transaction history.
    
    Attributes:
        customer_id: Unique identifier for the customer
        name: Customer name
        transactions: List of transaction records
        baseline_stats: Statistical baseline for pattern break detection
    """
    customer_id: str
    name: str
    transactions: list[TransactionRecord]
    baseline_stats: Optional[CustomerBaseline] = None
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary for JSON serialization."""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'transactions': [t.to_dict() for t in self.transactions],
            'baseline_stats': self.baseline_stats.to_dict() if self.baseline_stats else None
        }

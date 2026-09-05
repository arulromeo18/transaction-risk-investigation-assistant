"""
Transaction data models for the Transaction Risk Investigation Assistant.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class TransactionRecord:
    """
    Represents a single financial transaction.
    
    Attributes:
        transaction_id: Unique identifier for the transaction
        customer_id: Identifier for the customer account
        amount: Transaction amount in decimal format
        timestamp: Date and time of transaction
        merchant: Merchant name or transaction description
        transaction_type: Type of transaction (purchase, transfer, withdrawal)
        category: Optional merchant category (e.g., groceries, gas, online)
        location: Optional transaction location
    """
    transaction_id: str
    customer_id: str
    amount: Decimal
    timestamp: datetime
    merchant: str
    transaction_type: str  # purchase, transfer, withdrawal, deposit
    category: Optional[str] = None
    location: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary for JSON serialization."""
        return {
            'transaction_id': self.transaction_id,
            'customer_id': self.customer_id,
            'amount': str(self.amount),
            'timestamp': self.timestamp.isoformat(),
            'merchant': self.merchant,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'location': self.location
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'TransactionRecord':
        """Create transaction from dictionary."""
        return TransactionRecord(
            transaction_id=data['transaction_id'],
            customer_id=data['customer_id'],
            amount=Decimal(str(data['amount'])),
            timestamp=datetime.fromisoformat(data['timestamp']),
            merchant=data['merchant'],
            transaction_type=data['transaction_type'],
            category=data.get('category'),
            location=data.get('location')
        )

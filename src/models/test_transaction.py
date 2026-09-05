"""
Unit tests for TransactionRecord dataclass.
"""

import unittest
from datetime import datetime
from decimal import Decimal
from src.models.transaction import TransactionRecord


class TestTransactionRecord(unittest.TestCase):
    """Test cases for TransactionRecord dataclass."""
    
    def test_create_transaction_with_all_fields(self):
        """Test creating a transaction with all required and optional fields."""
        txn = TransactionRecord(
            transaction_id="TXN001",
            customer_id="CUST001",
            amount=Decimal("1500.50"),
            timestamp=datetime(2024, 1, 15, 14, 30, 0),
            merchant="Test Merchant",
            transaction_type="purchase",
            category="retail",
            location="New York, NY"
        )
        
        self.assertEqual(txn.transaction_id, "TXN001")
        self.assertEqual(txn.customer_id, "CUST001")
        self.assertEqual(txn.amount, Decimal("1500.50"))
        self.assertEqual(txn.merchant, "Test Merchant")
        self.assertEqual(txn.transaction_type, "purchase")
        self.assertEqual(txn.category, "retail")
        self.assertEqual(txn.location, "New York, NY")
    
    def test_create_transaction_without_optional_fields(self):
        """Test creating a transaction without optional fields."""
        txn = TransactionRecord(
            transaction_id="TXN002",
            customer_id="CUST002",
            amount=Decimal("500.00"),
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            merchant="Another Merchant",
            transaction_type="transfer"
        )
        
        self.assertIsNone(txn.category)
        self.assertIsNone(txn.location)
    
    def test_to_dict_conversion(self):
        """Test converting transaction to dictionary."""
        txn = TransactionRecord(
            transaction_id="TXN003",
            customer_id="CUST003",
            amount=Decimal("2500.75"),
            timestamp=datetime(2024, 1, 15, 16, 45, 30),
            merchant="Test Store",
            transaction_type="purchase",
            category="groceries",
            location="Boston, MA"
        )
        
        result = txn.to_dict()
        
        self.assertEqual(result['transaction_id'], "TXN003")
        self.assertEqual(result['customer_id'], "CUST003")
        self.assertEqual(result['amount'], "2500.75")
        self.assertEqual(result['timestamp'], "2024-01-15T16:45:30")
        self.assertEqual(result['merchant'], "Test Store")
        self.assertEqual(result['transaction_type'], "purchase")
        self.assertEqual(result['category'], "groceries")
        self.assertEqual(result['location'], "Boston, MA")
    
    def test_from_dict_conversion(self):
        """Test creating transaction from dictionary."""
        data = {
            'transaction_id': "TXN004",
            'customer_id': "CUST004",
            'amount': "3000.00",
            'timestamp': "2024-01-16T09:30:00",
            'merchant': "Online Store",
            'transaction_type': "purchase",
            'category': "electronics",
            'location': "San Francisco, CA"
        }
        
        txn = TransactionRecord.from_dict(data)
        
        self.assertEqual(txn.transaction_id, "TXN004")
        self.assertEqual(txn.customer_id, "CUST004")
        self.assertEqual(txn.amount, Decimal("3000.00"))
        self.assertEqual(txn.timestamp, datetime(2024, 1, 16, 9, 30, 0))
        self.assertEqual(txn.merchant, "Online Store")
        self.assertEqual(txn.transaction_type, "purchase")
        self.assertEqual(txn.category, "electronics")
        self.assertEqual(txn.location, "San Francisco, CA")
    
    def test_from_dict_without_optional_fields(self):
        """Test creating transaction from dictionary without optional fields."""
        data = {
            'transaction_id': "TXN005",
            'customer_id': "CUST005",
            'amount': "750.25",
            'timestamp': "2024-01-17T12:00:00",
            'merchant': "Gas Station",
            'transaction_type': "purchase"
        }
        
        txn = TransactionRecord.from_dict(data)
        
        self.assertEqual(txn.transaction_id, "TXN005")
        self.assertIsNone(txn.category)
        self.assertIsNone(txn.location)
    
    def test_round_trip_conversion(self):
        """Test converting to dict and back preserves data."""
        original = TransactionRecord(
            transaction_id="TXN006",
            customer_id="CUST006",
            amount=Decimal("1234.56"),
            timestamp=datetime(2024, 1, 18, 15, 20, 45),
            merchant="Test Merchant",
            transaction_type="transfer",
            category="banking",
            location="Chicago, IL"
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = TransactionRecord.from_dict(data)
        
        # Verify all fields match
        self.assertEqual(original.transaction_id, restored.transaction_id)
        self.assertEqual(original.customer_id, restored.customer_id)
        self.assertEqual(original.amount, restored.amount)
        self.assertEqual(original.timestamp, restored.timestamp)
        self.assertEqual(original.merchant, restored.merchant)
        self.assertEqual(original.transaction_type, restored.transaction_type)
        self.assertEqual(original.category, restored.category)
        self.assertEqual(original.location, restored.location)


if __name__ == '__main__':
    unittest.main()

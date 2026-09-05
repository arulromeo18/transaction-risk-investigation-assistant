"""
Large Transfer Detector for fraud pattern detection.

This module detects transactions with unusually large amounts that may
indicate account takeover or money laundering.

Validates: Requirements 2.2, 2.8
"""

from decimal import Decimal
from typing import Optional

from src.detectors.base import FraudDetector
from src.models.transaction import TransactionRecord
from src.models.customer import CustomerBaseline
from src.models.detection import FraudPattern


class LargeTransferDetector(FraudDetector):
    """
    Detects large transfers that exceed configured thresholds.
    
    This detector identifies transactions with amounts that may indicate
    fraud or money laundering activity. Two risk levels are supported:
    - High risk: Transactions >= $10,000
    - Medium risk: Transactions >= $5,000
    
    Validates: Requirements 2.2, 2.8
    """
    
    # Configuration thresholds
    HIGH_RISK_THRESHOLD = Decimal('10000')
    MEDIUM_RISK_THRESHOLD = Decimal('5000')
    
    @property
    def pattern_name(self) -> str:
        """Return the human-readable name of this fraud pattern."""
        return "Large Transfer"
    
    @property
    def pattern_type(self) -> str:
        """Return the type identifier for this pattern."""
        return "large_transfer"
    
    def detect(
        self,
        transactions: list[TransactionRecord],
        baseline: Optional[CustomerBaseline]
    ) -> Optional[FraudPattern]:
        """
        Detect large transfer patterns in transaction data.
        
        Analyzes all transactions to find amounts that exceed the medium
        risk threshold ($5,000). Risk scoring is based on the maximum
        transaction amount found.
        
        Args:
            transactions: List of transaction records to analyze
            baseline: Optional customer baseline (not used by this detector)
        
        Returns:
            FraudPattern if large transactions are detected, None otherwise
        """
        large_transactions = []
        max_amount = Decimal('0')
        
        for txn in transactions:
            if txn.amount >= self.MEDIUM_RISK_THRESHOLD:
                large_transactions.append(txn.transaction_id)
                max_amount = max(max_amount, txn.amount)
        
        if not large_transactions:
            return None
        
        # Calculate risk score based on maximum amount
        if max_amount >= self.HIGH_RISK_THRESHOLD:
            risk_score = 90
        else:
            risk_score = 70
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected {len(large_transactions)} large transaction(s) with maximum amount ${max_amount}",
            triggered_transactions=large_transactions,
            details={
                'max_amount': str(max_amount),
                'transaction_count': len(large_transactions),
                'threshold': str(self.MEDIUM_RISK_THRESHOLD)
            }
        )

"""
Structuring Detector for fraud pattern detection.

This module detects structuring patterns where transactions appear designed
to avoid reporting thresholds (typically $10,000 for currency reporting).

Validates: Requirements 2.6, 2.8
"""

from datetime import timedelta
from decimal import Decimal
from typing import Optional

from src.detectors.base import FraudDetector
from src.models.transaction import TransactionRecord
from src.models.customer import CustomerBaseline
from src.models.detection import FraudPattern


class StructuringDetector(FraudDetector):
    """
    Detects structuring patterns - multiple transactions just under threshold.
    
    This detector identifies patterns where multiple transactions appear
    designed to avoid reporting thresholds. It looks for:
    - Multiple transactions just below $10,000 (common reporting threshold)
    - Transactions occurring within a short time period (7 days)
    
    Risk scoring is based on the total amount and number of transactions:
    - Higher risk if total exceeds threshold significantly
    - Standard risk otherwise
    
    Validates: Requirements 2.6, 2.8
    """
    
    STRUCTURING_THRESHOLD = Decimal('10000')
    JUST_BELOW_MARGIN = Decimal('1000')  # Within $1000 of threshold
    MIN_TRANSACTIONS = 3
    TIME_WINDOW_DAYS = 7
    
    @property
    def pattern_name(self) -> str:
        """Return the human-readable name of this fraud pattern."""
        return "Structuring Pattern"
    
    @property
    def pattern_type(self) -> str:
        """Return the type identifier for this pattern."""
        return "structuring"
    
    def detect(
        self,
        transactions: list[TransactionRecord],
        baseline: Optional[CustomerBaseline]
    ) -> Optional[FraudPattern]:
        """
        Detect structuring patterns in transaction data.
        
        Analyzes transactions to find multiple amounts just below the $10,000
        threshold occurring within a short time window. This pattern may
        indicate attempts to avoid currency reporting requirements.
        
        Args:
            transactions: List of transaction records to analyze
            baseline: Optional customer baseline (not used by this detector)
        
        Returns:
            FraudPattern if structuring pattern is detected, None otherwise
        """
        # Find transactions just below threshold
        suspicious_txns = []
        for txn in transactions:
            lower_bound = self.STRUCTURING_THRESHOLD - self.JUST_BELOW_MARGIN
            if lower_bound <= txn.amount < self.STRUCTURING_THRESHOLD:
                suspicious_txns.append(txn)
        
        if len(suspicious_txns) < self.MIN_TRANSACTIONS:
            return None
        
        # Check if they occur within time window
        suspicious_txns.sort(key=lambda t: t.timestamp)
        
        # Find clusters within time window
        max_cluster = []
        for i in range(len(suspicious_txns)):
            window_start = suspicious_txns[i].timestamp
            window_end = window_start + timedelta(days=self.TIME_WINDOW_DAYS)
            
            cluster = []
            for j in range(i, len(suspicious_txns)):
                if suspicious_txns[j].timestamp <= window_end:
                    cluster.append(suspicious_txns[j])
            
            if len(cluster) > len(max_cluster):
                max_cluster = cluster
        
        if len(max_cluster) < self.MIN_TRANSACTIONS:
            return None
        
        total_amount = sum(t.amount for t in max_cluster)
        
        # Higher risk if total exceeds threshold significantly
        risk_score = 80 if total_amount >= self.STRUCTURING_THRESHOLD * 2 else 70
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected {len(max_cluster)} transactions just below ${self.STRUCTURING_THRESHOLD} threshold, totaling ${total_amount}",
            triggered_transactions=[t.transaction_id for t in max_cluster],
            details={
                'transaction_count': len(max_cluster),
                'total_amount': str(total_amount),
                'threshold': str(self.STRUCTURING_THRESHOLD),
                'time_window_days': self.TIME_WINDOW_DAYS
            }
        )

"""
Burst Payment Detector for fraud pattern detection.

This module detects rapid sequences of transactions that may indicate
card testing or automated fraud.

Validates: Requirements 2.3, 2.8
"""

from datetime import timedelta
from typing import Optional

from src.detectors.base import FraudDetector
from src.models.transaction import TransactionRecord
from src.models.customer import CustomerBaseline
from src.models.detection import FraudPattern


class BurstPaymentDetector(FraudDetector):
    """
    Detects burst payment patterns (many transactions in a short time).
    
    This detector uses a sliding window approach to identify rapid sequences
    of transactions that may indicate card testing, automated fraud, or
    compromised account activity. Two risk levels are supported:
    - High risk: >= 10 transactions in 1 hour
    - Medium risk: >= 5 transactions in 1 hour
    
    Validates: Requirements 2.3, 2.8
    """
    
    HIGH_RISK_COUNT = 10
    MEDIUM_RISK_COUNT = 5
    TIME_WINDOW_HOURS = 1
    
    @property
    def pattern_name(self) -> str:
        """Return the human-readable name of this fraud pattern."""
        return "Burst Payment Pattern"
    
    @property
    def pattern_type(self) -> str:
        """Return the type identifier for this pattern."""
        return "burst_payment"
    
    def detect(
        self,
        transactions: list[TransactionRecord],
        baseline: Optional[CustomerBaseline]
    ) -> Optional[FraudPattern]:
        """
        Detect burst payment patterns using sliding window analysis.
        
        Analyzes transaction timestamps to identify windows of time where
        transaction frequency exceeds normal levels. Uses a sliding window
        approach to find the maximum burst count.
        
        Args:
            transactions: List of transaction records to analyze
            baseline: Optional customer baseline (not used by this detector)
        
        Returns:
            FraudPattern if burst payment pattern is detected, None otherwise
        """
        if len(transactions) < self.MEDIUM_RISK_COUNT:
            return None
        
        # Sort transactions by timestamp
        sorted_txns = sorted(transactions, key=lambda t: t.timestamp)
        
        max_burst_count = 0
        max_burst_transactions = []
        
        # Sliding window approach
        for i in range(len(sorted_txns)):
            window_start = sorted_txns[i].timestamp
            window_end = window_start + timedelta(hours=self.TIME_WINDOW_HOURS)
            
            # Count transactions in window
            burst_txns = []
            for j in range(i, len(sorted_txns)):
                if sorted_txns[j].timestamp <= window_end:
                    burst_txns.append(sorted_txns[j])
                else:
                    break
            
            if len(burst_txns) > max_burst_count:
                max_burst_count = len(burst_txns)
                max_burst_transactions = [t.transaction_id for t in burst_txns]
        
        if max_burst_count < self.MEDIUM_RISK_COUNT:
            return None
        
        # Calculate risk score based on burst count
        if max_burst_count >= self.HIGH_RISK_COUNT:
            risk_score = 85
        else:
            risk_score = 65
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected burst of {max_burst_count} transactions within {self.TIME_WINDOW_HOURS} hour(s)",
            triggered_transactions=max_burst_transactions,
            details={
                'burst_count': max_burst_count,
                'time_window_hours': self.TIME_WINDOW_HOURS,
                'threshold': self.MEDIUM_RISK_COUNT
            }
        )

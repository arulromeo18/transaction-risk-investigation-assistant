"""
Odd-Hours Activity Detector for fraud pattern detection.

This module detects transactions occurring outside normal business hours
that may indicate compromised accounts.

Validates: Requirements 2.4, 2.8
"""

from typing import Optional

from src.detectors.base import FraudDetector
from src.models.transaction import TransactionRecord
from src.models.customer import CustomerBaseline
from src.models.detection import FraudPattern


class OddHoursDetector(FraudDetector):
    """
    Detects transactions during unusual hours (late night/early morning).
    
    This detector identifies transactions that occur during hours when
    legitimate activity is less common. Odd hours are defined as 11 PM - 6 AM
    (23:00 - 06:00). Risk increases with multiple odd-hour transactions.
    Two risk levels are supported:
    - High risk: >= 5 transactions during odd hours
    - Medium risk: >= 2 transactions during odd hours
    
    Validates: Requirements 2.4, 2.8
    """
    
    ODD_HOUR_START = 23  # 11 PM
    ODD_HOUR_END = 6     # 6 AM
    HIGH_RISK_COUNT = 5
    MEDIUM_RISK_COUNT = 2
    
    @property
    def pattern_name(self) -> str:
        """Return the human-readable name of this fraud pattern."""
        return "Odd-Hours Activity"
    
    @property
    def pattern_type(self) -> str:
        """Return the type identifier for this pattern."""
        return "odd_hours"
    
    def detect(
        self,
        transactions: list[TransactionRecord],
        baseline: Optional[CustomerBaseline]
    ) -> Optional[FraudPattern]:
        """
        Detect odd-hours activity in transaction data.
        
        Analyzes transaction timestamps to identify activity during unusual
        hours (11 PM - 6 AM). Counts the number of transactions occurring
        during these hours and assigns risk scores accordingly.
        
        Args:
            transactions: List of transaction records to analyze
            baseline: Optional customer baseline (not used by this detector)
        
        Returns:
            FraudPattern if odd-hours activity is detected, None otherwise
        """
        odd_hour_transactions = []
        
        for txn in transactions:
            hour = txn.timestamp.hour
            # Check if in odd hours range (23:00 - 06:00)
            if hour >= self.ODD_HOUR_START or hour < self.ODD_HOUR_END:
                odd_hour_transactions.append(txn.transaction_id)
        
        if len(odd_hour_transactions) < self.MEDIUM_RISK_COUNT:
            return None
        
        # Calculate risk score based on count
        if len(odd_hour_transactions) >= self.HIGH_RISK_COUNT:
            risk_score = 75
        else:
            risk_score = 55
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected {len(odd_hour_transactions)} transaction(s) during odd hours (11 PM - 6 AM)",
            triggered_transactions=odd_hour_transactions,
            details={
                'odd_hour_count': len(odd_hour_transactions),
                'odd_hour_range': f"{self.ODD_HOUR_START}:00-{self.ODD_HOUR_END}:00",
                'threshold': self.MEDIUM_RISK_COUNT
            }
        )

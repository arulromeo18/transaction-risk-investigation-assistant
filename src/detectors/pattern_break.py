"""
Pattern Break Detector for fraud pattern detection.

This module detects deviations from a customer's normal behavior baseline
that may indicate account compromise or fraudulent activity.

Validates: Requirements 2.5, 2.8
"""

from decimal import Decimal
from typing import Optional

from src.detectors.base import FraudDetector
from src.models.transaction import TransactionRecord
from src.models.customer import CustomerBaseline
from src.models.detection import FraudPattern


class PatternBreakDetector(FraudDetector):
    """
    Detects pattern breaks - deviations from customer baseline behavior.
    
    This detector compares transactions against a customer's historical
    baseline to identify unusual activity. It checks for:
    - Unusual transaction amounts (> 3x median baseline)
    - Unusual merchants (not in common merchant list)
    - Unusual transaction types (not in common types)
    
    Risk scoring is proportional to the number of pattern breaks detected,
    with scores ranging from 50-80.
    
    Validates: Requirements 2.5, 2.8
    """
    
    AMOUNT_MULTIPLIER = 3.0  # 3x median is considered unusual
    
    @property
    def pattern_name(self) -> str:
        """Return the human-readable name of this fraud pattern."""
        return "Pattern Break"
    
    @property
    def pattern_type(self) -> str:
        """Return the type identifier for this pattern."""
        return "pattern_break"
    
    def detect(
        self,
        transactions: list[TransactionRecord],
        baseline: Optional[CustomerBaseline]
    ) -> Optional[FraudPattern]:
        """
        Detect pattern breaks by comparing against customer baseline.
        
        Analyzes transactions for deviations from normal behavior patterns
        established in the customer baseline. Requires a baseline to operate.
        
        Args:
            transactions: List of transaction records to analyze
            baseline: Customer baseline statistics for comparison (required)
        
        Returns:
            FraudPattern if pattern breaks are detected, None otherwise
        """
        if not baseline:
            return None  # Need baseline for comparison
        
        unusual_transactions = []
        break_reasons = []
        
        for txn in transactions:
            # Check amount deviation (amounts exceeding 3x median)
            if txn.amount > baseline.median_transaction_amount * Decimal(str(self.AMOUNT_MULTIPLIER)):
                unusual_transactions.append(txn.transaction_id)
                break_reasons.append(f"Unusual amount: ${txn.amount}")
                continue
            
            # Check merchant deviation (new merchants not in baseline)
            if baseline.common_merchants and txn.merchant not in baseline.common_merchants:
                unusual_transactions.append(txn.transaction_id)
                break_reasons.append(f"New merchant: {txn.merchant}")
                continue
            
            # Check transaction type deviation (unusual types)
            if baseline.common_transaction_types and txn.transaction_type not in baseline.common_transaction_types:
                unusual_transactions.append(txn.transaction_id)
                break_reasons.append(f"Unusual type: {txn.transaction_type}")
        
        if not unusual_transactions:
            return None
        
        # Risk score based on number of breaks (50-80 range)
        risk_score = min(80, 50 + len(unusual_transactions) * 5)
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected {len(unusual_transactions)} transaction(s) deviating from customer baseline",
            triggered_transactions=unusual_transactions,
            details={
                'break_count': len(unusual_transactions),
                'break_reasons': break_reasons[:5],  # Limit to first 5 for readability
                'baseline_median_amount': str(baseline.median_transaction_amount)
            }
        )

"""
Velocity Detector for fraud pattern detection.

This module detects rapid acceleration in transaction frequency or amounts
that may indicate fraudulent activity or account compromise.

Validates: Requirements 2.7, 2.8
"""

from datetime import timedelta
from decimal import Decimal
from typing import Optional

from src.detectors.base import FraudDetector
from src.models.transaction import TransactionRecord
from src.models.customer import CustomerBaseline
from src.models.detection import FraudPattern


class VelocityDetector(FraudDetector):
    """
    Detects velocity patterns - rapid acceleration in transaction activity.
    
    This detector compares recent activity to historical baseline to identify
    sudden increases that may indicate fraud. It analyzes:
    - Transaction frequency acceleration (transactions per day)
    - Transaction amount acceleration (total amount per day)
    
    Acceleration is measured by comparing recent activity (last 7 days) to
    historical activity (previous 23 days). Risk scoring is based on the
    magnitude of acceleration detected.
    
    Validates: Requirements 2.7, 2.8
    """
    
    RECENT_WINDOW_DAYS = 7
    HISTORICAL_WINDOW_DAYS = 30
    VELOCITY_MULTIPLIER = 2.5  # 2.5x increase is considered suspicious
    
    @property
    def pattern_name(self) -> str:
        """Return the human-readable name of this fraud pattern."""
        return "Velocity Pattern"
    
    @property
    def pattern_type(self) -> str:
        """Return the type identifier for this pattern."""
        return "velocity"
    
    def detect(
        self,
        transactions: list[TransactionRecord],
        baseline: Optional[CustomerBaseline]
    ) -> Optional[FraudPattern]:
        """
        Detect velocity patterns by comparing recent to historical activity.
        
        Analyzes transaction frequency and amounts to identify rapid
        acceleration that deviates from normal patterns. Requires sufficient
        transaction history (at least 10 transactions).
        
        Args:
            transactions: List of transaction records to analyze
            baseline: Optional customer baseline (not used by this detector)
        
        Returns:
            FraudPattern if velocity acceleration is detected, None otherwise
        """
        if len(transactions) < 10:
            return None  # Need sufficient history
        
        # Sort by timestamp
        sorted_txns = sorted(transactions, key=lambda t: t.timestamp)
        
        # Get most recent timestamp
        latest_timestamp = sorted_txns[-1].timestamp
        
        # Split into recent and historical windows
        recent_cutoff = latest_timestamp - timedelta(days=self.RECENT_WINDOW_DAYS)
        historical_cutoff = latest_timestamp - timedelta(days=self.HISTORICAL_WINDOW_DAYS)
        
        recent_txns = [t for t in sorted_txns if t.timestamp >= recent_cutoff]
        historical_txns = [t for t in sorted_txns if historical_cutoff <= t.timestamp < recent_cutoff]
        
        if not historical_txns:
            return None  # Need historical baseline
        
        # Calculate velocities
        recent_count = len(recent_txns)
        recent_amount = sum(t.amount for t in recent_txns)
        
        historical_count = len(historical_txns)
        historical_amount = sum(t.amount for t in historical_txns)
        
        # Normalize by time period
        recent_daily_count = recent_count / self.RECENT_WINDOW_DAYS
        historical_daily_count = historical_count / (self.HISTORICAL_WINDOW_DAYS - self.RECENT_WINDOW_DAYS)
        
        recent_daily_amount = recent_amount / self.RECENT_WINDOW_DAYS
        historical_daily_amount = historical_amount / (self.HISTORICAL_WINDOW_DAYS - self.RECENT_WINDOW_DAYS)
        
        # Check for acceleration
        count_acceleration = recent_daily_count / historical_daily_count if historical_daily_count > 0 else 0
        amount_acceleration = float(recent_daily_amount / historical_daily_amount) if historical_daily_amount > 0 else 0
        
        if count_acceleration < self.VELOCITY_MULTIPLIER and amount_acceleration < self.VELOCITY_MULTIPLIER:
            return None
        
        # Risk score based on acceleration magnitude
        max_acceleration = max(count_acceleration, amount_acceleration)
        risk_score = min(85, int(60 + (max_acceleration - self.VELOCITY_MULTIPLIER) * 10))
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected {max_acceleration:.1f}x acceleration in transaction activity",
            triggered_transactions=[t.transaction_id for t in recent_txns],
            details={
                'count_acceleration': f"{count_acceleration:.2f}x",
                'amount_acceleration': f"{amount_acceleration:.2f}x",
                'recent_daily_count': f"{recent_daily_count:.1f}",
                'historical_daily_count': f"{historical_daily_count:.1f}"
            }
        )

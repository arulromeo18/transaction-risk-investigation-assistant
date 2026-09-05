"""
Data models for fraud detection results.

This module defines the data structures used to represent fraud detection
findings, including individual fraud patterns and complete detection results.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FraudPattern:
    """
    Represents a detected fraud pattern.
    
    Each FraudPattern instance captures a single type of suspicious behavior
    detected in a customer's transaction history, along with supporting details
    and a risk score.
    
    Validates: Requirements 2.8, 3.2
    
    Attributes:
        pattern_name: Human-readable name of the fraud pattern
                     (e.g., "Large Transfer", "Burst Payment Pattern")
        pattern_type: Type identifier for the pattern
                     (e.g., "large_transfer", "burst_payment")
        risk_score: Numerical risk score from 0-100, where higher values
                   indicate greater risk
        description: Human-readable description of what was detected,
                    including key metrics and context
        triggered_transactions: List of transaction IDs that triggered
                               this pattern detection
        details: Dictionary containing pattern-specific details such as
                thresholds, counts, amounts, and other relevant metrics
    """
    pattern_name: str
    pattern_type: str
    risk_score: int  # 0-100
    description: str
    triggered_transactions: list[str]
    details: dict
    
    def to_dict(self) -> dict:
        """
        Convert fraud pattern to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation suitable for API responses
        """
        return {
            'pattern_name': self.pattern_name,
            'pattern_type': self.pattern_type,
            'risk_score': self.risk_score,
            'description': self.description,
            'triggered_transactions': self.triggered_transactions,
            'details': self.details
        }


@dataclass
class DetectionResult:
    """
    Complete fraud detection results for a customer.
    
    This class aggregates all detected fraud patterns and provides an
    overall risk assessment along with optional AI-generated narrative
    and performance metrics.
    
    Validates: Requirements 2.8, 3.2
    
    Attributes:
        customer_id: Customer identifier
        detected_patterns: List of all fraud patterns detected in the
                          customer's transaction history
        overall_risk_score: Aggregate risk score across all patterns.
                           Calculated as the maximum of individual pattern
                           risk scores (0-100 scale)
        investigation_narrative: Optional AI-generated narrative describing
                                the findings and recommended actions.
                                May be None if Gemini API is unavailable
                                or times out
        processing_time_ms: Time taken for analysis in milliseconds,
                           measured from the start of rule engine processing
    """
    customer_id: str
    detected_patterns: list[FraudPattern]
    overall_risk_score: int
    investigation_narrative: Optional[str]
    processing_time_ms: int
    
    def to_dict(self) -> dict:
        """
        Convert detection result to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation suitable for API responses
        """
        return {
            'customer_id': self.customer_id,
            'detected_patterns': [p.to_dict() for p in self.detected_patterns],
            'overall_risk_score': self.overall_risk_score,
            'investigation_narrative': self.investigation_narrative,
            'processing_time_ms': self.processing_time_ms
        }

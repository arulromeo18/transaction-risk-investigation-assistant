"""
Abstract base class for fraud pattern detectors.

This module defines the FraudDetector interface that all fraud pattern
detectors must implement. Each detector analyzes transactions for a
specific fraud pattern and returns detection results.
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.transaction import TransactionRecord
    from src.models.customer import CustomerBaseline
    from src.models.detection import FraudPattern


class FraudDetector(ABC):
    """
    Abstract base class for fraud pattern detectors.
    
    Each detector implements one specific fraud pattern detection algorithm.
    Detectors are deterministic and stateless - they analyze transactions
    based solely on the provided data and fixed rule definitions.
    
    Validates: Requirements 2.8
    """
    
    @abstractmethod
    def detect(
        self,
        transactions: list['TransactionRecord'],
        baseline: Optional['CustomerBaseline']
    ) -> Optional['FraudPattern']:
        """
        Analyze transactions for fraud pattern.
        
        This method examines the provided transactions and determines whether
        they match the fraud pattern this detector is designed to identify.
        
        Args:
            transactions: List of transaction records to analyze
            baseline: Optional customer baseline statistics for context.
                     Used by pattern break detector to compare against
                     normal behavior. May be None if baseline is not available.
        
        Returns:
            FraudPattern object if the pattern is detected, None otherwise
        """
        pass
    
    @property
    @abstractmethod
    def pattern_name(self) -> str:
        """
        Return the human-readable name of this fraud pattern.
        
        Returns:
            Pattern name (e.g., "Large Transfer", "Burst Payment Pattern")
        """
        pass
    
    @property
    @abstractmethod
    def pattern_type(self) -> str:
        """
        Return the type identifier for this pattern.
        
        This identifier is used in API responses and for pattern categorization.
        Should be lowercase with underscores (e.g., "large_transfer", "burst_payment").
        
        Returns:
            Pattern type identifier
        """
        pass

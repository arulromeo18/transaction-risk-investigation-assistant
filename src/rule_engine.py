"""
Main rule engine for fraud detection.

This module implements the RuleEngine class that orchestrates fraud detection
by running multiple fraud pattern detectors and aggregating their results.
"""

import time
from typing import TYPE_CHECKING

from src.models.detection import DetectionResult

if TYPE_CHECKING:
    from src.detectors.base import FraudDetector
    from src.models.customer import CustomerProfile


class RuleEngine:
    """
    Main rule engine that orchestrates fraud detection.
    
    The RuleEngine processes customer transaction data through a pipeline of
    independent fraud pattern detectors. Each detector runs deterministically
    and independently, analyzing transactions for specific fraud patterns.
    
    The engine aggregates results from all detectors, calculates an overall
    risk score, and tracks processing time for performance monitoring.
    
    Validates: Requirements 2.8, 2.9
    """
    
    def __init__(self):
        """
        Initialize the rule engine.
        
        Creates an empty detector list and calls _register_detectors() to
        populate it with all available fraud pattern detectors.
        """
        self.detectors: list['FraudDetector'] = []
        self._register_detectors()
    
    def _register_detectors(self):
        """
        Register all fraud pattern detectors.
        
        This method is called during initialization to set up the list of
        detectors that will be used for fraud detection. Currently initialized
        as empty - detectors will be added in subsequent tasks as they are
        implemented.
        
        Future detectors to be registered:
        - LargeTransferDetector
        - BurstPaymentDetector
        - OddHoursDetector
        - PatternBreakDetector
        - StructuringDetector
        - VelocityDetector
        """
        # Detectors will be imported and registered here as they are implemented
        # Example (to be uncommented when detectors are available):
        # from src.detectors.large_transfer import LargeTransferDetector
        # from src.detectors.burst_payment import BurstPaymentDetector
        # from src.detectors.odd_hours import OddHoursDetector
        # from src.detectors.pattern_break import PatternBreakDetector
        # from src.detectors.structuring import StructuringDetector
        # from src.detectors.velocity import VelocityDetector
        #
        # self.detectors = [
        #     LargeTransferDetector(),
        #     BurstPaymentDetector(),
        #     OddHoursDetector(),
        #     PatternBreakDetector(),
        #     StructuringDetector(),
        #     VelocityDetector()
        # ]
        pass
    
    def analyze(self, profile: 'CustomerProfile') -> DetectionResult:
        """
        Analyze customer profile for fraud patterns.
        
        This method runs all registered fraud pattern detectors against the
        customer's transaction history. It collects detection results from
        each detector, calculates an overall risk score, and measures the
        total processing time.
        
        The overall risk score is calculated as the maximum of individual
        pattern risk scores. This approach ensures that a single high-risk
        pattern appropriately elevates the overall risk assessment.
        
        Args:
            profile: Customer profile containing transaction history and
                    optional baseline statistics
        
        Returns:
            DetectionResult containing:
            - All detected fraud patterns
            - Overall risk score (max of individual scores)
            - Processing time in milliseconds
            - investigation_narrative set to None (to be populated later
              by Gemini integration)
        
        Validates: Requirements 2.8, 2.9
        """
        start_time = time.time()
        
        detected_patterns = []
        
        # Run each detector
        for detector in self.detectors:
            pattern = detector.detect(profile.transactions, profile.baseline_stats)
            if pattern:
                detected_patterns.append(pattern)
        
        # Calculate overall risk score as maximum of individual scores
        # If no patterns detected, risk score is 0
        overall_risk = max(
            [p.risk_score for p in detected_patterns],
            default=0
        )
        
        # Calculate processing time in milliseconds
        processing_time = int((time.time() - start_time) * 1000)
        
        return DetectionResult(
            customer_id=profile.customer_id,
            detected_patterns=detected_patterns,
            overall_risk_score=overall_risk,
            investigation_narrative=None,  # Added later by Gemini integration
            processing_time_ms=processing_time
        )

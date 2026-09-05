"""
Fraud detector package.

This package contains all fraud pattern detector implementations.
Each detector analyzes transactions for a specific fraud pattern.
"""

from src.detectors.base import FraudDetector
from src.detectors.large_transfer import LargeTransferDetector
from src.detectors.burst_payment import BurstPaymentDetector
from src.detectors.odd_hours import OddHoursDetector
from src.detectors.pattern_break import PatternBreakDetector
from src.detectors.structuring import StructuringDetector
from src.detectors.velocity import VelocityDetector

__all__ = [
    'FraudDetector',
    'LargeTransferDetector',
    'BurstPaymentDetector',
    'OddHoursDetector',
    'PatternBreakDetector',
    'StructuringDetector',
    'VelocityDetector',
]

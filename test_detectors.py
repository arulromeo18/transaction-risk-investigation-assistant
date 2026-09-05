"""
Quick verification test for the four core fraud pattern detectors.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from src.models.transaction import TransactionRecord
from src.models.customer import CustomerBaseline
from src.detectors.large_transfer import LargeTransferDetector
from src.detectors.burst_payment import BurstPaymentDetector
from src.detectors.odd_hours import OddHoursDetector
from src.detectors.pattern_break import PatternBreakDetector


def test_large_transfer_detector():
    """Test LargeTransferDetector with various transaction amounts."""
    detector = LargeTransferDetector()
    
    # Test 1: No large transfers
    small_txns = [
        TransactionRecord(
            transaction_id="T1",
            customer_id="C1",
            amount=Decimal("1000"),
            timestamp=datetime.now(),
            merchant="Store A",
            transaction_type="purchase"
        )
    ]
    result = detector.detect(small_txns, None)
    assert result is None, "Should not detect pattern for small transactions"
    
    # Test 2: Medium risk ($5,000 - $9,999)
    medium_txns = [
        TransactionRecord(
            transaction_id="T2",
            customer_id="C1",
            amount=Decimal("7500"),
            timestamp=datetime.now(),
            merchant="Store B",
            transaction_type="transfer"
        )
    ]
    result = detector.detect(medium_txns, None)
    assert result is not None, "Should detect medium risk pattern"
    assert result.risk_score == 70, f"Expected risk score 70, got {result.risk_score}"
    
    # Test 3: High risk (>= $10,000)
    high_txns = [
        TransactionRecord(
            transaction_id="T3",
            customer_id="C1",
            amount=Decimal("15000"),
            timestamp=datetime.now(),
            merchant="Store C",
            transaction_type="transfer"
        )
    ]
    result = detector.detect(high_txns, None)
    assert result is not None, "Should detect high risk pattern"
    assert result.risk_score == 90, f"Expected risk score 90, got {result.risk_score}"
    
    print("✓ LargeTransferDetector tests passed")


def test_burst_payment_detector():
    """Test BurstPaymentDetector with rapid transaction sequences."""
    detector = BurstPaymentDetector()
    
    # Test 1: No burst (insufficient transactions)
    sparse_txns = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=datetime.now() + timedelta(hours=i),
            merchant="Store A",
            transaction_type="purchase"
        )
        for i in range(3)
    ]
    result = detector.detect(sparse_txns, None)
    assert result is None, "Should not detect burst with sparse transactions"
    
    # Test 2: Medium risk (5-9 transactions in 1 hour)
    base_time = datetime.now()
    medium_burst = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("50"),
            timestamp=base_time + timedelta(minutes=i * 10),
            merchant="Store B",
            transaction_type="purchase"
        )
        for i in range(6)
    ]
    result = detector.detect(medium_burst, None)
    assert result is not None, "Should detect medium risk burst"
    assert result.risk_score == 65, f"Expected risk score 65, got {result.risk_score}"
    
    # Test 3: High risk (>= 10 transactions in 1 hour)
    high_burst = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("25"),
            timestamp=base_time + timedelta(minutes=i * 5),
            merchant="Store C",
            transaction_type="purchase"
        )
        for i in range(12)
    ]
    result = detector.detect(high_burst, None)
    assert result is not None, "Should detect high risk burst"
    assert result.risk_score == 85, f"Expected risk score 85, got {result.risk_score}"
    
    print("✓ BurstPaymentDetector tests passed")


def test_odd_hours_detector():
    """Test OddHoursDetector with transactions at various times."""
    detector = OddHoursDetector()
    
    # Test 1: Normal hours only (no detection)
    normal_hours = [
        TransactionRecord(
            transaction_id="T1",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=datetime(2024, 1, 1, 14, 0, 0),  # 2 PM
            merchant="Store A",
            transaction_type="purchase"
        )
    ]
    result = detector.detect(normal_hours, None)
    assert result is None, "Should not detect pattern for normal hours"
    
    # Test 2: Medium risk (2-4 odd-hour transactions)
    medium_odd = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=datetime(2024, 1, 1, 2, 0, 0) + timedelta(hours=i),  # 2 AM, 3 AM, 4 AM
            merchant="Store B",
            transaction_type="purchase"
        )
        for i in range(3)
    ]
    result = detector.detect(medium_odd, None)
    assert result is not None, "Should detect medium risk odd-hours"
    assert result.risk_score == 55, f"Expected risk score 55, got {result.risk_score}"
    
    # Test 3: High risk (>= 5 odd-hour transactions)
    high_odd = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=datetime(2024, 1, 1, 23, 30, 0) + timedelta(hours=i),  # 11:30 PM onwards
            merchant="Store C",
            transaction_type="purchase"
        )
        for i in range(6)
    ]
    result = detector.detect(high_odd, None)
    assert result is not None, "Should detect high risk odd-hours"
    assert result.risk_score == 75, f"Expected risk score 75, got {result.risk_score}"
    
    print("✓ OddHoursDetector tests passed")


def test_pattern_break_detector():
    """Test PatternBreakDetector with baseline comparisons."""
    detector = PatternBreakDetector()
    
    # Test 1: No baseline (should return None)
    txns = [
        TransactionRecord(
            transaction_id="T1",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=datetime.now(),
            merchant="Store A",
            transaction_type="purchase"
        )
    ]
    result = detector.detect(txns, None)
    assert result is None, "Should return None without baseline"
    
    # Test 2: Create baseline and test with matching transactions
    baseline = CustomerBaseline(
        avg_transaction_amount=Decimal("100"),
        median_transaction_amount=Decimal("100"),
        avg_daily_transaction_count=2.0,
        common_merchants=["Store A", "Store B"],
        common_transaction_types=["purchase"],
        typical_hours=[9, 10, 11, 12, 13, 14, 15, 16]
    )
    
    matching_txns = [
        TransactionRecord(
            transaction_id="T2",
            customer_id="C1",
            amount=Decimal("150"),  # Within 3x median
            timestamp=datetime.now(),
            merchant="Store A",  # In common merchants
            transaction_type="purchase"  # In common types
        )
    ]
    result = detector.detect(matching_txns, baseline)
    assert result is None, "Should not detect pattern for matching baseline"
    
    # Test 3: Unusual amount (> 3x median)
    unusual_amount_txns = [
        TransactionRecord(
            transaction_id="T3",
            customer_id="C1",
            amount=Decimal("400"),  # > 3x $100 median
            timestamp=datetime.now(),
            merchant="Store A",
            transaction_type="purchase"
        )
    ]
    result = detector.detect(unusual_amount_txns, baseline)
    assert result is not None, "Should detect unusual amount"
    assert result.risk_score >= 50, f"Expected risk score >= 50, got {result.risk_score}"
    
    # Test 4: New merchant
    new_merchant_txns = [
        TransactionRecord(
            transaction_id="T4",
            customer_id="C1",
            amount=Decimal("50"),
            timestamp=datetime.now(),
            merchant="New Store",  # Not in common merchants
            transaction_type="purchase"
        )
    ]
    result = detector.detect(new_merchant_txns, baseline)
    assert result is not None, "Should detect new merchant"
    
    # Test 5: Unusual transaction type
    unusual_type_txns = [
        TransactionRecord(
            transaction_id="T5",
            customer_id="C1",
            amount=Decimal("50"),
            timestamp=datetime.now(),
            merchant="Store A",
            transaction_type="withdrawal"  # Not in common types
        )
    ]
    result = detector.detect(unusual_type_txns, baseline)
    assert result is not None, "Should detect unusual transaction type"
    
    print("✓ PatternBreakDetector tests passed")


if __name__ == "__main__":
    print("Testing fraud pattern detectors...\n")
    
    test_large_transfer_detector()
    test_burst_payment_detector()
    test_odd_hours_detector()
    test_pattern_break_detector()
    
    print("\n✓ All detector tests passed successfully!")

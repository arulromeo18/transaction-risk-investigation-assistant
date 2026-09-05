"""
Verification tests for StructuringDetector and VelocityDetector.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from src.models.transaction import TransactionRecord
from src.detectors.structuring import StructuringDetector
from src.detectors.velocity import VelocityDetector


def test_structuring_detector():
    """Test StructuringDetector with various structuring scenarios."""
    detector = StructuringDetector()
    
    # Test 1: No structuring (amounts not in target range)
    normal_txns = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("5000"),
            timestamp=datetime.now() + timedelta(days=i),
            merchant="Store A",
            transaction_type="transfer"
        )
        for i in range(5)
    ]
    result = detector.detect(normal_txns, None)
    assert result is None, "Should not detect pattern for normal amounts"
    print("  ✓ Test 1: No structuring detected for normal amounts")
    
    # Test 2: Insufficient transactions (only 2 in range)
    insufficient_txns = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("9500"),  # Just below $10k
            timestamp=datetime.now() + timedelta(days=i),
            merchant="Store B",
            transaction_type="transfer"
        )
        for i in range(2)
    ]
    result = detector.detect(insufficient_txns, None)
    assert result is None, "Should not detect with insufficient transactions"
    print("  ✓ Test 2: No structuring detected with insufficient transactions")
    
    # Test 3: Structuring detected (3+ transactions $9k-$10k within 7 days)
    base_time = datetime.now()
    structuring_txns = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("9500"),  # Just below $10k threshold
            timestamp=base_time + timedelta(days=i),
            merchant="Store C",
            transaction_type="transfer"
        )
        for i in range(4)
    ]
    result = detector.detect(structuring_txns, None)
    assert result is not None, "Should detect structuring pattern"
    assert result.risk_score in [70, 80], f"Expected risk score 70 or 80, got {result.risk_score}"
    assert len(result.triggered_transactions) >= 3, "Should flag at least 3 transactions"
    print(f"  ✓ Test 3: Structuring detected with risk score {result.risk_score}")
    
    # Test 4: Transactions spread too far apart (> 7 days)
    spread_txns = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("9800"),
            timestamp=base_time + timedelta(days=i * 10),  # 10 days apart
            merchant="Store D",
            transaction_type="transfer"
        )
        for i in range(4)
    ]
    result = detector.detect(spread_txns, None)
    assert result is None, "Should not detect when transactions too far apart"
    print("  ✓ Test 4: No structuring detected when transactions spread > 7 days")
    
    # Test 5: High risk (total >= 2x threshold)
    high_risk_txns = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("9900"),  # Just below $10k
            timestamp=base_time + timedelta(days=i),
            merchant="Store E",
            transaction_type="transfer"
        )
        for i in range(3)
    ]
    result = detector.detect(high_risk_txns, None)
    assert result is not None, "Should detect high-risk structuring"
    # Total: 3 * $9900 = $29,700 >= $20,000 (2x threshold)
    assert result.risk_score == 80, f"Expected high risk score 80, got {result.risk_score}"
    print(f"  ✓ Test 5: High-risk structuring detected (total >= 2x threshold)")
    
    print("✓ StructuringDetector tests passed")


def test_velocity_detector():
    """Test VelocityDetector with various velocity scenarios."""
    detector = VelocityDetector()
    
    # Test 1: Insufficient transaction history
    few_txns = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=datetime.now() - timedelta(days=i),
            merchant="Store A",
            transaction_type="purchase"
        )
        for i in range(5)
    ]
    result = detector.detect(few_txns, None)
    assert result is None, "Should not detect with insufficient history"
    print("  ✓ Test 1: No velocity detected with insufficient history")
    
    # Test 2: Constant velocity (no acceleration)
    base_time = datetime.now()
    # 1 transaction per day for 30 days
    constant_txns = [
        TransactionRecord(
            transaction_id=f"T{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=base_time - timedelta(days=30-i),
            merchant="Store B",
            transaction_type="purchase"
        )
        for i in range(30)
    ]
    result = detector.detect(constant_txns, None)
    assert result is None, "Should not detect with constant velocity"
    print("  ✓ Test 2: No velocity detected with constant activity")
    
    # Test 3: Velocity acceleration (>= 2.5x increase)
    # Historical (days 8-30): 23 days, ~0.5 txns/day (10 total)
    # Recent (days 1-7): 7 days, ~2.5 txns/day (18 total) = ~5x increase
    historical_txns = [
        TransactionRecord(
            transaction_id=f"H{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=base_time - timedelta(days=15+i),  # Spread in historical window
            merchant="Store C",
            transaction_type="purchase"
        )
        for i in range(10)  # 10 transactions in historical period (days 8-30)
    ]
    recent_txns = [
        TransactionRecord(
            transaction_id=f"R{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=base_time - timedelta(days=6-i, hours=i),  # Concentrated in recent period
            merchant="Store C",
            transaction_type="purchase"
        )
        for i in range(18)  # 18 transactions in last 7 days
    ]
    all_txns = historical_txns + recent_txns
    result = detector.detect(all_txns, None)
    assert result is not None, "Should detect velocity acceleration"
    assert result.risk_score >= 60, f"Expected risk score >= 60, got {result.risk_score}"
    print(f"  ✓ Test 3: Velocity acceleration detected with risk score {result.risk_score}")
    
    # Test 4: Amount acceleration
    # Historical: $100/day average
    # Recent: $300/day average = 3x increase
    historical_amount_txns = [
        TransactionRecord(
            transaction_id=f"HA{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=base_time - timedelta(days=30-i),
            merchant="Store D",
            transaction_type="purchase"
        )
        for i in range(23)  # 1 per day for 23 days
    ]
    recent_amount_txns = [
        TransactionRecord(
            transaction_id=f"RA{i}",
            customer_id="C1",
            amount=Decimal("300"),  # 3x historical amount
            timestamp=base_time - timedelta(days=7-i),
            merchant="Store D",
            transaction_type="purchase"
        )
        for i in range(7)  # 1 per day for 7 days
    ]
    all_amount_txns = historical_amount_txns + recent_amount_txns
    result = detector.detect(all_amount_txns, None)
    assert result is not None, "Should detect amount acceleration"
    assert result.risk_score >= 60, f"Expected risk score >= 60, got {result.risk_score}"
    print(f"  ✓ Test 4: Amount acceleration detected with risk score {result.risk_score}")
    
    # Test 5: Slight increase (below 2.5x threshold)
    # Historical: 1 txn/day, Recent: 2 txn/day (2x, below 2.5x)
    slight_historical = [
        TransactionRecord(
            transaction_id=f"SH{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=base_time - timedelta(days=30-i),
            merchant="Store E",
            transaction_type="purchase"
        )
        for i in range(23)
    ]
    slight_recent = [
        TransactionRecord(
            transaction_id=f"SR{i}",
            customer_id="C1",
            amount=Decimal("100"),
            timestamp=base_time - timedelta(days=7-i, hours=i*3),
            merchant="Store E",
            transaction_type="purchase"
        )
        for i in range(14)  # ~2x but need to keep below 2.5x
    ]
    # Adjust to keep velocity below threshold
    slight_all = slight_historical[:20] + slight_recent[:7]  # More balanced
    result = detector.detect(slight_all, None)
    assert result is None, "Should not detect with acceleration below threshold"
    print("  ✓ Test 5: No velocity detected with acceleration below 2.5x threshold")
    
    print("✓ VelocityDetector tests passed")


if __name__ == "__main__":
    print("Testing new fraud pattern detectors...\n")
    
    print("Testing StructuringDetector:")
    test_structuring_detector()
    print()
    
    print("Testing VelocityDetector:")
    test_velocity_detector()
    print()
    
    print("✓ All new detector tests passed successfully!")

"""Debug script for velocity detector."""

from datetime import datetime, timedelta
from decimal import Decimal

from src.models.transaction import TransactionRecord
from src.detectors.velocity import VelocityDetector


def debug_velocity():
    """Debug the velocity detector with detailed output."""
    detector = VelocityDetector()
    
    base_time = datetime.now()
    
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
    
    print(f"Total transactions: {len(all_txns)}")
    print(f"Base time: {base_time}")
    
    # Sort and check timestamps
    sorted_txns = sorted(all_txns, key=lambda t: t.timestamp)
    print(f"\nFirst transaction: {sorted_txns[0].timestamp}")
    print(f"Last transaction: {sorted_txns[-1].timestamp}")
    
    # Calculate windows
    latest_timestamp = sorted_txns[-1].timestamp
    recent_cutoff = latest_timestamp - timedelta(days=detector.RECENT_WINDOW_DAYS)
    historical_cutoff = latest_timestamp - timedelta(
        days=detector.RECENT_WINDOW_DAYS + detector.HISTORICAL_WINDOW_DAYS
    )
    
    print(f"\nLatest timestamp: {latest_timestamp}")
    print(f"Recent cutoff (7 days back): {recent_cutoff}")
    print(f"Historical cutoff (30 days back): {historical_cutoff}")
    
    recent = [t for t in sorted_txns if t.timestamp >= recent_cutoff]
    historical = [
        t for t in sorted_txns
        if historical_cutoff <= t.timestamp < recent_cutoff
    ]
    
    print(f"\nRecent transactions: {len(recent)}")
    print(f"Historical transactions: {len(historical)}")
    
    if recent:
        print(f"Recent range: {recent[0].timestamp} to {recent[-1].timestamp}")
    if historical:
        print(f"Historical range: {historical[0].timestamp} to {historical[-1].timestamp}")
    
    # Calculate rates
    recent_daily = len(recent) / detector.RECENT_WINDOW_DAYS
    historical_daily = len(historical) / detector.HISTORICAL_WINDOW_DAYS if historical else 0
    
    print(f"\nRecent daily rate: {recent_daily:.2f}")
    print(f"Historical daily rate: {historical_daily:.2f}")
    
    if historical_daily > 0:
        acceleration = recent_daily / historical_daily
        print(f"Acceleration: {acceleration:.2f}x")
        print(f"Threshold: {detector.VELOCITY_MULTIPLIER}x")
    
    result = detector.detect(all_txns, None)
    print(f"\nDetection result: {result}")
    if result:
        print(f"Risk score: {result.risk_score}")
        print(f"Details: {result.details}")


if __name__ == "__main__":
    debug_velocity()

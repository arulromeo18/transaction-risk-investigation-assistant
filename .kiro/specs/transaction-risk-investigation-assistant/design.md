# Design Document: Transaction Risk Investigation Assistant

## 1. System Overview

The Transaction Risk Investigation Assistant is a demonstration-focused fraud detection system built for a 2-hour hackathon presentation. The system consists of a Python backend with a deterministic rule-based fraud detection engine, Gemini API integration for narrative generation, and a React frontend for data visualization and interaction.

**Key Design Principles:**
- **Rapid Deployment:** Single-command startup with no external dependencies
- **Deterministic Detection:** Rule-based fraud patterns with predictable, explainable results
- **AI-Enhanced Presentation:** Gemini API for narrative generation only, not detection logic
- **Synthetic Data:** Pre-built datasets demonstrating various fraud scenarios
- **Time-Constrained Operation:** 60-second request timeout with graceful degradation

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Tailwind)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Profile Select│  │ CSV Upload   │  │ Visualization │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (Python 3.11 + Flask)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 API Layer (Flask)                     │  │
│  │  • POST /api/analyze  • GET /api/profiles            │  │
│  │  • CORS enabled       • Request validation           │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Rule Engine (Deterministic)              │  │
│  │  • Large Transfer Detection                           │  │
│  │  • Burst Payment Detection                            │  │
│  │  • Odd-Hours Activity Detection                       │  │
│  │  • Pattern Break Detection                            │  │
│  │  • Structuring Detection                              │  │
│  │  • Velocity Detection                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Gemini Integration (Async)                   │  │
│  │  • Narrative generation                               │  │
│  │  • Timeout handling (45s)                             │  │
│  │  • Fallback to rule results only                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Synthetic Data (Pre-loaded)                   │  │
│  │  • 4-5 customer profiles                              │  │
│  │  • Clean + fraudulent patterns                        │  │
│  │  • No external database                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
                 ┌────────────────────┐
                 │   Gemini API       │
                 │  (Text Generation) │
                 └────────────────────┘
```

### 2.2 Technology Stack

**Backend:**
- Python 3.11
- Flask 3.0+ (web framework)
- google-generativeai (Gemini API client)
- pandas (CSV parsing)
- python-dateutil (timestamp parsing)

**Frontend:**
- React 18+
- Tailwind CSS 3+
- Recharts (data visualization)
- Axios (HTTP client)

**Deployment:**
- Single command: `pip install -r requirements.txt && python app.py`
- No Docker, no database, no external configuration
- Port 8000 for backend, port 3000 for frontend (development)

## 3. Data Models

### 3.1 Transaction Record

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class TransactionRecord:
    """
    Represents a single financial transaction.
    
    Attributes:
        transaction_id: Unique identifier for the transaction
        customer_id: Identifier for the customer account
        amount: Transaction amount in decimal format
        timestamp: Date and time of transaction
        merchant: Merchant name or transaction description
        transaction_type: Type of transaction (purchase, transfer, withdrawal)
        category: Optional merchant category (e.g., groceries, gas, online)
        location: Optional transaction location
    """
    transaction_id: str
    customer_id: str
    amount: Decimal
    timestamp: datetime
    merchant: str
    transaction_type: str  # purchase, transfer, withdrawal, deposit
    category: Optional[str] = None
    location: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary for JSON serialization."""
        return {
            'transaction_id': self.transaction_id,
            'customer_id': self.customer_id,
            'amount': str(self.amount),
            'timestamp': self.timestamp.isoformat(),
            'merchant': self.merchant,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'location': self.location
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'TransactionRecord':
        """Create transaction from dictionary."""
        return TransactionRecord(
            transaction_id=data['transaction_id'],
            customer_id=data['customer_id'],
            amount=Decimal(str(data['amount'])),
            timestamp=datetime.fromisoformat(data['timestamp']),
            merchant=data['merchant'],
            transaction_type=data['transaction_type'],
            category=data.get('category'),
            location=data.get('location')
        )
```

### 3.2 Customer Profile

```python
@dataclass
class CustomerProfile:
    """
    Represents a customer with transaction history.
    
    Attributes:
        customer_id: Unique identifier for the customer
        name: Customer name
        transactions: List of transaction records
        baseline_stats: Statistical baseline for pattern break detection
    """
    customer_id: str
    name: str
    transactions: list[TransactionRecord]
    baseline_stats: Optional['CustomerBaseline'] = None
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary for JSON serialization."""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'transactions': [t.to_dict() for t in self.transactions],
            'baseline_stats': self.baseline_stats.to_dict() if self.baseline_stats else None
        }

@dataclass
class CustomerBaseline:
    """
    Statistical baseline for a customer's normal behavior.
    Used for pattern break detection.
    """
    avg_transaction_amount: Decimal
    median_transaction_amount: Decimal
    avg_daily_transaction_count: float
    common_merchants: list[str]
    common_transaction_types: list[str]
    typical_hours: list[int]  # Hours when customer typically transacts
    
    def to_dict(self) -> dict:
        return {
            'avg_transaction_amount': str(self.avg_transaction_amount),
            'median_transaction_amount': str(self.median_transaction_amount),
            'avg_daily_transaction_count': self.avg_daily_transaction_count,
            'common_merchants': self.common_merchants,
            'common_transaction_types': self.common_transaction_types,
            'typical_hours': self.typical_hours
        }
```

### 3.3 Fraud Detection Result

```python
@dataclass
class FraudPattern:
    """
    Represents a detected fraud pattern.
    
    Attributes:
        pattern_name: Name of the fraud pattern (e.g., "Large Transfer")
        pattern_type: Type identifier for the pattern
        risk_score: Numerical risk score (0-100)
        description: Human-readable description of the pattern
        triggered_transactions: Transaction IDs that triggered this pattern
        details: Additional pattern-specific details
    """
    pattern_name: str
    pattern_type: str
    risk_score: int  # 0-100
    description: str
    triggered_transactions: list[str]
    details: dict
    
    def to_dict(self) -> dict:
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
    
    Attributes:
        customer_id: Customer identifier
        detected_patterns: List of detected fraud patterns
        overall_risk_score: Aggregate risk score across all patterns
        investigation_narrative: Gemini-generated narrative (optional)
        processing_time_ms: Time taken for analysis in milliseconds
    """
    customer_id: str
    detected_patterns: list[FraudPattern]
    overall_risk_score: int
    investigation_narrative: Optional[str]
    processing_time_ms: int
    
    def to_dict(self) -> dict:
        return {
            'customer_id': self.customer_id,
            'detected_patterns': [p.to_dict() for p in self.detected_patterns],
            'overall_risk_score': self.overall_risk_score,
            'investigation_narrative': self.investigation_narrative,
            'processing_time_ms': self.processing_time_ms
        }
```

## 4. Rule Engine Design

### 4.1 Rule Engine Architecture

The rule engine processes transactions through a pipeline of independent fraud pattern detectors. Each detector is deterministic and stateless.

```python
from abc import ABC, abstractmethod
from typing import Protocol

class FraudDetector(ABC):
    """
    Abstract base class for fraud pattern detectors.
    Each detector implements one specific fraud pattern.
    """
    
    @abstractmethod
    def detect(self, transactions: list[TransactionRecord], 
               baseline: Optional[CustomerBaseline]) -> Optional[FraudPattern]:
        """
        Analyze transactions for fraud pattern.
        
        Args:
            transactions: List of transaction records to analyze
            baseline: Optional customer baseline for context
            
        Returns:
            FraudPattern if detected, None otherwise
        """
        pass
    
    @property
    @abstractmethod
    def pattern_name(self) -> str:
        """Return the name of this fraud pattern."""
        pass
    
    @property
    @abstractmethod
    def pattern_type(self) -> str:
        """Return the type identifier for this pattern."""
        pass

class RuleEngine:
    """
    Main rule engine that orchestrates fraud detection.
    Runs all registered detectors and aggregates results.
    """
    
    def __init__(self):
        self.detectors: list[FraudDetector] = []
        self._register_detectors()
    
    def _register_detectors(self):
        """Register all fraud pattern detectors."""
        self.detectors = [
            LargeTransferDetector(),
            BurstPaymentDetector(),
            OddHoursDetector(),
            PatternBreakDetector(),
            StructuringDetector(),
            VelocityDetector()
        ]
    
    def analyze(self, profile: CustomerProfile) -> DetectionResult:
        """
        Analyze customer profile for fraud patterns.
        
        Args:
            profile: Customer profile with transactions
            
        Returns:
            DetectionResult with all detected patterns
        """
        import time
        start_time = time.time()
        
        detected_patterns = []
        
        # Run each detector
        for detector in self.detectors:
            pattern = detector.detect(profile.transactions, profile.baseline_stats)
            if pattern:
                detected_patterns.append(pattern)
        
        # Calculate overall risk score (max of individual scores)
        overall_risk = max([p.risk_score for p in detected_patterns], default=0)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return DetectionResult(
            customer_id=profile.customer_id,
            detected_patterns=detected_patterns,
            overall_risk_score=overall_risk,
            investigation_narrative=None,  # Added later by Gemini integration
            processing_time_ms=processing_time
        )
```

### 4.2 Fraud Pattern Detectors

#### 4.2.1 Large Transfer Detector

Detects transactions with unusually large amounts that may indicate account takeover or money laundering.

```python
class LargeTransferDetector(FraudDetector):
    """
    Detects large transfers that exceed threshold.
    
    Thresholds:
    - High risk: >= $10,000
    - Medium risk: >= $5,000
    """
    
    # Configuration thresholds
    HIGH_RISK_THRESHOLD = Decimal('10000')
    MEDIUM_RISK_THRESHOLD = Decimal('5000')
    
    @property
    def pattern_name(self) -> str:
        return "Large Transfer"
    
    @property
    def pattern_type(self) -> str:
        return "large_transfer"
    
    def detect(self, transactions: list[TransactionRecord], 
               baseline: Optional[CustomerBaseline]) -> Optional[FraudPattern]:
        """Detect large transfer patterns."""
        large_transactions = []
        max_amount = Decimal('0')
        
        for txn in transactions:
            if txn.amount >= self.MEDIUM_RISK_THRESHOLD:
                large_transactions.append(txn.transaction_id)
                max_amount = max(max_amount, txn.amount)
        
        if not large_transactions:
            return None
        
        # Calculate risk score
        if max_amount >= self.HIGH_RISK_THRESHOLD:
            risk_score = 90
        else:
            risk_score = 70
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected {len(large_transactions)} large transaction(s) with maximum amount ${max_amount}",
            triggered_transactions=large_transactions,
            details={
                'max_amount': str(max_amount),
                'transaction_count': len(large_transactions),
                'threshold': str(self.MEDIUM_RISK_THRESHOLD)
            }
        )
```

#### 4.2.2 Burst Payment Detector

Detects rapid sequences of transactions that may indicate card testing or automated fraud.

```python
class BurstPaymentDetector(FraudDetector):
    """
    Detects burst payment patterns (many transactions in short time).
    
    Thresholds:
    - High risk: >= 10 transactions in 1 hour
    - Medium risk: >= 5 transactions in 1 hour
    """
    
    HIGH_RISK_COUNT = 10
    MEDIUM_RISK_COUNT = 5
    TIME_WINDOW_HOURS = 1
    
    @property
    def pattern_name(self) -> str:
        return "Burst Payment Pattern"
    
    @property
    def pattern_type(self) -> str:
        return "burst_payment"
    
    def detect(self, transactions: list[TransactionRecord], 
               baseline: Optional[CustomerBaseline]) -> Optional[FraudPattern]:
        """Detect burst payment patterns."""
        from datetime import timedelta
        
        if len(transactions) < self.MEDIUM_RISK_COUNT:
            return None
        
        # Sort transactions by timestamp
        sorted_txns = sorted(transactions, key=lambda t: t.timestamp)
        
        max_burst_count = 0
        max_burst_transactions = []
        
        # Sliding window approach
        for i in range(len(sorted_txns)):
            window_start = sorted_txns[i].timestamp
            window_end = window_start + timedelta(hours=self.TIME_WINDOW_HOURS)
            
            # Count transactions in window
            burst_txns = []
            for j in range(i, len(sorted_txns)):
                if sorted_txns[j].timestamp <= window_end:
                    burst_txns.append(sorted_txns[j])
                else:
                    break
            
            if len(burst_txns) > max_burst_count:
                max_burst_count = len(burst_txns)
                max_burst_transactions = [t.transaction_id for t in burst_txns]
        
        if max_burst_count < self.MEDIUM_RISK_COUNT:
            return None
        
        # Calculate risk score
        if max_burst_count >= self.HIGH_RISK_COUNT:
            risk_score = 85
        else:
            risk_score = 65
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected burst of {max_burst_count} transactions within {self.TIME_WINDOW_HOURS} hour(s)",
            triggered_transactions=max_burst_transactions,
            details={
                'burst_count': max_burst_count,
                'time_window_hours': self.TIME_WINDOW_HOURS,
                'threshold': self.MEDIUM_RISK_COUNT
            }
        )
```

#### 4.2.3 Odd-Hours Activity Detector

Detects transactions occurring outside normal business hours that may indicate compromised accounts.

```python
class OddHoursDetector(FraudDetector):
    """
    Detects transactions during unusual hours (late night/early morning).
    
    Odd hours: 11 PM - 6 AM (23:00 - 06:00)
    Risk increases with multiple odd-hour transactions.
    """
    
    ODD_HOUR_START = 23  # 11 PM
    ODD_HOUR_END = 6     # 6 AM
    HIGH_RISK_COUNT = 5
    MEDIUM_RISK_COUNT = 2
    
    @property
    def pattern_name(self) -> str:
        return "Odd-Hours Activity"
    
    @property
    def pattern_type(self) -> str:
        return "odd_hours"
    
    def detect(self, transactions: list[TransactionRecord], 
               baseline: Optional[CustomerBaseline]) -> Optional[FraudPattern]:
        """Detect odd-hours activity."""
        odd_hour_transactions = []
        
        for txn in transactions:
            hour = txn.timestamp.hour
            # Check if in odd hours range
            if hour >= self.ODD_HOUR_START or hour < self.ODD_HOUR_END:
                odd_hour_transactions.append(txn.transaction_id)
        
        if len(odd_hour_transactions) < self.MEDIUM_RISK_COUNT:
            return None
        
        # Calculate risk score
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
```

#### 4.2.4 Pattern Break Detector

Detects deviations from customer's normal behavior baseline.

```python
class PatternBreakDetector(FraudDetector):
    """
    Detects pattern breaks - deviations from customer baseline.
    
    Checks for:
    - Unusual transaction amounts (3x median)
    - Unusual merchants (not in common list)
    - Unusual transaction types
    """
    
    AMOUNT_MULTIPLIER = 3.0  # 3x median is unusual
    
    @property
    def pattern_name(self) -> str:
        return "Pattern Break"
    
    @property
    def pattern_type(self) -> str:
        return "pattern_break"
    
    def detect(self, transactions: list[TransactionRecord], 
               baseline: Optional[CustomerBaseline]) -> Optional[FraudPattern]:
        """Detect pattern breaks."""
        if not baseline:
            return None  # Need baseline for comparison
        
        unusual_transactions = []
        break_reasons = []
        
        for txn in transactions:
            # Check amount deviation
            if txn.amount > baseline.median_transaction_amount * Decimal(str(self.AMOUNT_MULTIPLIER)):
                unusual_transactions.append(txn.transaction_id)
                break_reasons.append(f"Unusual amount: ${txn.amount}")
                continue
            
            # Check merchant deviation
            if baseline.common_merchants and txn.merchant not in baseline.common_merchants:
                unusual_transactions.append(txn.transaction_id)
                break_reasons.append(f"New merchant: {txn.merchant}")
                continue
            
            # Check transaction type deviation
            if baseline.common_transaction_types and txn.transaction_type not in baseline.common_transaction_types:
                unusual_transactions.append(txn.transaction_id)
                break_reasons.append(f"Unusual type: {txn.transaction_type}")
        
        if not unusual_transactions:
            return None
        
        # Risk score based on number of breaks
        risk_score = min(80, 50 + len(unusual_transactions) * 5)
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected {len(unusual_transactions)} transaction(s) deviating from customer baseline",
            triggered_transactions=unusual_transactions,
            details={
                'break_count': len(unusual_transactions),
                'break_reasons': break_reasons[:5],  # Limit to first 5
                'baseline_median_amount': str(baseline.median_transaction_amount)
            }
        )
```

#### 4.2.5 Structuring Detector

Detects structuring patterns where transactions appear designed to avoid reporting thresholds.

```python
class StructuringDetector(FraudDetector):
    """
    Detects structuring patterns (multiple transactions just under threshold).
    
    Looks for:
    - Multiple transactions just below $10,000 (common reporting threshold)
    - Transactions in same day or short period
    """
    
    STRUCTURING_THRESHOLD = Decimal('10000')
    JUST_BELOW_MARGIN = Decimal('1000')  # Within $1000 of threshold
    MIN_TRANSACTIONS = 3
    TIME_WINDOW_DAYS = 7
    
    @property
    def pattern_name(self) -> str:
        return "Structuring Pattern"
    
    @property
    def pattern_type(self) -> str:
        return "structuring"
    
    def detect(self, transactions: list[TransactionRecord], 
               baseline: Optional[CustomerBaseline]) -> Optional[FraudPattern]:
        """Detect structuring patterns."""
        from datetime import timedelta
        
        # Find transactions just below threshold
        suspicious_txns = []
        for txn in transactions:
            lower_bound = self.STRUCTURING_THRESHOLD - self.JUST_BELOW_MARGIN
            if lower_bound <= txn.amount < self.STRUCTURING_THRESHOLD:
                suspicious_txns.append(txn)
        
        if len(suspicious_txns) < self.MIN_TRANSACTIONS:
            return None
        
        # Check if they occur within time window
        suspicious_txns.sort(key=lambda t: t.timestamp)
        
        # Find clusters within time window
        max_cluster = []
        for i in range(len(suspicious_txns)):
            window_start = suspicious_txns[i].timestamp
            window_end = window_start + timedelta(days=self.TIME_WINDOW_DAYS)
            
            cluster = []
            for j in range(i, len(suspicious_txns)):
                if suspicious_txns[j].timestamp <= window_end:
                    cluster.append(suspicious_txns[j])
            
            if len(cluster) > len(max_cluster):
                max_cluster = cluster
        
        if len(max_cluster) < self.MIN_TRANSACTIONS:
            return None
        
        total_amount = sum(t.amount for t in max_cluster)
        
        # Higher risk if total exceeds threshold significantly
        risk_score = 80 if total_amount >= self.STRUCTURING_THRESHOLD * 2 else 70
        
        return FraudPattern(
            pattern_name=self.pattern_name,
            pattern_type=self.pattern_type,
            risk_score=risk_score,
            description=f"Detected {len(max_cluster)} transactions just below ${self.STRUCTURING_THRESHOLD} threshold, totaling ${total_amount}",
            triggered_transactions=[t.transaction_id for t in max_cluster],
            details={
                'transaction_count': len(max_cluster),
                'total_amount': str(total_amount),
                'threshold': str(self.STRUCTURING_THRESHOLD),
                'time_window_days': self.TIME_WINDOW_DAYS
            }
        )
```

#### 4.2.6 Velocity Detector

Detects rapid acceleration in transaction frequency or amounts.

```python
class VelocityDetector(FraudDetector):
    """
    Detects velocity patterns (rapid acceleration in activity).
    
    Compares recent activity to historical baseline:
    - Transaction frequency acceleration
    - Transaction amount acceleration
    """
    
    RECENT_WINDOW_DAYS = 7
    HISTORICAL_WINDOW_DAYS = 30
    VELOCITY_MULTIPLIER = 2.5  # 2.5x increase is suspicious
    
    @property
    def pattern_name(self) -> str:
        return "Velocity Pattern"
    
    @property
    def pattern_type(self) -> str:
        return "velocity"
    
    def detect(self, transactions: list[TransactionRecord], 
               baseline: Optional[CustomerBaseline]) -> Optional[FraudPattern]:
        """Detect velocity patterns."""
        from datetime import timedelta, datetime
        
        if len(transactions) < 10:
            return None  # Need sufficient history
        
        # Sort by timestamp
        sorted_txns = sorted(transactions, key=lambda t: t.timestamp)
        
        # Get most recent timestamp
        latest_timestamp = sorted_txns[-1].timestamp
        
        # Split into recent and historical
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
        amount_acceleration = recent_daily_amount / historical_daily_amount if historical_daily_amount > 0 else 0
        
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
```

## 5. Gemini API Integration

### 5.1 Integration Architecture

The Gemini integration generates investigation narratives asynchronously with timeout handling to ensure the system remains responsive.

```python
import google.generativeai as genai
from typing import Optional
import asyncio
from concurrent.futures import TimeoutError

class GeminiIntegration:
    """
    Handles Gemini API integration for narrative generation.
    
    Features:
    - Async generation with timeout
    - Fallback to rule results only on failure
    - Structured prompts for consistent output
    """
    
    NARRATIVE_TIMEOUT_SECONDS = 45  # Leave 15s buffer for other processing
    MODEL_NAME = "gemini-1.5-flash"
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini integration.
        
        Args:
            api_key: Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.MODEL_NAME)
    
    async def generate_narrative_async(self, detection_result: DetectionResult, 
                                       profile: CustomerProfile) -> Optional[str]:
        """
        Generate investigation narrative asynchronously.
        
        Args:
            detection_result: Fraud detection results
            profile: Customer profile with transactions
            
        Returns:
            Investigation narrative or None on timeout/failure
        """
        try:
            prompt = self._build_prompt(detection_result, profile)
            
            # Generate with timeout
            response = await asyncio.wait_for(
                self._generate_with_retry(prompt),
                timeout=self.NARRATIVE_TIMEOUT_SECONDS
            )
            
            return response.text if response else None
            
        except asyncio.TimeoutError:
            print(f"Gemini API timeout after {self.NARRATIVE_TIMEOUT_SECONDS}s")
            return None
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    async def _generate_with_retry(self, prompt: str, max_retries: int = 2):
        """Generate with retry on transient failures."""
        for attempt in range(max_retries):
            try:
                # Run synchronous API call in executor
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    self.model.generate_content,
                    prompt
                )
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)  # Brief delay before retry
    
    def _build_prompt(self, detection_result: DetectionResult, 
                     profile: CustomerProfile) -> str:
        """
        Build structured prompt for narrative generation.
        
        The prompt provides:
        - Customer context
        - Detected fraud patterns with details
        - Request for structured investigation narrative
        """
        patterns_summary = []
        for pattern in detection_result.detected_patterns:
            patterns_summary.append(
                f"- {pattern.pattern_name} (Risk: {pattern.risk_score}/100)\n"
                f"  Description: {pattern.description}\n"
                f"  Details: {pattern.details}"
            )
        
        patterns_text = "\n\n".join(patterns_summary)
        
        prompt = f"""You are a fraud investigation specialist. Analyze the following fraud detection results and provide a clear, professional investigation narrative.

Customer: {profile.customer_id}
Transaction Count: {len(profile.transactions)}
Overall Risk Score: {detection_result.overall_risk_score}/100

Detected Fraud Patterns:
{patterns_text}

Please provide an investigation narrative with the following sections:

1. Executive Summary: Brief overview of the risk level and primary concerns
2. Pattern Analysis: Detailed analysis of each detected pattern
3. Risk Assessment: Overall risk evaluation and severity
4. Recommended Actions: Specific investigation steps and mitigation measures

Keep the narrative professional, clear, and actionable. Focus on facts from the detection results."""

        return prompt
    
    def generate_narrative_sync(self, detection_result: DetectionResult, 
                               profile: CustomerProfile) -> Optional[str]:
        """
        Synchronous wrapper for narrative generation.
        Used by Flask application.
        
        Args:
            detection_result: Fraud detection results
            profile: Customer profile with transactions
            
        Returns:
            Investigation narrative or None on timeout/failure
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                self.generate_narrative_async(detection_result, profile)
            )
        finally:
            loop.close()
```

### 5.2 Fallback Strategy

When Gemini API fails or times out:
1. Return detection results with `investigation_narrative: null`
2. Frontend displays detected patterns without narrative section
3. System remains functional for demonstrating rule engine capabilities

## 6. Synthetic Data Generation

### 6.1 Data Generator Design

```python
import random
from datetime import datetime, timedelta
from decimal import Decimal

class SyntheticDataGenerator:
    """
    Generates realistic customer profiles with fraud patterns.
    
    Creates 4-5 profiles demonstrating:
    - Clean customer (no fraud)
    - Large transfer fraud
    - Burst payment fraud
    - Structuring fraud
    - Multiple pattern fraud
    """
    
    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducibility."""
        random.seed(seed)
    
    def generate_profiles(self) -> list[CustomerProfile]:
        """Generate 4-5 customer profiles with various patterns."""
        profiles = [
            self._generate_clean_profile(),
            self._generate_large_transfer_profile(),
            self._generate_burst_payment_profile(),
            self._generate_structuring_profile(),
            self._generate_mixed_fraud_profile()
        ]
        return profiles
    
    def _generate_clean_profile(self) -> CustomerProfile:
        """Generate profile with normal activity, no fraud."""
        customer_id = "CUST001"
        transactions = []
        
        # Generate 30 days of normal transactions
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        
        for day in range(30):
            # 1-3 transactions per day during business hours
            txn_count = random.randint(1, 3)
            for _ in range(txn_count):
                amount = Decimal(str(random.uniform(20, 500))).quantize(Decimal('0.01'))
                hour = random.randint(9, 17)  # Business hours
                timestamp = base_date + timedelta(days=day, hours=hour, minutes=random.randint(0, 59))
                
                transactions.append(TransactionRecord(
                    transaction_id=f"TXN{len(transactions)+1:04d}",
                    customer_id=customer_id,
                    amount=amount,
                    timestamp=timestamp,
                    merchant=random.choice(["Grocery Store", "Gas Station", "Coffee Shop", "Restaurant"]),
                    transaction_type="purchase",
                    category="retail"
                ))
        
        baseline = self._calculate_baseline(transactions)
        
        return CustomerProfile(
            customer_id=customer_id,
            name="Alice Johnson (Clean Profile)",
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _generate_large_transfer_profile(self) -> CustomerProfile:
        """Generate profile with large transfer fraud."""
        customer_id = "CUST002"
        transactions = []
        
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        
        # Normal transactions for 20 days
        for day in range(20):
            txn_count = random.randint(1, 2)
            for _ in range(txn_count):
                amount = Decimal(str(random.uniform(30, 300))).quantize(Decimal('0.01'))
                hour = random.randint(9, 17)
                timestamp = base_date + timedelta(days=day, hours=hour)
                
                transactions.append(TransactionRecord(
                    transaction_id=f"TXN{len(transactions)+1:04d}",
                    customer_id=customer_id,
                    amount=amount,
                    timestamp=timestamp,
                    merchant=random.choice(["Store A", "Store B", "Store C"]),
                    transaction_type="purchase",
                    category="retail"
                ))
        
        # Fraud: Large transfers on day 21
        fraud_date = base_date + timedelta(days=21)
        large_amounts = [12500, 8700]
        
        for i, amount in enumerate(large_amounts):
            transactions.append(TransactionRecord(
                transaction_id=f"TXN{len(transactions)+1:04d}",
                customer_id=customer_id,
                amount=Decimal(str(amount)),
                timestamp=fraud_date + timedelta(hours=i*2),
                merchant="Wire Transfer Service",
                transaction_type="transfer",
                category="financial"
            ))
        
        baseline = self._calculate_baseline(transactions[:40])  # Baseline from normal period
        
        return CustomerProfile(
            customer_id=customer_id,
            name="Bob Smith (Large Transfer Fraud)",
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _generate_burst_payment_profile(self) -> CustomerProfile:
        """Generate profile with burst payment fraud."""
        customer_id = "CUST003"
        transactions = []
        
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        
        # Normal transactions
        for day in range(25):
            amount = Decimal(str(random.uniform(40, 400))).quantize(Decimal('0.01'))
            hour = random.randint(10, 16)
            timestamp = base_date + timedelta(days=day, hours=hour)
            
            transactions.append(TransactionRecord(
                transaction_id=f"TXN{len(transactions)+1:04d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=random.choice(["Shop A", "Shop B"]),
                transaction_type="purchase",
                category="retail"
            ))
        
        # Fraud: Burst of 12 transactions in 30 minutes
        burst_start = base_date + timedelta(days=26, hours=14)
        for i in range(12):
            transactions.append(TransactionRecord(
                transaction_id=f"TXN{len(transactions)+1:04d}",
                customer_id=customer_id,
                amount=Decimal(str(random.uniform(10, 50))).quantize(Decimal('0.01')),
                timestamp=burst_start + timedelta(minutes=i*2),
                merchant=f"Online Store {i%3}",
                transaction_type="purchase",
                category="online"
            ))
        
        baseline = self._calculate_baseline(transactions[:25])
        
        return CustomerProfile(
            customer_id=customer_id,
            name="Carol Davis (Burst Payment Fraud)",
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _generate_structuring_profile(self) -> CustomerProfile:
        """Generate profile with structuring fraud."""
        customer_id = "CUST004"
        transactions = []
        
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        
        # Normal transactions
        for day in range(20):
            amount = Decimal(str(random.uniform(50, 600))).quantize(Decimal('0.01'))
            hour = random.randint(9, 17)
            timestamp = base_date + timedelta(days=day, hours=hour)
            
            transactions.append(TransactionRecord(
                transaction_id=f"TXN{len(transactions)+1:04d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=random.choice(["Merchant A", "Merchant B"]),
                transaction_type="purchase"
            ))
        
        # Fraud: Structuring - 5 transactions just under $10k in 3 days
        structuring_amounts = [9500, 9200, 9800, 9400, 9600]
        for i, amount in enumerate(structuring_amounts):
            day_offset = 22 + (i // 2)
            transactions.append(TransactionRecord(
                transaction_id=f"TXN{len(transactions)+1:04d}",
                customer_id=customer_id,
                amount=Decimal(str(amount)),
                timestamp=base_date + timedelta(days=day_offset, hours=10 + i*2),
                merchant="Bank Transfer",
                transaction_type="transfer",
                category="financial"
            ))
        
        baseline = self._calculate_baseline(transactions[:20])
        
        return CustomerProfile(
            customer_id=customer_id,
            name="David Wilson (Structuring Fraud)",
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _generate_mixed_fraud_profile(self) -> CustomerProfile:
        """Generate profile with multiple fraud patterns."""
        customer_id = "CUST005"
        transactions = []
        
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        
        # Normal transactions during day
        for day in range(18):
            amount = Decimal(str(random.uniform(30, 400))).quantize(Decimal('0.01'))
            hour = random.randint(9, 17)
            timestamp = base_date + timedelta(days=day, hours=hour)
            
            transactions.append(TransactionRecord(
                transaction_id=f"TXN{len(transactions)+1:04d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=random.choice(["Store X", "Store Y"]),
                transaction_type="purchase"
            ))
        
        # Fraud 1: Odd hours transactions (3 AM)
        for day in [20, 21, 22]:
            transactions.append(TransactionRecord(
                transaction_id=f"TXN{len(transactions)+1:04d}",
                customer_id=customer_id,
                amount=Decimal("450.00"),
                timestamp=base_date + timedelta(days=day, hours=3),
                merchant="Online Casino",
                transaction_type="purchase",
                category="gambling"
            ))
        
        # Fraud 2: Velocity - sudden increase
        for i in range(15):
            transactions.append(TransactionRecord(
                transaction_id=f"TXN{len(transactions)+1:04d}",
                customer_id=customer_id,
                amount=Decimal(str(random.uniform(100, 800))).quantize(Decimal('0.01')),
                timestamp=base_date + timedelta(days=24, hours=10 + i),
                merchant=f"Merchant {i}",
                transaction_type="purchase"
            ))
        
        baseline = self._calculate_baseline(transactions[:18])
        
        return CustomerProfile(
            customer_id=customer_id,
            name="Eve Martinez (Multiple Fraud Patterns)",
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _calculate_baseline(self, transactions: list[TransactionRecord]) -> CustomerBaseline:
        """Calculate customer baseline statistics."""
        if not transactions:
            return None
        
        amounts = [t.amount for t in transactions]
        
        # Calculate statistics
        avg_amount = sum(amounts) / len(amounts)
        sorted_amounts = sorted(amounts)
        median_amount = sorted_amounts[len(sorted_amounts) // 2]
        
        # Calculate daily transaction count
        date_counts = {}
        for t in transactions:
            date_key = t.timestamp.date()
            date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        avg_daily_count = sum(date_counts.values()) / len(date_counts) if date_counts else 0
        
        # Extract common merchants and types
        merchant_counts = {}
        type_counts = {}
        hour_counts = {}
        
        for t in transactions:
            merchant_counts[t.merchant] = merchant_counts.get(t.merchant, 0) + 1
            type_counts[t.transaction_type] = type_counts.get(t.transaction_type, 0) + 1
            hour_counts[t.timestamp.hour] = hour_counts.get(t.timestamp.hour, 0) + 1
        
        common_merchants = sorted(merchant_counts.keys(), key=lambda m: merchant_counts[m], reverse=True)[:5]
        common_types = sorted(type_counts.keys(), key=lambda t: type_counts[t], reverse=True)[:3]
        typical_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:8]
        
        return CustomerBaseline(
            avg_transaction_amount=avg_amount,
            median_transaction_amount=median_amount,
            avg_daily_transaction_count=avg_daily_count,
            common_merchants=common_merchants,
            common_transaction_types=common_types,
            typical_hours=typical_hours
        )
```

### 6.2 Pre-generated Data Storage

Store pre-generated profiles in `data/profiles.json`:

```python
def save_profiles(profiles: list[CustomerProfile], filepath: str = "data/profiles.json"):
    """Save profiles to JSON file."""
    import json
    import os
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    data = {
        'profiles': [p.to_dict() for p in profiles],
        'generated_at': datetime.now().isoformat()
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_profiles(filepath: str = "data/profiles.json") -> list[CustomerProfile]:
    """Load profiles from JSON file."""
    import json
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    profiles = []
    for p_data in data['profiles']:
        transactions = [TransactionRecord.from_dict(t) for t in p_data['transactions']]
        
        baseline = None
        if p_data.get('baseline_stats'):
            b = p_data['baseline_stats']
            baseline = CustomerBaseline(
                avg_transaction_amount=Decimal(b['avg_transaction_amount']),
                median_transaction_amount=Decimal(b['median_transaction_amount']),
                avg_daily_transaction_count=b['avg_daily_transaction_count'],
                common_merchants=b['common_merchants'],
                common_transaction_types=b['common_transaction_types'],
                typical_hours=b['typical_hours']
            )
        
        profiles.append(CustomerProfile(
            customer_id=p_data['customer_id'],
            name=p_data['name'],
            transactions=transactions,
            baseline_stats=baseline
        ))
    
    return profiles
```

## 7. Backend API Specifications

### 7.1 Flask Application Structure

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize components
rule_engine = RuleEngine()
gemini_integration = GeminiIntegration(api_key=os.environ.get('GEMINI_API_KEY'))
profiles_cache = load_profiles('data/profiles.json')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """
    Get list of pre-loaded customer profiles.
    
    Returns:
        JSON array of customer profiles (without transactions)
    """
    profile_list = [
        {
            'customer_id': p.customer_id,
            'name': p.name,
            'transaction_count': len(p.transactions)
        }
        for p in profiles_cache
    ]
    return jsonify({'profiles': profile_list})

@app.route('/api/analyze', methods=['POST'])
def analyze_transactions():
    """
    Analyze transactions for fraud patterns.
    
    Request body:
        - customer_id: (optional) ID of pre-loaded profile
        - transactions: (optional) Array of transaction objects
        - csv_data: (optional) CSV string with transaction data
    
    Returns:
        JSON with detection results and investigation narrative
    """
    try:
        import time
        start_time = time.time()
        
        # Parse request
        data = request.get_json()
        
        # Load or parse profile
        if 'customer_id' in data:
            profile = next((p for p in profiles_cache if p.customer_id == data['customer_id']), None)
            if not profile:
                return jsonify({'error': 'Customer not found'}), 404
        elif 'transactions' in data:
            profile = _parse_transaction_json(data['transactions'])
        elif 'csv_data' in data:
            profile = _parse_transaction_csv(data['csv_data'])
        else:
            return jsonify({'error': 'No transaction data provided'}), 400
        
        # Run rule engine
        detection_result = rule_engine.analyze(profile)
        
        # Generate narrative if patterns detected and time permits
        elapsed = time.time() - start_time
        if detection_result.detected_patterns and elapsed < 50:
            narrative = gemini_integration.generate_narrative_sync(detection_result, profile)
            detection_result.investigation_narrative = narrative
        
        return jsonify(detection_result.to_dict())
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

def _parse_transaction_json(transactions_data: list) -> CustomerProfile:
    """Parse transactions from JSON array."""
    transactions = [TransactionRecord.from_dict(t) for t in transactions_data]
    customer_id = transactions[0].customer_id if transactions else "UNKNOWN"
    
    generator = SyntheticDataGenerator()
    baseline = generator._calculate_baseline(transactions)
    
    return CustomerProfile(
        customer_id=customer_id,
        name=f"Custom Upload - {customer_id}",
        transactions=transactions,
        baseline_stats=baseline
    )

def _parse_transaction_csv(csv_data: str) -> CustomerProfile:
    """Parse transactions from CSV string."""
    import pandas as pd
    from io import StringIO
    
    df = pd.read_csv(StringIO(csv_data))
    
    # Expected columns: transaction_id, customer_id, amount, timestamp, merchant, transaction_type
    required_cols = ['amount', 'timestamp', 'merchant']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"CSV must contain columns: {required_cols}")
    
    transactions = []
    customer_id = df['customer_id'].iloc[0] if 'customer_id' in df.columns else "CSV_UPLOAD"
    
    for idx, row in df.iterrows():
        transactions.append(TransactionRecord(
            transaction_id=row.get('transaction_id', f"TXN{idx:04d}"),
            customer_id=customer_id,
            amount=Decimal(str(row['amount'])),
            timestamp=pd.to_datetime(row['timestamp']),
            merchant=row['merchant'],
            transaction_type=row.get('transaction_type', 'purchase'),
            category=row.get('category'),
            location=row.get('location')
        ))
    
    generator = SyntheticDataGenerator()
    baseline = generator._calculate_baseline(transactions)
    
    return CustomerProfile(
        customer_id=customer_id,
        name=f"CSV Upload - {customer_id}",
        transactions=transactions,
        baseline_stats=baseline
    )

if __name__ == '__main__':
    # Generate synthetic data if not exists
    if not os.path.exists('data/profiles.json'):
        print("Generating synthetic data...")
        generator = SyntheticDataGenerator()
        profiles = generator.generate_profiles()
        save_profiles(profiles)
        print(f"Generated {len(profiles)} customer profiles")
    
    print("Starting Transaction Risk Investigation Assistant...")
    print("Backend listening on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
```

### 7.2 API Endpoints Summary

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/health` | GET | Health check | None | `{"status": "healthy", "timestamp": "..."}` |
| `/api/profiles` | GET | List pre-loaded profiles | None | `{"profiles": [...]}` |
| `/api/analyze` | POST | Analyze transactions | JSON/CSV data | `DetectionResult` JSON |

## 8. Frontend Design

### 8.1 Component Structure

```
src/
├── App.jsx                 # Main application component
├── components/
│   ├── ProfileSelector.jsx    # Profile selection dropdown
│   ├── FileUpload.jsx         # CSV file upload
│   ├── TransactionChart.jsx   # Transaction visualization
│   ├── PatternList.jsx        # Detected patterns display
│   ├── NarrativeDisplay.jsx   # Investigation narrative
│   ├── LoadingSpinner.jsx     # Loading indicator
│   └── ErrorDisplay.jsx       # Error message display
├── services/
│   └── api.js                 # API client
└── styles/
    └── tailwind.config.js     # Tailwind configuration
```

### 8.2 Main Application Component

```jsx
// src/App.jsx
import React, { useState, useEffect } from 'react';
import ProfileSelector from './components/ProfileSelector';
import FileUpload from './components/FileUpload';
import TransactionChart from './components/TransactionChart';
import PatternList from './components/PatternList';
import NarrativeDisplay from './components/NarrativeDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorDisplay from './components/ErrorDisplay';
import { getProfiles, analyzeTransactions } from './services/api';

function App() {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load profiles on mount
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const data = await getProfiles();
      setProfiles(data.profiles);
    } catch (err) {
      setError('Failed to load profiles');
    }
  };

  const handleProfileSelect = async (profileId) => {
    setSelectedProfile(profileId);
    setError(null);
    setLoading(true);

    try {
      const result = await analyzeTransactions({ customer_id: profileId });
      setAnalysisResult(result);
    } catch (err) {
      setError('Analysis failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (csvData) => {
    setError(null);
    setLoading(true);

    try {
      const result = await analyzeTransactions({ csv_data: csvData });
      setAnalysisResult(result);
    } catch (err) {
      setError('Upload failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-white mb-4">
            Transaction Risk Investigation Assistant
          </h1>
          <p className="text-xl text-blue-200">
            AI-Powered Fraud Detection & Analysis
          </p>
        </header>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-xl p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ProfileSelector
              profiles={profiles}
              onSelect={handleProfileSelect}
              disabled={loading}
            />
            <FileUpload
              onUpload={handleFileUpload}
              disabled={loading}
            />
          </div>
        </div>

        {/* Loading State */}
        {loading && <LoadingSpinner />}

        {/* Error Display */}
        {error && <ErrorDisplay message={error} />}

        {/* Results */}
        {analysisResult && !loading && (
          <div className="space-y-8">
            {/* Risk Score Header */}
            <div className="bg-white rounded-lg shadow-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-2">
                    Analysis Results
                  </h2>
                  <p className="text-gray-600">
                    Customer: {analysisResult.customer_id}
                  </p>
                </div>
                <div className="text-center">
                  <div className={`text-6xl font-bold ${
                    analysisResult.overall_risk_score >= 80 ? 'text-red-600' :
                    analysisResult.overall_risk_score >= 60 ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {analysisResult.overall_risk_score}
                  </div>
                  <div className="text-sm text-gray-600 mt-2">Risk Score</div>
                </div>
              </div>
            </div>

            {/* Detected Patterns */}
            <PatternList patterns={analysisResult.detected_patterns} />

            {/* Investigation Narrative */}
            {analysisResult.investigation_narrative && (
              <NarrativeDisplay narrative={analysisResult.investigation_narrative} />
            )}

            {/* Transaction Chart */}
            <TransactionChart data={analysisResult} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
```

### 8.3 Key Component Designs

```jsx
// src/components/PatternList.jsx
import React from 'react';

function PatternList({ patterns }) {
  const getRiskColor = (score) => {
    if (score >= 80) return 'bg-red-100 border-red-500 text-red-900';
    if (score >= 60) return 'bg-yellow-100 border-yellow-500 text-yellow-900';
    return 'bg-blue-100 border-blue-500 text-blue-900';
  };

  return (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <h3 className="text-2xl font-bold text-gray-800 mb-6">
        Detected Fraud Patterns ({patterns.length})
      </h3>
      <div className="space-y-4">
        {patterns.map((pattern, idx) => (
          <div
            key={idx}
            className={`border-l-4 p-4 rounded-r-lg ${getRiskColor(pattern.risk_score)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="text-lg font-semibold mb-2">
                  {pattern.pattern_name}
                </h4>
                <p className="text-sm mb-3">{pattern.description}</p>
                <div className="text-xs space-y-1">
                  <p><strong>Triggered Transactions:</strong> {pattern.triggered_transactions.length}</p>
                  {Object.entries(pattern.details).map(([key, value]) => (
                    <p key={key}>
                      <strong>{key.replace(/_/g, ' ')}:</strong> {value}
                    </p>
                  ))}
                </div>
              </div>
              <div className="ml-4 text-right">
                <div className="text-3xl font-bold">{pattern.risk_score}</div>
                <div className="text-xs">Risk Score</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PatternList;
```

```jsx
// src/components/NarrativeDisplay.jsx
import React from 'react';

function NarrativeDisplay({ narrative }) {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-xl p-8 border-2 border-blue-200">
      <div className="flex items-center mb-6">
        <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mr-4">
          <span className="text-2xl">🤖</span>
        </div>
        <h3 className="text-2xl font-bold text-gray-800">
          AI Investigation Narrative
        </h3>
      </div>
      <div className="prose prose-lg max-w-none">
        <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
          {narrative}
        </div>
      </div>
    </div>
  );
}

export default NarrativeDisplay;
```

```jsx
// src/components/TransactionChart.jsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function TransactionChart({ data }) {
  // This is a simplified version - actual implementation would parse transaction data
  const chartData = [
    { date: '2024-01-01', amount: 450, flagged: false },
    { date: '2024-01-02', amount: 320, flagged: false },
    { date: '2024-01-03', amount: 12500, flagged: true },
    // ... more data points
  ];

  return (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <h3 className="text-2xl font-bold text-gray-800 mb-6">
        Transaction Timeline
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="amount"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props;
              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={payload.flagged ? 8 : 4}
                  fill={payload.flagged ? '#ef4444' : '#3b82f6'}
                />
              );
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TransactionChart;
```

### 8.4 API Service

```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 60000; // 60 seconds

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getProfiles = async () => {
  const response = await apiClient.get('/api/profiles');
  return response.data;
};

export const analyzeTransactions = async (data) => {
  const response = await apiClient.post('/api/analyze', data);
  return response.data;
};

export default apiClient;
```

## 9. Deployment Strategy

### 9.1 Single-Command Deployment

**Backend:**
```bash
pip install -r requirements.txt && python app.py
```

**requirements.txt:**
```
Flask==3.0.0
flask-cors==4.0.0
google-generativeai==0.3.2
pandas==2.1.4
python-dateutil==2.8.2
```

**Frontend:**
```bash
npm install && npm start
```

**package.json:**
```json
{
  "name": "transaction-risk-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### 9.2 Environment Setup

**Environment Variables (.env):**
```
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=production
```

### 9.3 Project Structure

```
transaction-risk-investigation-assistant/
├── backend/
│   ├── app.py                      # Flask application
│   ├── models.py                   # Data models
│   ├── rule_engine.py              # Rule engine and detectors
│   ├── gemini_integration.py       # Gemini API integration
│   ├── synthetic_data.py           # Data generator
│   ├── requirements.txt            # Python dependencies
│   └── data/
│       └── profiles.json           # Pre-generated profiles
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   ├── package.json
│   └── vite.config.js
├── .env
├── .gitignore
└── README.md
```

## 10. Error Handling and Timeout Management

### 10.1 Timeout Strategy

**Request Flow Timeline (60-second budget):**
1. Request received: t=0
2. Rule engine analysis: t=0 to t=~2s (fast, deterministic)
3. Gemini narrative generation: t=2s to t=47s (45-second timeout)
4. Response assembly: t=47s to t=50s
5. Response sent: t=50s (10-second buffer)

### 10.2 Error Handling Matrix

| Error Type | HTTP Code | Response | User Experience |
|------------|-----------|----------|-----------------|
| Invalid CSV format | 400 | `{"error": "Invalid CSV format: ..."}` | Error message displayed |
| Missing customer ID | 404 | `{"error": "Customer not found"}` | Error message displayed |
| Gemini API timeout | 200 | Results with `investigation_narrative: null` | Patterns shown without narrative |
| Gemini API failure | 200 | Results with `investigation_narrative: null` | Patterns shown without narrative |
| Internal error | 500 | `{"error": "Internal error: ..."}` | Error message displayed |
| Request timeout | 504 | Gateway timeout | "Analysis taking too long" message |

### 10.3 Graceful Degradation

```python
def analyze_with_timeout(profile: CustomerProfile) -> DetectionResult:
    """
    Analyze with timeout handling and graceful degradation.
    
    Priority:
    1. Always return rule engine results (fast, reliable)
    2. Add Gemini narrative if time permits
    3. Never block beyond 60 seconds
    """
    import time
    
    start_time = time.time()
    
    # Phase 1: Rule engine (always succeeds)
    detection_result = rule_engine.analyze(profile)
    
    # Phase 2: Gemini narrative (optional, with timeout)
    elapsed = time.time() - start_time
    time_remaining = 60 - elapsed
    
    if detection_result.detected_patterns and time_remaining > 15:
        try:
            narrative = gemini_integration.generate_narrative_sync(
                detection_result, profile
            )
            detection_result.investigation_narrative = narrative
        except Exception as e:
            # Log but don't fail - return results without narrative
            print(f"Narrative generation failed: {e}")
    
    return detection_result
```

## 11. Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Rule Engine Determinism

For any transaction record, evaluating it through the rule engine twice should produce identical results.

**Validates: Requirements 2.8**

### Property 2: Large Transfer Detection Accuracy

For any transaction with amount >= $5,000, the large transfer detector should flag it as part of the detected patterns.

**Validates: Requirements 2.2**

### Property 3: Burst Payment Detection Accuracy

For any transaction sequence with 5 or more transactions within 1 hour, the burst payment detector should flag the burst.

**Validates: Requirements 2.3**

### Property 4: Odd-Hours Detection Accuracy

For any transaction occurring between 11 PM (23:00) and 6 AM (06:00), the odd-hours detector should flag it when there are at least 2 such transactions.

**Validates: Requirements 2.4**

### Property 5: Pattern Break Detection Accuracy

For any transaction with amount exceeding 3x the customer's median transaction amount, the pattern break detector should flag it when baseline data is available.

**Validates: Requirements 2.5**

### Property 6: Structuring Detection Accuracy

For any sequence of 3 or more transactions within $1,000 of the $10,000 threshold occurring within 7 days, the structuring detector should flag the pattern.

**Validates: Requirements 2.6**

### Property 7: Velocity Detection Accuracy

For any customer with recent daily transaction rate 2.5x or more than historical rate, the velocity detector should flag the acceleration.

**Validates: Requirements 2.7**

### Property 8: Narrative Generation Contains Required Elements

For any generated investigation narrative, it should contain pattern descriptions, risk assessment, and recommended actions when parsing the text.

**Validates: Requirements 3.4**

### Property 9: API Response Structure Validity

For any valid transaction data posted to /api/analyze, the response should contain the fields: detected_patterns, overall_risk_score, investigation_narrative (may be null), and processing_time_ms.

**Validates: Requirements 8.2**

### Property 10: Input Validation Rejects Malformed Data

For any malformed JSON or CSV input (missing required fields, invalid formats), the API should return HTTP 400 with an error message.

**Validates: Requirements 8.4**

### Property 11: Transaction Record Field Completeness

For any generated or parsed transaction record, it should contain amount, timestamp, merchant, and transaction_type fields with valid values.

**Validates: Requirements 9.1, 9.2, 9.3, 9.4**

### Property 12: CSV Parsing Correctness

For any valid CSV string with standard headers (amount, timestamp, merchant), parsing should produce transaction records with all fields correctly populated.

**Validates: Requirements 9.6**

## 12. Testing Strategy

### 12.1 Property-Based Tests

**Unit tests focus on:**
- Specific examples of each fraud pattern
- Edge cases (empty transactions, single transaction, etc.)
- Error conditions (malformed data, missing fields)

**Property tests focus on:**
- Rule engine determinism across random transaction sets
- Detection accuracy across various transaction patterns
- API response structure across various inputs
- Input validation across various malformed inputs

**Minimum 100 iterations per property test** to ensure comprehensive coverage through randomization.

### 12.2 Integration Tests

- Complete workflow from profile selection to results display
- CSV upload and parsing
- Gemini API integration (with mocks for reliability)
- Frontend-backend communication
- Timeout and error handling

### 12.3 Manual Testing

- Visual design validation
- User experience flow
- Hackathon presentation rehearsal
- Network failure scenarios

## 13. Success Criteria

The design successfully addresses all requirements when:

1. **Deployment:** System starts with single command in under 90 seconds
2. **Detection:** Rule engine correctly detects 4-6 fraud patterns deterministically
3. **Integration:** Gemini generates narratives with fallback on failure
4. **Data:** 4-5 synthetic profiles demonstrate various fraud scenarios
5. **UI:** React frontend displays charts, patterns, and narratives professionally
6. **Performance:** All requests complete within 60 seconds
7. **Reliability:** System handles errors gracefully without crashing

## 14. Future Enhancements (Out of Scope for Hackathon)

- Real-time streaming analysis
- Historical pattern trends
- Multi-customer comparison
- Configurable rule thresholds via UI
- Export investigation reports to PDF
- Integration with actual banking systems

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Programming Language:** Python (Backend), JavaScript/React (Frontend)

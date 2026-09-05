"""
Synthetic data generator for Transaction Risk Investigation Assistant.

Generates customer profiles with various transaction patterns including
clean profiles and profiles with fraud patterns for demonstration purposes.
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
from src.models.transaction import TransactionRecord
from src.models.customer import CustomerProfile, CustomerBaseline


class SyntheticDataGenerator:
    """
    Generates synthetic customer profiles with realistic transaction patterns.
    
    Creates profiles demonstrating:
    - Clean/normal transaction behavior
    - Large transfer fraud patterns
    - Burst payment patterns
    - Structuring patterns (just below $10k threshold)
    - Mixed fraud patterns
    """
    
    # Common merchant names for realistic transactions
    MERCHANTS = {
        'groceries': ['Whole Foods', 'Safeway', 'Trader Joe\'s', 'Kroger'],
        'gas': ['Shell', 'Chevron', 'BP', 'Exxon'],
        'restaurants': ['Chipotle', 'Starbucks', 'McDonald\'s', 'Olive Garden'],
        'online': ['Amazon', 'eBay', 'Etsy', 'Walmart.com'],
        'utilities': ['PG&E', 'Comcast', 'AT&T', 'Water District'],
        'retail': ['Target', 'Best Buy', 'Home Depot', 'Macy\'s']
    }
    
    TRANSACTION_TYPES = ['purchase', 'transfer', 'withdrawal', 'deposit']
    
    def __init__(self, seed: int = 42):
        """
        Initialize the synthetic data generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        random.seed(seed)
        self.base_date = datetime.now() - timedelta(days=60)
    
    def generate_profiles(self) -> List[CustomerProfile]:
        """
        Generate a complete set of customer profiles.
        
        Returns:
            List of CustomerProfile objects with varied patterns
        """
        profiles = [
            self._generate_clean_profile("C001", "Alice Johnson"),
            self._generate_large_transfer_profile("C002", "Bob Martinez"),
            self._generate_burst_payment_profile("C003", "Carol Zhang"),
            self._generate_structuring_profile("C004", "David Kim"),
            self._generate_mixed_fraud_profile("C005", "Emma Wilson")
        ]
        
        return profiles
    
    def _generate_clean_profile(self, customer_id: str, name: str) -> CustomerProfile:
        """
        Generate a customer profile with normal, clean transaction behavior.
        
        Creates realistic patterns:
        - Regular purchases at common merchants
        - Reasonable amounts
        - Normal business hours
        - Consistent frequency
        
        Args:
            customer_id: Customer identifier
            name: Customer name
            
        Returns:
            CustomerProfile with clean transaction history
        """
        transactions = []
        current_date = self.base_date
        
        # Generate 30-40 transactions over 60 days
        for i in range(35):
            # Random day within the period, with some clustering
            days_offset = random.randint(0, 59)
            transaction_date = self.base_date + timedelta(days=days_offset)
            
            # Normal business hours (8 AM - 8 PM)
            hour = random.randint(8, 20)
            minute = random.randint(0, 59)
            timestamp = transaction_date.replace(hour=hour, minute=minute, second=0)
            
            # Select random category and merchant
            category = random.choice(list(self.MERCHANTS.keys()))
            merchant = random.choice(self.MERCHANTS[category])
            
            # Normal transaction amounts
            if category == 'groceries':
                amount = Decimal(str(round(random.uniform(25, 150), 2)))
            elif category == 'gas':
                amount = Decimal(str(round(random.uniform(30, 80), 2)))
            elif category == 'restaurants':
                amount = Decimal(str(round(random.uniform(15, 75), 2)))
            elif category == 'online':
                amount = Decimal(str(round(random.uniform(20, 200), 2)))
            elif category == 'utilities':
                amount = Decimal(str(round(random.uniform(50, 150), 2)))
            else:  # retail
                amount = Decimal(str(round(random.uniform(40, 300), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-{i:03d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=merchant,
                transaction_type='purchase',
                category=category,
                location='Local'
            )
            transactions.append(transaction)
        
        # Sort by timestamp
        transactions.sort(key=lambda t: t.timestamp)
        
        # Calculate baseline
        baseline = self._calculate_baseline(transactions)
        
        return CustomerProfile(
            customer_id=customer_id,
            name=name,
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _generate_large_transfer_profile(self, customer_id: str, name: str) -> CustomerProfile:
        """
        Generate a customer profile with large transfer fraud patterns.
        
        Creates patterns:
        - Normal transactions for baseline
        - 2-3 very large transfers (>= $10,000)
        - Some medium-large transfers ($5,000-$9,999)
        
        Args:
            customer_id: Customer identifier
            name: Customer name
            
        Returns:
            CustomerProfile with large transfer fraud patterns
        """
        transactions = []
        
        # Generate 25 normal transactions for baseline
        for i in range(25):
            days_offset = random.randint(0, 45)
            transaction_date = self.base_date + timedelta(days=days_offset)
            hour = random.randint(8, 20)
            minute = random.randint(0, 59)
            timestamp = transaction_date.replace(hour=hour, minute=minute, second=0)
            
            category = random.choice(['groceries', 'gas', 'restaurants'])
            merchant = random.choice(self.MERCHANTS[category])
            amount = Decimal(str(round(random.uniform(30, 150), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-{i:03d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=merchant,
                transaction_type='purchase',
                category=category,
                location='Local'
            )
            transactions.append(transaction)
        
        # Add large transfers (fraud patterns)
        large_transfer_dates = [
            self.base_date + timedelta(days=50),
            self.base_date + timedelta(days=53),
            self.base_date + timedelta(days=56)
        ]
        
        for idx, date in enumerate(large_transfer_dates):
            hour = random.randint(10, 18)
            timestamp = date.replace(hour=hour, minute=random.randint(0, 59), second=0)
            
            # Very large amounts
            amount = Decimal(str(round(random.uniform(10000, 25000), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-L{idx:02d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant='Wire Transfer' if idx % 2 == 0 else 'International Bank',
                transaction_type='transfer',
                category='transfer',
                location='International' if idx == 2 else 'Domestic'
            )
            transactions.append(transaction)
        
        # Add a couple medium-large transfers
        for idx in range(2):
            date = self.base_date + timedelta(days=48 + idx)
            hour = random.randint(11, 17)
            timestamp = date.replace(hour=hour, minute=random.randint(0, 59), second=0)
            amount = Decimal(str(round(random.uniform(6000, 9500), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-M{idx:02d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant='Bank Transfer',
                transaction_type='transfer',
                category='transfer',
                location='Domestic'
            )
            transactions.append(transaction)
        
        # Sort by timestamp
        transactions.sort(key=lambda t: t.timestamp)
        
        # Calculate baseline from first 25 transactions
        baseline = self._calculate_baseline(transactions[:25])
        
        return CustomerProfile(
            customer_id=customer_id,
            name=name,
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _generate_burst_payment_profile(self, customer_id: str, name: str) -> CustomerProfile:
        """
        Generate a customer profile with burst payment fraud patterns.
        
        Creates patterns:
        - Normal transactions for baseline
        - 10-15 rapid transactions within 1 hour window
        - Multiple bursts to trigger detection
        
        Args:
            customer_id: Customer identifier
            name: Customer name
            
        Returns:
            CustomerProfile with burst payment patterns
        """
        transactions = []
        
        # Generate 20 normal transactions for baseline
        for i in range(20):
            days_offset = random.randint(0, 45)
            transaction_date = self.base_date + timedelta(days=days_offset)
            hour = random.randint(9, 19)
            minute = random.randint(0, 59)
            timestamp = transaction_date.replace(hour=hour, minute=minute, second=0)
            
            category = random.choice(['groceries', 'restaurants', 'online'])
            merchant = random.choice(self.MERCHANTS[category])
            amount = Decimal(str(round(random.uniform(25, 120), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-{i:03d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=merchant,
                transaction_type='purchase',
                category=category,
                location='Local'
            )
            transactions.append(transaction)
        
        # Generate first burst of payments (12 transactions in 45 minutes)
        burst_start = self.base_date + timedelta(days=52, hours=14)
        for i in range(12):
            minutes_offset = i * 3 + random.randint(0, 2)  # Every 3 minutes
            timestamp = burst_start + timedelta(minutes=minutes_offset)
            
            amount = Decimal(str(round(random.uniform(5, 50), 2)))
            merchants = ['Online Merchant', 'E-commerce Store', 'Digital Service', 'Web Purchase']
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-B1-{i:02d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=random.choice(merchants),
                transaction_type='purchase',
                category='online',
                location='Online'
            )
            transactions.append(transaction)
        
        # Generate second burst of payments (8 transactions in 30 minutes)
        burst_start2 = self.base_date + timedelta(days=55, hours=22)
        for i in range(8):
            minutes_offset = i * 3 + random.randint(0, 2)
            timestamp = burst_start2 + timedelta(minutes=minutes_offset)
            
            amount = Decimal(str(round(random.uniform(10, 75), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-B2-{i:02d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant='Fast Payment Service',
                transaction_type='purchase',
                category='online',
                location='Online'
            )
            transactions.append(transaction)
        
        # Sort by timestamp
        transactions.sort(key=lambda t: t.timestamp)
        
        # Calculate baseline from first 20 transactions
        baseline = self._calculate_baseline(transactions[:20])
        
        return CustomerProfile(
            customer_id=customer_id,
            name=name,
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _generate_structuring_profile(self, customer_id: str, name: str) -> CustomerProfile:
        """
        Generate a customer profile with structuring fraud patterns.
        
        Creates patterns:
        - Normal transactions for baseline
        - 4-5 transactions just under $10,000 threshold
        - Amounts between $9,000 and $9,900
        - Within 7-day window
        
        Args:
            customer_id: Customer identifier
            name: Customer name
            
        Returns:
            CustomerProfile with structuring patterns
        """
        transactions = []
        
        # Generate 22 normal transactions for baseline
        for i in range(22):
            days_offset = random.randint(0, 45)
            transaction_date = self.base_date + timedelta(days=days_offset)
            hour = random.randint(9, 18)
            minute = random.randint(0, 59)
            timestamp = transaction_date.replace(hour=hour, minute=minute, second=0)
            
            category = random.choice(['groceries', 'gas', 'retail'])
            merchant = random.choice(self.MERCHANTS[category])
            amount = Decimal(str(round(random.uniform(40, 200), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-{i:03d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=merchant,
                transaction_type='purchase',
                category=category,
                location='Local'
            )
            transactions.append(transaction)
        
        # Generate structuring pattern (5 transactions just under $10k)
        structuring_base = self.base_date + timedelta(days=50)
        structuring_amounts = [9200, 9500, 9100, 9700, 9400]  # All under $10k
        
        for idx, amount_val in enumerate(structuring_amounts):
            days_offset = idx + random.randint(0, 1)  # Within 6 days
            date = structuring_base + timedelta(days=days_offset)
            hour = random.randint(10, 16)
            timestamp = date.replace(hour=hour, minute=random.randint(0, 59), second=0)
            
            amount = Decimal(str(amount_val))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-S{idx:02d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant='Cash Deposit' if idx % 2 == 0 else 'Bank Transfer',
                transaction_type='deposit' if idx % 2 == 0 else 'transfer',
                category='banking',
                location='Bank Branch'
            )
            transactions.append(transaction)
        
        # Sort by timestamp
        transactions.sort(key=lambda t: t.timestamp)
        
        # Calculate baseline from first 22 transactions
        baseline = self._calculate_baseline(transactions[:22])
        
        return CustomerProfile(
            customer_id=customer_id,
            name=name,
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _generate_mixed_fraud_profile(self, customer_id: str, name: str) -> CustomerProfile:
        """
        Generate a customer profile with multiple fraud patterns combined.
        
        Creates patterns:
        - Normal transactions for baseline
        - Large transfers
        - Burst payments
        - Odd-hours activity
        - Pattern breaks
        
        Args:
            customer_id: Customer identifier
            name: Customer name
            
        Returns:
            CustomerProfile with mixed fraud patterns
        """
        transactions = []
        
        # Generate 18 normal transactions for baseline
        for i in range(18):
            days_offset = random.randint(0, 40)
            transaction_date = self.base_date + timedelta(days=days_offset)
            hour = random.randint(9, 18)
            minute = random.randint(0, 59)
            timestamp = transaction_date.replace(hour=hour, minute=minute, second=0)
            
            category = random.choice(['groceries', 'gas', 'restaurants'])
            merchant = random.choice(self.MERCHANTS[category])
            amount = Decimal(str(round(random.uniform(30, 120), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-{i:03d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant=merchant,
                transaction_type='purchase',
                category=category,
                location='Local'
            )
            transactions.append(transaction)
        
        # Add large transfer
        large_transfer_date = self.base_date + timedelta(days=48, hours=15)
        transaction = TransactionRecord(
            transaction_id=f"{customer_id}-LT01",
            customer_id=customer_id,
            amount=Decimal('12500.00'),
            timestamp=large_transfer_date,
            merchant='Wire Transfer',
            transaction_type='transfer',
            category='transfer',
            location='International'
        )
        transactions.append(transaction)
        
        # Add burst of payments (7 transactions in 40 minutes)
        burst_start = self.base_date + timedelta(days=52, hours=23, minutes=15)  # Odd hours
        for i in range(7):
            minutes_offset = i * 5 + random.randint(0, 2)
            timestamp = burst_start + timedelta(minutes=minutes_offset)
            amount = Decimal(str(round(random.uniform(15, 60), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-B{i:02d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant='Online Gaming Site',
                transaction_type='purchase',
                category='online',
                location='Online'
            )
            transactions.append(transaction)
        
        # Add odd-hours transactions
        odd_hours_dates = [
            self.base_date + timedelta(days=50, hours=2),   # 2 AM
            self.base_date + timedelta(days=51, hours=3),   # 3 AM
            self.base_date + timedelta(days=54, hours=1),   # 1 AM
        ]
        
        for idx, odd_date in enumerate(odd_hours_dates):
            timestamp = odd_date.replace(minute=random.randint(0, 59), second=0)
            amount = Decimal(str(round(random.uniform(100, 500), 2)))
            
            transaction = TransactionRecord(
                transaction_id=f"{customer_id}-OH{idx:02d}",
                customer_id=customer_id,
                amount=amount,
                timestamp=timestamp,
                merchant='ATM Withdrawal' if idx % 2 == 0 else 'Late Night Store',
                transaction_type='withdrawal' if idx % 2 == 0 else 'purchase',
                category='cash' if idx % 2 == 0 else 'convenience',
                location='ATM' if idx % 2 == 0 else 'Unknown'
            )
            transactions.append(transaction)
        
        # Add pattern break - unusual merchant
        pattern_break_date = self.base_date + timedelta(days=55, hours=14)
        transaction = TransactionRecord(
            transaction_id=f"{customer_id}-PB01",
            customer_id=customer_id,
            amount=Decimal('450.00'),  # Higher than baseline
            timestamp=pattern_break_date,
            merchant='Luxury Jewelry Store',  # New merchant type
            transaction_type='purchase',
            category='luxury',
            location='Upscale Mall'
        )
        transactions.append(transaction)
        
        # Sort by timestamp
        transactions.sort(key=lambda t: t.timestamp)
        
        # Calculate baseline from first 18 transactions
        baseline = self._calculate_baseline(transactions[:18])
        
        return CustomerProfile(
            customer_id=customer_id,
            name=name,
            transactions=transactions,
            baseline_stats=baseline
        )
    
    def _calculate_baseline(self, transactions: List[TransactionRecord]) -> CustomerBaseline:
        """
        Calculate customer baseline statistics from transaction history.
        
        Args:
            transactions: List of transaction records to analyze
            
        Returns:
            CustomerBaseline with calculated statistics
        """
        if not transactions:
            # Return default baseline if no transactions
            return CustomerBaseline(
                avg_transaction_amount=Decimal('0'),
                median_transaction_amount=Decimal('0'),
                avg_daily_transaction_count=0.0,
                common_merchants=[],
                common_transaction_types=[],
                typical_hours=[]
            )
        
        # Calculate amounts
        amounts = [t.amount for t in transactions]
        avg_amount = sum(amounts) / len(amounts)
        sorted_amounts = sorted(amounts)
        median_amount = sorted_amounts[len(sorted_amounts) // 2]
        
        # Calculate daily transaction count
        date_counts = {}
        for t in transactions:
            date_key = t.timestamp.date()
            date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        avg_daily_count = sum(date_counts.values()) / len(date_counts) if date_counts else 0.0
        
        # Extract common merchants, types, and hours
        merchant_counts = {}
        type_counts = {}
        hour_counts = {}
        
        for t in transactions:
            merchant_counts[t.merchant] = merchant_counts.get(t.merchant, 0) + 1
            type_counts[t.transaction_type] = type_counts.get(t.transaction_type, 0) + 1
            hour_counts[t.timestamp.hour] = hour_counts.get(t.timestamp.hour, 0) + 1
        
        # Get top merchants, types, and hours
        common_merchants = sorted(
            merchant_counts.keys(),
            key=lambda m: merchant_counts[m],
            reverse=True
        )[:5]
        
        common_types = sorted(
            type_counts.keys(),
            key=lambda t: type_counts[t],
            reverse=True
        )[:3]
        
        typical_hours = sorted(
            hour_counts.keys(),
            key=lambda h: hour_counts[h],
            reverse=True
        )[:8]
        
        return CustomerBaseline(
            avg_transaction_amount=avg_amount,
            median_transaction_amount=median_amount,
            avg_daily_transaction_count=avg_daily_count,
            common_merchants=common_merchants,
            common_transaction_types=common_types,
            typical_hours=typical_hours
        )

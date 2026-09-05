"""
Utility functions for loading and managing customer profiles.
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from src.models.transaction import TransactionRecord
from src.models.customer import CustomerProfile, CustomerBaseline


def load_profiles(filepath: str = 'data/profiles.json') -> List[CustomerProfile]:
    """
    Load customer profiles from JSON file.
    
    Args:
        filepath: Path to the profiles JSON file
        
    Returns:
        List of CustomerProfile objects
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    profiles = []
    for p_data in data['profiles']:
        # Load transactions
        transactions = [TransactionRecord.from_dict(t) for t in p_data['transactions']]
        
        # Load baseline if present
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


def get_profile_by_id(customer_id: str, profiles: List[CustomerProfile]) -> Optional[CustomerProfile]:
    """
    Get a specific customer profile by ID.
    
    Args:
        customer_id: Customer identifier
        profiles: List of profiles to search
        
    Returns:
        CustomerProfile if found, None otherwise
    """
    for profile in profiles:
        if profile.customer_id == customer_id:
            return profile
    return None

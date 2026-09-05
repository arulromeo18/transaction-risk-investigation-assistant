"""
Transaction Risk Investigation Assistant
Main Flask application entry point
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from io import StringIO
import pandas as pd
from datetime import datetime
from decimal import Decimal

from src.rule_engine import RuleEngine
from src.data_loader import load_profiles, get_profile_by_id
from src.models.customer import CustomerProfile, CustomerBaseline
from src.models.transaction import TransactionRecord

app = Flask(__name__)
CORS(app)

# Initialize components
rule_engine = RuleEngine()
profiles_cache = []

# Load profiles on startup
try:
    profiles_cache = load_profiles('data/profiles.json')
    print(f"Loaded {len(profiles_cache)} customer profiles")
except Exception as e:
    print(f"Warning: Could not load profiles: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify service is running."""
    return jsonify({
        'status': 'healthy',
        'service': 'Transaction Risk Investigation Assistant',
        'detectors_count': len(rule_engine.detectors),
        'profiles_loaded': len(profiles_cache)
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint."""
    return jsonify({
        'message': 'Transaction Risk Investigation Assistant API',
        'version': '1.0.0',
        'track_id': 'PS6',
        'endpoints': {
            'health': '/health',
            'profiles': '/api/profiles',
            'analyze': '/api/analyze'
        }
    }), 200

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """
    Get list of pre-loaded customer profiles.
    
    Returns:
        JSON array of customer profiles (without full transaction data)
    """
    try:
        profile_list = [
            {
                'customer_id': p.customer_id,
                'name': p.name,
                'transaction_count': len(p.transactions)
            }
            for p in profiles_cache
        ]
        return jsonify({'profiles': profile_list}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve profiles: {str(e)}'}), 500

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
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Load or parse profile
        if 'customer_id' in data:
            profile = get_profile_by_id(data['customer_id'], profiles_cache)
            if not profile:
                return jsonify({'error': f'Customer {data["customer_id"]} not found'}), 404
        elif 'transactions' in data:
            profile = _parse_transaction_json(data['transactions'], data.get('customer_id', 'CUSTOM'))
        elif 'csv_data' in data:
            profile = _parse_transaction_csv(data['csv_data'])
        else:
            return jsonify({'error': 'No transaction data provided. Include customer_id, transactions, or csv_data'}), 400
        
        # Run rule engine
        detection_result = rule_engine.analyze(profile)
        
        # TODO: Add Gemini narrative generation in next phase
        
        return jsonify(detection_result.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

def _parse_transaction_json(transactions_data: list, customer_id: str) -> CustomerProfile:
    """
    Parse transactions from JSON array.
    
    Args:
        transactions_data: List of transaction dictionaries
        customer_id: Customer identifier
        
    Returns:
        CustomerProfile with transactions and calculated baseline
    """
    transactions = [TransactionRecord.from_dict(t) for t in transactions_data]
    
    # Calculate baseline from transactions
    baseline = CustomerBaseline.calculate_from_transactions(transactions)
    
    return CustomerProfile(
        customer_id=customer_id,
        name=f"Custom Upload - {customer_id}",
        transactions=transactions,
        baseline_stats=baseline
    )

def _parse_transaction_csv(csv_data: str) -> CustomerProfile:
    """
    Parse transactions from CSV string.
    
    Expected columns: transaction_id, customer_id, amount, timestamp, merchant, transaction_type
    Optional columns: category, location
    
    Args:
        csv_data: CSV string with transaction data
        
    Returns:
        CustomerProfile with transactions and calculated baseline
    """
    try:
        df = pd.read_csv(StringIO(csv_data))
        
        # Check required columns
        required_cols = ['amount', 'timestamp', 'merchant']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV must contain columns: {missing_cols}")
        
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
        
        # Calculate baseline
        baseline = CustomerBaseline.calculate_from_transactions(transactions)
        
        return CustomerProfile(
            customer_id=customer_id,
            name=f"CSV Upload - {customer_id}",
            transactions=transactions,
            baseline_stats=baseline
        )
    except Exception as e:
        raise ValueError(f"CSV parsing failed: {str(e)}")

if __name__ == '__main__':
    print("Starting Transaction Risk Investigation Assistant...")
    print(f"Loaded {len(rule_engine.detectors)} fraud detectors")
    print(f"Loaded {len(profiles_cache)} customer profiles")
    print("Server listening on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)

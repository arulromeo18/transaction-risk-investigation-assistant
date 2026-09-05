"""
Transaction Risk Investigation Assistant
Main Flask application entry point
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify service is running."""
    return jsonify({
        'status': 'healthy',
        'service': 'Transaction Risk Investigation Assistant'
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint."""
    return jsonify({
        'message': 'Transaction Risk Investigation Assistant API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'profiles': '/api/profiles',
            'analyze': '/api/analyze'
        }
    }), 200

if __name__ == '__main__':
    print("Starting Transaction Risk Investigation Assistant...")
    print("Server listening on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)

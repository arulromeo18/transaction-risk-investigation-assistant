**TRACK_ID=PS6**

# Transaction Risk Investigation Assistant

A fraud detection demonstration system designed for hackathon presentations. The system processes customer transaction data through a deterministic rule-based engine to identify suspicious patterns, generates natural language investigation narratives using Gemini API, and presents findings through a professional web interface.

## Features

- **Deterministic Fraud Detection**: Rule-based engine with 4-6 distinct fraud patterns
  - Large Transfer Detection
  - Burst Payment Detection
  - Odd-Hours Activity Detection
  - Pattern Break Detection
  - Structuring Detection
  - Velocity Detection

- **AI-Powered Narratives**: Gemini API integration for generating investigation summaries

- **Pre-built Synthetic Data**: 4-5 customer profiles with known fraud patterns for demonstration

- **Professional Web Interface**: React + Tailwind CSS with data visualizations

- **Single-Command Deployment**: No external dependencies or configuration required

## Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend development)
- Gemini API key (optional - system works without it, but narratives won't be generated)

## Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd transaction-risk-investigation-assistant
pip install -r requirements.txt
```

## Running the Application

Start the backend server with a single command:

```bash
pip install -r requirements.txt && python app.py
```

The server will start on http://localhost:8000

Expected startup time: < 90 seconds

## Configuration

### Environment Variables

- `GEMINI_API_KEY` (optional): Your Gemini API key for narrative generation
  - If not set, the system will return fraud detection results without AI-generated narratives

```bash
# On Windows
set GEMINI_API_KEY=your_api_key_here

# On Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

## API Documentation

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Transaction Risk Investigation Assistant"
}
```

### GET /api/profiles

Retrieve list of pre-loaded customer profiles.

**Response:**
```json
{
  "profiles": [
    {
      "customer_id": "CUST001",
      "name": "Clean Profile",
      "transaction_count": 50
    }
  ]
}
```

### POST /api/analyze

Analyze transactions for fraud patterns.

**Request Body:**
```json
{
  "customer_id": "CUST001"
}
```

Or with custom transaction data:
```json
{
  "transactions": [
    {
      "transaction_id": "TXN001",
      "customer_id": "CUST999",
      "amount": "5000.00",
      "timestamp": "2024-01-15T14:30:00",
      "merchant": "Online Store",
      "transaction_type": "purchase"
    }
  ]
}
```

Or with CSV data:
```json
{
  "csv_data": "transaction_id,customer_id,amount,timestamp,merchant,transaction_type\nTXN001,CUST999,5000.00,2024-01-15T14:30:00,Online Store,purchase"
}
```

**Response:**
```json
{
  "customer_id": "CUST001",
  "detected_patterns": [
    {
      "pattern_name": "Large Transfer",
      "pattern_type": "large_transfer",
      "risk_score": 90,
      "description": "Detected 2 large transaction(s) with maximum amount $15000.00",
      "triggered_transactions": ["TXN123", "TXN124"],
      "details": {
        "max_amount": "15000.00",
        "transaction_count": 2,
        "threshold": "5000"
      }
    }
  ],
  "overall_risk_score": 90,
  "investigation_narrative": "AI-generated narrative here...",
  "processing_time_ms": 1250
}
```

## Usage

### Using Pre-loaded Profiles

1. Get list of available profiles: `GET /api/profiles`
2. Analyze a profile: `POST /api/analyze` with `{"customer_id": "CUST001"}`

### Uploading Custom CSV Data

Send a POST request to `/api/analyze` with CSV data in the `csv_data` field.

Required CSV columns:
- `transaction_id`: Unique transaction identifier
- `customer_id`: Customer identifier
- `amount`: Transaction amount (decimal)
- `timestamp`: Transaction timestamp (ISO format)
- `merchant`: Merchant name
- `transaction_type`: Type of transaction (purchase, transfer, withdrawal, deposit)

Optional columns:
- `category`: Merchant category
- `location`: Transaction location

## Project Structure

```
transaction-risk-investigation-assistant/
├── app.py                    # Flask application entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules
├── data/                    # Synthetic data files
│   └── profiles.json        # Pre-loaded customer profiles
├── src/                     # Source code
│   ├── models/              # Data models
│   │   ├── transaction.py   # Transaction record model
│   │   ├── customer.py      # Customer profile model
│   │   └── detection.py     # Detection result models
│   ├── detectors/           # Fraud pattern detectors
│   │   ├── base.py          # Base detector class
│   │   ├── large_transfer.py
│   │   ├── burst_payment.py
│   │   ├── odd_hours.py
│   │   ├── pattern_break.py
│   │   ├── structuring.py
│   │   └── velocity.py
│   ├── rule_engine.py       # Main rule engine
│   ├── gemini_integration.py # Gemini API integration
│   └── data_generator.py    # Synthetic data generator
└── frontend/                # React frontend (to be implemented)
```

## Development Timeline

This project follows an incremental development approach:

1. **Phase 1**: Scaffold & Project Setup
2. **Phase 2**: Synthetic Data Generation
3. **Phase 3**: Deterministic Rule Engine
4. **Phase 4**: Backend API Endpoints
5. **Phase 5**: Gemini API Integration
6. **Phase 6**: Frontend Implementation
7. **Phase 7**: Frontend Production Build
8. **Phase 8**: End-to-End Testing & Documentation

## Troubleshooting

### Server won't start

- Verify Python 3.11+ is installed: `python --version`
- Check if port 8000 is already in use
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Slow startup

- First run may take longer due to dependency installation
- Expected startup time: < 90 seconds after dependencies are installed

### No investigation narratives

- Check if `GEMINI_API_KEY` environment variable is set
- System works without API key but won't generate AI narratives
- Verify API key is valid

### API timeout

- Analysis should complete within 60 seconds
- If Gemini API is slow, system will return results without narrative
- Check network connectivity if using Gemini API

## License

This is a demonstration project for hackathon purposes.

## Support

For issues or questions, please refer to the project documentation or contact the development team.

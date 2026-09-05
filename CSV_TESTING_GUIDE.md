# CSV Upload Testing Guide

## Sample CSV File: sample_transactions.csv

This file demonstrates the CSV upload feature with suspicious transactions that will trigger multiple fraud patterns.

### Transaction Summary:
- **8 transactions** from customer "CSV_TEST"
- **Normal transactions (3):** Starbucks, Whole Foods, Shell (days 1-2)
- **Suspicious transactions (3):** Late-night purchases at 11:45 PM - 11:58 PM on the same day
  - $1,250 from "Unknown Vendor" 
  - $1,450 from "Suspicious LLC" (International)
  - $1,680 Cash Advance (high-risk category)
- **Recovery transactions (2):** Target, Chipotle (normal behavior resumed)

### Expected Detection Results:

#### Patterns That Should Trigger:
1. **Velocity Spike (Risk: 80-85):**
   - 3 transactions within 13 minutes (23:45 - 23:58)
   - Rapid-fire pattern indicative of card testing or fraud

2. **Odd Hours Activity (Risk: 70-75):**
   - All 3 suspicious transactions occurred between 11:45 PM - 11:58 PM
   - Outside normal business hours

3. **Unusual Merchant (Risk: 75-80):**
   - "Unknown Vendor" and "Suspicious LLC" are not in baseline
   - First-time merchants with large amounts

4. **Amount Outlier (Risk: 80-90):**
   - $1,250, $1,450, $1,680 are significantly higher than baseline avg (~$370)
   - 3-4x larger than normal transactions

5. **High-Risk Category (Risk: 85-90):**
   - Cash Advance of $1,680 (high-risk transaction type)

6. **Geographic Anomaly (Risk: 75-80):**
   - "Suspicious LLC" marked as "International"
   - Unexpected location

### Expected Overall Risk Score: 85-92/100 🚨

---

## How to Test CSV Upload

### Method 1: Using the Web Interface (If Implemented)
1. Start the application: `python app.py`
2. Open http://localhost:8000
3. Look for "Upload CSV" button or file input
4. Select `sample_transactions.csv`
5. Click "Analyze"

### Method 2: Using PowerShell API Call
```powershell
# Make sure server is running first
$csvContent = Get-Content sample_transactions.csv -Raw
$body = @{ csv_data = $csvContent } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" -Method POST -Body $body -ContentType "application/json"
```

### Method 3: Using Python
```python
import requests

with open("sample_transactions.csv", "r") as f:
    csv_data = f.read()

response = requests.post(
    "http://localhost:8000/api/analyze",
    json={"csv_data": csv_data}
)

print(response.json())
```

---

## CSV Format Requirements

The API accepts CSV files with the following columns:

**Required:**
- `amount` (numeric)
- `timestamp` (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)
- `merchant` (string)

**Optional:**
- `transaction_id` (string) - auto-generated if missing
- `customer_id` (string) - defaults to "CSV_UPLOAD"
- `transaction_type` (string) - defaults to "purchase"
- `category` (string)
- `location` (string)

**Example:**
```csv
transaction_id,customer_id,amount,timestamp,merchant,transaction_type,category,location
TXN001,CUST123,45.99,2026-09-01T10:30:00,Starbucks,purchase,restaurants,Local
TXN002,CUST123,125.50,2026-09-01T14:22:00,Whole Foods,purchase,groceries,Local
```

---

## What Makes This CSV Suspicious?

This sample demonstrates a common fraud pattern:

1. **Establish Normal Behavior** (Txn 1-3):
   - Small to medium purchases at known merchants
   - Normal business hours
   - Creates baseline for comparison

2. **Fraud Attack** (Txn 4-6):
   - **Timing:** All within 13 minutes late at night
   - **Merchants:** Unknown/suspicious vendors
   - **Amounts:** 10-15x larger than normal
   - **Location:** International transaction appears
   - **Type:** Cash advance (high-risk)

3. **Cover Tracks** (Txn 7-8):
   - Return to normal behavior
   - Attempt to look legitimate
   - But system already flagged the anomalies

This pattern mimics real-world card theft where fraudsters:
- Test the card with small purchases
- Rush to extract maximum value quickly
- Use multiple merchants to spread risk
- Mix in legitimate-looking transactions

**The AI system should generate a narrative highlighting the suspicious 13-minute window and recommending immediate card freeze + customer contact.**

---

## Success Criteria

✅ CSV file parses correctly  
✅ 8 transactions loaded  
✅ Baseline calculated from data  
✅ Multiple fraud patterns detected  
✅ Risk score 85+ assigned  
✅ AI narrative generated (if Gemini API key set)  
✅ Response time <60 seconds  

---

**Ready to test!** The sample CSV is designed to trigger multiple alarms and demonstrate the system's capabilities.

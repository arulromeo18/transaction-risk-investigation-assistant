# Implementation Plan: Transaction Risk Investigation Assistant

## Overview

This implementation plan follows a specific build order optimized for a hackathon presentation. The system will be built incrementally, starting with scaffolding, then synthetic data, core rule engine, backend APIs, Gemini integration, frontend, and finally end-to-end testing. Each task builds on previous work to ensure continuous progress without orphaned code.

**TRACK_ID: PS6** - This identifier must appear as the first line of README.md

**Key Constraints:**
- Single-command startup: `pip install -r requirements.txt && python app.py`
- Startup time: < 90 seconds
- API request timeout: < 60 seconds
- Port: 8000
- Python: 3.11
- No external database or configuration files

## Tasks

### Phase 1: Scaffold & Project Setup

- [x] 1. Create project structure and initial files
  - Create app.py with minimal Flask application
  - Create requirements.txt with all dependencies (Flask, google-generativeai, pandas, python-dateutil, flask-cors)
  - Create README.md with **TRACK_ID=PS6** as first line and setup instructions
  - Create folder structure: data/, src/, src/detectors/, src/models/
  - Initialize git repository and create .gitignore
  - _Requirements: 1.1, 1.3, 1.4, 1.5_

- [-] 2. Verify basic Flask application starts
  - Run `pip install -r requirements.txt && python app.py` to verify startup
  - Confirm server listens on port 8000
  - Add health check endpoint at /health
  - Measure startup time (should be < 90s)
  - _Requirements: 1.1, 1.2, 1.3_

### Phase 2: Synthetic Data Generation

- [x] 3. Implement data models
  - [x] 3.1 Create TransactionRecord dataclass in src/models/transaction.py
    - Implement to_dict() and from_dict() methods
    - Include all required fields: transaction_id, customer_id, amount, timestamp, merchant, transaction_type
    - Support optional fields: category, location
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 3.2 Create CustomerProfile and CustomerBaseline dataclasses in src/models/customer.py
    - Implement to_dict() methods for JSON serialization
    - Include baseline statistics calculation
    - _Requirements: 4.3_

- [ ] 4. Implement synthetic data generator
  - [x] 4.1 Create SyntheticDataGenerator class in src/data_generator.py
    - Implement _generate_clean_profile() for normal activity
    - Implement _generate_large_transfer_profile() with fraud patterns
    - Implement _generate_burst_payment_profile() with rapid transactions
    - Implement _generate_structuring_profile() with amounts just under $10k threshold
    - Implement _generate_mixed_fraud_profile() with multiple fraud patterns
    - Implement _calculate_baseline() for computing customer statistics
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6_
  
  - [~] 4.2 Generate and save synthetic data to data/profiles.json
    - Generate 4-5 customer profiles with varied patterns
    - Save profiles with timestamps
    - Implement load_profiles() function to read from JSON
    - _Requirements: 4.1, 4.5_

- [~] 5. Checkpoint - Verify synthetic data
  - Load profiles from data/profiles.json
  - Verify each profile contains appropriate transaction counts and patterns
  - Ensure all tests pass, ask the user if questions arise.

### Phase 3: Deterministic Rule Engine

- [ ] 6. Create rule engine architecture
  - [~] 6.1 Create FraudDetector abstract base class in src/detectors/base.py
    - Define detect() abstract method
    - Define pattern_name and pattern_type properties
    - _Requirements: 2.8_
  
  - [~] 6.2 Create FraudPattern and DetectionResult dataclasses in src/models/detection.py
    - Implement to_dict() methods for API responses
    - Include risk_score, description, triggered_transactions fields
    - _Requirements: 2.8, 3.2_
  
  - [~] 6.3 Create RuleEngine class in src/rule_engine.py
    - Implement analyze() method that runs all detectors
    - Calculate overall risk score (max of individual scores)
    - Track processing time
    - _Requirements: 2.8, 2.9_

- [ ] 7. Implement core fraud pattern detectors (4 required patterns)
  - [~] 7.1 Implement LargeTransferDetector in src/detectors/large_transfer.py
    - Detect transactions >= $5,000 (medium risk) or >= $10,000 (high risk)
    - Return risk score 70 (medium) or 90 (high)
    - _Requirements: 2.2, 2.8_
  
  - [ ]* 7.2 Write property test for LargeTransferDetector
    - **Property 1: Threshold detection consistency**
    - For any transaction list, if all transactions are below $5,000, LargeTransferDetector should return None
    - **Validates: Requirements 2.2**
  
  - [~] 7.3 Implement BurstPaymentDetector in src/detectors/burst_payment.py
    - Detect >= 5 transactions in 1 hour (medium risk) or >= 10 in 1 hour (high risk)
    - Use sliding window approach
    - Return risk score 65 (medium) or 85 (high)
    - _Requirements: 2.3, 2.8_
  
  - [ ]* 7.4 Write property test for BurstPaymentDetector
    - **Property 2: Sliding window consistency**
    - For any sorted transaction list with timestamps, if no 1-hour window contains >= 5 transactions, BurstPaymentDetector should return None
    - **Validates: Requirements 2.3**
  
  - [~] 7.5 Implement OddHoursDetector in src/detectors/odd_hours.py
    - Detect transactions between 11 PM and 6 AM
    - Require >= 2 transactions (medium risk) or >= 5 (high risk)
    - Return risk score 55 (medium) or 75 (high)
    - _Requirements: 2.4, 2.8_
  
  - [ ]* 7.6 Write property test for OddHoursDetector
    - **Property 3: Hour range detection**
    - For any transaction list where all transactions occur between 6 AM and 11 PM, OddHoursDetector should return None
    - **Validates: Requirements 2.4**
  
  - [~] 7.7 Implement PatternBreakDetector in src/detectors/pattern_break.py
    - Detect amounts > 3x median baseline
    - Detect new merchants not in baseline
    - Detect unusual transaction types
    - Return risk score 50-80 based on break count
    - _Requirements: 2.5, 2.8_
  
  - [ ]* 7.8 Write property test for PatternBreakDetector
    - **Property 4: Baseline consistency**
    - For any transaction list matching the baseline (same merchants, types, and amounts within 3x median), PatternBreakDetector should return None
    - **Validates: Requirements 2.5**

- [ ] 8. Implement additional fraud pattern detectors (2 optional patterns if time permits)
  - [~] 8.1 Implement StructuringDetector in src/detectors/structuring.py
    - Detect >= 3 transactions just below $10,000 within 7 days
    - Check for amounts between $9,000 and $10,000
    - Return risk score 70-80 based on total amount
    - _Requirements: 2.6, 2.8_
  
  - [ ]* 8.2 Write property test for StructuringDetector
    - **Property 5: Structuring threshold detection**
    - For any transaction list where no transactions fall between $9,000 and $10,000, StructuringDetector should return None
    - **Validates: Requirements 2.6**
  
  - [~] 8.3 Implement VelocityDetector in src/detectors/velocity.py
    - Compare recent 7 days to previous 23 days
    - Detect >= 2.5x increase in frequency or amount
    - Return risk score 60-85 based on acceleration
    - _Requirements: 2.7, 2.8_
  
  - [ ]* 8.4 Write property test for VelocityDetector
    - **Property 6: Velocity acceleration detection**
    - For any transaction list with constant daily frequency and amount, VelocityDetector should return None
    - **Validates: Requirements 2.7**

- [~] 9. Integrate detectors into RuleEngine
  - Register all 4-6 detectors in RuleEngine._register_detectors()
  - Verify analyze() runs all detectors and aggregates results
  - Test with synthetic profiles
  - _Requirements: 2.1, 2.8_

- [~] 10. Checkpoint - Rule engine verification
  - Run rule engine on all synthetic profiles
  - Verify clean profile triggers no patterns
  - Verify fraud profiles trigger >= 2 patterns each
  - Ensure all tests pass, ask the user if questions arise.

### Phase 4: Backend API Endpoints

- [ ] 11. Implement API endpoints in app.py
  - [~] 11.1 Implement GET /api/profiles endpoint
    - Return list of pre-loaded customer profiles (without full transaction data)
    - Include customer_id, name, and transaction_count
    - _Requirements: 8.3_
  
  - [~] 11.2 Implement POST /api/analyze endpoint
    - Accept customer_id for pre-loaded profiles
    - Accept transactions array for custom data
    - Accept csv_data string for CSV uploads
    - Return DetectionResult JSON
    - _Requirements: 8.1, 8.2_
  
  - [~] 11.3 Implement request validation and error handling
    - Return HTTP 400 for malformed requests
    - Return HTTP 404 for unknown customer_id
    - Return HTTP 500 for internal errors with details
    - _Requirements: 8.4, 8.5_
  
  - [~] 11.4 Implement CSV parsing function
    - Parse CSV string using pandas
    - Map columns to TransactionRecord fields
    - Handle missing optional fields
    - _Requirements: 9.6_
  
  - [~] 11.5 Enable CORS for frontend communication
    - Add flask-cors to allow cross-origin requests during development
    - _Requirements: 8.6_

- [ ]* 12. Write integration tests for API endpoints
  - Test GET /api/profiles returns valid profile list
  - Test POST /api/analyze with customer_id
  - Test POST /api/analyze with custom transaction data
  - Test error handling for invalid inputs
  - _Requirements: 6.3, 8.1, 8.2, 8.4, 8.5_

- [~] 13. Checkpoint - API verification
  - Test all endpoints with curl or Postman
  - Verify request timeout < 60 seconds for analysis
  - Ensure all tests pass, ask the user if questions arise.

### Phase 5: Gemini API Integration

- [ ] 14. Implement Gemini integration
  - [~] 14.1 Create GeminiIntegration class in src/gemini_integration.py
    - Initialize with API key from environment variable GEMINI_API_KEY
    - Use gemini-1.5-flash model
    - _Requirements: 3.1_
  
  - [~] 14.2 Implement narrative generation with timeout
    - Implement generate_narrative_async() with 45-second timeout
    - Implement _build_prompt() to structure detection results
    - Include retry logic for transient failures
    - _Requirements: 3.3, 3.4, 6.1_
  
  - [~] 14.3 Implement synchronous wrapper for Flask
    - Implement generate_narrative_sync() using asyncio
    - Handle asyncio event loop in Flask context
    - _Requirements: 3.1, 3.3_
  
  - [~] 14.4 Implement fallback handling
    - Return None on timeout or API failure
    - Log errors without crashing
    - _Requirements: 3.5, 6.2_

- [~] 15. Integrate Gemini into API endpoint
  - Add Gemini narrative generation to POST /api/analyze
  - Only call Gemini if patterns are detected and time permits (< 50s elapsed)
  - Set investigation_narrative field in DetectionResult
  - Verify end-to-end request completes within 60 seconds
  - _Requirements: 3.3, 6.1, 6.2_

- [ ]* 16. Write integration tests for Gemini integration
  - Test narrative generation succeeds with valid API key
  - Test fallback when GEMINI_API_KEY is not set
  - Test timeout handling
  - _Requirements: 3.5, 6.2_

- [~] 17. Checkpoint - Gemini integration verification
  - Set GEMINI_API_KEY environment variable
  - Test analysis with narrative generation
  - Verify graceful fallback when API key is missing
  - Ensure all tests pass, ask the user if questions arise.

### Phase 6: Frontend Implementation

- [ ] 18. Create React application structure
  - [~] 18.1 Initialize React app with Vite
    - Create package.json with React 18, Tailwind CSS 3, Recharts, Axios
    - Configure Tailwind CSS
    - Create src/ folder structure
    - _Requirements: 5.1, 5.2_
  
  - [~] 18.2 Create API service client in src/services/api.js
    - Implement getProfiles() function
    - Implement analyzeTransactions() function
    - Configure base URL for backend (http://localhost:8000)
    - _Requirements: 8.1, 8.2_

- [ ] 19. Implement core UI components
  - [~] 19.1 Create App.jsx main component
    - Implement state management for profiles, results, loading, errors
    - Load profiles on mount
    - Implement handleProfileSelect() and handleFileUpload()
    - Create professional gradient background (slate-900, blue-900)
    - _Requirements: 5.6, 6.5_
  
  - [~] 19.2 Create ProfileSelector component
    - Dropdown for selecting pre-loaded customer profiles
    - Disable during loading
    - _Requirements: 5.7_
  
  - [~] 19.3 Create FileUpload component
    - File input for CSV upload
    - Read and parse CSV file
    - Send csv_data to backend
    - Disable during loading
    - _Requirements: 5.8, 5.9_
  
  - [~] 19.4 Create LoadingSpinner component
    - Professional loading animation
    - Display during API calls
    - _Requirements: 6.5_
  
  - [~] 19.5 Create ErrorDisplay component
    - Display error messages with styling
    - Show meaningful error text
    - _Requirements: 6.3_

- [ ] 20. Implement results visualization components
  - [~] 20.1 Create PatternList component
    - Display detected fraud patterns as cards
    - Show pattern name, risk score, description, details
    - Color-code by risk level (red >= 80, yellow >= 60, green < 60)
    - _Requirements: 5.4, 5.6, 10.6, 10.8_
  
  - [~] 20.2 Create NarrativeDisplay component
    - Display Gemini-generated investigation narrative
    - Format with proper sections and styling
    - Show placeholder when narrative is not available
    - _Requirements: 5.5, 10.7_
  
  - [~] 20.3 Create TransactionChart component
    - Use Recharts to visualize transactions over time
    - Display amount vs. timestamp
    - Highlight flagged transactions
    - _Requirements: 5.3, 10.1, 10.5_
  
  - [~] 20.4 Create risk score header display
    - Large risk score number with color coding
    - Customer ID and analysis metadata
    - _Requirements: 5.6, 10.3_

- [ ]* 21. Write component tests
  - Test ProfileSelector renders and handles selection
  - Test FileUpload handles file input
  - Test PatternList displays patterns correctly
  - Test error and loading states
  - _Requirements: 5.1, 5.6_

- [~] 22. Checkpoint - Frontend verification
  - Run frontend development server
  - Test profile selection and analysis
  - Test CSV upload flow
  - Verify charts and visualizations render
  - Ensure all tests pass, ask the user if questions arise.

### Phase 7: Frontend Production Build

- [ ] 23. Build and integrate frontend with backend
  - [~] 23.1 Create production build
    - Run `npm run build` to create dist/ folder
    - Verify build completes successfully
    - _Requirements: 5.6_
  
  - [~] 23.2 Configure Flask to serve frontend static files
    - Update app.py to serve dist/index.html at root route
    - Serve static assets from dist/ folder
    - Ensure API routes still work at /api/*
    - _Requirements: 1.1_
  
  - [~] 23.3 Commit production build files to git
    - Add dist/ folder to git (don't .gitignore it)
    - Commit with message describing production build
    - _Requirements: 7.1, 7.2, 7.4_

- [~] 24. Checkpoint - Production build verification
  - Start app.py and verify frontend loads at http://localhost:8000
  - Test all features through production build
  - Ensure all tests pass, ask the user if questions arise.

### Phase 8: End-to-End Testing & Documentation

- [ ] 25. Perform fresh-clone test
  - [~] 25.1 Clone repository to clean directory
    - Simulate fresh deployment
    - _Requirements: 7.1, 7.2_
  
  - [~] 25.2 Run single-command startup
    - Execute `pip install -r requirements.txt && python app.py`
    - Verify startup completes in < 90 seconds
    - Verify server listens on port 8000
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [~] 25.3 Test complete workflow
    - Open http://localhost:8000 in browser
    - Select pre-loaded profile and verify analysis
    - Upload CSV file and verify analysis
    - Verify all detected patterns display correctly
    - Verify investigation narrative appears (if GEMINI_API_KEY is set)
    - Verify charts and visualizations render
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_
  
  - [~] 25.4 Measure performance
    - Verify API requests complete in < 60 seconds
    - Test with and without GEMINI_API_KEY
    - Test concurrent requests
    - _Requirements: 6.1, 6.2, 6.4_

- [ ]* 26. Write end-to-end integration tests
  - Test complete analysis workflow from profile selection to results display
  - Test CSV upload workflow
  - Test error handling and fallback scenarios
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [ ] 27. Finalize documentation
  - [~] 27.1 Complete README.md
    - Verify TRACK_ID=PS6 is first line
    - Add project description and features
    - Add setup instructions (prerequisites, installation, running)
    - Add usage instructions (selecting profiles, uploading CSV, interpreting results)
    - Add API documentation
    - Add environment variables section (GEMINI_API_KEY optional)
    - Add troubleshooting section
    - _Requirements: 1.1, 7.5_
  
  - [~] 27.2 Review git commit history
    - Verify commits show incremental progress
    - Verify commit messages are descriptive
    - Ensure each major milestone has a commit
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [~] 27.3 Create final presentation checklist
    - Document startup procedure
    - List demonstration scenarios (clean profile, fraud profiles)
    - Note key talking points (deterministic rules, Gemini narratives, visualizations)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [~] 28. Final checkpoint - System ready for presentation
  - Verify all features work end-to-end
  - Verify documentation is complete and accurate
  - Verify git history shows incremental development
  - System is ready for hackathon presentation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- **Optional Tasks**: Tasks marked with `*` are test-related sub-tasks that can be skipped for faster MVP delivery. Property tests validate universal correctness properties from the design document, while integration tests verify end-to-end workflows.

- **Build Order**: The task sequence follows the user's specified build order:
  1. Scaffold (Tasks 1-2)
  2. Synthetic data (Tasks 3-5)
  3. Rule engine (Tasks 6-10)
  4. Backend APIs (Tasks 11-13)
  5. Gemini integration (Tasks 14-17)
  6. Frontend development (Tasks 18-22)
  7. Production build (Tasks 23-24)
  8. End-to-end testing (Tasks 25-28)

- **No Orphaned Code**: Each task builds on previous work and integrates immediately. The rule engine is tested with synthetic data before API development. APIs are tested with curl before frontend development. Frontend is built against working APIs. Production build is committed and verified before final testing.

- **Checkpoints**: Regular checkpoints ensure incremental validation. Each checkpoint task includes "Ensure all tests pass, ask the user if questions arise" to catch issues early.

- **Time-Sensitive Requirements**: The 90-second startup and 60-second request constraints are verified explicitly in tasks 2, 13, 17, and 25.4.

- **Gemini API Key**: The system works without GEMINI_API_KEY (returns detection results only). With the key, it generates investigation narratives. This flexibility is tested in task 17.

- **Property-Based Tests**: Six properties from the design document are implemented as separate sub-tasks. Each property validates universal correctness properties of specific fraud detectors.

- **Requirements Traceability**: Each task explicitly references the requirements it implements, ensuring complete coverage.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1", "3.1", "3.2"] },
    { "id": 1, "tasks": ["2", "4.1"] },
    { "id": 2, "tasks": ["4.2"] },
    { "id": 3, "tasks": ["6.1", "6.2"] },
    { "id": 4, "tasks": ["6.3", "7.1"] },
    { "id": 5, "tasks": ["7.2", "7.3"] },
    { "id": 6, "tasks": ["7.4", "7.5"] },
    { "id": 7, "tasks": ["7.6", "7.7"] },
    { "id": 8, "tasks": ["7.8", "8.1"] },
    { "id": 9, "tasks": ["8.2", "8.3"] },
    { "id": 10, "tasks": ["8.4", "9"] },
    { "id": 11, "tasks": ["11.1", "11.2", "11.3"] },
    { "id": 12, "tasks": ["11.4", "11.5"] },
    { "id": 13, "tasks": ["12"] },
    { "id": 14, "tasks": ["14.1", "14.2"] },
    { "id": 15, "tasks": ["14.3", "14.4"] },
    { "id": 16, "tasks": ["15"] },
    { "id": 17, "tasks": ["16"] },
    { "id": 18, "tasks": ["18.1", "18.2"] },
    { "id": 19, "tasks": ["19.1", "19.2", "19.3"] },
    { "id": 20, "tasks": ["19.4", "19.5", "20.1"] },
    { "id": 21, "tasks": ["20.2", "20.3", "20.4"] },
    { "id": 22, "tasks": ["21"] },
    { "id": 23, "tasks": ["23.1"] },
    { "id": 24, "tasks": ["23.2"] },
    { "id": 25, "tasks": ["23.3"] },
    { "id": 26, "tasks": ["25.1", "25.2"] },
    { "id": 27, "tasks": ["25.3", "25.4"] },
    { "id": 28, "tasks": ["26", "27.1"] },
    { "id": 29, "tasks": ["27.2", "27.3"] }
  ]
}
```

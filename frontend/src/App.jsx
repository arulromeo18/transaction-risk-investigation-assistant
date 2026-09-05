import { useState, useEffect } from 'react';
import './index.css';
import { getProfiles, analyzeTransactions } from './api';

function App() {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const data = await getProfiles();
      setProfiles(data.profiles);
    } catch (err) {
      setError('Failed to load profiles: ' + err.message);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedProfile) return;
    
    setError(null);
    setLoading(true);
    setAnalysisResult(null);

    try {
      const result = await analyzeTransactions({ customer_id: selectedProfile });
      setAnalysisResult(result);
    } catch (err) {
      setError('Analysis failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score) => {
    if (score >= 80) return 'text-red-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getRiskBgColor = (score) => {
    if (score >= 80) return 'bg-red-100 border-red-500';
    if (score >= 60) return 'bg-yellow-100 border-yellow-500';
    return 'bg-green-100 border-green-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-white mb-4">
            Transaction Risk Investigation Assistant
          </h1>
          <p className="text-xl text-blue-200">
            AI-Powered Fraud Detection & Analysis
          </p>
          <p className="text-sm text-blue-300 mt-2">
            TRACK_ID: PS6
          </p>
        </header>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-2xl p-6 mb-8">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Customer Profile
              </label>
              <select
                value={selectedProfile}
                onChange={(e) => setSelectedProfile(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">-- Choose a customer --</option>
                {profiles.map((p) => (
                  <option key={p.customer_id} value={p.customer_id}>
                    {p.customer_id}: {p.name} ({p.transaction_count} transactions)
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={handleAnalyze}
              disabled={!selectedProfile || loading}
              className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Analyzing...' : 'Analyze Transactions'}
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-xl p-12 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Analyzing transaction patterns...</p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg shadow-lg mb-8">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-red-800 font-medium">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {analysisResult && !loading && (
          <div className="space-y-8">
            {/* Risk Score Header */}
            <div className="bg-white rounded-lg shadow-2xl p-8">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold text-gray-800 mb-2">
                    Analysis Results
                  </h2>
                  <p className="text-gray-600">
                    Customer: {analysisResult.customer_id}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Processing Time: {analysisResult.processing_time_ms}ms
                  </p>
                </div>
                <div className="text-center">
                  <div className={`text-7xl font-bold ${getRiskColor(analysisResult.overall_risk_score)}`}>
                    {analysisResult.overall_risk_score}
                  </div>
                  <div className="text-sm text-gray-600 mt-2 font-medium">Overall Risk Score</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {analysisResult.overall_risk_score >= 80 ? 'HIGH RISK' :
                     analysisResult.overall_risk_score >= 60 ? 'MEDIUM RISK' : 'LOW RISK'}
                  </div>
                </div>
              </div>
            </div>

            {/* Detected Patterns */}
            <div className="bg-white rounded-lg shadow-2xl p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Detected Fraud Patterns ({analysisResult.detected_patterns.length})
              </h3>
              {analysisResult.detected_patterns.length === 0 ? (
                <div className="text-center py-8">
                  <svg className="mx-auto h-16 w-16 text-green-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-xl text-gray-600 font-medium">No Fraud Patterns Detected</p>
                  <p className="text-gray-500 mt-2">This account appears to have normal transaction activity.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {analysisResult.detected_patterns.map((pattern, idx) => (
                    <div
                      key={idx}
                      className={`border-l-4 p-6 rounded-r-lg ${getRiskBgColor(pattern.risk_score)}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-xl font-semibold mb-2 text-gray-900">
                            {pattern.pattern_name}
                          </h4>
                          <p className="text-gray-700 mb-4">{pattern.description}</p>
                          <div className="text-sm space-y-2">
                            <p className="font-medium text-gray-900">
                              <span className="font-bold">Triggered Transactions:</span> {pattern.triggered_transactions.length}
                            </p>
                            <div className="grid grid-cols-2 gap-2 mt-3">
                              {Object.entries(pattern.details).map(([key, value]) => (
                                <p key={key} className="text-gray-700">
                                  <span className="font-semibold">{key.replace(/_/g, ' ')}:</span> {value}
                                </p>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="ml-6 text-right">
                          <div className={`text-5xl font-bold ${getRiskColor(pattern.risk_score)}`}>
                            {pattern.risk_score}
                          </div>
                          <div className="text-xs text-gray-600 mt-1">Risk Score</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Investigation Narrative */}
            {analysisResult.investigation_narrative && (
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-2xl p-8 border-2 border-blue-200">
                <div className="flex items-center mb-6">
                  <div className="w-14 h-14 bg-blue-600 rounded-full flex items-center justify-center mr-4">
                    <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800">
                      AI Investigation Narrative
                    </h3>
                    <p className="text-sm text-gray-600">Generated by Gemini AI</p>
                  </div>
                </div>
                <div className="prose prose-lg max-w-none">
                  <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                    {analysisResult.investigation_narrative}
                  </div>
                </div>
              </div>
            )}

            {!analysisResult.investigation_narrative && analysisResult.detected_patterns.length > 0 && (
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-lg shadow-lg">
                <div className="flex items-center">
                  <svg className="h-6 w-6 text-yellow-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-yellow-800">
                    <span className="font-semibold">Note:</span> AI narrative not available. Set GEMINI_API_KEY environment variable to enable narrative generation.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Initial State */}
        {!analysisResult && !loading && !error && (
          <div className="bg-white rounded-lg shadow-xl p-12 text-center">
            <svg className="mx-auto h-24 w-24 text-gray-400 mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-2xl font-semibold text-gray-700 mb-4">
              Select a Customer Profile to Begin
            </h3>
            <p className="text-gray-500 max-w-2xl mx-auto">
              Choose a customer from the dropdown above and click "Analyze Transactions" to detect fraud patterns 
              and generate an investigation report.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

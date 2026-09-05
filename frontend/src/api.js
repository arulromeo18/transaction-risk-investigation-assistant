import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
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

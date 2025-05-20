import axios from 'axios';

const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_BASE_URL,
  timeout: parseInt(process.env.EXPO_PUBLIC_API_TIMEOUT) || 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

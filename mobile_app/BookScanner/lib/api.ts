import axios from 'axios';
import { getAccessToken } from './auth';
import { getRefreshToken, saveTokens, removeTokens } from './auth';

const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_BASE_URL,
  timeout: parseInt(process.env.EXPO_PUBLIC_API_TIMEOUT) || 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add access token to headers
api.interceptors.request.use(async (config) => {
  const token = await getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


// Add response interceptor to handle token refresh on 401
let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (error: any) => void }> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (token) {
      resolve(token);
    } else {
      reject(error);
    }
  });
  failedQueue = [];
};

export const refreshAccessToken = async (): Promise<string | null> => {
  const refresh = await getRefreshToken();
  if (!refresh) return null;

  try {
    const response = await api.post('/token/refresh/', { refresh });
    const newAccessToken = response.data.access;
    const newRefreshToken = response.data.refresh ?? refresh;

    await saveTokens(newAccessToken, newRefreshToken);
    return newAccessToken;
  } catch (error) {
    await removeTokens();
    return null;
  }
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = 'Bearer ' + token;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newAccessToken = await refreshAccessToken();
        originalRequest.headers.Authorization = 'Bearer ' + newAccessToken;
        processQueue(null, newAccessToken);
        return api(originalRequest);
      } catch (err) {
        processQueue(err, null);
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;

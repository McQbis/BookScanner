import axios from 'axios';
import { getRefreshToken, saveTokens } from './auth';
import { Toast } from 'react-native-toast-message/lib/src/Toast';

export const refreshAccessToken = async (): Promise<string | null> => {
  const refresh = await getRefreshToken();
  if (!refresh) return null;

  try {
    const response = await axios.post(
      `${process.env.EXPO_PUBLIC_API_BASE_URL}/token/refresh/`,
      { refresh },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: parseInt(process.env.EXPO_PUBLIC_API_TIMEOUT) || 5000,
      }
    );

    const newAccessToken = response.data.access;
    const newRefreshToken = response.data.refresh ?? refresh;

    await saveTokens(newAccessToken, newRefreshToken);
    return newAccessToken;
  } catch (error) {
    return null;
  }
};

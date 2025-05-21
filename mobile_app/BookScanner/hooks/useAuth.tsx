import { useEffect, useState, createContext, useContext } from 'react';
import { saveTokens, getAccessToken, removeTokens, getRefreshToken } from '@/lib/auth';
import { refreshAccessToken } from '@/lib/api';
import { router } from 'expo-router';

type User = { email: string };
type AuthContextType = {
  user: User | null;
  token: string | null;
  login: (access: string, refresh: string, user: User) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      let access = await getAccessToken();
      if (!access) {
        access = await refreshAccessToken();
      }

      if (access) {
        setToken(access);
        setUser({ email: 'from_storage@example.com' });
      }

      setIsLoading(false);
    };
    bootstrap();
  }, []);

  const login = async (access: string, refresh: string, user: User) => {
    await saveTokens(access, refresh);
    setToken(access);
    setUser(user);
    router.replace('/photo-catalog');
  };

  const logout = async () => {
    await removeTokens();
    setToken(null);
    setUser(null);
    router.replace('/');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};
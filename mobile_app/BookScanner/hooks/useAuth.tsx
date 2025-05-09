import { useEffect, useState, createContext, useContext } from 'react';
import { saveToken, getToken, removeToken } from '@/lib/auth';
import { router } from 'expo-router';

type User = { email: string };
type AuthContextType = {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => Promise<void>;
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
      const token = await getToken();
      if (token) {
        setToken(token);
        setUser({ email: 'from_storage@example.com' });
      }
      setIsLoading(false);
    };
    bootstrap();
  }, []);

  const login = async (token: string, user: User) => {
    await saveToken(token);
    setToken(token);
    setUser(user);
    router.replace('/photo-catalog');
  };

  const logout = async () => {
    await removeToken();
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
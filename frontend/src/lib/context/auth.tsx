// frontend/src/lib/context/auth.tsx
'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  user: any; // In a real app, you'd have a proper User type
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string) => Promise<void>;
  isAuthenticated: boolean;
  verifyUser: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in on initial load
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Verify the token with the backend
      verifyUser();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('auth_token', data.access_token);
        // Use the actual user data from the response instead of hardcoded values
        setUser(data.user);
        router.push('/tasks');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, password: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        // Registration successful, redirect to login
        router.push('/login');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    // Import the authAPI to use its logout method
    const { authAPI } = await import('../api/auth');
    await authAPI.logout();
    setUser(null);
    router.push('/login');
  };

  const verifyUser = async (): Promise<boolean> => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');

      if (!token) {
        setUser(null);
        return false;
      }

      // Verify token and get user info by making a request to the /me endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        // Token is valid, set user with actual data from the backend
        const userData = await response.json();
        setUser(userData);
        return true;
      } else {
        // Token is invalid, clear it and redirect to login
        localStorage.removeItem('auth_token');
        setUser(null);
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          router.push('/login');
        }
        return false;
      }
    } catch (error) {
      console.error('Error verifying user:', error);
      localStorage.removeItem('auth_token');
      setUser(null);
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        router.push('/login');
      }
      return false;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    register,
    verifyUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;}

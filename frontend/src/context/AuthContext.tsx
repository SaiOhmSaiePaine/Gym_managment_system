import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface User {
  id: string;
  name: string;
  email: string;
  created_at?: string;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Create Auth Context
export const AuthContext = createContext<AuthContextType | null>(null);

// Custom hook for using auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

// Auth Provider Component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          // Configure axios headers
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Get user information
          const response = await axios.get(`${API_URL}/api/users/me`);
          setUser(response.data);
        } catch (err) {
          console.error('Authentication error:', err);
          // Clear invalid token
          logout();
        } finally {
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, [token]);

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      setIsLoading(true);
      
      const response = await axios.post(`${API_URL}/api/users/login`, {
        email,
        password
      });
      
      const { token, user } = response.data;
      
      // Save token to local storage
      localStorage.setItem('token', token);
      
      // Set axios default headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Update state
      setToken(token);
      setUser(user);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed');
      throw new Error(err.response?.data?.error || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      setError(null);
      setIsLoading(true);
      
      const response = await axios.post(`${API_URL}/api/users/register`, {
        name,
        email,
        password
      });
      
      const { token, user } = response.data;
      
      // Save token to local storage
      localStorage.setItem('token', token);
      
      // Set axios default headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Update state
      setToken(token);
      setUser(user);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Registration failed');
      throw new Error(err.response?.data?.error || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    // Remove token from local storage
    localStorage.removeItem('token');
    
    // Remove axios default headers
    delete axios.defaults.headers.common['Authorization'];
    
    // Update state
    setToken(null);
    setUser(null);
  };
  
  const isAuthenticated = !!token && !!user;
  
  const value = {
    token,
    user,
    login,
    register,
    logout,
    isAuthenticated,
    isLoading,
    error
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;

"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';

interface WorkbenchUser {
  id: string;
  username: string;
  email: string;
  role: 'checker' | 'admin';
  isVerified: boolean;
  permissions: string[];
  full_name?: string;
}

interface WorkbenchAuthContextType {
  user: WorkbenchUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (dynamicToken: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
  isAdmin: () => boolean;
  isChecker: () => boolean;
  token: string | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const WorkbenchAuthContext = createContext<WorkbenchAuthContextType | undefined>(undefined);

export function WorkbenchAuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<WorkbenchUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const checkExistingAuth = async () => {
      try {
        const storedToken = localStorage.getItem('workbench_token');
        if (storedToken) {
          // Verify token with backend
          const response = await fetch(`${API_BASE_URL}/api/workbench/auth/verify`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${storedToken}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            if (data.valid && data.user) {
              setUser(data.user);
              setToken(storedToken);
            }
          } else {
            // Invalid token, remove it
            localStorage.removeItem('workbench_token');
          }
        }
      } catch (error) {
        console.error('Error verifying workbench token:', error);
        localStorage.removeItem('workbench_token');
      } finally {
        setIsLoading(false);
      }
    };

    checkExistingAuth();
  }, []);

  const login = async (dynamicToken: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/workbench/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          dynamic_token: dynamicToken
        })
      });

      const data = await response.json();

      if (data.success && data.user && data.token) {
        setUser(data.user);
        setToken(data.token);
        localStorage.setItem('workbench_token', data.token);
      } else {
        throw new Error(data.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (token) {
        // Notify backend of logout
        await fetch(`${API_BASE_URL}/api/workbench/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('workbench_token');
    }
  };

  const hasPermission = (permission: string): boolean => {
    return user?.permissions.includes(permission) || false;
  };

  const isAdmin = (): boolean => {
    return user?.role === 'admin' || false;
  };

  const isChecker = (): boolean => {
    return user?.role === 'checker' || false;
  };

  const value: WorkbenchAuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    hasPermission,
    isAdmin,
    isChecker,
    token
  };

  return (
    <WorkbenchAuthContext.Provider value={value}>
      {children}
    </WorkbenchAuthContext.Provider>
  );
}

export function useWorkbenchAuth() {
  const context = useContext(WorkbenchAuthContext);
  if (context === undefined) {
    throw new Error('useWorkbenchAuth must be used within a WorkbenchAuthProvider');
  }
  return context;
}

// HOC for protecting workbench routes
export function withWorkbenchAuth<P extends object>(
  Component: React.ComponentType<P>,
  requiredPermissions?: string[]
) {
  return function ProtectedComponent(props: P) {
    const { isAuthenticated, isLoading, hasPermission, user } = useWorkbenchAuth();

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    if (!isAuthenticated) {
      // Redirect to login if not authenticated
      if (typeof window !== 'undefined') {
        window.location.href = '/workbench/login';
      }
      return null;
    }

    // Check required permissions
    if (requiredPermissions && requiredPermissions.length > 0) {
      const hasRequiredPermissions = requiredPermissions.some(permission => 
        hasPermission(permission)
      );

      if (!hasRequiredPermissions) {
        return (
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Access Denied
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                You don't have permission to access this resource.
              </p>
              <p className="text-sm text-gray-500">
                Required permissions: {requiredPermissions.join(', ')}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Your role: {user?.role}
              </p>
            </div>
          </div>
        );
      }
    }

    return <Component {...props} />;
  };
}
import { useState, useEffect } from 'react';

export const useDynamicAuth = () => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [mockUser, setMockUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Check if Dynamic.xyz is configured
  const isDynamicConfigured = !!process.env.NEXT_PUBLIC_DYNAMIC_ENVIRONMENT_ID;

  let dynamicContext: any = {};
  
  if (isDynamicConfigured) {
    try {
      // Only import Dynamic context if configured
      const { useDynamicContext } = require('@dynamic-labs/sdk-react-core');
      dynamicContext = useDynamicContext();
    } catch (error) {
      console.warn('Dynamic.xyz SDK not available:', error);
    }
  }

  const { 
    isAuthenticated: dynamicIsAuthenticated = false, 
    user: dynamicUser = null, 
    primaryWallet = null,
    isLoading: dynamicLoading = false,
    handleLogIn = async () => {},
    handleLogOut = async () => {}
  } = dynamicContext;

  // Mock authentication for development when Dynamic.xyz is not configured
  const [mockIsAuthenticated, setMockIsAuthenticated] = useState(false);

  useEffect(() => {
    if (!isDynamicConfigured) {
      // Check for mock authentication in localStorage
      const mockAuth = localStorage.getItem('mock_auth');
      if (mockAuth) {
        setMockIsAuthenticated(true);
        setMockUser(JSON.parse(mockAuth));
        setAuthToken('mock_jwt_token');
      }
    }
  }, [isDynamicConfigured]);

  // Use Dynamic.xyz auth if configured, otherwise use mock auth
  const isAuthenticated = isDynamicConfigured ? dynamicIsAuthenticated : mockIsAuthenticated;
  const currentUser = isDynamicConfigured ? dynamicUser : mockUser;
  const currentLoading = isDynamicConfigured ? dynamicLoading : isLoading;

  // Convert user to our format
  const user = currentUser ? {
    id: currentUser.userId || currentUser.id || 'demo-user',
    wallet: primaryWallet?.address || currentUser.wallet,
    email: currentUser.email || 'demo@example.com',
    ...currentUser
  } : null;

  useEffect(() => {
    // Get JWT token for API calls
    if (isAuthenticated) {
      if (isDynamicConfigured && primaryWallet) {
        // In a real implementation, you'd get a JWT from your backend
        // after verifying the wallet signature
        const token = localStorage.getItem('auth_token') || 'dynamic_jwt_token';
        setAuthToken(token);
      } else if (!isDynamicConfigured) {
        setAuthToken('mock_jwt_token');
      }
    } else {
      setAuthToken(null);
      if (!isDynamicConfigured) {
        localStorage.removeItem('mock_auth');
      }
      localStorage.removeItem('auth_token');
    }
  }, [isAuthenticated, primaryWallet, isDynamicConfigured]);

  const login = async () => {
    try {
      if (isDynamicConfigured) {
        await handleLogIn();
        // After successful login, redirect to chat
        if (dynamicIsAuthenticated) {
          window.location.href = '/chat';
        }
      } else {
        // Mock login
        setIsLoading(true);
        const mockUserData = {
          id: 'demo-user',
          email: 'demo@example.com',
          wallet: '0x1234...5678'
        };
        localStorage.setItem('mock_auth', JSON.stringify(mockUserData));
        setMockUser(mockUserData);
        setMockIsAuthenticated(true);
        setIsLoading(false);
        window.location.href = '/chat';
      }
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoading(false);
    }
  };

  const signup = async () => {
    // Both Dynamic.xyz and mock handle signup the same as login
    return login();
  };

  const logout = async () => {
    try {
      if (isDynamicConfigured) {
        await handleLogOut();
      } else {
        // Mock logout
        setMockIsAuthenticated(false);
        setMockUser(null);
        localStorage.removeItem('mock_auth');
      }
      setAuthToken(null);
      localStorage.removeItem('auth_token');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return {
    isAuthenticated,
    user,
    isLoading: currentLoading,
    authToken,
    wallet: primaryWallet,
    login,
    signup,
    logout
  };
};
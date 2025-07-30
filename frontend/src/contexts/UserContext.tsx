'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useDynamicContext } from '@dynamic-labs/sdk-react-core';

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  walletAddress?: string;
  plan: 'free' | 'plus' | 'enterprise';
  credits: number;
  monthlyCredits: number;
  planExpiry?: string;
  createdAt: string;
  lastLogin: string;
}

export interface UserContextType {
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: () => void;
  logout: () => void;
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;
  consumeCredits: (amount: number) => Promise<boolean>;
  purchaseCredits: (amount: number) => Promise<void>;
  upgradePlan: (plan: string) => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

const PLANS = {
  free: { credits: 500, price: 0 },
  plus: { credits: 5000, price: 20 },
  enterprise: { credits: 'custom', price: 'custom' },
};

export function UserProvider({ children }: { children: React.ReactNode }) {
  const { user: dynamicUser, setShowAuthFlow, handleLogOut, isAuthenticated } = useDynamicContext();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user profile when Dynamic user changes
  useEffect(() => {
    const loadUserProfile = async () => {
      if (!dynamicUser || !isAuthenticated) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      try {
        // Try to load existing user profile
        const userId = dynamicUser.userId || dynamicUser.verifiedCredentials[0]?.address || dynamicUser.email;
        const storedProfile = localStorage.getItem(`user_profile_${userId}`);
        
        if (storedProfile) {
          const profile = JSON.parse(storedProfile);
          setUser(profile);
        } else {
          // Create new user profile
          const newProfile: UserProfile = {
            id: userId,
            email: dynamicUser.email || `${userId}@handywriterz.ai`,
            name: dynamicUser.alias || dynamicUser.email?.split('@')[0] || 'User',
            avatar: dynamicUser.avatar,
            walletAddress: dynamicUser.verifiedCredentials[0]?.address,
            plan: 'free',
            credits: 500,
            monthlyCredits: 500,
            planExpiry: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 year for free plan
            createdAt: new Date().toISOString(),
            lastLogin: new Date().toISOString(),
          };
          
          localStorage.setItem(`user_profile_${userId}`, JSON.stringify(newProfile));
          setUser(newProfile);
        }
      } catch (error) {
        console.error('Error loading user profile:', error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadUserProfile();
  }, [dynamicUser, isAuthenticated]);

  const login = () => {
    setShowAuthFlow(true);
  };

  const logout = async () => {
    await handleLogOut();
    setUser(null);
  };

  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!user) return;

    const updatedUser = { ...user, ...updates };
    setUser(updatedUser);
    localStorage.setItem(`user_profile_${user.id}`, JSON.stringify(updatedUser));
  };

  const consumeCredits = async (amount: number): Promise<boolean> => {
    if (!user || user.credits < amount) {
      return false;
    }

    await updateProfile({ credits: user.credits - amount });
    return true;
  };

  const purchaseCredits = async (amount: number) => {
    if (!user) return;

    // In a real app, this would integrate with payment processing
    await updateProfile({ credits: user.credits + amount });
  };

  const upgradePlan = async (plan: string) => {
    if (!user) return;

    const planData = PLANS[plan as keyof typeof PLANS];
    if (!planData) return;

    const planExpiry = new Date();
    planExpiry.setMonth(planExpiry.getMonth() + 1);

    await updateProfile({
      plan: plan as 'free' | 'plus' | 'enterprise',
      monthlyCredits: typeof planData.credits === 'number' ? planData.credits : user.monthlyCredits,
      credits: typeof planData.credits === 'number' ? planData.credits : user.credits,
      planExpiry: planExpiry.toISOString(),
    });
  };

  const value: UserContextType = {
    user,
    isLoading,
    isAuthenticated: isAuthenticated && !!user,
    login,
    logout,
    updateProfile,
    consumeCredits,
    purchaseCredits,
    upgradePlan,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
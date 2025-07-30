'use client'

import React, { useState, useEffect } from 'react'
import { X, User, Activity, Grid, Users, MessageSquare, Settings, Shield, Copy, ExternalLink, CreditCard } from 'lucide-react'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { ThemeSelector } from '@/components/ThemeSelector'
import { useTheme } from '@/contexts/ThemeContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/components/ui/use-toast'
import { useRouter } from 'next/navigation'

interface SettingsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface BillingSummary {
  plan: string;
  renew_date: string;
  usage_usd: number;
  credits_remaining: number;
  max_words: number;
  features: string[];
}

interface UserProfile {
  email: string;
  user_id: string;
  wallet_address?: string;
  avatar?: string;
  display_name?: string;
}

type SettingsTab = 'profile' | 'usage' | 'general' | 'community' | 'feedback' | 'api' | 'terms'

const settingsTabs = [
  { id: 'profile' as SettingsTab, icon: User, label: 'Profile' },
  { id: 'usage' as SettingsTab, icon: Activity, label: 'Usage' },
  { id: 'general' as SettingsTab, icon: Grid, label: 'General' },
  { id: 'community' as SettingsTab, icon: Users, label: 'Community' },
  { id: 'feedback' as SettingsTab, icon: MessageSquare, label: 'Feedback' },
  { id: 'api' as SettingsTab, icon: Settings, label: 'API Setting' },
  { id: 'terms' as SettingsTab, icon: Shield, label: 'Term & Policy' },
]

export function SettingsModal({ open, onOpenChange }: SettingsModalProps) {
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile')
  const [billingSummary, setBillingSummary] = useState<BillingSummary | null>(null)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(false)
  const { theme, setTheme } = useTheme()
  const { toast } = useToast()
  const router = useRouter()

  // Load user data when modal opens
  useEffect(() => {
    if (open) {
      loadUserData()
    }
  }, [open])

  const loadUserData = async () => {
    setLoading(true)
    try {
      // Load billing summary
      const billingResponse = await fetch('/api/billing/summary', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      
      if (billingResponse.ok) {
        const billingData = await billingResponse.json()
        setBillingSummary(billingData)
      }

      // Load user profile (mock for now - replace with Dynamic.xyz data)
      setUserProfile({
        email: 'user@example.com',
        user_id: 'demo-user',
        display_name: 'Demo User',
        wallet_address: '0x1234...5678'
      })
    } catch (error) {
      console.error('Error loading user data:', error)
      toast({
        title: "Error",
        description: "Failed to load user data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "Copied",
      description: "Link copied to clipboard",
    })
  }

  const handleUpgrade = () => {
    onOpenChange(false)
    router.push('/pricing')
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        if (loading || !userProfile) {
          return (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          )
        }

        return (
          <div className="space-y-6">
            {/* User Profile Section */}
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-lg font-semibold text-white">
                  {userProfile.display_name?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {userProfile.display_name || 'User'}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {userProfile.email}
                </p>
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Account Information</p>
            </div>

            {/* Account Details */}
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-900 dark:text-gray-100">{userProfile.email}</span>
                  <Button variant="outline" size="sm" className="ml-4">
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Manage via Dynamic
                  </Button>
                </div>
              </div>

              {userProfile.wallet_address && (
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Wallet Address</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400 font-mono">{userProfile.wallet_address}</span>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => copyToClipboard(userProfile.wallet_address!)}
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}

              {/* Invite Friends Section */}
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Invite friends</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                  Get 10 bonus credits for you and your invitees when they make their first purchase
                </p>
                <div className="flex items-center space-x-2">
                  <Input
                    value={`https://handywriterz.ai/signup?ref=${userProfile.user_id}`}
                    readOnly
                    className="flex-1 text-sm bg-gray-50 dark:bg-gray-800"
                  />
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => copyToClipboard(`https://handywriterz.ai/signup?ref=${userProfile.user_id}`)}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )

      case 'usage':
        if (loading || !billingSummary) {
          return (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          )
        }

        const creditsUsedPercent = billingSummary.credits_remaining > 0 
          ? ((100 - billingSummary.credits_remaining) / 100) * 100 
          : 0

        return (
          <div className="space-y-6">
            {/* Plan Section */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/50 dark:to-purple-900/50 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Current Plan</h3>
                <Button onClick={handleUpgrade} className="bg-blue-600 hover:bg-blue-700 text-white">
                  <CreditCard className="w-4 h-4 mr-2" />
                  Upgrade Plan
                </Button>
              </div>
              
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold">
                    {billingSummary.plan.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <div className="flex items-center gap-3">
                    <h4 className="text-xl font-bold text-gray-900 dark:text-white capitalize">
                      {billingSummary.plan} Plan
                    </h4>
                    <Badge 
                      variant={billingSummary.plan === 'free' ? 'secondary' : 'default'}
                      className="capitalize"
                    >
                      {billingSummary.plan}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {billingSummary.renew_date !== 'N/A' ? `Renews on ${billingSummary.renew_date}` : 'No renewal date'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Credits Remaining</p>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {billingSummary.credits_remaining}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Monthly Usage</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    ${billingSummary.usage_usd.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            {/* Credits Progress */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-base font-medium text-gray-900 dark:text-white">Credit Usage</h3>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {billingSummary.credits_remaining} credits remaining
                </span>
              </div>
              <Progress 
                value={creditsUsedPercent} 
                className="h-3 mb-4" 
              />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Credits reset {billingSummary.renew_date !== 'N/A' ? `on ${billingSummary.renew_date}` : 'each month'}
              </p>
            </div>

            {/* Plan Features */}
            <div>
              <h3 className="text-base font-medium text-gray-900 dark:text-white mb-4">Plan Features</h3>
              <div className="grid grid-cols-1 gap-2">
                {billingSummary.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                    <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button variant="outline" onClick={handleUpgrade} className="flex-1">
                View All Plans
              </Button>
              <Button variant="outline" onClick={() => router.push('/pricing')} className="flex-1">
                Buy Credits
              </Button>
            </div>
          </div>
        )

      case 'general':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Theme</h3>
              <div className="grid grid-cols-3 gap-4">
                <button
                  onClick={() => setTheme('system')}
                  className={`p-4 rounded-lg border-2 transition-colors text-center ${
                    theme === 'system'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <Settings className="h-6 w-6 text-gray-600 dark:text-gray-400 mx-auto mb-2" />
                  <div className="text-sm font-medium text-gray-900 dark:text-white">System Mode</div>
                </button>
                
                <button
                  onClick={() => setTheme('light')}
                  className={`p-4 rounded-lg border-2 transition-colors text-center ${
                    theme === 'light'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <div className="h-6 w-6 bg-white border border-gray-300 rounded-full mx-auto mb-2 flex items-center justify-center">
                    <div className="h-3 w-3 bg-yellow-400 rounded-full"></div>
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">Light Mode</div>
                </button>
                
                <button
                  onClick={() => setTheme('dark')}
                  className={`p-4 rounded-lg border-2 transition-colors text-center ${
                    theme === 'dark'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <div className="h-6 w-6 bg-gray-800 rounded-full mx-auto mb-2 flex items-center justify-center">
                    <div className="h-3 w-3 bg-gray-600 rounded-full"></div>
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">Dark Mode</div>
                </button>
              </div>
            </div>
          </div>
        )

      case 'community':
        return (
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500 dark:text-gray-400">Community features coming soon...</p>
          </div>
        )

      case 'feedback':
        return (
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500 dark:text-gray-400">Feedback section coming soon...</p>
          </div>
        )

      case 'api':
        return (
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500 dark:text-gray-400">API settings coming soon...</p>
          </div>
        )

      case 'terms':
        return (
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500 dark:text-gray-400">Terms & Policy coming soon...</p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] p-0 overflow-hidden bg-white dark:bg-gray-900">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Setting</h2>
          <button
            onClick={() => onOpenChange(false)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex flex-1 min-h-0">
          {/* Sidebar */}
          <div className="w-64 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
            <nav className="p-4 space-y-1">
              {settingsTabs.map((tab) => {
                const Icon = tab.icon
                const isActive = activeTab === tab.id
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-yellow-200 dark:bg-yellow-900 text-gray-900 dark:text-white'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-3" />
                    {tab.label}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {renderTabContent()}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
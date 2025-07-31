'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { useTheme } from '@/contexts/ThemeContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Separator } from '@/components/ui/separator';
import {
  ArrowLeft,
  Moon,
  Sun,
  Monitor,
  Bell,
  Shield,
  CreditCard,
  User,
  Palette,
  Globe,
  FileText,
  Download
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';

export default function SettingsPage() {
  const router = useRouter();
  const user = { id: "demo-user" };
  const { theme, setTheme } = useTheme();

  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    marketing: false
  });

  const [preferences, setPreferences] = useState({
    language: 'en',
    citationStyle: 'Harvard',
    autoSave: true,
    showReasoning: true
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen bg-gray-900 text-white items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <Sidebar
        currentChatId={null}
        onNewChat={() => router.push('/chat')}
        onSelectChat={() => {}}
        onDeleteChat={() => {}}
        userId={user?.id}
      />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-6">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.back()}
              className="hover:bg-gray-800"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <h1 className="text-3xl font-bold">Settings</h1>
          </div>

          {/* Appearance Settings */}
          <Card className="bg-gray-800 border-gray-700 mb-6">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-blue-400" />
                <CardTitle>Appearance</CardTitle>
              </div>
              <CardDescription>Customize how HandyWriterz looks</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label className="text-base mb-4 block">Theme</Label>
                <RadioGroup value={theme} onValueChange={(value: any) => setTheme(value)}>
                  <div className="flex items-center space-x-2 mb-3">
                    <RadioGroupItem value="light" id="light" />
                    <Label htmlFor="light" className="flex items-center gap-2 cursor-pointer">
                      <Sun className="h-4 w-4" />
                      Light
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 mb-3">
                    <RadioGroupItem value="dark" id="dark" />
                    <Label htmlFor="dark" className="flex items-center gap-2 cursor-pointer">
                      <Moon className="h-4 w-4" />
                      Dark
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="system" id="system" />
                    <Label htmlFor="system" className="flex items-center gap-2 cursor-pointer">
                      <Monitor className="h-4 w-4" />
                      System
                    </Label>
                  </div>
                </RadioGroup>
              </div>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card className="bg-gray-800 border-gray-700 mb-6">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-blue-400" />
                <CardTitle>Notifications</CardTitle>
              </div>
              <CardDescription>Manage your notification preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="email-notif" className="text-base">Email notifications</Label>
                  <p className="text-sm text-gray-400">Receive updates about your documents</p>
                </div>
                <Switch
                  id="email-notif"
                  checked={notifications.email}
                  onCheckedChange={(checked) => setNotifications({...notifications, email: checked})}
                />
              </div>
              <Separator className="bg-gray-700" />
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="push-notif" className="text-base">Push notifications</Label>
                  <p className="text-sm text-gray-400">Get notified in your browser</p>
                </div>
                <Switch
                  id="push-notif"
                  checked={notifications.push}
                  onCheckedChange={(checked) => setNotifications({...notifications, push: checked})}
                />
              </div>
              <Separator className="bg-gray-700" />
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="marketing-notif" className="text-base">Marketing emails</Label>
                  <p className="text-sm text-gray-400">New features and special offers</p>
                </div>
                <Switch
                  id="marketing-notif"
                  checked={notifications.marketing}
                  onCheckedChange={(checked) => setNotifications({...notifications, marketing: checked})}
                />
              </div>
            </CardContent>
          </Card>

          {/* Writing Preferences */}
          <Card className="bg-gray-800 border-gray-700 mb-6">
            <CardHeader>
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-400" />
                <CardTitle>Writing Preferences</CardTitle>
              </div>
              <CardDescription>Default settings for your documents</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="auto-save" className="text-base">Auto-save</Label>
                  <p className="text-sm text-gray-400">Automatically save your work</p>
                </div>
                <Switch
                  id="auto-save"
                  checked={preferences.autoSave}
                  onCheckedChange={(checked) => setPreferences({...preferences, autoSave: checked})}
                />
              </div>
              <Separator className="bg-gray-700" />
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="show-reasoning" className="text-base">Show AI reasoning</Label>
                  <p className="text-sm text-gray-400">Display agent thought process</p>
                </div>
                <Switch
                  id="show-reasoning"
                  checked={preferences.showReasoning}
                  onCheckedChange={(checked) => setPreferences({...preferences, showReasoning: checked})}
                />
              </div>
            </CardContent>
          </Card>

          {/* Account Actions */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-blue-400" />
                <CardTitle>Account</CardTitle>
              </div>
              <CardDescription>Manage your account settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                variant="outline"
                className="w-full justify-start border-gray-700 hover:bg-gray-700"
                onClick={() => router.push('/settings/billing')}
              >
                <CreditCard className="h-4 w-4 mr-2" />
                Billing & Subscription
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start border-gray-700 hover:bg-gray-700"
                onClick={() => router.push('/settings/security')}
              >
                <Shield className="h-4 w-4 mr-2" />
                Security & Privacy
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start border-gray-700 hover:bg-gray-700"
              >
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
              <Separator className="bg-gray-700" />
              <Button
                variant="destructive"
                className="w-full"
              >
                Delete Account
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

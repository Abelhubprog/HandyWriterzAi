'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDynamicAuth } from '@/hooks/useDynamicAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  User,
  Mail,
  Wallet,
  CreditCard,
  FileText,
  Trophy,
  Settings,
  LogOut,
  ChevronRight,
  Download,
  Share2
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import { ThemeSwitcher } from '@/components/ThemeSwitcher';

interface UserStats {
  documentsCreated: number;
  totalWords: number;
  avgQualityScore: number;
  creditsUsed: number;
  creditsRemaining: number;
}

export default function ProfilePage() {
  const router = useRouter();
  const { isAuthenticated, user, isLoading, logout } = useDynamicAuth();
  const [userStats, setUserStats] = useState<UserStats>({
    documentsCreated: 12,
    totalWords: 45000,
    avgQualityScore: 92,
    creditsUsed: 37,
    creditsRemaining: 463
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

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

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
        <div className="max-w-6xl mx-auto p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold">Profile</h1>
            <div className="flex items-center gap-4">
              <ThemeSwitcher />
              <Button
                variant="outline"
                onClick={() => router.push('/settings')}
                className="border-gray-700 hover:bg-gray-800"
              >
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button
                variant="destructive"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>

          {/* User Info Card */}
          <Card className="bg-gray-800 border-gray-700 mb-6">
            <CardContent className="p-6">
              <div className="flex items-start gap-6">
                <Avatar className="h-24 w-24">
                  <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.email}`} />
                  <AvatarFallback className="bg-blue-600 text-white text-2xl">
                    {user?.email?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>

                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-2xl font-bold">{user?.email || 'User'}</h2>
                    <Badge className="bg-blue-600 text-white">Pro</Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      <span>{user?.email || 'demo@example.com'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Wallet className="h-4 w-4" />
                      <span className="font-mono text-xs">
                        {user?.wallet ? `${user.wallet.slice(0, 6)}...${user.wallet.slice(-4)}` : 'No wallet connected'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-3xl font-bold text-blue-400">{userStats.creditsRemaining}</div>
                  <div className="text-sm text-gray-400">Credits remaining</div>
                  <Button
                    size="sm"
                    className="mt-2 bg-blue-600 hover:bg-blue-700"
                    onClick={() => router.push('/pricing')}
                  >
                    <CreditCard className="h-3 w-3 mr-1" />
                    Buy Credits
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats Overview */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Documents</p>
                    <p className="text-2xl font-bold">{userStats.documentsCreated}</p>
                  </div>
                  <FileText className="h-8 w-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Words</p>
                    <p className="text-2xl font-bold">{userStats.totalWords.toLocaleString()}</p>
                  </div>
                  <FileText className="h-8 w-8 text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Avg. Quality</p>
                    <p className="text-2xl font-bold">{userStats.avgQualityScore}%</p>
                  </div>
                  <Trophy className="h-8 w-8 text-yellow-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Credits Used</p>
                    <p className="text-2xl font-bold">{userStats.creditsUsed}</p>
                  </div>
                  <CreditCard className="h-8 w-8 text-purple-400" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Documents */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle>Recent Documents</CardTitle>
              <CardDescription>Your latest generated documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { title: 'AI in Healthcare: A Comprehensive Analysis', type: 'Research Paper', date: '2 hours ago', words: 3500 },
                  { title: 'Market Research: Sustainable Energy Solutions', type: 'Report', date: '1 day ago', words: 2800 },
                  { title: 'PhD Dissertation: Quantum Computing Applications', type: 'Dissertation', date: '3 days ago', words: 12000 },
                ].map((doc, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-900 rounded-lg hover:bg-gray-850 transition-colors cursor-pointer">
                    <div className="flex items-center gap-4">
                      <FileText className="h-10 w-10 text-blue-400" />
                      <div>
                        <h4 className="font-semibold">{doc.title}</h4>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span>{doc.type}</span>
                          <span>•</span>
                          <span>{doc.words.toLocaleString()} words</span>
                          <span>•</span>
                          <span>{doc.date}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="ghost" className="hover:bg-gray-700">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="ghost" className="hover:bg-gray-700">
                        <Share2 className="h-4 w-4" />
                      </Button>
                      <ChevronRight className="h-4 w-4 text-gray-500" />
                    </div>
                  </div>
                ))}
              </div>

              <Button
                variant="outline"
                className="w-full mt-4 border-gray-700 hover:bg-gray-800"
                onClick={() => router.push('/library')}
              >
                View All Documents
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

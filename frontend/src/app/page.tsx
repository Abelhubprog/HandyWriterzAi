'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Brain } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { UserMenu } from '@/components/UserMenu';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/50 to-purple-900/50 text-white overflow-hidden">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width=%2260%22%20height=%2260%22%20viewBox=%220%200%2060%2060%22%20xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg%20fill=%22none%22%20fill-rule=%22evenodd%22%3E%3Cg%20fill=%22%239C92AC%22%20fill-opacity=%220.03%22%3E%3Cpath%20d=%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>

      {/* Navigation - Ultra minimal */}
      <nav className="relative z-10 container mx-auto px-6 py-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-8 w-8 text-blue-400" />
            <span className="text-2xl font-bold">HandyWriterz</span>
          </div>
          <div className="flex items-center gap-6">
            <UserMenu compact />
            <Button
              onClick={() => router.push('/chat')}
              className="bg-white text-gray-900 hover:bg-gray-100 font-medium"
            >
              Start Writing
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Ultra Minimalist */}
      <section className="relative z-10 container mx-auto px-6 min-h-[calc(100vh-120px)] flex items-center justify-center">
        <div className="text-center max-w-4xl mx-auto">
          {/* Main heading with gradient */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold mb-8 leading-tight">
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              AI-powered
            </span>
            <br />
            <span className="text-white">academic writing</span>
          </h1>

          {/* Simple subtitle */}
          <p className="text-xl md:text-2xl text-gray-300 mb-12 font-light">
            30+ specialized agents. One powerful platform.
          </p>

          {/* CTA Button */}
          <Button
            size="lg"
            onClick={() => router.push('/chat')}
            className="bg-blue-600 hover:bg-blue-700 text-white text-lg px-10 py-6 rounded-full shadow-2xl shadow-blue-500/20 hover:shadow-blue-500/30 hover:scale-105 transition-all duration-300"
          >
            Start Writing Free
            <ArrowRight className="ml-3 h-5 w-5" />
          </Button>

          {/* Minimal social proof */}
          <div className="mt-16 flex items-center justify-center gap-8 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <span className="text-2xl">✨</span>
              <span>100K+ documents created</span>
            </div>
            <div className="hidden sm:block w-px h-6 bg-gray-600"></div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">⚡</span>
              <span>Powered by GPT-4 & Claude</span>
            </div>
          </div>
        </div>
      </section>

      {/* Floating gradient orbs for visual interest */}
      <div className="absolute top-1/4 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-1/3 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <style jsx>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}

'use client';
import { useDynamicContext } from '@dynamic-labs/sdk-react-core';
import { Button } from './ui/button';

export default function Hero() {
  const { setShowAuthFlow } = useDynamicContext();
  return (
    <section className="relative min-h-screen flex items-center justify-center text-center bg-slate-900 text-white overflow-hidden">
      <div className="absolute inset-0 bg-black opacity-50"></div>
      <div className="relative z-10 p-4">
        <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-4">
          Write Brilliantly, Submit Confidently
        </h1>
        <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto mb-8">
          Leverage our advanced AI for top-tier academic research and writing, complete with built-in Turnitin clearance to ensure originality.
        </p>
        <Button onClick={() => setShowAuthFlow(true)} size="lg">
          Get Started Now
        </Button>
      </div>
    </section>
  );
}
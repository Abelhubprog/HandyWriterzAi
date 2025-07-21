'use client';
import { useDynamicContext } from '@dynamic-labs/sdk-react-core';
import { Button } from './ui/button';

export default function CTA() {
  const { setShowAuthFlow } = useDynamicContext();
  return (
    <section className="py-20 bg-slate-800 text-white">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-4">Ready to Get Started?</h2>
        <p className="text-slate-300 max-w-2xl mx-auto mb-8">
          Join thousands of students who are writing brilliantly and submitting confidently with HandyWriterz.
        </p>
        <Button onClick={() => setShowAuthFlow?.(true)} size="lg">
          Sign Up for Free
        </Button>
      </div>
    </section>
  );
}
"use client";

import React from 'react';
import { Button } from '@/components/ui/button';
import { Loader2, ClipboardList } from 'lucide-react';

interface ClaimButtonProps {
  onClick: () => void;
  loading?: boolean;
  disabled?: boolean;
  className?: string;
}

export function ClaimButton({ 
  onClick, 
  loading = false, 
  disabled = false,
  className = ""
}: ClaimButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={loading || disabled}
      className={`bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 ${className}`}
      variant="default"
    >
      {loading ? (
        <>
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          Claiming...
        </>
      ) : (
        <>
          <ClipboardList className="w-4 h-4 mr-2" />
          Claim Next Assignment
        </>
      )}
    </Button>
  );
}
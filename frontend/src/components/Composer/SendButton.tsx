'use client';

import React from 'react';
import { ArrowUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SendButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

export function SendButton({ onClick, disabled }: SendButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={disabled}
      size="icon"
      className={cn(
        "h-10 w-10 rounded-full transition-all",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        disabled
          ? "bg-muted text-muted-foreground cursor-not-allowed"
          : "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm hover:shadow-md"
      )}
    >
      <ArrowUp className="h-5 w-5" />
      <span className="sr-only">Send message</span>
    </Button>
  );
}

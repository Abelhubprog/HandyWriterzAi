'use client';

import React, { useEffect, useState } from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';

interface WriteupType {
  value: string;
  label: string;
}

interface WriteupSelectProps {
  value: string;
  onValueChange: (value: string) => void;
  disabled?: boolean;
}

// Default writeup types - will be replaced by API call
const DEFAULT_WRITEUP_TYPES: WriteupType[] = [
  { value: 'general', label: 'General' },
  { value: 'essay', label: 'Essay' },
  { value: 'report', label: 'Report' },
  { value: 'dissertation', label: 'PhD Dissertation' },
  { value: 'case_study', label: 'Case Study' },
  { value: 'market_research', label: 'Market Research' },
  { value: 'technical_report', label: 'Technical Report' },
  { value: 'presentation', label: 'Presentation' },
  { value: 'coding', label: 'Coding' },
];

export function WriteupSelect({ value, onValueChange, disabled }: WriteupSelectProps) {
  const [writeupTypes, setWriteupTypes] = useState<WriteupType[]>(DEFAULT_WRITEUP_TYPES);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Fetch writeup types from API
    const fetchWriteupTypes = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('/api/writing-types');
        if (response.ok) {
          const data: WriteupType[] = await response.json();
          if (Array.isArray(data) && data.length > 0) {
            setWriteupTypes(data);
          }
        }
      } catch (error) {
        console.error('Failed to fetch writeup types:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWriteupTypes();
  }, []);

  return (
    <Select value={value} onValueChange={onValueChange} disabled={disabled || isLoading}>
      <SelectTrigger
        className={cn(
          "h-10 px-3 text-sm font-medium",
          "bg-transparent hover:bg-secondary/20",
          "border-0 focus:ring-0 focus:ring-offset-0",
          "min-w-[140px] text-muted-foreground"
        )}
      >
        <SelectValue placeholder="Select type" />
      </SelectTrigger>
      <SelectContent 
        position="popper" 
        side="top" 
        align="start"
        className="z-50 max-h-96 overflow-y-auto bg-background border-border"
        avoidCollisions={true}
        collisionPadding={8}
      >
        {writeupTypes.map((type) => (
          <SelectItem 
            key={type.value} 
            value={type.value} 
            className="text-sm text-foreground hover:bg-secondary/80 focus:bg-secondary/80"
          >
            {type.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

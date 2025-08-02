"use client";

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { FileX, Inbox } from 'lucide-react';

interface EmptyStateProps {
  message?: string;
  title?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function EmptyState({ 
  message = "No items found", 
  title = "Nothing here yet",
  icon,
  className = ""
}: EmptyStateProps) {
  const defaultIcon = icon || <Inbox className="w-12 h-12 text-gray-400" />;

  return (
    <Card className={`w-full ${className}`}>
      <CardContent className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4">
          {defaultIcon}
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          {title}
        </h3>
        <p className="text-gray-600 dark:text-gray-400 max-w-md">
          {message}
        </p>
      </CardContent>
    </Card>
  );
}
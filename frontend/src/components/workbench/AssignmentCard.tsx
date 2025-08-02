"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, User, FileText } from 'lucide-react';

export interface AssignmentSummary {
  id: string;
  title: string;
  status: string;
  created_at: string;
  assigned_checker_id?: number | null;
}

interface AssignmentCardProps {
  summary: AssignmentSummary;
}

export function AssignmentCard({ summary }: AssignmentCardProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold truncate flex-1">
            {summary.title || 'Untitled Assignment'}
          </CardTitle>
          <Badge className={`ml-2 ${getStatusColor(summary.status)}`}>
            {summary.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
          <FileText className="w-4 h-4 mr-2" />
          <span>ID: {summary.id}</span>
        </div>
        
        <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
          <Calendar className="w-4 h-4 mr-2" />
          <span>Created: {formatDate(summary.created_at)}</span>
        </div>
        
        {summary.assigned_checker_id && (
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <User className="w-4 h-4 mr-2" />
            <span>Assigned to Checker: {summary.assigned_checker_id}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
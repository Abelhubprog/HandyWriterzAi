'use client'

import React from 'react';
import { Brain, Zap, FileText, Globe, Shield, Loader2 } from 'lucide-react';

interface StreamingStatusProps {
  events: any[];
  isConnected: boolean;
  lastHeartbeatTs?: number | null;
  totalCost?: number;
  plagiarismScore?: number;
  qualityScore?: number;
}

export function StreamingStatus({ 
  events, 
  isConnected,
  lastHeartbeatTs = null,
  totalCost = 0,
  plagiarismScore = 0,
  qualityScore = 0
}: StreamingStatusProps) {
  const currentEvent = events[events.length - 1];
  const now = Date.now();
  const hbFresh = lastHeartbeatTs ? (now - lastHeartbeatTs) < 25000 : false;
  
  const getStatusIcon = (eventType: string) => {
    switch (eventType) {
      case 'parsing_files':
        return <FileText className="h-4 w-4 text-blue-400" />;
      case 'routing_agents':
        return <Brain className="h-4 w-4 text-purple-400" />;
      case 'researching':
        return <Globe className="h-4 w-4 text-green-400" />;
      case 'writing':
        return <Zap className="h-4 w-4 text-yellow-400" />;
      case 'quality_check':
        return <Shield className="h-4 w-4 text-blue-400" />;
      default:
        return <Loader2 className="h-4 w-4 text-gray-400 animate-spin" />;
    }
  };

  const getStatusText = (eventType: string) => {
    switch (eventType) {
      case 'parsing_files':
        return 'Parsing uploaded files...';
      case 'routing_agents':
        return 'Routing to specialized agents...';
      case 'researching':
        return 'Conducting research...';
      case 'writing':
        return 'Generating content...';
      case 'quality_check':
        return 'Performing quality checks...';
      case 'finalizing':
        return 'Finalizing response...';
      default:
        return 'Processing request...';
    }
  };

  if (!isConnected || !currentEvent) {
    return null;
  }

  return (
    <div className="border-b border-gray-700 bg-gray-800/50 px-6 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {getStatusIcon(currentEvent.type)}
          <span className="text-sm text-gray-300">
            {getStatusText(currentEvent.type)}
          </span>
          {currentEvent.progress && (
            <div className="w-32 bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${currentEvent.progress}%` }}
              />
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <span className={`inline-block w-2 h-2 rounded-full ${hbFresh ? 'bg-emerald-500' : 'bg-yellow-500'} animate-pulse`} />
            <span>{hbFresh ? 'Live' : 'Reconnecting...'}</span>
          </span>
          {totalCost > 0 && (
            <span>Cost: ${totalCost.toFixed(4)}</span>
          )}
          {plagiarismScore > 0 && (
            <span>Originality: {(100 - plagiarismScore).toFixed(1)}%</span>
          )}
          {qualityScore > 0 && (
            <span>Quality: {qualityScore.toFixed(1)}%</span>
          )}
        </div>
      </div>
    </div>
  );
}

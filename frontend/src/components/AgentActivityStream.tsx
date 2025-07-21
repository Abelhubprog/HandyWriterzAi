import React from 'react';
import { TimelineEvent } from '@/hooks/useStream';
import { CheckCircle, Clock, AlertCircle, FileText, DollarSign, Shield, Download } from 'lucide-react';

interface AgentActivityStreamProps {
  events: TimelineEvent[];
  totalCost?: number;
  plagiarismScore?: number;
  qualityScore?: number;
  derivatives?: { kind: string; url: string }[];
}

export const AgentActivityStream: React.FC<AgentActivityStreamProps> = ({ 
  events, 
  totalCost, 
  plagiarismScore, 
  qualityScore,
  derivatives = []
}) => {
  const getEventIcon = (event: TimelineEvent) => {
    switch (event.type) {
      case 'node_finished':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'node_started':
        return <Clock className="w-4 h-4 text-blue-400 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      case 'format_done':
        return <FileText className="w-4 h-4 text-purple-400" />;
      case 'plagiarism_score':
        return <Shield className="w-4 h-4 text-orange-400" />;
      case 'derivative_ready':
        return <Download className="w-4 h-4 text-cyan-400" />;
      default:
        return <div className="w-4 h-4 rounded-full bg-gray-400" />;
    }
  };

  const getEventColor = (event: TimelineEvent) => {
    switch (event.type) {
      case 'node_finished':
        return 'border-green-400';
      case 'node_started':
        return 'border-blue-400';
      case 'error':
        return 'border-red-400';
      case 'format_done':
        return 'border-purple-400';
      case 'plagiarism_score':
        return 'border-orange-400';
      case 'derivative_ready':
        return 'border-cyan-400';
      default:
        return 'border-gray-600';
    }
  };

  const getEventTitle = (event: TimelineEvent) => {
    switch (event.type) {
      case 'node_started':
        return `Starting ${event.name}`;
      case 'node_finished':
        return `Completed ${event.name}`;
      case 'search_result':
        return `Found ${event.payload?.count || 0} sources`;
      case 'embedding_done':
        return `Processed ${event.payload?.chunks || 0} chunks`;
      case 'format_done':
        return 'Document formatted';
      case 'plagiarism_score':
        return `Originality: ${event.payload?.score || 0}%`;
      case 'derivative_ready':
        return `${event.payload?.kind || 'Asset'} ready`;
      case 'workflow_finished':
        return 'Workflow completed';
      case 'error':
        return 'Error occurred';
      default:
        return event.name || 'Unknown event';
    }
  };

  const getEventDescription = (event: TimelineEvent) => {
    switch (event.type) {
      case 'node_finished':
        return event.tokens ? `${event.tokens} tokens` : '';
      case 'search_result':
        return `${event.payload?.agent || 'Agent'} search`;
      case 'embedding_done':
        return `File: ${event.payload?.file || 'Unknown'}`;
      case 'plagiarism_score':
        const score = event.payload?.score || 0;
        return score > 15 ? 'Review needed' : 'Acceptable';
      case 'derivative_ready':
        return 'Ready for download';
      case 'workflow_finished':
        return `Quality: ${event.payload?.quality || 0}%`;
      case 'error':
        return event.error || 'Unknown error';
      default:
        return event.payload?.message || '';
    }
  };

  return (
    <div className="p-4 bg-gray-800 border-t border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          Agent Activity
        </h3>
        
        {/* Cost and Quality Display */}
        <div className="flex items-center gap-4 text-sm">
          {totalCost && (
            <div className="flex items-center gap-1 text-green-400">
              <DollarSign className="w-3 h-3" />
              <span>${totalCost.toFixed(2)}</span>
            </div>
          )}
          
          {qualityScore && (
            <div className="flex items-center gap-1 text-blue-400">
              <span>Quality: {qualityScore}%</span>
            </div>
          )}
          
          {plagiarismScore !== undefined && (
            <div className={`flex items-center gap-1 ${plagiarismScore > 15 ? 'text-red-400' : 'text-green-400'}`}>
              <Shield className="w-3 h-3" />
              <span>{plagiarismScore}%</span>
            </div>
          )}
        </div>
      </div>

      {/* Events Timeline */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {events.slice(-10).map((event, index) => (
          <div key={index} className={`flex items-start gap-3 p-3 rounded-lg border-l-2 ${getEventColor(event)} bg-gray-750`}>
            <div className="flex-shrink-0 mt-0.5">
              {getEventIcon(event)}
            </div>
            
            <div className="flex-grow min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-white truncate">
                  {getEventTitle(event)}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
              
              {getEventDescription(event) && (
                <p className="text-xs text-gray-400 mt-1">
                  {getEventDescription(event)}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Derivatives */}
      {derivatives.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <h4 className="text-sm font-medium text-white mb-2">Available Downloads</h4>
          <div className="flex flex-wrap gap-2">
            {derivatives.map((derivative, index) => (
              <a
                key={index}
                href={derivative.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded-full transition-colors"
              >
                <Download className="w-3 h-3" />
                {derivative.kind}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
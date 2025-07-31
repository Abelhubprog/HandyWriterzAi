'use client'

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Brain, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DownloadMenu } from '@/components/DownloadMenu';
import { ResponseActions } from '@/components/ResponseActions';
import type { Message } from '@/types';

interface MessageBubbleProps {
  message: Message;
  isLast: boolean;
  reasoning?: string;
  traceId?: string | null;
  totalCost?: number;
  plagiarismScore?: number;
  qualityScore?: number;
  derivatives?: { kind: string; url: string }[];
}

export function MessageBubble({
  message,
  isLast,
  reasoning,
  traceId,
  totalCost,
  plagiarismScore,
  qualityScore,
  derivatives = []
}: MessageBubbleProps) {
  const [showReasoning, setShowReasoning] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(
        typeof message.content === 'string' ? message.content : JSON.stringify(message.content)
      );
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleFeedback = (type: 'positive' | 'negative') => {
    // TODO: Implement feedback API call
    console.log(`Feedback: ${type} for message ${message.id}`);
  };

  if (message.type === 'human') {
    return (
      <div className="mb-6 w-full">
        <div className="flex justify-end">
          <div className="max-w-[70%] min-w-0">
            <div className="bg-primary text-primary-foreground px-4 py-3 rounded-2xl rounded-br-md">
              <div className="text-sm whitespace-pre-wrap break-words overflow-wrap-anywhere">
                {typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
              </div>
            </div>
            <div className="text-xs text-muted-foreground mt-1 text-right">
              You • {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'now'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6 w-full">
      <div className="flex justify-start">
        <div className="max-w-[85%] min-w-0">
          <div className="bg-secondary text-foreground px-4 py-3 rounded-2xl rounded-bl-md">
            <div className="text-sm whitespace-pre-wrap break-words overflow-wrap-anywhere leading-relaxed">
              {typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
            </div>
            
            {/* Reasoning Toggle */}
            {reasoning && (
              <div className="mt-4 border-t border-border pt-3">
                <button
                  onClick={() => setShowReasoning(!showReasoning)}
                  className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showReasoning ? (
                    <ChevronDown className="h-3 w-3" />
                  ) : (
                    <ChevronRight className="h-3 w-3" />
                  )}
                  <Brain className="h-3 w-3" />
                  Show reasoning
                </button>
                
                {showReasoning && (
                  <div className="mt-2 p-3 bg-muted/50 rounded-lg border border-border">
                    <div className="text-xs text-muted-foreground font-mono whitespace-pre-wrap break-words">
                      {reasoning}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Download Menu for completed responses */}
            {isLast && traceId && derivatives.length > 0 && (
              <div className="mt-4 border-t border-border pt-3">
                <DownloadMenu
                  traceId={traceId}
                  derivatives={derivatives}
                  plagiarismScore={plagiarismScore}
                  qualityScore={qualityScore}
                  onOriginalityCheck={() => {
                    window.open(`/originality/${traceId}`, '_blank');
                  }}
                />
              </div>
            )}
          </div>

          {/* Message Actions - ChatGPT Style */}
          <div className="flex items-center justify-between mt-2">
            <div className="text-xs text-muted-foreground">
              HandyWriterz • {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'now'}
            </div>
            
            <ResponseActions
              messageId={message.id || 'unknown'}
              messageContent={typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
              conversationId={traceId}
            />
          </div>

          {/* Metrics for completed responses */}
          {isLast && (totalCost > 0 || plagiarismScore > 0 || qualityScore > 0) && (
            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
              {totalCost > 0 && <span>Cost: ${totalCost.toFixed(4)}</span>}
              {plagiarismScore > 0 && <span>Originality: {(100 - plagiarismScore).toFixed(1)}%</span>}
              {qualityScore > 0 && <span>Quality: {qualityScore.toFixed(1)}%</span>}
            </div>
          )}

          {copied && (
            <div className="text-xs text-green-400 mt-1">
              Copied to clipboard!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
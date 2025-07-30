'use client'

import React, { useEffect, useRef, useCallback } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { StreamingStatus } from '@/components/StreamingStatus';
import { MessageBubble } from '@/components/MessageBubble';
import { ResponseActions } from '@/components/ResponseActions';
import type { Message } from '@/types';
import { TimelineEvent } from '@/hooks/useStream';
import { ProcessedEvent } from '@/components/ActivityTimeline';
import { useToast } from '@/components/ui/use-toast';

interface EnhancedChatViewProps {
  messages: Message[];
  isLoading: boolean;
  liveActivityEvents: TimelineEvent[];
  historicalActivities: Record<string, ProcessedEvent[]>;
  traceId?: string | null;
  totalCost?: number;
  plagiarismScore?: number;
  qualityScore?: number;
  derivatives?: { kind: string; url: string }[];
  streamingText?: string;
  reasoningText?: string;
  isConnected?: boolean;
  onExport: (format: 'pdf' | 'docx' | 'md') => void;
}

export function EnhancedChatView({
  messages,
  isLoading,
  liveActivityEvents,
  historicalActivities,
  traceId,
  totalCost,
  plagiarismScore,
  qualityScore,
  derivatives = [],
  streamingText = '',
  reasoningText = '',
  isConnected = false,
  onExport,
}: EnhancedChatViewProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, streamingText]);

  const displayMessages = React.useMemo(() => {
    const allMessages = [...messages];
    if (isLoading && streamingText && traceId) {
      const lastMessageIndex = allMessages.findLastIndex(m => m.type === 'ai');
      if (lastMessageIndex >= 0) {
        allMessages[lastMessageIndex] = {
          ...allMessages[lastMessageIndex],
          content: streamingText
        };
      } else {
        allMessages.push({
          id: traceId,
          type: 'ai',
          content: streamingText,
          timestamp: new Date().toISOString()
        });
      }
    }
    return allMessages;
  }, [messages, streamingText, isLoading, traceId]);

  const getReasoningForMessage = (messageId?: string, isLast?: boolean) => {
    if (isLast && isLoading && reasoningText && messageId === traceId) {
      return reasoningText;
    }
    if (!messageId || !historicalActivities[messageId]) return undefined;
    const reasoningEvents = historicalActivities[messageId].filter(
      event => event.title?.toLowerCase().includes('thinking') || 
               event.title?.toLowerCase().includes('reasoning')
    );
    return reasoningEvents.map(event => 
      typeof event.data === 'string' ? event.data : 
      event.data?.text || event.data?.details || ''
    ).join('\n');
  };

  const handleCopy = useCallback((content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      toast({
        title: "Copied to clipboard",
      });
    }, (err) => {
      toast({
        title: "Failed to copy",
        description: "Could not copy text to clipboard.",
        variant: "destructive",
      });
      console.error('Failed to copy: ', err);
    });
  }, [toast]);

  return (
    <div className="flex-1 flex flex-col bg-gray-900">
      {isLoading && (
        <StreamingStatus
          events={liveActivityEvents}
          isConnected={isConnected}
          totalCost={totalCost}
          plagiarismScore={plagiarismScore}
          qualityScore={qualityScore}
        />
      )}
      <ScrollArea className="flex-1" ref={scrollAreaRef}>
        <div className="p-6 space-y-4 max-w-4xl mx-auto w-full">
          {displayMessages.length === 0 ? (
            <div className="text-center text-gray-400 py-12">
              <p>No messages yet. Start the conversation!</p>
            </div>
          ) : (
            displayMessages.map((message, index) => {
              const isLast = index === displayMessages.length - 1;
              const reasoning = message.type === 'ai' ? getReasoningForMessage(message.id, isLast) : undefined;
              
              return (
                <div key={message.id || index}>
                  <MessageBubble
                    message={message}
                    isLast={isLast}
                    reasoning={reasoning}
                    traceId={traceId}
                    totalCost={isLast ? totalCost : undefined}
                    plagiarismScore={isLast ? plagiarismScore : undefined}
                    qualityScore={isLast ? qualityScore : undefined}
                    derivatives={isLast ? derivatives : []}
                  />
                  {message.type === 'ai' && !isLoading && (
                    <div className="pl-12">
                       <ResponseActions
                          messageId={message.id!}
                          messageContent={message.content as string}
                          conversationId={traceId}
                          onCopy={() => handleCopy(message.content as string)}
                          onExport={onExport}
                       />
                    </div>
                  )}
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
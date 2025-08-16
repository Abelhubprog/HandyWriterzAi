'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Composer } from './Composer/Composer';
import { MessageBubble } from './MessageBubble';
import { cn } from '@/lib/utils';
import { useActiveConversation, useStreamingState, useChatActions } from '@/store/useChatStore';
import { useStream } from '@/hooks/useStream';
import { apiClient } from '@/services/advancedApiClient';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Clock, Brain, Search, FileText, CheckCircle } from 'lucide-react';
import { ProgressChips } from '@/components/ProgressChips';
import { StreamingStatus } from '@/components/StreamingStatus';
import { SSEErrorOverlay } from '@/components/SSEErrorOverlay';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date | string;
  attachments?: Array<{
    url: string;
    mime: string;
    name: string;
    size: number;
    file_id?: string;
  }>;
  writeupType?: string;
}

interface ChatPaneProps {
  conversationId?: string;
  className?: string;
  onConversationCreate?: (conversationId: string) => void;
}

export function ChatPane({ conversationId, className, onConversationCreate }: ChatPaneProps) {
  const activeConversation = useActiveConversation();
  const streamingState = useStreamingState();
  const {
    createConversation,
    selectConversation,
    addMessage,
    updateMessage,
    deleteConversation,
    updateConversationTitle,
    startStreaming,
    updateStreamingMessage,
    updateAgentStatus,
    stopStreaming,
    setError,
    clearError,
    loadConversations,
  } = useChatActions();

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Select conversation when conversationId changes
  useEffect(() => {
    if (conversationId) {
      selectConversation(conversationId);
    }
  }, [conversationId, selectConversation]);

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use unified stream hook against Next proxy /api/chat/stream/[traceId]
  const [traceId, setTraceId] = useState<string | null>(null);
  const stream = useStream(traceId, {
    onMessage: (evt) => {
      // Map new step-wise schema into store-friendly messages
      switch (evt.type) {
        case 'planning_started':
          updateAgentStatus('Planning the approach...');
          break;
        case 'search_started':
        case 'search_progress':
          updateAgentStatus('Searching sources...');
          break;
        case 'verify_started':
          updateAgentStatus('Verifying sources...');
          break;
        case 'writer_started':
          updateAgentStatus('Composing...');
          break;
        // token/content appended via apiClient.streamResponse handler to avoid double appends
        case 'token':
        case 'content':
          break;
        case 'evaluator_started':
          updateAgentStatus('Evaluating...');
          break;
        case 'formatter_started':
          updateAgentStatus('Formatting...');
          break;
        case 'workflow_finished':
        case 'done':
          stopStreaming();
          break;
        default:
          // keep timeline via useStream internal store
          break;
      }
    },
    onClose: () => {
      stopStreaming();
    }
  });

  // Auto-scroll to bottom when new messages arrive or streaming updates
  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages, streamingState.streamingMessage]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Helper function to calculate progress based on agent status
  const getProgressValue = useCallback((status: string | undefined): number => {
    if (!status) return 0;
    
    const statusMap: Record<string, number> = {
      'Processing request...': 10,
      'Planning the approach...': 20,
      'Searching sources...': 40,
      'Verifying sources...': 60,
      'Composing...': 80,
      'Evaluating...': 90,
      'Formatting...': 95,
      'Completed': 100
    };
    
    return statusMap[status] || 15;
  }, []);

  const handleSend = useCallback(async (payload: {
    conversationId: string;
    author: 'user';
    content: string;
    writeupType: string;
    attachments?: Array<{
      url: string;
      mime: string;
      name: string;
      size: number;
      file_id?: string;
    }>;
  }) => {
    if (streamingState.isStreaming) {
      console.log('Already streaming, ignoring duplicate request');
      return;
    }

    try {
      let currentConversationId = payload.conversationId;

      if (!activeConversation || !currentConversationId) {
        currentConversationId = createConversation({
          role: 'user',
          content: payload.content,
          writeupType: payload.writeupType,
          attachments: payload.attachments,
        });
        selectConversation(currentConversationId);
      } else {
        addMessage({
          conversationId: currentConversationId,
          role: 'user',
          content: payload.content,
          writeupType: payload.writeupType,
          attachments: payload.attachments,
        });
      }

      // Start streaming and clear previous stream text
      const newTraceId = (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
        ? crypto.randomUUID()
        : Math.random().toString(36).slice(2));
      startStreaming(newTraceId);
      setTraceId(newTraceId);
      updateAgentStatus('Processing request...');
      updateStreamingMessage(''); // reset buffer

      // Extract actual backend file IDs (not URLs)
      const file_ids = payload.attachments
        ?.map(a => a.file_id)
        .filter(Boolean) || [];

      console.log('Sending chat request with file_ids:', file_ids);

      const requestBody = {
        prompt: payload.content,
        mode: payload.writeupType || "general",
        file_ids: file_ids, // Use actual backend file IDs
        user_params: { 
          writeupType: payload.writeupType,
          citationStyle: 'Harvard',
          wordCount: 3000,
          model: 'gemini-2.0-flash-exp',
          user_id: 'current_user'
        }
      };

      // Use AdvancedApiClient to call backend directly
      const { data: result } = await apiClient.chat(requestBody);

      // Add assistant message placeholder; final text will be appended as stream
      const assistantMessageId = addMessage({
        conversationId: currentConversationId,
        role: 'assistant',
        content: '', // Will be populated by streaming
      });

      // Update trace ID for streaming
      const streamTraceId = result.trace_id || result.conversation_id || newTraceId;
      setTraceId(streamTraceId);
      
      // Start SSE streaming via Next proxy route
      apiClient.streamResponse(`/api/chat/stream/${streamTraceId}`, { method: 'GET' }, (chunk) => {
        console.log('SSE chunk received:', chunk);
        
        // Handle different event types
        switch (chunk.type) {
          case 'connected':
            console.log('SSE connection established');
            break;
          case 'planning_started':
            updateAgentStatus('Planning the approach...');
            break;
          case 'search_started':
          case 'search_progress':
            updateAgentStatus('Searching sources...');
            break;
          case 'verify_started':
            updateAgentStatus('Verifying sources...');
            break;
          case 'writer_started':
            updateAgentStatus('Composing...');
            break;
          case 'token':
            if (chunk.delta) {
              updateStreamingMessage((streamingState.streamingMessage || '') + chunk.delta);
            }
            break;
          case 'evaluator_started':
            updateAgentStatus('Evaluating...');
            break;
          case 'formatter_started':
            updateAgentStatus('Formatting...');
            break;
          case 'workflow_complete':
          case 'workflow_finished':
            console.log('Workflow completed successfully');
            // Commit the streaming message to the conversation
            if (streamingState.streamingMessage && assistantMessageId) {
              updateMessage(assistantMessageId, {
                content: streamingState.streamingMessage
              });
            }
            updateAgentStatus('Complete');
            stopStreaming();
            break;
          case 'workflow_failed':
            console.error('Workflow failed:', chunk.error);
            setError(chunk.error || 'Workflow failed');
            stopStreaming();
            break;
          case 'workflow_finished':
          case 'done':
            stopStreaming();
            break;
          case 'parse_error':
            console.error('SSE parse error:', chunk.error);
            // Don't stop streaming for parse errors, just log them
            break;
          case 'error':
            console.error('SSE error:', chunk.error);
            setError(chunk.error || 'Unknown streaming error');
            stopStreaming();
            break;
          default:
            // Log unknown event types for debugging
            console.log('Unknown SSE event type:', chunk.type, chunk);
        }
      }).catch(error => {
        console.error('SSE streaming error:', error);
        
        // Provide more specific error messages
        let errorMessage = 'Streaming connection failed';
        if (error.code === 'STREAM_TIMEOUT') {
          errorMessage = 'Request timed out - please try again';
        } else if (error.code === 'STREAM_CONNECTION_FAILED') {
          errorMessage = 'Could not connect to server - check your connection';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        setError(errorMessage);
        stopStreaming();
      });
      // Do not stopStreaming here; the hook will close on workflow_finished

      if (!conversationId) {
        onConversationCreate?.(currentConversationId);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      stopStreaming();
    }
  }, [
    streamingState.isStreaming,
    addMessage,
    startStreaming,
    updateStreamingMessage,
    updateAgentStatus,
    stopStreaming,
    conversationId,
    onConversationCreate,
    activeConversation,
    createConversation,
    selectConversation
  ]);

  return (
    <div className={cn("h-full flex flex-col", className)}>
      {/* SSE error overlay */}
      {stream.lastError && <SSEErrorOverlay message={stream.lastError} />}
      <div className="flex-1 flex items-center justify-center px-4 overflow-hidden">
        <div className="w-full max-w-4xl h-full flex flex-col">
          {!activeConversation?.messages || activeConversation.messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="w-full">
                <div className="text-center text-muted-foreground mb-8">
                  <h2 className="text-2xl font-semibold mb-2">What are you working on?</h2>
                  <p className="text-sm">Start a conversation to get help with your writing</p>
                </div>
                <div className="w-full max-w-3xl mx-auto">
                  <Composer
                    conversationId="new-chat"
                    onSend={handleSend}
                    disabled={streamingState.isStreaming}
                  />
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Progress Indicator - shows when streaming */}
              {streamingState.isStreaming && (
                <div className="mb-4 p-4 bg-card border border-border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="h-4 w-4 text-primary animate-pulse" />
                    <span className="text-sm font-medium">
                      {streamingState.agentStatus || 'Processing request...'}
                    </span>
                  </div>
                  <Progress value={getProgressValue(streamingState.agentStatus)} className="h-2" />
                  <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>Generating your content...</span>
                  </div>
                  <ProgressChips events={stream.events} />
                </div>
              )}

              {/* Live connection status bar */}
              <StreamingStatus 
                events={stream.events}
                isConnected={stream.isConnected}
                lastHeartbeatTs={stream.lastHeartbeatTs}
                totalCost={0}
              />
              
              <div className="flex-1 overflow-hidden">
                <div
                  ref={scrollAreaRef}
                  className="h-full overflow-y-auto pr-4"
                  style={{ scrollbarGutter: 'stable' }}
                >
                  <div className="py-8 space-y-6">
                    {activeConversation?.messages.map((message) => (
                      <MessageBubble
                        key={message.id}
                        message={{
                          id: message.id,
                          type: message.role === 'user' ? 'human' : 'ai',
                          content: message.content,
                          timestamp: typeof message.timestamp === 'string'
                            ? message.timestamp
                            : new Date(message.timestamp).toISOString(),
                        }}
                        isLast={message.id === activeConversation.messages[activeConversation.messages.length - 1]?.id}
                      />
                    ))}

                    {/* Show streaming message buffer from store */}
                    {streamingState.isStreaming && (streamingState.streamingMessage?.length > 0) && (
                      <MessageBubble
                        message={{
                          id: 'streaming',
                          type: 'ai',
                          content: streamingState.streamingMessage,
                          timestamp: new Date().toISOString(),
                        }}
                        isLast={true}
                      />
                    )}

                    {/* Show agent status */}
                    {streamingState.isStreaming && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground px-4">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                        <span>{streamingState.agentStatus || 'Working...'}</span>
                      </div>
                    )}

                    <div ref={messagesEndRef} />
                  </div>
                </div>
              </div>

              <div className="flex-shrink-0 pt-4">
                <Composer
                  conversationId={activeConversation?.id || "continue-chat"}
                  onSend={handleSend}
                  disabled={streamingState.isStreaming}
                />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

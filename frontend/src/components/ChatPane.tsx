'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Composer } from './Composer/Composer';
import { MessageBubble } from './MessageBubble';
import { useChatStream } from '@/lib/useChatStream';
import { cn } from '@/lib/utils';
import { useActiveConversation, useStreamingState, useChatActions } from '@/store/useChatStore';

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
  }>;
  writeupType?: string;
}

interface ChatPaneProps {
  conversationId?: string;
  className?: string;
  onConversationCreate?: (conversationId: string) => void;
}

export function ChatPane({ conversationId, className, onConversationCreate }: ChatPaneProps) {
  // useActiveConversation returns a conversation object or undefined
  const activeConversation = useActiveConversation();
  // useStreamingState returns the streaming state object
  const streamingState = useStreamingState();
  // useChatActions returns an object with all action functions
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
  const { isStreaming, startStream, stopStream } = useChatStream();

  const startSSEStream = useCallback((traceId: string) => {
    const eventSource = new EventSource(`/api/stream/${traceId}`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'workflow_progress') {
          updateAgentStatus(data.data.current_node || 'Processing...');
          if (data.data.response) {
            updateStreamingMessage(data.data.response);
          }
        } else if (data.type === 'workflow_complete') {
          stopStreaming();
          eventSource.close();
        } else if (data.type === 'workflow_failed') {
          updateAgentStatus('Error occurred');
          stopStreaming();
          eventSource.close();
        }
      } catch (e) {
        console.error('SSE parsing error:', e);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
      stopStreaming();
    };

    return eventSource;
  }, [updateAgentStatus, updateStreamingMessage, stopStreaming]);

  // Auto-scroll to bottom when new messages arrive or streaming updates
  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages, streamingState.streamingMessage]);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
    }>;
  }) => {
    console.log('Send button clicked with payload:', payload);
    
    // Prevent sending if already streaming
    if (streamingState.isStreaming) {
      console.log('Already streaming, preventing send');
      return;
    }

    try {
      // Create conversation if we don't have an active one or it's empty/invalid
      let currentConversationId = payload.conversationId;
      
      if (!activeConversation || !currentConversationId) {
        // Create a new conversation with the first message
        currentConversationId = createConversation({
          role: 'user',
          content: payload.content,
          writeupType: payload.writeupType,
          attachments: payload.attachments,
        });
        selectConversation(currentConversationId);
      } else {
        // Add user message to existing conversation
        addMessage({
          conversationId: currentConversationId,
          role: 'user',
          content: payload.content,
          writeupType: payload.writeupType,
          attachments: payload.attachments,
        });
      }

      // Start streaming
      const traceId = (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
        ? crypto.randomUUID()
        : Math.random().toString(36).slice(2));
      startStreaming(traceId);
      updateAgentStatus('Processing request...');

      // Send to correct backend endpoint  
      const requestBody = {
        prompt: payload.content,
        mode: payload.writeupType || "general",
        file_ids: payload.attachments?.map(a => a.url) || [],
        user_params: { writeupType: payload.writeupType }
      };
      
      console.log('Sending API request to /api/chat:', requestBody);
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('API response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('API response result:', result);
      
      // Handle the response
      if (result.success !== false) {
        // Add final assistant message
        addMessage({
          conversationId: currentConversationId,
          role: 'assistant',
          content: result.response || 'I received your message and processed it successfully.',
        });
      } else {
        throw new Error(result.response || 'Unknown error occurred');
      }

      // Start SSE stream for real-time updates if trace_id is available
      if (result.trace_id) {
        startSSEStream(result.trace_id);
      }

      stopStreaming();

      // Notify parent if new conversation
      if (!conversationId) {
        onConversationCreate?.(currentConversationId);
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      stopStreaming();
    }
  }, [
    streamingState.isStreaming,
    streamingState.streamingMessage,
    addMessage,
    startStreaming,
    updateStreamingMessage,
    updateAgentStatus,
    stopStreaming,
    startStream,
    conversationId,
    onConversationCreate,
  ]);

  return (
    <div className={cn("h-full flex flex-col", className)}>
      {/* Centered chat interface like ChatGPT */}
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

                    {/* Show streaming message */}
                    {streamingState.isStreaming && streamingState.streamingMessage && (
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
                    {streamingState.isStreaming && streamingState.agentStatus && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground px-4">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                        <span>{streamingState.agentStatus}</span>
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

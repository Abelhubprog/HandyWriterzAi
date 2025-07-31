'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Composer } from './Composer/Composer';
import { MessageBubble } from './MessageBubble';
import { useChatStream } from '@/lib/useChatStream';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { v4 as uuidv4 } from 'uuid';

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
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(conversationId);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isStreaming, startStream, stopStream } = useChatStream();

  // Load messages when conversation changes
  useEffect(() => {
    console.log('ChatPane: conversationId changed from', currentConversationId, 'to', conversationId);
    
    if (conversationId !== currentConversationId) {
      setStreamingMessageId(null);
      setCurrentConversationId(conversationId);
      
      if (conversationId) {
        // Load existing conversation
        console.log('Loading conversation:', conversationId);
        import('@/lib/conversationStore').then(({ ConversationStore }) => {
          const conversation = ConversationStore.getConversation(conversationId);
          console.log('Loaded conversation:', conversation);
          if (conversation && conversation.messages) {
            setMessages(conversation.messages);
          } else {
            setMessages([]);
          }
        });
      } else {
        // New conversation
        console.log('New conversation - clearing messages');
        setMessages([]);
      }
    }
  }, [conversationId, currentConversationId]);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

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
    // Prevent sending if already streaming
    if (isStreaming) {
      return;
    }

    // Stop any existing stream
    stopStream();

    // Add user message
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: payload.content,
      timestamp: new Date(),
      attachments: payload.attachments,
      writeupType: payload.writeupType,
    };

    // Create assistant message placeholder
    const assistantMessageId = uuidv4();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    // Generate conversation ID if this is a new conversation
    const actualConversationId = conversationId || uuidv4();
    
    // Add both messages at once to prevent race conditions
    const newMessages = [...messages, userMessage, assistantMessage];
    setMessages(newMessages);
    setStreamingMessageId(assistantMessageId);

    // Save to conversation store
    import('@/lib/conversationStore').then(({ ConversationStore }) => {
      if (!conversationId) {
        // Create new conversation
        ConversationStore.createNewConversation(actualConversationId, userMessage);
        // Notify parent component of new conversation
        onConversationCreate?.(actualConversationId);
        // Update the conversation ID in parent component
        if (payload.conversationId !== actualConversationId) {
          payload.conversationId = actualConversationId;
        }
      } else {
        // Update existing conversation
        ConversationStore.updateConversationWithMessage(actualConversationId, newMessages);
      }
    });

    // Start streaming
    try {
      await startStream('/api/chat/send', payload, {
        onToken: (token) => {
          setMessages(prev => {
            const updated = prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + token }
                : msg
            );
            
            // Save updated messages to store
            import('@/lib/conversationStore').then(({ ConversationStore }) => {
              ConversationStore.updateConversationWithMessage(actualConversationId, updated);
            });
            
            return updated;
          });
        },
        onComplete: () => {
          setStreamingMessageId(null);
        },
        onError: (error) => {
          console.error('Stream error:', error);
          setStreamingMessageId(null);
          // Update the assistant message with error
          setMessages(prev => {
            const updated = prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: 'Sorry, an error occurred while processing your request.' }
                : msg
            );
            
            // Save error message to store
            import('@/lib/conversationStore').then(({ ConversationStore }) => {
              ConversationStore.updateConversationWithMessage(actualConversationId, updated);
            });
            
            return updated;
          });
        },
      });
    } catch (error) {
      console.error('Failed to start stream:', error);
      setStreamingMessageId(null);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: 'Sorry, an error occurred while processing your request.' }
            : msg
        )
      );
    }
  }, [isStreaming, startStream, stopStream]);

  return (
    <div className={cn("h-full flex flex-col", className)}>
      {/* Centered chat interface like ChatGPT */}
      <div className="flex-1 flex items-center justify-center px-4 overflow-hidden">
        <div className="w-full max-w-4xl h-full flex flex-col">
          {messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="w-full">
                <div className="text-center text-muted-foreground mb-8">
                  <h2 className="text-2xl font-semibold mb-2">What are you working on?</h2>
                  <p className="text-sm">Start a conversation to get help with your writing</p>
                </div>
                <div className="w-full max-w-3xl mx-auto">
                  <Composer
                    conversationId={conversationId || uuidv4()}
                    onSend={handleSend}
                    disabled={isStreaming}
                  />
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="flex-1 overflow-hidden">
                <ScrollArea ref={scrollAreaRef} className="h-full [&>div>div]:!pr-6" style={{ scrollbarGutter: 'stable' }}>
                  <div className="py-8 space-y-6 pr-4">
                    {messages.map((message) => (
                      <MessageBubble
                        key={message.id}
                        message={{
                          id: message.id,
                          type: message.role === 'user' ? 'human' : 'ai',
                          content: message.content,
                          timestamp: message.timestamp instanceof Date 
                            ? message.timestamp.toISOString() 
                            : typeof message.timestamp === 'string' 
                              ? message.timestamp 
                              : new Date().toISOString(),
                        }}
                        isLast={message.id === messages[messages.length - 1]?.id}
                      />
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>
              </div>
              
              <div className="flex-shrink-0 pt-4">
                <Composer
                  conversationId={conversationId || uuidv4()}
                  onSend={handleSend}
                  disabled={isStreaming}
                />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

import { useState, useEffect, useCallback, useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useStream } from './useStream';
import { useFileUpload } from './useFileUpload';
import { apiClient } from '../services/advancedApiClient';

export interface ChatMessage {
  id: string;
  type: 'human' | 'ai';
  content: string;
  timestamp: number;
  metadata?: {
    model?: string;
    tokens?: number;
    cost?: number;
    processing_time?: number;
    sources?: any[];
    quality_score?: number;
  };
}

export interface ChatRequest {
  prompt: string;
  mode: string;
  file_ids: string[];
  user_params: {
    citationStyle: string;
    wordCount: number;
    model: string;
    user_id: string;
    academic_level?: string;
    deadline?: string;
    special_instructions?: string;
  };
}

export interface ChatResponse {
  success: boolean;
  response: string;
  sources: any[];
  workflow_status: string;
  system_used: string;
  complexity_score: number;
  routing_reason: string;
  routing_confidence?: number;
  processing_time: number;
  conversation_id?: string;
  citation_count?: number;
  agent_metrics?: any;
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  created_at: number;
  updated_at: number;
  status: 'active' | 'completed' | 'failed' | 'cancelled';
  metadata: {
    total_cost: number;
    total_tokens: number;
    quality_scores: number[];
    processing_times: number[];
  };
}

export interface UseAdvancedChatOptions {
  sessionId?: string;
  onMessage?: (message: ChatMessage) => void;
  onError?: (error: Error) => void;
  onCostUpdate?: (cost: number) => void;
  onQualityUpdate?: (score: number) => void;
  maxRetries?: number;
  retryDelay?: number;
}

export const useAdvancedChat = (options: UseAdvancedChatOptions = {}) => {
  const {
    sessionId: initialSessionId,
    onMessage,
    onError,
    onCostUpdate,
    onQualityUpdate,
    maxRetries = 3,
    retryDelay = 1000
  } = options;

  const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentTraceId, setCurrentTraceId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [estimatedCost, setEstimatedCost] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState(0);
  const [routingDecision, setRoutingDecision] = useState<any>(null);
  
  const queryClient = useQueryClient();
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // File upload hook
  const { getFileIds, clearFiles } = useFileUpload();

  // WebSocket streaming
  const { 
    events, 
    streamingText, 
    totalCost, 
    plagiarismScore, 
    qualityScore, 
    derivatives,
    isConnected,
    connectionError 
  } = useStream(currentTraceId, {
    onMessage: (event) => {
      if (event.type === 'stream' && event.text) {
        // Update the current AI message with streaming text
        setMessages(prev => prev.map(msg => 
          msg.id === currentTraceId 
            ? { ...msg, content: msg.content + event.text }
            : msg
        ));
      }
      
      if (event.type === 'workflow_finished') {
        setIsProcessing(false);
        onQualityUpdate?.(event.payload?.quality || 0);
      }
      
      if (event.type === 'error') {
        handleError(new Error(event.error || 'Unknown error'));
      }
    },
    onError: (error) => {
      handleError(error);
    }
  });

  // Load chat session
  const { data: session, isLoading: isLoadingSession } = useQuery({
    queryKey: ['chat-session', sessionId],
    queryFn: async () => {
      if (!sessionId) return null;
      
      const response = await fetch(`/api/chat/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load chat session');
      }
      
      return response.json();
    },
    enabled: !!sessionId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });

  // Chat mutation with advanced error handling
  const chatMutation = useMutation({
    mutationFn: async (request: ChatRequest): Promise<ChatResponse> => {
      // Cancel any ongoing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      abortControllerRef.current = new AbortController();
      
      // Use AdvancedApiClient to call backend directly
      const { data } = await apiClient.chat(request);
      
      // Transform backend response to expected ChatResponse format
      return {
        success: data.success !== false,
        response: data.message || '',
        sources: data.sources || [],
        workflow_status: data.status || 'completed',
        system_used: 'advanced',
        complexity_score: data.complexity_score || 0,
        routing_reason: data.routing_reason || 'Advanced processing',
        routing_confidence: data.routing_confidence || 1.0,
        processing_time: data.processing_time || 0,
        conversation_id: data.trace_id || data.conversation_id,
        citation_count: data.citation_count || 0,
        agent_metrics: data.agent_metrics || {}
      };
    },
    onSuccess: (response) => {
      const traceId = response.conversation_id || Date.now().toString();
      setCurrentTraceId(traceId);
      setEstimatedCost(0); // Backend doesn't provide cost estimate
      setEstimatedTime(response.processing_time || 0);
      setRoutingDecision({
        system: response.system_used as 'simple' | 'advanced' | 'hybrid',
        reason: response.routing_reason,
        confidence: response.routing_confidence || 0
      });
      setRetryCount(0);
      
      // Create placeholder AI message for streaming
      const aiMessage: ChatMessage = {
        id: traceId,
        type: 'ai',
        content: '', // Will be populated by streaming
        timestamp: Date.now(),
        metadata: {
          model: response.system_used,
          cost: 0,
          processing_time: response.processing_time,
          sources: response.sources,
          quality_score: response.complexity_score
        }
      };
      
      setMessages(prev => [...prev, aiMessage]);
      onMessage?.(aiMessage);
      
      // Start streaming from backend SSE endpoint
      if (traceId) {
        console.log('Starting SSE stream for trace:', traceId);
        apiClient.streamResponse(`/api/stream/${traceId}`, { method: 'GET' }, (chunk) => {
          console.log('SSE chunk received:', chunk);
          
          if (chunk.type === 'token' && chunk.delta) {
            // Update the AI message content with streaming text
            setMessages(prev => prev.map(msg => 
              msg.id === traceId 
                ? { ...msg, content: msg.content + chunk.delta }
                : msg
            ));
          }
          
          if (chunk.type === 'workflow_finished') {
            setIsProcessing(false);
            console.log('Workflow finished');
          }
          
          if (chunk.type === 'error') {
            handleError(new Error(chunk.error || 'Unknown streaming error'));
          }
        }).catch(error => {
          console.error('SSE streaming error:', error);
          handleError(error);
        });
      }
    },
    onError: (error) => {
      handleError(error as Error);
    },
    retry: false // Handle retries manually
  });

  // Advanced error handling with exponential backoff
  const handleError = useCallback((error: Error) => {
    console.error('Chat error:', error);
    setIsProcessing(false);
    
    // Check if we should retry
    if (retryCount < maxRetries && !error.message.includes('abort')) {
      const delay = retryDelay * Math.pow(2, retryCount);
      
      retryTimeoutRef.current = setTimeout(() => {
        setRetryCount(prev => prev + 1);
        console.log(`Retrying chat request (${retryCount + 1}/${maxRetries})`);
        
        // Retry the last request
        if (chatMutation.variables) {
          chatMutation.mutate(chatMutation.variables);
        }
      }, delay);
    } else {
      onError?.(error);
    }
  }, [retryCount, maxRetries, retryDelay, onError, chatMutation]);

  // Send message with validation and preprocessing
  const sendMessage = useCallback(async (
    prompt: string,
    mode: string = 'general',
    options: {
      citationStyle?: string;
      wordCount?: number;
      model?: string;
      academicLevel?: string;
      deadline?: string;
      specialInstructions?: string;
    } = {}
  ) => {
    if (!prompt.trim()) {
      throw new Error('Message cannot be empty');
    }
    
    if (isProcessing) {
      throw new Error('Another message is currently being processed');
    }
    
    setIsProcessing(true);
    
    // Add user message immediately
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'human',
      content: prompt,
      timestamp: Date.now()
    };
    
    setMessages(prev => [...prev, userMessage]);
    onMessage?.(userMessage);
    
    // Get uploaded file IDs - these will be included in the chat request
    const fileIds = getFileIds();
    
    if (fileIds.length > 0) {
      console.log('Including files in chat request:', fileIds);
    }
    
    // Prepare request
    const request: ChatRequest = {
      prompt,
      mode,
      file_ids: fileIds,
      user_params: {
        citationStyle: options.citationStyle || 'Harvard',
        wordCount: options.wordCount || 3000,
        model: options.model || 'gemini-2.5-pro',
        user_id: 'current_user', // Replace with actual user ID
        academic_level: options.academicLevel,
        deadline: options.deadline,
        special_instructions: options.specialInstructions
      }
    };
    
    // Send to backend
    try {
      await chatMutation.mutateAsync(request);
      
      // Clear uploaded files after successful submission
      clearFiles();
    } catch (error) {
      setIsProcessing(false);
      throw error;
    }
  }, [isProcessing, getFileIds, clearFiles, onMessage, chatMutation]);

  // Cancel current request
  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }
    
    setIsProcessing(false);
    setRetryCount(0);
    setCurrentTraceId(null);
  }, []);

  // Create new session
  const createSession = useCallback(async () => {
    const response = await fetch('/api/chat/sessions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to create chat session');
    }
    
    const session = await response.json();
    setSessionId(session.id);
    setMessages([]);
    
    return session;
  }, []);

  // Load session messages
  useEffect(() => {
    if (session?.messages) {
      setMessages(session.messages);
    }
  }, [session]);

  // Update cost tracking
  useEffect(() => {
    if (totalCost !== undefined) {
      onCostUpdate?.(totalCost);
    }
  }, [totalCost, onCostUpdate]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  return {
    // State
    sessionId,
    messages,
    isProcessing,
    isLoadingSession,
    estimatedCost,
    estimatedTime,
    routingDecision,
    
    // WebSocket data
    events,
    streamingText,
    totalCost,
    plagiarismScore,
    qualityScore,
    derivatives,
    isConnected,
    connectionError,
    
    // Actions
    sendMessage,
    cancelRequest,
    createSession,
    
    // Status
    retryCount,
    maxRetries,
    
    // Mutation state
    isLoading: chatMutation.isPending,
    error: chatMutation.error,
    
    // Session data
    session
  };
};
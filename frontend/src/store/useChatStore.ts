import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { ConversationStore, type StoredConversation } from '@/lib/conversationStore';
import { nanoid } from 'nanoid';

export interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  writeupType?: string;
  attachments?: Array<{
    url: string;
    mime: string;
    name: string;
    size: number;
  }>;
  metadata?: {
    system_used?: string;
    complexity_score?: number;
    processing_time?: number;
    sources?: any[];
    trace_id?: string;
  };
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview: string;
  messages: Message[];
}

interface StreamingState {
  isStreaming: boolean;
  currentTraceId?: string;
  streamingMessage?: string;
  agentStatus?: string;
}

interface ChatState {
  // Conversations
  conversations: Conversation[];
  activeConversationId?: string;
  
  // Streaming
  streaming: StreamingState;
  
  // UI State
  sidebarOpen: boolean;
  showReasoningToggle: boolean;
  
  // Error handling
  error?: string;
  lastFailedMessage?: Message;
  
  // Actions
  loadConversations: () => void;
  createConversation: (firstMessage?: Message) => string;
  selectConversation: (id: string) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  deleteConversation: (id: string) => void;
  updateConversationTitle: (id: string, title: string) => void;
  
  // Streaming actions
  startStreaming: (traceId: string) => void;
  updateStreamingMessage: (content: string) => void;
  updateAgentStatus: (status: string) => void;
  stopStreaming: () => void;
  
  // UI actions
  setSidebarOpen: (open: boolean) => void;
  setShowReasoningToggle: (show: boolean) => void;
  setError: (error?: string) => void;
  clearError: () => void;
  
  // Retry functionality
  retryLastFailedMessage: () => Promise<void>;
}

export const useChatStore = create<ChatState>()(
  subscribeWithSelector(
    persist(
      immer((set, get) => ({
        conversations: [],
        streaming: {
          isStreaming: false,
        },
        sidebarOpen: true,
        showReasoningToggle: false,
        
        loadConversations: () => {
          const stored = ConversationStore.getAllConversations();
          set((state) => {
            state.conversations = stored.map(conv => ({
              ...conv,
              messages: conv.messages.map(msg => ({
                ...msg,
                id: msg.id || nanoid(),
                timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : new Date(msg.timestamp).toISOString(),
              }))
            }));
          });
        },
        
        createConversation: (firstMessage) => {
          const id = nanoid();
          const conversation: Conversation = {
            id,
            title: firstMessage?.content?.slice(0, 50) + (firstMessage?.content?.length > 50 ? '...' : '') || 'New conversation',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            message_count: firstMessage ? 1 : 0,
            last_message_preview: firstMessage?.content?.slice(0, 100) || '',
            messages: firstMessage ? [{
              ...firstMessage,
              id: nanoid(),
              conversationId: id,
              timestamp: new Date().toISOString(),
            }] : [],
          };
          
          set((state) => {
            state.conversations.unshift(conversation);
            state.activeConversationId = id;
          });
          
          // Persist to localStorage
          ConversationStore.saveConversation(conversation);
          
          return id;
        },
        
        selectConversation: (id) => {
          set((state) => {
            state.activeConversationId = id;
            state.error = undefined;
          });
        },
        
        addMessage: (messageData) => {
          const message: Message = {
            ...messageData,
            id: nanoid(),
            timestamp: new Date().toISOString(),
          };
          
          set((state) => {
            const conversation = state.conversations.find(c => c.id === message.conversationId);
            if (conversation) {
              conversation.messages.push(message);
              conversation.message_count = conversation.messages.length;
              conversation.updated_at = message.timestamp;
              
              if (message.role === 'user') {
                conversation.last_message_preview = message.content.slice(0, 100);
                conversation.title = conversation.messages.length === 1 
                  ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
                  : conversation.title;
              }
            }
          });
          
          // Persist to localStorage
          const state = get();
          const conversation = state.conversations.find(c => c.id === message.conversationId);
          if (conversation) {
            ConversationStore.updateConversationWithMessage(conversation.id, conversation.messages);
          }
        },
        
        updateMessage: (id, updates) => {
          set((state) => {
            for (const conversation of state.conversations) {
              const message = conversation.messages.find(m => m.id === id);
              if (message) {
                Object.assign(message, updates);
                conversation.updated_at = new Date().toISOString();
                break;
              }
            }
          });
        },
        
        deleteConversation: (id) => {
          set((state) => {
            state.conversations = state.conversations.filter(c => c.id !== id);
            if (state.activeConversationId === id) {
              state.activeConversationId = state.conversations[0]?.id;
            }
          });
          
          ConversationStore.deleteConversation(id);
        },
        
        updateConversationTitle: (id, title) => {
          set((state) => {
            const conversation = state.conversations.find(c => c.id === id);
            if (conversation) {
              conversation.title = title;
              conversation.updated_at = new Date().toISOString();
            }
          });
          
          ConversationStore.updateConversationTitle(id, title);
        },
        
        startStreaming: (traceId) => {
          set((state) => {
            state.streaming = {
              isStreaming: true,
              currentTraceId: traceId,
              streamingMessage: '',
              agentStatus: 'Starting...',
            };
          });
        },
        
        updateStreamingMessage: (content) => {
          set((state) => {
            if (state.streaming.isStreaming) {
              state.streaming.streamingMessage = content;
            }
          });
        },
        
        updateAgentStatus: (status) => {
          set((state) => {
            if (state.streaming.isStreaming) {
              state.streaming.agentStatus = status;
            }
          });
        },
        
        stopStreaming: () => {
          set((state) => {
            state.streaming = {
              isStreaming: false,
            };
          });
        },
        
        setSidebarOpen: (open) => {
          set((state) => {
            state.sidebarOpen = open;
          });
        },
        
        setShowReasoningToggle: (show) => {
          set((state) => {
            state.showReasoningToggle = show;
          });
        },
        
        setError: (error) => {
          set((state) => {
            state.error = error;
          });
        },
        
        clearError: () => {
          set((state) => {
            state.error = undefined;
            state.lastFailedMessage = undefined;
          });
        },
        
        retryLastFailedMessage: async () => {
          const state = get();
          if (!state.lastFailedMessage) return;
          
          // Implementation would depend on the API client
          console.log('Retrying message:', state.lastFailedMessage);
        },
      })),
      {
        name: 'handywriterz-chat-store',
        version: 1,
        partialize: (state) => ({
          sidebarOpen: state.sidebarOpen,
          showReasoningToggle: state.showReasoningToggle,
          // Don't persist conversations (handled by ConversationStore)
          // Don't persist streaming state (ephemeral)
          // Don't persist errors (ephemeral)
        }),
      }
    )
  )
);

// Convenience hooks
export const useActiveConversation = () => useChatStore((state) => {
  const activeId = state.activeConversationId;
  return activeId ? state.conversations.find(c => c.id === activeId) : undefined;
});

export const useStreamingState = () => useChatStore((state) => state.streaming);

export const useChatActions = () => useChatStore((state) => ({
  createConversation: state.createConversation,
  selectConversation: state.selectConversation,
  addMessage: state.addMessage,
  updateMessage: state.updateMessage,
  deleteConversation: state.deleteConversation,
  startStreaming: state.startStreaming,
  updateStreamingMessage: state.updateStreamingMessage,
  updateAgentStatus: state.updateAgentStatus,
  stopStreaming: state.stopStreaming,
  setError: state.setError,
  clearError: state.clearError,
}));
'use client'

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import type { Message } from "@/types";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { EnhancedChatView } from "@/components/EnhancedChatView";
import Sidebar from "@/components/Sidebar";
import { ChatHeader } from "@/components/ChatHeader";
import { MessageInputBar } from "@/components/MessageInputBar";
import { Button } from "@/components/ui/button";
import { useStream } from "@/hooks/useStream";
import { useDynamicAuth } from "@/hooks/useDynamicAuth";

export default function ChatPage() {
  const { isAuthenticated, user: dynamicUser, isLoading } = useDynamicAuth();
  const router = useRouter();

  // Redirect to auth if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen bg-gray-900 text-white items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect via useEffect
  }

  const user = {
    userId: dynamicUser?.id || dynamicUser?.userId || "demo-user",
    walletAddress: dynamicUser?.wallet || null
  };
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<ProcessedEvent[]>([]);
  const [historicalActivities, setHistoricalActivities] = useState<Record<string, ProcessedEvent[]>>({});
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Reference to MessageInputBar for example cards
  const messageInputRef = useRef<any>(null);

  const handleStreamClose = useCallback(() => {
    setIsChatLoading(false);
  }, []);

  const {
    events,
    streamingText,
    reasoningText,
    totalCost,
    plagiarismScore,
    qualityScore,
    derivatives,
    isConnected,
    reset: resetStream
  } = useStream(currentConversationId, {
    onClose: handleStreamClose
  });

  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!user) return;
      try {
        const identifier = user.walletAddress || user.userId;
        const response = await fetch(`/api/users/${identifier}/conversations`);
        if (response.ok) {
          const data = await response.json();
          setChatHistory(data.conversations || []);
        }
      } catch (error) {
        console.error("Failed to fetch chat history:", error);
      }
    };
    fetchChatHistory();
  }, [user]);

  const handleSubmit = useCallback(
    async (submittedInputValue: string, writeupType: string, model: string, fileIds: string[]) => {
      if (!submittedInputValue.trim() && fileIds.length === 0) return;

      setIsChatLoading(true);
      setError(null);
      resetStream();

      const userMessage: Message = {
        id: Date.now().toString(),
        type: "human",
        content: submittedInputValue,
        timestamp: new Date().toISOString(),
      };
      const newMessages = [...messages, userMessage];
      setMessages(newMessages);

      // Save to conversation store
      if (currentConversationId) {
        import('@/lib/conversationStore').then(({ ConversationStore }) => {
          ConversationStore.updateConversationWithMessage(currentConversationId, newMessages);
        });
      }

      const requestPayload = {
        prompt: submittedInputValue,
        mode: writeupType,
        file_ids: fileIds,
        user_params: {
          citationStyle: "Harvard",
          wordCount: 3000,
          model: model,
          user_id: user?.userId || "anonymous"
        }
      };

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestPayload),
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const result = await response.json();

        if (result.trace_id) {
          setCurrentConversationId(result.trace_id);
          const aiMessage: Message = {
            id: result.trace_id,
            type: "ai",
            content: "",
            timestamp: new Date().toISOString(),
          };
          const newMessagesWithAI = [...newMessages, aiMessage];
          setMessages(newMessagesWithAI);

          // Create new conversation in store if this is the first message
          if (!currentConversationId) {
            import('@/lib/conversationStore').then(({ ConversationStore }) => {
              const firstUserMessage = newMessagesWithAI.find(m => m.type === 'human');
              ConversationStore.createNewConversation(result.trace_id, firstUserMessage);
            });
          }
        } else {
          throw new Error("No trace_id received from backend.");
        }

      } catch (error) {
        if (error instanceof Error) setError(error.message);
        else setError("An unknown error occurred");
        setIsChatLoading(false);
      }
    },
    [user, resetStream]
  );

  const handleCancel = useCallback(() => {
    setIsChatLoading(false);
    // Here you might want to send a cancellation request to the backend
  }, []);

  const handleNewChat = useCallback(() => {
    setMessages([]);
    setCurrentConversationId(null);
    setError(null);
    resetStream();
  }, [resetStream]);

  const handleSelectChat = useCallback(async (chatId: string) => {
    try {
      setIsChatLoading(true);
      setError(null);

      const { ConversationStore } = await import('@/lib/conversationStore');
      const conversation = ConversationStore.getConversation(chatId);

      if (conversation) {
        setMessages(conversation.messages || []);
        setCurrentConversationId(chatId);
      } else {
        throw new Error('Conversation not found');
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
      setError('Failed to load conversation');
    } finally {
      setIsChatLoading(false);
    }
  }, []);

  const handleDeleteChat = useCallback((chatId: string) => {
    if (currentConversationId === chatId) {
      handleNewChat();
    }
  }, [currentConversationId, handleNewChat]);

  const handleExport = useCallback(async (format: 'pdf' | 'docx' | 'md') => {
    if (!currentConversationId) return;
    try {
      const response = await fetch(`/api/export/${currentConversationId}?format=${format}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation-${currentConversationId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed. Please try again.');
    }
  }, [currentConversationId]);

  const getCurrentConversationTitle = useCallback(() => {
    if (!currentConversationId || messages.length === 0) return undefined;
    const firstUserMessage = messages.find(m => m.type === 'human');
    if (firstUserMessage && typeof firstUserMessage.content === 'string') {
      const title = firstUserMessage.content.slice(0, 50);
      return title.length < firstUserMessage.content.length ? `${title}...` : title;
    }
    return `Conversation ${currentConversationId.slice(0, 8)}`;
  }, [currentConversationId, messages]);

  // Callback for example cards to set text in MessageInputBar
  const handleExampleClick = useCallback((text: string) => {
    if (messageInputRef.current?.setTextFromExample) {
      messageInputRef.current.setTextFromExample(text);
    }
  }, []);

  return (
    <div className="flex h-screen bg-gray-900 text-white font-sans antialiased">
      <Sidebar
        currentChatId={currentConversationId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        userId={user?.userId}
      />
      <main className="flex-1 flex flex-col min-w-0 relative">
        {messages.length > 0 && (
          <ChatHeader
            conversationId={currentConversationId}
            conversationTitle={getCurrentConversationTitle()}
            onExport={handleExport}
          />
        )}
        <div className="flex-1 flex flex-col overflow-hidden pb-20"> {/* Add padding bottom for fixed input bar */}
          {messages.length === 0 ? (
            <div className="flex-1 overflow-y-auto">
              <WelcomeScreen
                handleSubmit={handleSubmit}
                isLoading={isChatLoading}
                onCancel={handleCancel}
                onExampleClick={handleExampleClick}
              />
            </div>
          ) : error ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-4">
              <h1 className="text-2xl text-red-400 font-bold">Error</h1>
              <p className="text-red-400 text-center max-w-md">{error}</p>
              <Button variant="destructive" onClick={() => window.location.reload()}>
                Retry
              </Button>
            </div>
          ) : (
            <EnhancedChatView
              messages={messages}
              isLoading={isChatLoading}
              liveActivityEvents={events}
              historicalActivities={historicalActivities}
              traceId={currentConversationId}
              totalCost={totalCost}
              plagiarismScore={plagiarismScore}
              qualityScore={qualityScore}
              derivatives={derivatives}
              streamingText={streamingText}
              reasoningText={reasoningText}
              isConnected={isConnected}
              onExport={handleExport}
            />
          )}
        </div>
        {/* MessageInputBar is now fixed at bottom */}
        <MessageInputBar
          ref={messageInputRef}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={isChatLoading}
        />
      </main>
    </div>
  );
}

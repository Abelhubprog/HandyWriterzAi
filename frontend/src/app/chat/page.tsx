'use client'

import { useState, useEffect, useRef, useCallback } from "react";
import { useDynamicContext } from "@dynamic-labs/sdk-react-core";
import type { Message } from "@langchain/langgraph-sdk";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { Button } from "@/components/ui/button";
import { ChatHistory } from "@/components/ChatHistory";
import { useStream } from "@/hooks/useStream";

export default function ChatPage() {
  const { user } = useDynamicContext();
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<ProcessedEvent[]>([]);
  const [historicalActivities, setHistoricalActivities] = useState<Record<string, ProcessedEvent[]>>({});
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  
  // WebSocket streaming
  const { 
    events, 
    streamingText, 
    totalCost, 
    plagiarismScore, 
    qualityScore, 
    derivatives,
    isConnected 
  } = useStream(currentConversationId, {
    onMessage: (event) => {
      if (event.type === 'stream' && event.text) {
        // Update the AI message with streaming text
        setMessages(prev => prev.map(msg => 
          msg.id === currentConversationId 
            ? { ...msg, content: (msg.content as string) + event.text }
            : msg
        ));
      }
    }
  });

  useEffect(() => {
    // Fetch chat history on component mount
    const fetchChatHistory = async () => {
      if (!user) return;
      try {
        // Use wallet address if available, otherwise use userId
        const identifier = user.walletAddress || user.userId;
        const response = await fetch(`http://localhost:8000/api/users/${identifier}/conversations`);
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

  const scrollAreaRef = useRef<HTMLDivElement>(null!);
  const hasFinalizeEventOccurredRef = useRef(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]");
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [messages]);

  useEffect(() => {
    if (hasFinalizeEventOccurredRef.current && !isLoading && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.type === "ai" && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }));
      }
      hasFinalizeEventOccurredRef.current = false;
    }
  }, [messages, isLoading, processedEventsTimeline]);

  const handleSubmit = useCallback(
    async (submittedInputValue: string, writeupType: string, model: string, fileIds: string[]) => {
      if (!submittedInputValue.trim() && fileIds.length === 0) return;
      
      setProcessedEventsTimeline([]);
      setIsLoading(true);
      setError(null);
      hasFinalizeEventOccurredRef.current = false;

      // Add user message to the chat
      const userMessage: Message = {
        id: Date.now().toString(),
        type: "human",
        content: submittedInputValue,
      };
      setMessages(prev => [...prev, userMessage]);

      // Create request payload with file IDs
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
        const response = await fetch("http://localhost:8000/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify(requestPayload),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Backend response:", result);
        
        // Extract trace_id from response  
        const traceId = result.trace_id;
        if (traceId) {
          setCurrentConversationId(traceId);
          
          // Add placeholder AI message that will be updated via WebSocket
          const aiMessage: Message = {
            id: traceId,
            type: "ai",
            content: "", // This will be populated by streaming
          };
          setMessages(prev => [...prev, aiMessage]);
        }
        
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        } else {
          setError("An unknown error occurred");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [user]
  );

  const handleCancel = useCallback(() => {
    setIsLoading(false);
    setProcessedEventsTimeline([]);
  }, []);

  return (
    <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
      <aside className="w-1/4 p-4 border-r border-neutral-700 flex flex-col">
        <div className="flex-grow">
          <ChatHistory history={chatHistory} onSelectConversation={(id) => console.log(id)} />
        </div>
        <div className="mt-auto">
          {/* User Profile and Settings */}
        </div>
      </aside>
      <main className="h-full w-full flex flex-col">
        <div className="flex-grow">
          {messages.length === 0 ? (
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={isLoading}
              onCancel={handleCancel}
            />
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-full">
              <div className="flex flex-col items-center justify-center gap-4">
                <h1 className="text-2xl text-red-400 font-bold">Error</h1>
                <p className="text-red-400">{JSON.stringify(error)}</p>
                <Button variant="destructive" onClick={() => window.location.reload()}>
                  Retry
                </Button>
              </div>
            </div>
          ) : (
            <ChatMessagesView
              messages={messages}
              isLoading={isLoading}
              scrollAreaRef={scrollAreaRef}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              liveActivityEvents={events}
              historicalActivities={historicalActivities}
              traceId={currentConversationId}
              totalCost={totalCost}
              plagiarismScore={plagiarismScore}
              qualityScore={qualityScore}
              derivatives={derivatives}
            />
          )}
        </div>
      </main>
    </div>
  );
}
'use client'

import { ChatPane } from '@/components/ChatPane';
import Sidebar from '@/components/Sidebar';
import { useState, useCallback } from 'react';

export default function ChatPage() {
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

  const handleNewChat = useCallback(() => {
    setCurrentConversationId(null);
  }, []);

  const handleSelectChat = useCallback((chatId: string) => {
    setCurrentConversationId(chatId);
  }, []);

  const handleDeleteChat = useCallback((chatId: string) => {
    if (currentConversationId === chatId) {
      handleNewChat();
    }
  }, [currentConversationId, handleNewChat]);

  const handleConversationCreate = useCallback((conversationId: string) => {
    setCurrentConversationId(conversationId);
  }, []);

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <div className="flex-shrink-0">
        <Sidebar
          currentChatId={currentConversationId}
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          userId="demo-user"
        />
      </div>
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <ChatPane 
          conversationId={currentConversationId || undefined} 
          onConversationCreate={handleConversationCreate}
        />
      </main>
    </div>
  );
}

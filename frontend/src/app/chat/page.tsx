'use client'

import { ChatPane } from '@/components/ChatPane';
import Sidebar from '@/components/Sidebar';
import { useCallback } from 'react';
import { useChatStore, useChatActions } from '@/store/useChatStore';

export default function ChatPage() {
  const activeConversationId = useChatStore((state) => state.activeConversationId);
  const { selectConversation, deleteConversation, loadConversations } = useChatActions();

  const handleNewChat = useCallback(() => {
    // Clear the active conversation to start fresh
    selectConversation('');
    console.log('New chat clicked - cleared active conversation');
  }, [selectConversation]);

  const handleSelectChat = useCallback((chatId: string) => {
    selectConversation(chatId);
  }, [selectConversation]);

  const handleDeleteChat = useCallback((chatId: string) => {
    deleteConversation(chatId);
  }, [deleteConversation]);

  const handleConversationCreate = useCallback((conversationId: string) => {
    selectConversation(conversationId);
  }, [selectConversation]);

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <div className="flex-shrink-0">
        <Sidebar
          currentChatId={activeConversationId}
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          userId="demo-user"
        />
      </div>
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <ChatPane 
          conversationId={activeConversationId || undefined} 
          onConversationCreate={handleConversationCreate}
        />
      </main>
    </div>
  );
}

'use client'

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Plus, MessageSquare, Library, Settings, User, ChevronDown, MoreHorizontal, Edit, Trash } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview?: string;
}

interface ChatSidebarProps {
  currentChatId?: string | null;
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
  userId?: string;
}

export function ChatSidebar({ 
  currentChatId, 
  onNewChat, 
  onSelectChat, 
  onDeleteChat,
  userId = "demo-user"
}: ChatSidebarProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load conversations from local storage
  useEffect(() => {
    const loadConversations = () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Import the conversation store dynamically to avoid SSR issues
        import('@/lib/conversationStore').then(({ ConversationStore }) => {
          const storedConversations = ConversationStore.getAllConversations();
          setConversations(storedConversations);
          setIsLoading(false);
        });
      } catch (error) {
        console.error('Error loading conversations:', error);
        setError('Failed to load chat history');
        setConversations([]);
        setIsLoading(false);
      }
    };

    loadConversations();
  }, [userId]);

  // Refresh conversations from local storage
  const fetchConversations = useCallback(async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const { ConversationStore } = await import('@/lib/conversationStore');
      const storedConversations = ConversationStore.getAllConversations();
      setConversations(storedConversations);
    } catch (error) {
      console.error('Error loading conversations:', error);
      setError('Failed to load chat history');
      setConversations([]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  // Filter conversations based on search query
  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.last_message_preview?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
      
      if (diffInHours < 1) {
        return 'Just now';
      } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)} hour${Math.floor(diffInHours) !== 1 ? 's' : ''} ago`;
      } else if (diffInHours < 48) {
        return 'Yesterday';
      } else {
        return date.toLocaleDateString();
      }
    } catch {
      return 'Unknown';
    }
  };

  const handleDeleteConversation = useCallback(async (conversationId: string) => {
    try {
      const { ConversationStore } = await import('@/lib/conversationStore');
      ConversationStore.deleteConversation(conversationId);
      
      // Remove from local state
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      
      // Call parent handler
      onDeleteChat(conversationId);
      
      // If we deleted the current conversation, trigger new chat
      if (currentChatId === conversationId) {
        onNewChat();
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
      alert('Failed to delete conversation. Please try again.');
    }
  }, [currentChatId, onDeleteChat, onNewChat]);

  const handleRenameConversation = useCallback(async (conversationId: string) => {
    const newTitle = prompt('Enter new conversation title:');
    if (!newTitle || !newTitle.trim()) return;
    
    try {
      const { ConversationStore } = await import('@/lib/conversationStore');
      ConversationStore.updateConversationTitle(conversationId, newTitle.trim());
      
      // Update local state
      setConversations(prev => 
        prev.map(conv => 
          conv.id === conversationId 
            ? { ...conv, title: newTitle.trim() }
            : conv
        )
      );
    } catch (error) {
      console.error('Error renaming conversation:', error);
      alert('Failed to rename conversation. Please try again.');
    }
  }, []);

  return (
    <div className="flex flex-col h-full bg-gray-900 border-r border-gray-700 text-white w-80">
      {/* Header with New Chat button */}
      <div className="p-3 border-b border-gray-700">
        <Button
          onClick={onNewChat}
          className="w-full bg-transparent border border-gray-600 hover:bg-gray-800 text-white justify-start gap-2"
          variant="outline"
        >
          <Plus className="h-4 w-4" />
          New chat
        </Button>
      </div>

      {/* Search */}
      <div className="p-3 border-b border-gray-700">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search chats"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-gray-800 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2">
          {isLoading ? (
            <div className="text-center py-8 text-gray-400">
              Loading conversations...
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-red-400 text-sm mb-2">{error}</p>
              <Button 
                onClick={fetchConversations}
                variant="outline" 
                size="sm"
                className="text-gray-300 border-gray-600 hover:bg-gray-800"
              >
                Retry
              </Button>
            </div>
          ) : filteredConversations.length > 0 ? (
            <div className="space-y-1">
              {filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                    currentChatId === conversation.id
                      ? 'bg-gray-800 border border-gray-600'
                      : 'hover:bg-gray-800'
                  }`}
                  onClick={() => onSelectChat(conversation.id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <MessageSquare className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <h3 className="text-sm font-medium text-white truncate">
                        {conversation.title}
                      </h3>
                    </div>
                    {conversation.last_message_preview && (
                      <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed">
                        {conversation.last_message_preview}
                      </p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      {formatTimestamp(conversation.updated_at)}
                    </p>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0 text-gray-400 hover:text-white"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="bg-gray-800 border-gray-600">
                      <DropdownMenuItem 
                        className="text-gray-300 hover:bg-gray-700 cursor-pointer"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRenameConversation(conversation.id);
                        }}
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        Rename
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="text-red-400 hover:bg-gray-700 cursor-pointer"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm('Are you sure you want to delete this conversation?')) {
                            handleDeleteConversation(conversation.id);
                          }
                        }}
                      >
                        <Trash className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              {searchQuery ? 'No chats found' : 'No conversations yet'}
            </div>
          )}
        </div>
      </div>

      {/* Navigation Menu */}
      <div className="border-t border-gray-700 p-2">
        <div className="space-y-1">
          <Button
            variant="ghost"
            onClick={() => router.push('/library')}
            className="w-full justify-start gap-3 text-gray-300 hover:text-white hover:bg-gray-800"
          >
            <Library className="h-4 w-4" />
            Library
          </Button>
          
          <Button
            variant="ghost"
            onClick={() => router.push('/settings')}
            className="w-full justify-start gap-3 text-gray-300 hover:text-white hover:bg-gray-800"
          >
            <Settings className="h-4 w-4" />
            Settings
          </Button>
        </div>
      </div>

      {/* User Profile */}
      <div className="border-t border-gray-700 p-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-gray-300 hover:text-white hover:bg-gray-800 p-2"
            >
              <Avatar className="h-6 w-6">
                <AvatarImage src="/api/placeholder/32/32" alt="User" />
                <AvatarFallback className="bg-blue-600 text-white text-xs">
                  {userId.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm truncate">{userId}</span>
              <ChevronDown className="h-4 w-4 ml-auto" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="bg-gray-800 border-gray-600 w-56">
            <DropdownMenuItem 
              className="text-gray-300 hover:bg-gray-700 cursor-pointer"
              onClick={() => router.push('/profile')}
            >
              <User className="h-4 w-4 mr-2" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem 
              className="text-gray-300 hover:bg-gray-700 cursor-pointer"
              onClick={() => router.push('/settings')}
            >
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-gray-600" />
            <DropdownMenuItem 
              className="text-red-400 hover:bg-gray-700 cursor-pointer"
              onClick={() => {
                // Handle sign out logic
                localStorage.removeItem('access_token');
                router.push('/');
              }}
            >
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
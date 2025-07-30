'use client'

import { useState } from 'react';
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

interface ChatItem {
  id: string;
  title: string;
  timestamp: string;
  preview?: string;
}

interface ImprovedSidebarProps {
  currentChatId?: string | null;
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
}

export function ImprovedSidebar({ 
  currentChatId, 
  onNewChat, 
  onSelectChat, 
  onDeleteChat 
}: ImprovedSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Mock chat data - replace with real data from your store
  const mockChats: ChatItem[] = [
    {
      id: '1',
      title: 'PhD Dissertation Research',
      timestamp: 'Yesterday',
      preview: 'Create a comprehensive PhD dissertation on AI-Powered Educational Technology Impact...'
    },
    {
      id: '2', 
      title: 'Market Research Analysis',
      timestamp: '2 days ago',
      preview: 'Industry analysis for strategic insights...'
    },
    {
      id: '3',
      title: 'Technical Report Writing',
      timestamp: '1 week ago',
      preview: 'Complex data analysis and clear conclusions...'
    }
  ];

  const filteredChats = mockChats.filter(chat =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chat.preview?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatTimestamp = (timestamp: string) => {
    // Simple timestamp formatting - enhance as needed
    return timestamp;
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 border-r border-gray-700 text-white">
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
          {filteredChats.length > 0 ? (
            <div className="space-y-1">
              {filteredChats.map((chat) => (
                <div
                  key={chat.id}
                  className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                    currentChatId === chat.id
                      ? 'bg-gray-800 border border-gray-600'
                      : 'hover:bg-gray-800'
                  }`}
                  onClick={() => onSelectChat(chat.id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <MessageSquare className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <h3 className="text-sm font-medium text-white truncate">
                        {chat.title}
                      </h3>
                    </div>
                    {chat.preview && (
                      <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed">
                        {chat.preview}
                      </p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      {formatTimestamp(chat.timestamp)}
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
                      <DropdownMenuItem className="text-gray-300 hover:bg-gray-700">
                        <Edit className="h-4 w-4 mr-2" />
                        Rename
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="text-red-400 hover:bg-gray-700"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteChat(chat.id);
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
            className="w-full justify-start gap-3 text-gray-300 hover:text-white hover:bg-gray-800"
          >
            <Library className="h-4 w-4" />
            Library
          </Button>
          
          <Button
            variant="ghost"
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
                  U
                </AvatarFallback>
              </Avatar>
              <span className="text-sm">User Account</span>
              <ChevronDown className="h-4 w-4 ml-auto" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="bg-gray-800 border-gray-600 w-56">
            <DropdownMenuItem className="text-gray-300 hover:bg-gray-700">
              <User className="h-4 w-4 mr-2" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-gray-700">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-gray-600" />
            <DropdownMenuItem className="text-red-400 hover:bg-gray-700">
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
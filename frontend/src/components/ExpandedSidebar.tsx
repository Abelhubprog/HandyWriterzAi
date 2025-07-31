import {
  FolderIcon,
  SettingsIcon,
  SearchIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronDownIcon,
  MoreHorizontalIcon,
  EditIcon,
  TrashIcon,
  MessageSquareIcon,
} from 'lucide-react'
import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { SettingsModal } from '@/components/SettingsModal'

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview?: string;
}

interface ExpandedSidebarProps {
  onToggle: () => void
  currentChatId?: string | null;
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
  userId?: string;
}

export function ExpandedSidebar({
  onToggle,
  currentChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  userId = "demo-user"
}: ExpandedSidebarProps) {
  const router = useRouter()
  const [convosOpen, setConvosOpen] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)

  // Load conversations from local storage
  useEffect(() => {
    const loadConversations = () => {
      setIsLoading(true);

      try {
        import('@/lib/conversationStore').then(({ ConversationStore }) => {
          const storedConversations = ConversationStore.getAllConversations();
          setConversations(storedConversations);
          setIsLoading(false);
        });
      } catch (error) {
        console.error('Error loading conversations:', error);
        setConversations([]);
        setIsLoading(false);
      }
    };

    loadConversations();

    // Listen for storage changes to refresh conversations
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'handywriterz_conversations') {
        loadConversations();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically for updates
    const interval = setInterval(loadConversations, 2000);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [userId]);

  // Filter conversations based on search query
  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.last_message_preview?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDeleteConversation = useCallback(async (conversationId: string) => {
    try {
      const { ConversationStore } = await import('@/lib/conversationStore');
      ConversationStore.deleteConversation(conversationId);

      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      onDeleteChat(conversationId);

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
    <div className="flex flex-col h-full">
      {/* Header with toggle */}
      <div className="p-4 flex items-center justify-between border-b border-border">
        <h2 className="text-lg font-semibold text-foreground">HandyWriterz</h2>
        <Button
          onClick={onToggle}
          variant="ghost"
          size="icon"
          className="w-8 h-8 text-muted-foreground hover:text-foreground hover:bg-secondary"
          aria-expanded={true}
        >
          <ChevronLeftIcon className="w-4 h-4" />
        </Button>
      </div>

      {/* New chat + Search */}
      <div className="p-4 space-y-3">
        <Button
          onClick={onNewChat}
          className="flex items-center w-full px-3 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          New chat
        </Button>
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search chats"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              setConvosOpen(true)
            }}
            className="w-full pl-9 pr-3 py-2 bg-secondary rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-sm text-foreground placeholder-muted-foreground"
          />
        </div>
      </div>

      {/* My Conversations */}
      <div className="px-4 flex-1 overflow-hidden">
        <button
          onClick={() => setConvosOpen(!convosOpen)}
          className="flex items-center w-full py-2 text-sm hover:bg-secondary rounded-md px-2 text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          aria-expanded={convosOpen}
        >
          <ChevronDownIcon className={`w-4 h-4 mr-2 transform transition-transform duration-200 ${convosOpen ? 'rotate-0' : '-rotate-90'}`} />
          My Conversations
        </button>

        <div className={`transition-all duration-300 ease-in-out overflow-hidden ${convosOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
          <div className="mt-2 overflow-y-auto">
            {isLoading ? (
              <div className="text-muted-foreground italic text-sm px-2 py-2">Loading...</div>
            ) : filteredConversations.length > 0 ? (
              <ul className="space-y-1">
                {filteredConversations.map(conversation => (
                  <li key={conversation.id}>
                    <div
                      className={`group flex items-center justify-between px-2 py-2 rounded-md cursor-pointer transition-colors ${
                        currentChatId === conversation.id
                          ? 'bg-secondary'
                          : 'hover:bg-secondary/50'
                      }`}
                      onClick={() => onSelectChat(conversation.id)}
                    >
                      <div className="flex items-center min-w-0 flex-1">
                        <MessageSquareIcon className="w-4 h-4 mr-2 text-muted-foreground flex-shrink-0" />
                        <span className="text-sm truncate text-foreground">
                          {conversation.title}
                        </span>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0 text-muted-foreground hover:text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreHorizontalIcon className="h-3 w-3" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-background border-border">
                          <DropdownMenuItem
                            className="text-foreground hover:bg-secondary cursor-pointer text-xs"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRenameConversation(conversation.id);
                            }}
                          >
                            <EditIcon className="h-3 w-3 mr-2" />
                            Rename
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive hover:bg-secondary cursor-pointer text-xs"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (confirm('Are you sure you want to delete this conversation?')) {
                                handleDeleteConversation(conversation.id);
                              }
                            }}
                          >
                            <TrashIcon className="h-3 w-3 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-muted-foreground italic text-sm px-2 py-2">
                {searchQuery ? 'No chats found' : 'No conversations yet'}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Library */}
      <div className="px-4 py-2">
        <Link
          href="/library"
          className="flex items-center px-3 py-2 hover:bg-secondary rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-ring text-foreground"
        >
          <FolderIcon className="w-4 h-4 mr-2" />
          Library
        </Link>
      </div>

      {/* Settings + Account */}
      <div className="px-4 pb-4 space-y-2 border-t border-border pt-4">
        <button
          onClick={() => setShowSettingsModal(true)}
          className="flex items-center w-full px-3 py-2 hover:bg-secondary rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-ring text-foreground"
        >
          <SettingsIcon className="w-4 h-4 mr-2" />
          Settings
        </button>

        <div className="flex items-center mt-4 px-3 py-2 bg-secondary rounded-md">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mr-3 flex items-center justify-center">
            <span className="text-sm font-medium text-white">
              {userId.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm text-foreground truncate">{userId}</div>
            <button
              onClick={() => {
  localStorage.removeItem('access_token');
  window.location.href = '/';
}}
              className="text-xs text-muted-foreground hover:underline focus:outline-none focus:ring-2 focus:ring-ring"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <SettingsModal
        open={showSettingsModal}
        onOpenChange={setShowSettingsModal}
      />
    </div>
  )
}

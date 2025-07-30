'use client'

import { useRouter } from 'next/navigation'
import { useSidebar } from '@/hooks/useSidebar'
import { CollapsedSidebar } from '@/components/CollapsedSidebar'
import { ExpandedSidebar } from '@/components/ExpandedSidebar'

interface SidebarProps {
  currentChatId?: string | null;
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
  userId?: string;
}

export default function Sidebar({
  currentChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  userId = "demo-user"
}: SidebarProps) {
  const router = useRouter()
  const { collapsed, isMobile, showMobileOverlay, toggle, closeMobileOverlay } = useSidebar()

  const handleOpenSearch = () => {
    if (collapsed && !isMobile) {
      toggle() // Expand sidebar to show search
    }
    // Focus on search input after expansion
    setTimeout(() => {
      const searchInput = document.querySelector('input[placeholder="Search chats"]') as HTMLInputElement
      if (searchInput) {
        searchInput.focus()
      }
    }, 300)
  }

  const handleOpenLibrary = () => {
    router.push('/library')
  }

  const handleOpenSettings = () => {
    if (collapsed && !isMobile) {
      toggle() // Expand sidebar to show settings modal
    }
    // The ExpandedSidebar handles the modal opening
  }

  const handleOpenProfile = () => {
    router.push('/profile')
  }

  return (
    <>
      {/* Main sidebar */}
      <aside
        className={`flex flex-col h-screen bg-gray-900 text-gray-100 border-r border-gray-800 transition-all duration-300 ease-in-out ${
          collapsed ? 'w-16' : 'w-64'
        }`}
        role="navigation"
      >
        {collapsed ? (
          <CollapsedSidebar
            onToggle={toggle}
            onNewChat={onNewChat}
            onOpenSearch={handleOpenSearch}
            onOpenLibrary={handleOpenLibrary}
            onOpenSettings={handleOpenSettings}
            onOpenProfile={handleOpenProfile}
            userId={userId}
          />
        ) : (
          <ExpandedSidebar
            onToggle={toggle}
            currentChatId={currentChatId}
            onNewChat={onNewChat}
            onSelectChat={onSelectChat}
            onDeleteChat={onDeleteChat}
            userId={userId}
          />
        )}
      </aside>

      {/* Mobile overlay */}
      {isMobile && showMobileOverlay && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden">
          <div className="w-64 h-full bg-gray-900">
            <ExpandedSidebar
              onToggle={closeMobileOverlay}
              currentChatId={currentChatId}
              onNewChat={() => {
                onNewChat()
                closeMobileOverlay()
              }}
              onSelectChat={(chatId) => {
                onSelectChat(chatId)
                closeMobileOverlay()
              }}
              onDeleteChat={onDeleteChat}
              userId={userId}
            />
          </div>
        </div>
      )}
    </>
  )
}
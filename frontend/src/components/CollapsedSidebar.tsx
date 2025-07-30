import {
  FolderIcon,
  SettingsIcon,
  SearchIcon,
  PlusIcon,
  ChevronRightIcon,
  UserIcon,
} from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Tooltip } from '@/components/ui/tooltip'
import { SettingsModal } from '@/components/SettingsModal'

interface CollapsedSidebarProps {
  onToggle: () => void
  onNewChat: () => void
  onOpenSearch: () => void
  onOpenLibrary: () => void
  onOpenSettings: () => void
  onOpenProfile: () => void
  userId?: string
}

export function CollapsedSidebar({
  onToggle,
  onNewChat,
  onOpenSearch,
  onOpenLibrary,
  onOpenSettings,
  onOpenProfile,
  userId = "demo-user"
}: CollapsedSidebarProps) {
  const [showSettingsModal, setShowSettingsModal] = useState(false)

  return (
    <div className="flex flex-col h-full">
      {/* Toggle button */}
      <div className="p-3 flex justify-center border-b border-gray-800">
        <Tooltip content="Expand sidebar">
          <Button
            onClick={onToggle}
            variant="ghost"
            size="icon"
            className="w-8 h-8 text-gray-400 hover:text-white hover:bg-gray-800"
            aria-expanded={false}
          >
            <ChevronRightIcon className="w-4 h-4" />
          </Button>
        </Tooltip>
      </div>

      {/* Main navigation icons */}
      <div className="flex-1 py-4 space-y-2">
        <div className="px-3 flex justify-center">
          <Tooltip content="New chat">
            <Button
              onClick={onNewChat}
              variant="ghost"
              size="icon"
              className="w-8 h-8 text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <PlusIcon className="w-4 h-4" />
            </Button>
          </Tooltip>
        </div>

        <div className="px-3 flex justify-center">
          <Tooltip content="Search chats">
            <Button
              onClick={onOpenSearch}
              variant="ghost"
              size="icon"
              className="w-8 h-8 text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <SearchIcon className="w-4 h-4" />
            </Button>
          </Tooltip>
        </div>

        <div className="px-3 flex justify-center">
          <Tooltip content="Library">
            <Button
              onClick={onOpenLibrary}
              variant="ghost"
              size="icon"
              className="w-8 h-8 text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <FolderIcon className="w-4 h-4" />
            </Button>
          </Tooltip>
        </div>
      </div>

      {/* Bottom section */}
      <div className="border-t border-gray-800 py-4 space-y-2">
        <div className="px-3 flex justify-center">
          <Tooltip content="Settings">
            <Button
              onClick={() => setShowSettingsModal(true)}
              variant="ghost"
              size="icon"
              className="w-8 h-8 text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <SettingsIcon className="w-4 h-4" />
            </Button>
          </Tooltip>
        </div>

        <div className="px-3 flex justify-center">
          <Tooltip content={`Profile (${userId})`}>
            <Button
              onClick={onOpenProfile}
              variant="ghost"
              size="icon"
              className="w-8 h-8 text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <div className="w-6 h-6 bg-gray-700 rounded-full flex items-center justify-center">
                <span className="text-xs font-medium">
                  {userId.charAt(0).toUpperCase()}
                </span>
              </div>
            </Button>
          </Tooltip>
        </div>
      </div>

      <SettingsModal 
        open={showSettingsModal} 
        onOpenChange={setShowSettingsModal} 
      />
    </div>
  )
}
'use client'

import React from 'react';
import { Download, Share, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { UserMenu } from '@/components/UserMenu'
import { CreditsBadge } from '@/components/CreditsBadge'

interface ChatHeaderProps {
  conversationId?: string | null;
  conversationTitle?: string;
  onExport?: (format: 'pdf' | 'docx' | 'md') => void;
  onShare?: () => void;
}

export function ChatHeader({ 
  conversationId, 
  conversationTitle, 
  onExport, 
  onShare 
}: ChatHeaderProps) {
  const handleExport = async (format: 'pdf' | 'docx' | 'md') => {
    if (!conversationId) return;
    
    try {
      if (onExport) {
        onExport(format);
      } else {
        // Default export implementation
        const response = await fetch(`/api/export/${conversationId}?format=${format}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `conversation-${conversationId}.${format}`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        } else {
          throw new Error('Export failed');
        }
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed. Please try again.');
    }
  };

  const handleShare = () => {
    if (onShare) {
      onShare();
    } else {
      // Default share implementation
      if (navigator.share && conversationId) {
        navigator.share({
          title: conversationTitle || 'HandyWriterz Conversation',
          url: `${window.location.origin}/chat/${conversationId}`,
        }).catch(console.error);
      } else {
        // Fallback to clipboard
        const url = `${window.location.origin}/chat/${conversationId}`;
        navigator.clipboard.writeText(url).then(() => {
          alert('Link copied to clipboard!');
        }).catch(() => {
          alert('Could not copy link. Please try again.');
        });
      }
    }
  };

  if (!conversationId) {
    return null; // Don't show header for welcome screen
  }

  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-gray-700 bg-gray-900">
      <div className="flex-1">
        <h1 className="text-lg font-medium text-white truncate">
          {conversationTitle || 'Conversation'}
        </h1>
      </div>
      
      <div className="flex items-center gap-2">
        {/* Credits + User */}
        <CreditsBadge />
        <UserMenu compact />

        {/* Export Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="text-gray-300 hover:text-white hover:bg-gray-800"
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-gray-800 border-gray-600">
            <DropdownMenuItem 
              onClick={() => handleExport('pdf')}
              className="text-gray-300 hover:bg-gray-700 cursor-pointer"
            >
              📄 Export as PDF
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => handleExport('docx')}
              className="text-gray-300 hover:bg-gray-700 cursor-pointer"
            >
              📝 Export as DOCX
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => handleExport('md')}
              className="text-gray-300 hover:bg-gray-700 cursor-pointer"
            >
              📋 Export as Markdown
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Share Button */}
        <Button
          onClick={handleShare}
          variant="ghost"
          size="sm"
          className="text-gray-300 hover:text-white hover:bg-gray-800"
        >
          <Share className="h-4 w-4 mr-2" />
          Share
        </Button>

        {/* More Options */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="text-gray-300 hover:text-white hover:bg-gray-800 p-2"
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-gray-800 border-gray-600">
            <DropdownMenuItem className="text-gray-300 hover:bg-gray-700">
              Rename conversation
            </DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-gray-700">
              Archive conversation
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-gray-600" />
            <DropdownMenuItem className="text-red-400 hover:bg-gray-700">
              Delete conversation
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}

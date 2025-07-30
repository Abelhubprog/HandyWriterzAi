'use client'

import React, { useState } from 'react';
import { Copy, Share2, Download, ThumbsUp, ThumbsDown, Check, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/components/ui/use-toast';

interface ResponseActionsProps {
  messageId: string;
  messageContent?: string;
  conversationId?: string | null;
  onCopy?: () => void;
  onExport?: (format: 'pdf' | 'docx' | 'md') => void;
}

export function ResponseActions({ 
  messageId, 
  messageContent, 
  conversationId, 
  onCopy, 
  onExport 
}: ResponseActionsProps) {
  const [copied, setCopied] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const { toast } = useToast();

  const handleCopy = async () => {
    if (onCopy) {
      onCopy();
      return;
    }
    
    if (messageContent) {
      try {
        await navigator.clipboard.writeText(messageContent);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        toast({
          title: "Copied to clipboard",
          duration: 2000,
        });
      } catch (error) {
        toast({
          title: "Failed to copy",
          variant: "destructive",
        });
      }
    }
  };

  const handleShareLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast({
        title: "Link copied",
        description: "Conversation link copied to clipboard.",
      });
    } catch (error) {
      toast({
        title: "Failed to copy link",
        variant: "destructive",
      });
    }
  };

  const handleSocialShare = (platform: string) => {
    const text = encodeURIComponent(
      messageContent 
        ? messageContent.slice(0, 280) + (messageContent.length > 280 ? '...' : '')
        : 'Check out this AI-generated response from HandyWriterz'
    );
    const url = encodeURIComponent(window.location.href);
    
    let shareUrl = '';
    switch (platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
        break;
      case 'linkedin':
        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
        break;
      case 'reddit':
        shareUrl = `https://reddit.com/submit?url=${url}&title=${text}`;
        break;
    }
    
    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
    }
  };

  const handleDownload = async (format: 'pdf' | 'docx' | 'md') => {
    if (onExport) {
      onExport(format);
      return;
    }

    if (!conversationId) {
      toast({
        title: "Download failed",
        description: "No conversation ID available.",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsDownloading(true);
      const response = await fetch(`/api/export/${conversationId}?format=${format}`);
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `conversation-${conversationId}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: "Download started",
        description: `Downloading as ${format.toUpperCase()}...`,
      });
    } catch (error) {
      console.error('Download error:', error);
      toast({
        title: "Download failed",
        description: "Could not download the conversation.",
        variant: "destructive",
      });
    } finally {
      setIsDownloading(false);
    }
  };

  const handleFeedback = (type: 'positive' | 'negative') => {
    // TODO: Implement feedback API call
    toast({
      title: `${type === 'positive' ? 'Positive' : 'Negative'} feedback recorded`,
      description: "Thank you for your feedback!",
    });
  };

  return (
    <div className="flex items-center gap-1 text-gray-500">
      {/* Copy Button */}
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={handleCopy} 
        className="h-7 px-2 hover:bg-gray-700/50 hover:text-white"
        title="Copy message"
      >
        {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
      </Button>

      {/* Share Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-7 px-2 hover:bg-gray-700/50 hover:text-white"
            title="Share"
          >
            <Share2 className="h-3 w-3" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="bg-gray-800 border-gray-600 text-gray-200">
          <DropdownMenuItem 
            onClick={handleShareLink}
            className="hover:bg-gray-700 focus:bg-gray-700"
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Copy link
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-gray-600" />
          <DropdownMenuItem 
            onClick={() => handleSocialShare('twitter')}
            className="hover:bg-gray-700 focus:bg-gray-700"
          >
            Share on X
          </DropdownMenuItem>
          <DropdownMenuItem 
            onClick={() => handleSocialShare('linkedin')}
            className="hover:bg-gray-700 focus:bg-gray-700"
          >
            Share on LinkedIn
          </DropdownMenuItem>
          <DropdownMenuItem 
            onClick={() => handleSocialShare('reddit')}
            className="hover:bg-gray-700 focus:bg-gray-700"
          >
            Share on Reddit
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Download Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button 
            variant="ghost" 
            size="sm" 
            disabled={isDownloading}
            className="h-7 px-2 hover:bg-gray-700/50 hover:text-white"
            title="Download"
          >
            <Download className="h-3 w-3" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="bg-gray-800 border-gray-600 text-gray-200">
          <DropdownMenuItem 
            onClick={() => handleDownload('pdf')} 
            disabled={isDownloading}
            className="hover:bg-gray-700 focus:bg-gray-700"
          >
            Download PDF
          </DropdownMenuItem>
          <DropdownMenuItem 
            onClick={() => handleDownload('docx')} 
            disabled={isDownloading}
            className="hover:bg-gray-700 focus:bg-gray-700"
          >
            Download DOCX
          </DropdownMenuItem>
          <DropdownMenuItem 
            onClick={() => handleDownload('md')} 
            disabled={isDownloading}
            className="hover:bg-gray-700 focus:bg-gray-700"
          >
            Download Markdown
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Feedback Buttons */}
      <div className="border-l border-gray-700 h-4 mx-2" />
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => handleFeedback('positive')}
        className="h-7 px-2 hover:bg-gray-700/50 hover:text-green-400"
        title="Good response"
      >
        <ThumbsUp className="h-3 w-3" />
      </Button>
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => handleFeedback('negative')}
        className="h-7 px-2 hover:bg-gray-700/50 hover:text-red-400"
        title="Poor response"
      >
        <ThumbsDown className="h-3 w-3" />
      </Button>
    </div>
  );
}
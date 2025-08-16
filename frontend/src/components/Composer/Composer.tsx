'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { AttachButton } from './AttachButton';
import { WriteupSelect } from './WriteupSelect';
import { MicButton } from './MicButton';
import { SendButton } from './SendButton';
import { cn } from '@/lib/utils';
import { useToast } from '@/components/ui/use-toast';

interface FileAttachment {
  id: string;
  file: File;
  url: string;
  name: string;
  size: number;
  mime: string;
  uploading?: boolean;
  uploaded?: boolean;
  file_id?: string; // Backend file ID for actual processing
  error?: string;
}

interface ComposerProps {
  conversationId: string;
  onSend: (payload: {
    conversationId: string;
    author: 'user';
    content: string;
    writeupType: string;
    attachments?: Array<{
      url: string;
      mime: string;
      name: string;
      size: number;
      file_id?: string;
    }>;
  }) => void;
  disabled?: boolean;
  className?: string;
}

export function Composer({ conversationId, onSend, disabled = false, className }: ComposerProps) {
  const [content, setContent] = useState('');
  const [writeupType, setWriteupType] = useState('general');
  const [attachments, setAttachments] = useState<FileAttachment[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const canSend = (content.trim().length > 0 || attachments.length > 0) && !disabled;

  const handleSend = useCallback(async () => {
    if (!canSend || disabled) return;

    // Prevent double submission
    const currentContent = content.trim();
    if (!currentContent && attachments.length === 0) return;

    // Check if any files are still uploading
    const stillUploading = attachments.some(a => a.uploading);
    
    if (stillUploading) {
      toast({
        title: "Files still uploading",
        description: "Please wait for all files to finish uploading.",
        variant: "destructive",
      });
      return;
    }

    // Get all attachments (uploaded or not)
    const uploadedAttachments = attachments;

    // Clear state immediately to prevent duplicate sends
    setContent('');
    setAttachments([]);

    const payload = {
      conversationId,
      author: 'user' as const,
      content: currentContent,
      writeupType,
      attachments: uploadedAttachments.map(a => ({
        url: a.url,
        mime: a.mime,
        name: a.name,
        size: a.size,
        file_id: a.file_id, // Include backend file ID for processing
      })),
    };

    try {
      await onSend(payload);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Restore content if send failed
      setContent(currentContent);
      setAttachments(attachments);
    } finally {
      textareaRef.current?.focus();
    }
  }, [content, writeupType, attachments, conversationId, onSend, canSend, disabled, toast]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleFiles = useCallback(async (files: FileList) => {
    const newAttachments: FileAttachment[] = Array.from(files).map((file, index) => ({
      id: `${file.name}-${Date.now()}-${Math.random().toString(36)}-${index}`,
      file,
      url: URL.createObjectURL(file),
      name: file.name,
      size: file.size,
      mime: file.type,
      uploading: true,
      uploaded: false,
    }));

    setAttachments(prev => [...prev, ...newAttachments]);

    // Upload files to backend - NO FAKE FALLBACKS
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });

    try {
      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const uploadResult = await uploadResponse.json();
      
      if (!uploadResponse.ok || !uploadResult.success) {
        throw new Error(uploadResult.error || 'Upload failed');
      }

      const fileIds = uploadResult.file_ids || [];
      console.log('Files uploaded successfully:', fileIds);

      // Update attachments with actual backend file IDs
      setAttachments(prev =>
        prev.map((attachment) => {
          const newAttachmentIndex = newAttachments.findIndex(na => na.id === attachment.id);
          if (newAttachmentIndex >= 0 && fileIds[newAttachmentIndex]) {
            return {
              ...attachment,
              uploading: false,
              uploaded: true,
              file_id: fileIds[newAttachmentIndex], // Store the actual backend file ID
            };
          }
          return attachment;
        })
      );

      toast({
        title: "Files uploaded successfully",
        description: `${fileIds.length} files ready for processing.`,
      });

    } catch (error) {
      console.error('File upload failed:', error);
      
      // Remove failed uploads - no fake success
      setAttachments(prev =>
        prev.filter(a => !newAttachments.find(na => na.id === a.id))
      );
      
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload files. Please try again.",
        variant: "destructive",
      });
    }
  }, [toast]);

  const handleTranscript = useCallback((transcript: string) => {
    setContent(prev => prev + (prev ? ' ' : '') + transcript);
    textareaRef.current?.focus();
  }, []);

  const removeAttachment = useCallback((id: string) => {
    setAttachments(prev => {
      const attachment = prev.find(a => a.id === id);
      if (attachment?.url.startsWith('blob:')) {
        URL.revokeObjectURL(attachment.url);
      }
      return prev.filter(a => a.id !== id);
    });
  }, []);

  // Drag and drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.currentTarget === e.target) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  // Cleanup blob URLs on unmount
  useEffect(() => {
    return () => {
      attachments.forEach(a => {
        if (a.url.startsWith('blob:')) {
          URL.revokeObjectURL(a.url);
        }
      });
    };
  }, [attachments]);

  return (
    <div className={cn("w-full px-4 py-4", className)}>
      <div
        className={cn(
          "w-full rounded-2xl border bg-background",
          "flex flex-col gap-2 px-4 py-3 transition-all relative",
          isDragging && "border-primary ring-2 ring-primary/20"
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {/* File attachments preview */}
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 pb-2">
            {attachments.map((attachment, index) => (
              <div
                key={`attachment-${attachment.id}-${index}`}
                className="relative group flex items-center gap-2 px-3 py-1.5 bg-muted rounded-lg text-xs"
              >
                {attachment.mime.startsWith('image/') ? (
                  <img
                    src={attachment.url}
                    alt={attachment.name}
                    className="w-8 h-8 object-cover rounded"
                  />
                ) : (
                  <div className="w-8 h-8 bg-muted-foreground/10 rounded flex items-center justify-center">
                    📄
                  </div>
                )}
                <span className="max-w-[120px] truncate">{attachment.name}</span>
                {attachment.uploading && (
                  <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                )}
                <button
                  onClick={() => removeAttachment(attachment.id)}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-destructive text-destructive-foreground rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Textarea */}
        <TextareaAutosize
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message HandyWriterz..."
          className={cn(
            "w-full bg-transparent outline-none resize-none text-sm",
            "leading-6 scrollbar-thin placeholder:text-muted-foreground",
            "max-h-[300px] overflow-y-auto break-words overflow-wrap-anywhere"
          )}
          minRows={1}
          maxRows={10}
          disabled={disabled}
        />

        {/* Action row */}
        <div className="flex items-center justify-between text-muted-foreground">
          <div className="flex items-center gap-2">
            <AttachButton onFiles={handleFiles} disabled={disabled} />
            <WriteupSelect value={writeupType} onValueChange={setWriteupType} disabled={disabled} />
          </div>
          <div className="flex items-center gap-2">
            <MicButton onTranscript={handleTranscript} disabled={disabled} />
            <SendButton onClick={handleSend} disabled={!canSend} />
          </div>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
        />
      </div>
    </div>
  );
}

'use client'

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Plus, ArrowUp, Mic, X, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/components/ui/use-toast';

interface FileAttachment {
  id: string;
  name: string;
  size: number;
  type: string;
  file: File;
}

interface MessageInputBarProps {
  onSubmit: (inputValue: string, writeupType: string, model: string, fileIds: string[]) => void;
  onCancel: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

const writeUpTypes = [
  { value: 'general', label: 'General' },
  { value: 'essay', label: 'Essay' },
  { value: 'report', label: 'Report' },
  { value: 'dissertation', label: 'PhD Dissertation' },
  { value: 'case_study', label: 'Case Study' },
  { value: 'market_research', label: 'Market Research' },
  { value: 'technical_report', label: 'Technical Report' },
  { value: 'presentation', label: 'Presentation' },
  { value: 'coding', label: 'Coding' },
];

interface MessageInputBarWithPromptProps extends MessageInputBarProps {
  prompt?: string;
}

export const MessageInputBar = React.forwardRef<
  { setTextFromExample: (text: string) => void },
  MessageInputBarWithPromptProps
>(function MessageInputBar({
  onSubmit,
  onCancel,
  isLoading,
  disabled = false,
  prompt = "What are you working on?",
}, ref) {
  const [inputValue, setInputValue] = useState('');
  const [writeupType, setWriteupType] = useState('general');
  const [attachedFiles, setAttachedFiles] = useState<FileAttachment[]>([]);
  const [canSend, setCanSend] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const { toast } = useToast();

  const handleWriteupTypeChange = useCallback((value: string) => {
    setWriteupType(value);
  }, []);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Expose method for parent to set text (for example cards)
  const setTextFromExample = useCallback((text: string) => {
    setInputValue(text);
    if (textareaRef.current) {
      textareaRef.current.focus();
      // Auto-resize textarea
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, []);

  // Expose methods via ref
  React.useImperativeHandle(ref, () => ({
    setTextFromExample,
  }), [setTextFromExample]);

  useEffect(() => {
    setCanSend((inputValue.trim().length > 0 || attachedFiles.length > 0) && !isLoading);
  }, [inputValue, attachedFiles.length, isLoading]);

  const handleFileChange = useCallback((files: FileList | null) => {
    if (!files) return;
    const newFiles = Array.from(files);
    const newAttachments: FileAttachment[] = [];

    newFiles.forEach(file => {
      if (file.size > 100 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: `File ${file.name} exceeds the 100MB limit.`,
          variant: "destructive",
        });
        return;
      }

      newAttachments.push({
        id: `${file.name}-${file.lastModified}`,
        name: file.name,
        size: file.size,
        type: file.type,
        file,
      });
    });

    setAttachedFiles(prev => {
      if (prev.length + newAttachments.length > 10) {
        toast({
          title: "File limit reached",
          description: "You can attach a maximum of 10 files.",
          variant: "destructive",
        });
        return prev;
      }
      return [...prev, ...newAttachments];
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [toast]);

  const handleDragEvents = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragEnter = (e: React.DragEvent) => {
    handleDragEvents(e);
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    handleDragEvents(e);
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    handleDragEvents(e);
    setIsDragOver(false);
    handleFileChange(e.dataTransfer.files);
  };

  const handleSubmit = useCallback((e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!canSend || disabled) return;

    // This is a mock upload, replace with actual upload logic
    const fileIds = attachedFiles.map(f => f.id);
    onSubmit(inputValue, writeupType, 'gemini-2.5-pro', fileIds);

    setInputValue('');
    setAttachedFiles([]);
    if (textareaRef.current) {
      textareaRef.current.value = '';
      textareaRef.current.style.height = 'auto';
    }
  }, [inputValue, writeupType, attachedFiles, canSend, disabled, onSubmit]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  const removeFile = useCallback((fileId: string) => {
    setAttachedFiles(prev => prev.filter(file => file.id !== fileId));
  }, []);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur-sm border-t border-border transition-all duration-200 ${
        isDragOver ? 'bg-blue-900/20 border-blue-500/50' : ''
      }`}
      style={{ marginLeft: '240px' }} // Account for sidebar width
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragEvents}
      onDrop={handleDrop}
    >
      <div className="max-w-2xl mx-auto px-4 py-4 flex flex-col items-center">
        {/* Prompt above input bar */}
        {prompt && (
          <div className="mb-2 text-lg md:text-xl font-semibold text-center text-foreground/90 dark:text-white">
            {prompt}
          </div>
        )}
        {/* File Chips - Outside input container */}
        {attachedFiles.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {attachedFiles.map((file) => (
              <div
                key={file.id}
                className="inline-flex items-center gap-2 px-3 py-1 bg-gray-800/80 border border-gray-700 rounded-full text-sm group hover:bg-gray-750 transition-colors"
              >
                <span className="text-gray-300 font-medium truncate max-w-[150px]">
                  {file.name}
                </span>
                <span className="text-gray-500 text-xs">
                  {formatFileSize(file.size)}
                </span>
                <button
                  onClick={() => removeFile(file.id)}
                  className="text-gray-500 hover:text-red-400 transition-colors ml-1 p-0.5 rounded-full hover:bg-gray-700"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.mp3,.wav,.mp4"
          onChange={(e) => handleFileChange(e.target.files)}
          className="hidden"
        />

        {/* Unified Input Bar - Matching design from images */}
        <div className="flex items-center bg-background border border-border rounded-2xl px-3 py-2 gap-2 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary/30 transition-all shadow-lg w-full">
          {/* + Files Button - Direct file picker */}
          <Button
            disabled={disabled || attachedFiles.length >= 10}
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            className="h-10 w-10 text-muted-foreground hover:text-primary hover:bg-accent rounded-xl transition-all flex-shrink-0"
            title="Add files"
          >
            <Plus className="h-5 w-5" />
          </Button>

          {/* Write-up Type Dropdown - Prominent */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="secondary"
                disabled={disabled}
                className="h-10 px-4 text-base font-semibold rounded-xl flex-shrink-0 transition-all"
              >
                <span>
                  {writeUpTypes.find(t => t.value === writeupType)?.label}
                </span>
                <ChevronDown className="h-4 w-4 ml-1" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 bg-background border-border" side="top" align="start">
              {writeUpTypes.map((type) => (
                <DropdownMenuItem
                  key={type.value}
                  onClick={() => handleWriteupTypeChange(type.value)}
                  className={`text-foreground hover:bg-accent focus:bg-accent cursor-pointer ${
                    writeupType === type.value ? 'bg-accent/50' : ''
                  }`}
                >
                  {type.label}
                  {writeupType === type.value && (
                    <span className="ml-auto text-primary">✓</span>
                  )}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Textarea - Takes remaining space */}
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="w-full min-h-[40px] max-h-32 resize-none bg-transparent border-none px-3 py-2 pr-10 text-foreground placeholder-muted-foreground focus:outline-none focus:ring-0 text-base"
              disabled={disabled || isLoading}
              rows={1}
            />
            {/* Mic Button inside textarea */}
            <Button
              disabled={disabled}
              variant="ghost"
              size="icon"
              className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 text-muted-foreground hover:text-primary hover:bg-accent/50 rounded-lg transition-all"
              title="Voice input"
            >
              <Mic className="h-4 w-4" />
            </Button>
          </div>

          {/* Send/Cancel Button */}
          {isLoading ? (
            <Button
              onClick={onCancel}
              size="icon"
              className="h-10 w-10 bg-destructive hover:bg-destructive/80 text-white rounded-xl transition-all flex-shrink-0"
              title="Cancel"
            >
              <X className="h-5 w-5" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={!canSend || disabled}
              size="icon"
              className={`h-10 w-10 rounded-xl transition-all duration-200 flex-shrink-0 ${
                canSend && !disabled
                  ? 'bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:scale-105'
                  : 'bg-muted text-muted-foreground cursor-not-allowed opacity-60'
              }`}
              title="Send message"
            >
              <ArrowUp className={`h-5 w-5 transition-transform ${canSend && !disabled ? 'rotate-0' : 'rotate-12'}`} />
            </Button>
          )}
        </div>
      </div>

      {/* Drag Overlay */}
      {isDragOver && (
        <div className="absolute inset-0 bg-blue-500/10 flex items-center justify-center pointer-events-none z-50">
          <div className="text-center p-6 border-2 border-dashed border-blue-400 rounded-xl bg-blue-900/20">
            <Plus className="h-8 w-8 text-blue-400 mx-auto mb-2" />
            <p className="text-lg font-medium text-blue-300">Drop files to attach</p>
            <p className="text-sm text-blue-400">Up to 10 files, 100MB each</p>
          </div>
        </div>
      )}
    </div>
  );
});

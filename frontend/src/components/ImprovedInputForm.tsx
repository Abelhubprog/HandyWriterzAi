'use client'

import React, { useState, useRef, useCallback } from 'react';
import { Plus, Send, Paperclip, X, ChevronDown, Mic, CornerDownLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface FileAttachment {
  id: string;
  name: string;
  size: number;
  type: string;
}

interface ImprovedInputFormProps {
  onSubmit: (inputValue: string, writeupType: string, model: string, fileIds: string[]) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

const writeUpTypes = [
  { value: 'general', label: '📄 General Writing', description: 'Standard academic content' },
  { value: 'essay', label: '📝 Essay', description: 'Structured argumentative essays' },
  { value: 'report', label: '📊 Report', description: 'Professional reports and analysis' },
  { value: 'dissertation', label: '🎓 Dissertation', description: 'PhD-level research papers' },
  { value: 'case_study', label: '🔍 Case Study', description: 'Detailed case analysis' },
  { value: 'case_scenario', label: '🎯 Case Scenario', description: 'Scenario-based analysis' },
  { value: 'reflection', label: '💭 Reflection', description: 'Reflective writing pieces' },
  { value: 'presentation', label: '📱 Presentation', description: 'Slide presentations' },
  { value: 'coding', label: '💻 Coding Help', description: 'Programming assistance' },
];

export function ImprovedInputForm({
  onSubmit,
  onCancel,
  isLoading,
  hasHistory,
}: ImprovedInputFormProps) {
  const [inputValue, setInputValue] = useState('');
  const [writeupType, setWriteupType] = useState('general');
  const [attachedFiles, setAttachedFiles] = useState<FileAttachment[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback((e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if ((!inputValue.trim() && attachedFiles.length === 0) || isLoading) return;
    
    const fileIds = attachedFiles.map(file => file.id);
    onSubmit(inputValue, writeupType, 'gemini-2.5-pro', fileIds);
    setInputValue('');
    setAttachedFiles([]);
  }, [inputValue, writeupType, attachedFiles, isLoading, onSubmit]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const newAttachments: FileAttachment[] = [];

    files.forEach(file => {
      // Validate file size (100MB limit)
      if (file.size > 100 * 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 100MB.`);
        return;
      }

      // Check if we already have 10 files
      if (attachedFiles.length + newAttachments.length >= 10) {
        alert('Maximum 10 files allowed.');
        return;
      }

      newAttachments.push({
        id: Date.now().toString() + Math.random(),
        name: file.name,
        size: file.size,
        type: file.type,
      });
    });

    setAttachedFiles(prev => [...prev, ...newAttachments]);
    
    // Clear the input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [attachedFiles.length]);

  const removeFile = useCallback((fileId: string) => {
    setAttachedFiles(prev => prev.filter(file => file.id !== fileId));
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const newAttachments: FileAttachment[] = [];

    files.forEach(file => {
      if (file.size > 100 * 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 100MB.`);
        return;
      }

      if (attachedFiles.length + newAttachments.length >= 10) {
        alert('Maximum 10 files allowed.');
        return;
      }

      newAttachments.push({
        id: Date.now().toString() + Math.random(),
        name: file.name,
        size: file.size,
        type: file.type,
      });
    });

    setAttachedFiles(prev => [...prev, ...newAttachments]);
  }, [attachedFiles.length]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const selectedWriteUpType = writeUpTypes.find(type => type.value === writeupType);
  const isSubmitDisabled = (!inputValue.trim() && attachedFiles.length === 0) || isLoading;

  return (
    <div className="border-t border-gray-700 bg-gray-900">
      {/* File Attachments */}
      {attachedFiles.length > 0 && (
        <div className="px-4 py-3 border-b border-gray-700">
          <div className="flex flex-wrap gap-2">
            {attachedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center gap-2 px-3 py-1 bg-gray-800 border border-gray-600 rounded-full text-sm"
              >
                <Paperclip className="h-3 w-3 text-gray-400" />
                <span className="text-gray-300 truncate max-w-32">
                  {file.name}
                </span>
                <span className="text-gray-500 text-xs">
                  {formatFileSize(file.size)}
                </span>
                <button
                  onClick={() => removeFile(file.id)}
                  className="text-gray-400 hover:text-red-400 transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div 
        className={`p-4 transition-colors ${
          isDragging ? 'bg-blue-900/20 border-blue-500' : ''
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex items-end gap-3">
          {/* Tools Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700 shrink-0"
              >
                <span className="text-sm">{selectedWriteUpType?.label.split(' ')[0]} Tools</span>
                <ChevronDown className="h-4 w-4 ml-1" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="bg-gray-800 border-gray-600 w-64">
              {writeUpTypes.map((type) => (
                <DropdownMenuItem
                  key={type.value}
                  onClick={() => setWriteupType(type.value)}
                  className={`text-gray-300 hover:bg-gray-700 ${
                    writeupType === type.value ? 'bg-gray-700' : ''
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{type.label}</span>
                    <span className="text-xs text-gray-400">{type.description}</span>
                  </div>
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator className="bg-gray-600" />
              <DropdownMenuItem className="text-gray-300 hover:bg-gray-700">
                <span className="text-sm">🎨 Custom Templates</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Attach Files Button */}
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            size="sm"
            className="bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700 shrink-0"
            disabled={attachedFiles.length >= 10}
          >
            <Paperclip className="h-4 w-4" />
          </Button>

          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.txt,.md,.png,.jpg,.jpeg,.gif,.mp3,.wav,.mp4"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Text Input */}
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isDragging ? "Drop files here or type your message..." : "Message HandyWriterz..."}
              className="min-h-[52px] max-h-32 resize-none bg-gray-800 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 pr-12"
              disabled={isLoading}
            />
            
            {/* Send Button - Positioned inside textarea */}
            <div className="absolute bottom-2 right-2">
              {isLoading ? (
                <Button
                  onClick={onCancel}
                  size="sm"
                  variant="outline"
                  className="h-8 w-8 p-0 bg-gray-700 border-gray-600 hover:bg-gray-600"
                >
                  <X className="h-4 w-4" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={isSubmitDisabled}
                  size="sm"
                  className={`h-8 w-8 p-0 transition-all ${
                    isSubmitDisabled
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {inputValue.trim() || attachedFiles.length > 0 ? (
                    <Send className="h-4 w-4" />
                  ) : (
                    <Mic className="h-4 w-4" />
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Hint Text */}
        <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
          <span>
            {attachedFiles.length > 0 && (
              `${attachedFiles.length}/10 files • `
            )}
            Supports files up to 100MB each
          </span>
          <span className="flex items-center gap-1">
            <CornerDownLeft className="h-3 w-3" />
            to send, Shift + 
            <CornerDownLeft className="h-3 w-3" />
            for new line
          </span>
        </div>
      </div>
    </div>
  );
}
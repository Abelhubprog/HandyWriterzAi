'use client'

import React, { useState, useEffect, useRef } from 'react';
import { 
  FileText, 
  Download, 
  Eye, 
  Trash2, 
  MessageSquare, 
  ArrowLeft, 
  Upload, 
  FolderPlus,
  Folder,
  FolderOpen,
  Plus,
  Search
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { useRouter } from 'next/navigation';
import { StoredConversation } from '@/lib/conversationStore';
import { agenticDocClient } from '@/lib/agentic-doc-client';

interface LibraryFolder {
  id: string;
  name: string;
  created_at: string;
  parent_id?: string;
}

interface LibraryFile {
  id: string;
  name: string;
  type: 'conversation' | 'document';
  size: number;
  created_at: string;
  folder_id?: string;
  content?: StoredConversation;
}

export default function LibraryPage() {
  const [libraryItems, setLibraryItems] = useState<StoredConversation[]>([]);
  const [folders, setFolders] = useState<LibraryFolder[]>([
    { id: 'conversations', name: 'Conversations', created_at: new Date().toISOString() },
    { id: 'documents', name: 'Documents', created_at: new Date().toISOString() },
  ]);
  const [files, setFiles] = useState<LibraryFile[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string>('conversations');
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    const loadLibraryData = async () => {
      try {
        const { ConversationStore } = await import('@/lib/conversationStore');
        const conversations = ConversationStore.getAllConversations();
        // Only show conversations with AI responses (completed conversations)
        const completedConversations = conversations.filter(
          conv => conv.message_count > 1 && conv.messages.some(m => m.type === 'ai')
        );
        setLibraryItems(completedConversations);

        // Convert conversations to library files format
        const conversationFiles: LibraryFile[] = completedConversations.map(conv => ({
          id: conv.id,
          name: conv.title,
          type: 'conversation' as const,
          size: conv.messages.reduce((acc, msg) => acc + (msg.content?.length || 0), 0) * 2,
          created_at: conv.created_at,
          folder_id: 'conversations',
          content: conv
        }));

        setFiles(conversationFiles);
      } catch (error) {
        console.error('Error loading library data:', error);
        toast({
          title: "Failed to load library",
          description: "Could not load your saved conversations.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadLibraryData();
  }, [toast]);

  const handlePreview = (file: LibraryFile) => {
    if (file.type === 'conversation' && file.content) {
      router.push(`/chat?conversation=${file.id}`);
    }
  };

  const handleDownload = async (file: LibraryFile, format: 'pdf' | 'docx' | 'md' = 'pdf') => {
    try {
      if (file.type === 'conversation' && file.content) {
        // Create a simple text export of the conversation
        const content = file.content.messages
          .map(msg => `**${msg.type === 'human' ? 'You' : 'HandyWriterz'}:**\n${msg.content}\n\n`)
          .join('');
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${file.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${format === 'md' ? 'md' : 'txt'}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }

      toast({
        title: "Download started",
        description: `Downloading "${file.name}"...`,
      });
    } catch (error) {
      toast({
        title: "Download failed",
        description: "Could not download the file.",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (file: LibraryFile) => {
    if (!confirm(`Are you sure you want to delete "${file.name}"?`)) return;

    try {
      if (file.type === 'conversation') {
        const { ConversationStore } = await import('@/lib/conversationStore');
        ConversationStore.deleteConversation(file.id);
        setLibraryItems(prev => prev.filter(item => item.id !== file.id));
      }
      
      setFiles(prev => prev.filter(f => f.id !== file.id));
      
      toast({
        title: "File deleted",
        description: `"${file.name}" has been removed from your library.`,
      });
    } catch (error) {
      toast({
        title: "Failed to delete",
        description: "Could not delete the file.",
        variant: "destructive",
      });
    }
  };

  const handleUpload = async (uploadFiles: FileList) => {
    if (!uploadFiles.length) return;

    setIsUploading(true);
    
    try {
      // Process each file
      for (const file of Array.from(uploadFiles)) {
        // For now, we'll just add them to the documents folder
        // In a real implementation, you'd upload to the backend
        const newFile: LibraryFile = {
          id: `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          name: file.name,
          type: 'document',
          size: file.size,
          created_at: new Date().toISOString(),
          folder_id: 'documents'
        };
        
        setFiles(prev => [...prev, newFile]);
      }

      toast({
        title: "Upload successful",
        description: `${uploadFiles.length} file(s) uploaded to library.`,
      });
    } catch (error) {
      toast({
        title: "Upload failed",
        description: "Could not upload files.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleCreateFolder = () => {
    const folderName = prompt('Enter folder name:');
    if (!folderName || !folderName.trim()) return;

    const newFolder: LibraryFolder = {
      id: `folder_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: folderName.trim(),
      created_at: new Date().toISOString()
    };

    setFolders(prev => [...prev, newFolder]);
    toast({
      title: "Folder created",
      description: `"${folderName}" folder has been created.`,
    });
  };

  const getFileIcon = (file: LibraryFile) => {
    if (file.type === 'conversation') {
      return <MessageSquare className="h-5 w-5 text-blue-500" />;
    }
    return <FileText className="h-5 w-5 text-green-500" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Filter files based on selected folder and search query
  const filteredFiles = files.filter(file => {
    const matchesFolder = file.folder_id === selectedFolder;
    const matchesSearch = searchQuery === '' || 
      file.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFolder && matchesSearch;
  });

  if (isLoading) {
    return (
      <div className="h-full bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading your library...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.push('/chat')}
            className="text-gray-400 hover:text-white hover:bg-gray-700/50"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Chat
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">My Library</h1>
            <p className="text-gray-400 text-sm">
              All your documents and conversations in one place
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={(e) => e.target.files && handleUpload(e.target.files)}
            className="hidden"
          />
          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"
          >
            <Upload className="h-4 w-4 mr-2" />
            {isUploading ? 'Uploading...' : 'Upload'}
          </Button>
        </div>
      </header>

      {/* Two-column layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Folders */}
        <div className="w-64 border-r border-gray-800 flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold">Folders</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleCreateFolder}
                className="h-8 w-8 text-gray-400 hover:text-white hover:bg-gray-700"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2">
            {folders.map((folder) => (
              <button
                key={folder.id}
                onClick={() => setSelectedFolder(folder.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-left transition-colors ${
                  selectedFolder === folder.id
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-600/30'
                    : 'text-gray-300 hover:bg-gray-800'
                }`}
              >
                {selectedFolder === folder.id ? (
                  <FolderOpen className="h-4 w-4 flex-shrink-0" />
                ) : (
                  <Folder className="h-4 w-4 flex-shrink-0" />
                )}
                <span className="truncate">{folder.name}</span>
                <span className="text-xs text-gray-500 ml-auto">
                  {files.filter(f => f.folder_id === folder.id).length}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Right Content - Files */}
        <div className="flex-1 flex flex-col">
          {/* Search and controls */}
          <div className="p-4 border-b border-gray-800">
            <div className="flex items-center gap-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-gray-800 border-gray-600 text-white"
                />
              </div>
              <div className="text-sm text-gray-400">
                {filteredFiles.length} items
              </div>
            </div>
          </div>

          {/* Files table */}
          <div className="flex-1 overflow-auto">
            {filteredFiles.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-gray-600 mb-4">
                  {selectedFolder === 'conversations' ? (
                    <MessageSquare className="h-16 w-16 mx-auto" />
                  ) : (
                    <FileText className="h-16 w-16 mx-auto" />
                  )}
                </div>
                <h3 className="text-xl font-semibold text-gray-300 mb-2">
                  {searchQuery ? 'No files found' : 'No files in this folder'}
                </h3>
                <p className="text-gray-500 mb-6">
                  {selectedFolder === 'conversations' 
                    ? 'Start a conversation to see it saved here.'
                    : 'Upload documents to organize them here.'
                  }
                </p>
                {selectedFolder === 'conversations' ? (
                  <Button onClick={() => router.push('/chat')} className="bg-blue-600 hover:bg-blue-700">
                    Start New Conversation
                  </Button>
                ) : (
                  <Button onClick={() => fileInputRef.current?.click()} className="bg-blue-600 hover:bg-blue-700">
                    Upload Files
                  </Button>
                )}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="border-b-gray-700">
                    <TableHead className="w-[50px]"></TableHead>
                    <TableHead className="text-white font-semibold">Name</TableHead>
                    <TableHead className="text-white font-semibold">Created</TableHead>
                    <TableHead className="text-white font-semibold">Type</TableHead>
                    <TableHead className="text-white font-semibold">Size</TableHead>
                    <TableHead className="text-right text-white font-semibold">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredFiles.map((file) => (
                    <TableRow key={file.id} className="border-b-gray-700/50 hover:bg-gray-800/70">
                      <TableCell>{getFileIcon(file)}</TableCell>
                      <TableCell className="font-medium text-gray-200">
                        <div className="max-w-md">
                          <div className="truncate">{file.name}</div>
                          {file.type === 'conversation' && file.content?.last_message_preview && (
                            <div className="text-sm text-gray-500 truncate mt-1">
                              {file.content.last_message_preview}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-400">
                        {new Date(file.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="border-gray-600 text-gray-300">
                          {file.type === 'conversation' ? 'Conversation' : 'Document'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-gray-400">{formatFileSize(file.size)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => handlePreview(file)}
                            className="text-gray-400 hover:text-white hover:bg-gray-700/50"
                            title="Open file"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => handleDownload(file)}
                            className="text-gray-400 hover:text-white hover:bg-gray-700/50"
                            title="Download file"
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => handleDelete(file)}
                            className="text-red-500 hover:text-red-400 hover:bg-red-500/10"
                            title="Delete file"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
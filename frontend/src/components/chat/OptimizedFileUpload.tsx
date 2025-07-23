/**
 * Optimized File Upload Component for Railway Deployment
 * Handles chat context files with improved UX and performance
 */

'use client';

import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  X, 
  File, 
  Image, 
  FileText, 
  Video, 
  Music,
  Archive,
  AlertCircle,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import * as tus from 'tus-js-client';

// Configuration for Railway deployment
const MAX_FILES = 10; // Reduced for better performance
const MAX_SIZE = 25 * 1024 * 1024; // 25MB per file (Railway friendly)
const TOTAL_MAX_SIZE = 100 * 1024 * 1024; // 100MB total
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error' | 'processing';
  file_id?: string;
  error?: string;
  preview?: string;
  chunks?: number;
}

interface OptimizedFileUploadProps {
  onFilesReady: (fileIds: string[]) => void;
  disabled?: boolean;
  className?: string;
}

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) return <Image className="h-4 w-4" />;
  if (type.startsWith('video/')) return <Video className="h-4 w-4" />;
  if (type.startsWith('audio/')) return <Music className="h-4 w-4" />;
  if (type.includes('pdf') || type.includes('document')) return <FileText className="h-4 w-4" />;
  if (type.includes('zip') || type.includes('archive')) return <Archive className="h-4 w-4" />;
  return <File className="h-4 w-4" />;
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const OptimizedFileUpload: React.FC<OptimizedFileUploadProps> = ({
  onFilesReady,
  disabled = false,
  className = ''
}) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [totalProgress, setTotalProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // File validation
  const validateFiles = (newFiles: File[]): { valid: File[], errors: string[] } => {
    const errors: string[] = [];
    const valid: File[] = [];

    // Check total file count
    if (files.length + newFiles.length > MAX_FILES) {
      errors.push(`Maximum ${MAX_FILES} files allowed`);
      return { valid: [], errors };
    }

    // Check individual files
    for (const file of newFiles) {
      if (file.size > MAX_SIZE) {
        errors.push(`${file.name} exceeds ${formatFileSize(MAX_SIZE)} limit`);
        continue;
      }

      // Check if file already exists
      if (files.some(f => f.name === file.name && f.size === file.size)) {
        errors.push(`${file.name} already uploaded`);
        continue;
      }

      valid.push(file);
    }

    // Check total size
    const currentSize = files.reduce((sum, f) => sum + f.size, 0);
    const newSize = valid.reduce((sum, f) => sum + f.size, 0);
    if (currentSize + newSize > TOTAL_MAX_SIZE) {
      errors.push(`Total size would exceed ${formatFileSize(TOTAL_MAX_SIZE)} limit`);
      return { valid: [], errors };
    }

    return { valid, errors };
  };

  // Upload single file with tus resumable upload
  const uploadFile = useCallback(async (file: File): Promise<string> => {
    const fileId = crypto.randomUUID();
    
    // Add file to state immediately
    const uploadFile: UploadedFile = {
      id: fileId,
      name: file.name,
      size: file.size,
      type: file.type,
      progress: 0,
      status: 'uploading'
    };

    // Generate preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setFiles(prev => prev.map(f => 
          f.id === fileId ? { ...f, preview: e.target?.result as string } : f
        ));
      };
      reader.readAsDataURL(file);
    }

    setFiles(prev => [...prev, uploadFile]);

    return new Promise((resolve, reject) => {
      const upload = new tus.Upload(file, {
        endpoint: `${BACKEND_URL}/api/files/upload`,
        retryDelays: [0, 1000, 3000, 5000],
        chunkSize: 5 * 1024 * 1024, // 5MB chunks for Railway
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        metadata: {
          filename: file.name,
          filetype: file.type,
          filesize: file.size.toString(),
          context: 'chat'
        },
        
        onError: (error) => {
          console.error('Upload failed:', error);
          setFiles(prev => prev.map(f => 
            f.id === fileId 
              ? { ...f, status: 'error', error: error.message }
              : f
          ));
          reject(error);
        },

        onProgress: (bytesUploaded, bytesTotal) => {
          const progress = Math.round((bytesUploaded / bytesTotal) * 100);
          setFiles(prev => prev.map(f => 
            f.id === fileId 
              ? { ...f, progress }
              : f
          ));
          
          // Update total progress
          updateTotalProgress();
        },

        onSuccess: () => {
          const uploadedFileId = upload.url?.split('/').pop() || fileId;
          
          setFiles(prev => prev.map(f => 
            f.id === fileId 
              ? { 
                  ...f, 
                  status: 'processing', 
                  file_id: uploadedFileId, 
                  progress: 100 
                }
              : f
          ));

          // Start background processing
          processFile(uploadedFileId, fileId);
          resolve(uploadedFileId);
        }
      });

      upload.start();
    });
  }, [files]);

  // Process file after upload (chunking, embedding)
  const processFile = async (fileId: string, localId: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/files/${fileId}/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ context: 'chat' })
      });

      if (response.ok) {
        const result = await response.json();
        setFiles(prev => prev.map(f => 
          f.id === localId 
            ? { 
                ...f, 
                status: 'completed',
                chunks: result.chunks || 0
              }
            : f
        ));
      } else {
        throw new Error('Processing failed');
      }
    } catch (error) {
      console.error('File processing failed:', error);
      setFiles(prev => prev.map(f => 
        f.id === localId 
          ? { ...f, status: 'error', error: 'Processing failed' }
          : f
      ));
    }
  };

  // Update total progress
  const updateTotalProgress = () => {
    setFiles(current => {
      if (current.length === 0) {
        setTotalProgress(0);
        return current;
      }
      
      const totalProgress = current.reduce((sum, f) => sum + f.progress, 0);
      setTotalProgress(totalProgress / current.length);
      return current;
    });
  };

  // Handle file drop/selection
  const handleFiles = useCallback(async (newFiles: File[]) => {
    if (disabled) return;

    const { valid, errors } = validateFiles(newFiles);
    
    // Show errors
    if (errors.length > 0) {
      // You can replace this with a proper toast notification
      alert(errors.join('\n'));
      return;
    }

    // Upload valid files
    try {
      const uploadPromises = valid.map(file => uploadFile(file));
      await Promise.all(uploadPromises);
      
      // Notify parent when all files are ready
      const completedFileIds = files
        .filter(f => f.status === 'completed' && f.file_id)
        .map(f => f.file_id!);
      
      if (completedFileIds.length > 0) {
        onFilesReady(completedFileIds);
      }
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }, [files, disabled, uploadFile, onFilesReady]);

  // Dropzone configuration
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleFiles,
    disabled,
    maxFiles: MAX_FILES,
    maxSize: MAX_SIZE,
    multiple: true,
    noClick: files.length >= MAX_FILES
  });

  // Remove file
  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
    updateTotalProgress();
  };

  // Get completed file IDs
  const getCompletedFileIds = () => {
    return files
      .filter(f => f.status === 'completed' && f.file_id)
      .map(f => f.file_id!);
  };

  // Clear all files
  const clearAll = () => {
    setFiles([]);
    setTotalProgress(0);
  };

  const isUploading = files.some(f => f.status === 'uploading');
  const hasErrors = files.some(f => f.status === 'error');
  const completedCount = files.filter(f => f.status === 'completed').length;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Zone */}
      <Card className={`border-2 border-dashed transition-colors ${
        isDragActive 
          ? 'border-blue-500 bg-blue-50' 
          : disabled 
            ? 'border-gray-200 bg-gray-50'
            : 'border-gray-300 hover:border-gray-400'
      }`}>
        <CardContent className="p-6">
          <div 
            {...getRootProps()} 
            className={`text-center ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <input {...getInputProps()} ref={fileInputRef} />
            
            <Upload className={`mx-auto h-12 w-12 mb-4 ${
              disabled ? 'text-gray-300' : 'text-gray-400'
            }`} />
            
            <h3 className="text-lg font-medium mb-2">
              {isDragActive 
                ? 'Drop files here...' 
                : 'Upload context files'
              }
            </h3>
            
            <p className="text-sm text-gray-500 mb-4">
              Drag & drop files or click to browse
            </p>
            
            <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-400">
              <Badge variant="outline">Max {MAX_FILES} files</Badge>
              <Badge variant="outline">Up to {formatFileSize(MAX_SIZE)} each</Badge>
              <Badge variant="outline">Total: {formatFileSize(TOTAL_MAX_SIZE)}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Progress Bar */}
      {(isUploading || files.length > 0) && (
        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">
              {completedCount}/{files.length} files processed
            </span>
            <span className="text-gray-500">
              {Math.round(totalProgress)}%
            </span>
          </div>
          <Progress value={totalProgress} className="h-2" />
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-medium">Uploaded Files</h4>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={clearAll}
                disabled={isUploading}
              >
                Clear All
              </Button>
            </div>
            
            <div className="space-y-2">
              {files.map((file) => (
                <div 
                  key={file.id} 
                  className="flex items-center gap-3 p-3 border rounded-lg"
                >
                  {/* File Preview/Icon */}
                  <div className="flex-shrink-0">
                    {file.preview ? (
                      <img 
                        src={file.preview} 
                        alt={file.name}
                        className="w-10 h-10 object-cover rounded"
                      />
                    ) : (
                      <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center">
                        {getFileIcon(file.type)}
                      </div>
                    )}
                  </div>

                  {/* File Info */}
                  <div className="flex-grow min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium truncate">
                        {file.name}
                      </p>
                      
                      {/* Status Badge */}
                      {file.status === 'uploading' && (
                        <Badge variant="secondary">
                          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                          Uploading
                        </Badge>
                      )}
                      {file.status === 'processing' && (
                        <Badge variant="secondary">
                          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                          Processing
                        </Badge>
                      )}
                      {file.status === 'completed' && (
                        <Badge variant="default">
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                          Ready
                        </Badge>
                      )}
                      {file.status === 'error' && (
                        <Badge variant="destructive">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          Error
                        </Badge>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 text-xs text-gray-500 mt-1">
                      <span>{formatFileSize(file.size)}</span>
                      {file.chunks && (
                        <span>{file.chunks} chunks</span>
                      )}
                      {file.error && (
                        <span className="text-red-500">{file.error}</span>
                      )}
                    </div>

                    {/* Progress Bar for individual file */}
                    {file.status === 'uploading' && (
                      <Progress value={file.progress} className="h-1 mt-2" />
                    )}
                  </div>

                  {/* Remove Button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(file.id)}
                    disabled={file.status === 'uploading'}
                    className="flex-shrink-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
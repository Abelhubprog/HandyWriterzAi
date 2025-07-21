import React, { useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileTile } from '@/components/ui/FileTile';
import { UploadCloud, AlertCircle } from 'lucide-react';
import { useFileUpload } from '@/hooks/useFileUpload';

interface ContextUploaderProps {
  onFileIdsChange: (fileIds: string[]) => void;
  maxFiles?: number;
  maxFileSize?: number;
}

export const ContextUploader: React.FC<ContextUploaderProps> = ({ 
  onFileIdsChange, 
  maxFiles = 50, 
  maxFileSize = 100 * 1024 * 1024 // 100MB
}) => {
  const { 
    files, 
    totalProgress, 
    uploadFiles, 
    removeFile, 
    clearFiles, 
    getFileIds, 
    isUploading 
  } = useFileUpload();

  // Notify parent when file IDs change
  useEffect(() => {
    onFileIdsChange(getFileIds());
  }, [files, getFileIds, onFileIdsChange]);

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      console.warn('Some files were rejected:', rejectedFiles);
    }

    // Check total file count
    if (files.length + acceptedFiles.length > maxFiles) {
      alert(`Maximum ${maxFiles} files allowed`);
      return;
    }

    try {
      await uploadFiles(acceptedFiles);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }, [uploadFiles, files.length, maxFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    maxFiles,
    maxSize: maxFileSize,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'audio/*': ['.mp3', '.wav', '.m4a', '.flac'],
      'video/*': ['.mp4', '.avi', '.mov', '.wmv']
    }
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return '🖼️';
    if (type.startsWith('audio/')) return '🎵';
    if (type.startsWith('video/')) return '🎬';
    if (type.includes('pdf')) return '📄';
    if (type.includes('word')) return '📝';
    if (type.includes('excel') || type.includes('csv')) return '📊';
    return '📄';
  };

  return (
    <div className="flex flex-col gap-4 p-4 border rounded-lg bg-gray-800 border-gray-700">
      <div
        {...getRootProps()}
        className={`flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-gray-700' : 'border-gray-600 hover:bg-gray-700'}`}
      >
        <input {...getInputProps()} />
        <UploadCloud className="w-10 h-10 mb-2 text-gray-400" />
        <p className="text-sm text-gray-400 text-center">
          {isDragActive ? 'Drop the files here ...' : `Drag 'n' drop up to ${maxFiles} files here, or click to select`}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Max {formatFileSize(maxFileSize)} per file • PDF, DOCX, Images, Audio, Video supported
        </p>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="flex items-center gap-2 p-2 bg-gray-700 rounded">
          <div className="w-full bg-gray-600 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${totalProgress}%` }}
            />
          </div>
          <span className="text-xs text-gray-300">{Math.round(totalProgress)}%</span>
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="flex flex-col gap-2 max-h-64 overflow-y-auto">
          {files.map(file => (
            <div key={file.id} className="flex items-center gap-3 p-3 bg-gray-700 rounded-lg">
              <div className="flex-shrink-0">
                {file.thumbnail ? (
                  <img src={file.thumbnail} alt="" className="w-8 h-8 object-cover rounded" />
                ) : (
                  <span className="text-lg">{getFileIcon(file.type)}</span>
                )}
              </div>
              
              <div className="flex-grow min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white truncate">{file.name}</span>
                  <span className="text-xs text-gray-400">{formatFileSize(file.size)}</span>
                </div>
                
                {file.status === 'uploading' && (
                  <div className="w-full bg-gray-600 rounded-full h-1 mt-1">
                    <div 
                      className="bg-blue-500 h-1 rounded-full transition-all duration-300" 
                      style={{ width: `${file.progress}%` }}
                    />
                  </div>
                )}
                
                {file.status === 'error' && (
                  <div className="flex items-center gap-1 mt-1">
                    <AlertCircle className="w-3 h-3 text-red-400" />
                    <span className="text-xs text-red-400">{file.error}</span>
                  </div>
                )}
              </div>
              
              <div className="flex items-center gap-2">
                {file.status === 'completed' && (
                  <span className="text-xs text-green-400">✓</span>
                )}
                <button
                  onClick={() => removeFile(file.id)}
                  className="text-gray-400 hover:text-red-400 text-sm"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

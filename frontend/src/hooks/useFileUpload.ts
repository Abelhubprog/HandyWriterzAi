import { useState, useCallback } from 'react';
import * as tus from 'tus-js-client';

export interface UploadFile {
  id: string;
  name: string;
  size: number;
  type: string;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  file_id?: string;
  error?: string;
  thumbnail?: string;
}

export const useFileUpload = () => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [totalProgress, setTotalProgress] = useState(0);

  const uploadFile = useCallback(async (file: File): Promise<string> => {
    const uploadId = crypto.randomUUID();
    
    // Add file to state
    const uploadFile: UploadFile = {
      id: uploadId,
      name: file.name,
      size: file.size,
      type: file.type,
      progress: 0,
      status: 'pending'
    };
    
    setFiles(prev => [...prev, uploadFile]);

    return new Promise((resolve, reject) => {
      // Create thumbnail for images
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setFiles(prev => prev.map(f => 
            f.id === uploadId 
              ? { ...f, thumbnail: e.target?.result as string }
              : f
          ));
        };
        reader.readAsDataURL(file);
      }

      // Initialize tus upload
      const upload = new tus.Upload(file, {
        endpoint: 'http://localhost:8000/api/files/upload',
        retryDelays: [0, 1000, 3000, 5000],
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        metadata: {
          filename: file.name,
          filetype: file.type,
          filesize: file.size.toString()
        },
        onError: (error) => {
          console.error('Upload failed:', error);
          setFiles(prev => prev.map(f => 
            f.id === uploadId 
              ? { ...f, status: 'error', error: error.message }
              : f
          ));
          reject(error);
        },
        onProgress: (bytesUploaded, bytesTotal) => {
          const progress = Math.round((bytesUploaded / bytesTotal) * 100);
          setFiles(prev => prev.map(f => 
            f.id === uploadId 
              ? { ...f, progress, status: 'uploading' }
              : f
          ));
          
          // Calculate total progress
          setFiles(current => {
            const totalFiles = current.length;
            const totalProgress = current.reduce((sum, f) => sum + f.progress, 0);
            setTotalProgress(totalProgress / totalFiles);
            return current;
          });
        },
        onSuccess: () => {
          // Extract file_id from upload URL
          const fileId = upload.url?.split('/').pop();
          
          setFiles(prev => prev.map(f => 
            f.id === uploadId 
              ? { ...f, status: 'completed', file_id: fileId, progress: 100 }
              : f
          ));
          
          resolve(fileId!);
        }
      });

      // Start upload
      upload.start();
    });
  }, []);

  const uploadFiles = useCallback(async (fileList: FileList | File[]) => {
    const fileArray = Array.from(fileList);
    const uploadPromises = fileArray.map(file => uploadFile(file));
    
    try {
      const fileIds = await Promise.all(uploadPromises);
      return fileIds;
    } catch (error) {
      console.error('Batch upload failed:', error);
      throw error;
    }
  }, [uploadFile]);

  const removeFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
    setTotalProgress(0);
  }, []);

  const getFileIds = useCallback(() => {
    return files
      .filter(f => f.status === 'completed' && f.file_id)
      .map(f => f.file_id!);
  }, [files]);

  return {
    files,
    totalProgress,
    uploadFile,
    uploadFiles,
    removeFile,
    clearFiles,
    getFileIds,
    isUploading: files.some(f => f.status === 'uploading'),
    hasFiles: files.length > 0,
    completedFiles: files.filter(f => f.status === 'completed')
  };
};
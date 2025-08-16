import { useState, useCallback } from 'react';

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

      (async () => {
        try {
          // Mark uploading (no granular progress with fetch)
          setFiles(prev => prev.map(f => f.id === uploadId ? { ...f, status: 'uploading', progress: 10 } : f));

          // Try direct-to-R2 presigned PUT first
          let firstId: string | null = null;
          try {
            const presignForm = new FormData();
            presignForm.append('filename', file.name);
            presignForm.append('filesize', String(file.size));
            presignForm.append('mime_type', file.type || 'application/octet-stream');
            const presignRes = await fetch('/api/files/presign', {
              method: 'POST',
              body: presignForm,
              headers: {
                ...(typeof window !== 'undefined' && localStorage.getItem('access_token')
                  ? { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
                  : {})
              }
            })
            if (presignRes.ok) {
              const presign = await presignRes.json()
              const uploadUrl: string = presign.upload_url
              const headers: Record<string,string> = presign.headers || {}
              const putRes = await fetch(uploadUrl, {
                method: 'PUT',
                body: file,
                headers
              })
              if (!putRes.ok) throw new Error(`PUT failed: ${putRes.status}`)
              firstId = String(presign.file_id)
            }
          } catch (e) {
            // Fallback to backend multipart upload
            const form = new FormData();
            form.append('files', file);
            const res = await fetch('/api/upload', {
              method: 'POST',
              body: form,
              headers: {
                ...(typeof window !== 'undefined' && localStorage.getItem('access_token')
                  ? { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
                  : {})
              }
            });
            if (!res.ok) {
              const text = await res.text();
              throw new Error(text || `Upload failed: ${res.status}`);
            }
            const data = await res.json();
            const fileIds: string[] = data.file_ids || [];
            firstId = fileIds[0] || null;
          }
          if (!firstId) throw new Error('No file_id returned');

          setFiles(prev => prev.map(f =>
            f.id === uploadId
              ? { ...f, status: 'completed', file_id: firstId, progress: 100 }
              : f
          ));

          // Update total progress
          setFiles(current => {
            const totalFiles = current.length;
            const totalProgress = current.reduce((sum, f) => sum + f.progress, 0);
            setTotalProgress(totalProgress / Math.max(totalFiles, 1));
            return current;
          });

          resolve(firstId);
        } catch (error: any) {
          console.error('Upload failed:', error);
          setFiles(prev => prev.map(f =>
            f.id === uploadId
              ? { ...f, status: 'error', error: error?.message || 'Upload failed' }
              : f
          ));
          reject(error);
        }
      })();
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

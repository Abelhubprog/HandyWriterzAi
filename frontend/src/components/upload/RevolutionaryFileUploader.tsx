/**
 * Revolutionary File Uploader for YC Demo Day
 * Handles 10 multimodal files: PDF, DOCX, MP3, WAV, MP4, YouTube, XLSX, TXT
 * Real-time processing visualization with Gemini 2.5 Pro integration
 */

'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Upload, 
  FileText, 
  Music, 
  Video, 
  Table, 
  Link, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Eye, 
  Trash2,
  Sparkles,
  Brain,
  Zap,
  FileAudio,
  FileVideo,
  FileSpreadsheet,
  Youtube,
  Mic,
  Image,
  X,
  Play,
  Download
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { multimodalProcessor } from '@/services/multimodal-processor';
import { ProcessedContent, ProcessingProgress, MultimediaInsight } from '@/types/multimodal';

interface FileUploadItem {
  id: string;
  file: File | null;
  url?: string; // For YouTube links
  name: string;
  type: 'pdf' | 'docx' | 'mp3' | 'wav' | 'mp4' | 'youtube' | 'xlsx' | 'txt';
  size: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  uploadProgress: number;
  processingProgress: number;
  insights: MultimediaInsight[];
  previewContent?: string;
  processingTime: number;
  quality: number;
  tokensGenerated: number;
  thumbnail?: string;
}

interface RevolutionaryFileUploaderProps {
  onFilesProcessed: (processedFiles: ProcessedContent[]) => void;
  onProcessingUpdate: (progress: ProcessingProgress[]) => void;
  maxFiles?: number;
  maxFileSize?: number; // in MB
  traceId: string;
}

export const RevolutionaryFileUploader: React.FC<RevolutionaryFileUploaderProps> = ({
  onFilesProcessed,
  onProcessingUpdate,
  maxFiles = 10,
  maxFileSize = 500,
  traceId
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<FileUploadItem[]>([]);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);
  const [totalInsights, setTotalInsights] = useState(0);
  const [processingStats, setProcessingStats] = useState({
    totalFiles: 0,
    completedFiles: 0,
    totalProcessingTime: 0,
    averageQuality: 0,
    totalTokens: 0
  });
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const supportedFileTypes = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'audio/mpeg': 'mp3',
    'audio/wav': 'wav',
    'video/mp4': 'mp4',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'text/plain': 'txt',
  } as const;

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.slice(0, maxFiles - uploadedFiles.length).map(file => {
      const fileType = supportedFileTypes[file.type as keyof typeof supportedFileTypes] || 'txt';
      return {
        id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        file,
        name: file.name,
        type: fileType,
        size: file.size,
        status: 'pending' as const,
        uploadProgress: 0,
        processingProgress: 0,
        insights: [],
        processingTime: 0,
        quality: 0,
        tokensGenerated: 0
      };
    });

    setUploadedFiles(prev => [...prev, ...newFiles]);
    
    // Start upload immediately
    newFiles.forEach(fileItem => {
      uploadFile(fileItem);
    });
  }, [uploadedFiles.length, maxFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: Object.keys(supportedFileTypes).reduce((acc, key) => {
      acc[key] = [];
      return acc;
    }, {} as any),
    maxFiles: maxFiles - uploadedFiles.length,
    maxSize: maxFileSize * 1024 * 1024,
    disabled: uploadedFiles.length >= maxFiles
  });

  const uploadFile = async (fileItem: FileUploadItem) => {
    try {
      setUploadedFiles(prev => prev.map(item => 
        item.id === fileItem.id 
          ? { ...item, status: 'uploading' }
          : item
      ));

      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploadedFiles(prev => prev.map(item => 
          item.id === fileItem.id 
            ? { ...item, uploadProgress: progress }
            : item
        ));
      }

      setUploadedFiles(prev => prev.map(item => 
        item.id === fileItem.id 
          ? { ...item, status: 'completed', uploadProgress: 100 }
          : item
      ));

    } catch (error) {
      console.error('Upload failed:', error);
      setUploadedFiles(prev => prev.map(item => 
        item.id === fileItem.id 
          ? { ...item, status: 'error' }
          : item
      ));
    }
  };

  const addYouTubeUrl = () => {
    if (!youtubeUrl.trim()) return;

    const youtubeFile: FileUploadItem = {
      id: `youtube_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      file: null,
      url: youtubeUrl,
      name: `YouTube: ${youtubeUrl}`,
      type: 'youtube',
      size: 0,
      status: 'completed',
      uploadProgress: 100,
      processingProgress: 0,
      insights: [],
      processingTime: 0,
      quality: 0,
      tokensGenerated: 0
    };

    setUploadedFiles(prev => [...prev, youtubeFile]);
    setYoutubeUrl('');
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(item => item.id !== fileId));
  };

  const startProcessing = async () => {
    if (uploadedFiles.length === 0) return;

    setIsProcessing(true);
    setOverallProgress(0);

    try {
      // Initialize real-time connection
      multimodalProcessor.initializeRealtimeConnection(traceId, (event) => {
        // Update individual file progress
        setUploadedFiles(prev => prev.map(item => 
          item.id === event.fileId 
            ? { 
                ...item, 
                status: event.stage === 'completed' ? 'completed' : 'processing',
                processingProgress: event.progress,
                processingTime: event.processingTime || 0,
                insights: event.insights || item.insights
              }
            : item
        ));

        // Update overall progress
        const completedFiles = uploadedFiles.filter(f => f.status === 'completed').length;
        setOverallProgress((completedFiles / uploadedFiles.length) * 100);
      });

      // Prepare processing requests
      const processingRequests = uploadedFiles.map(file => ({
        fileId: file.id,
        fileType: file.type,
        fileName: file.name,
        url: file.url || '',
        processingOptions: {
          useGeminiVision: ['mp4', 'youtube'].includes(file.type),
          extractCharts: ['pdf', 'docx', 'xlsx'].includes(file.type),
          identifySpeakers: ['mp3', 'wav', 'youtube'].includes(file.type),
          preserveCitations: ['pdf', 'docx'].includes(file.type),
          generateInsights: true
        }
      }));

      // Start multimodal processing
      const processedContent = await multimodalProcessor.processFiles(
        processingRequests,
        traceId,
        (progress) => {
          onProcessingUpdate(progress);
          updateProcessingStats(progress);
        }
      );

      onFilesProcessed(processedContent);
      setIsProcessing(false);

    } catch (error) {
      console.error('Processing failed:', error);
      setIsProcessing(false);
    }
  };

  const updateProcessingStats = (progress: ProcessingProgress[]) => {
    const totalFiles = progress.length;
    const completedFiles = progress.filter(p => p.stage === 'completed').length;
    const totalProcessingTime = progress.reduce((sum, p) => sum + p.processingTime, 0);
    const totalInsightsCount = progress.reduce((sum, p) => sum + p.insights.length, 0);

    setProcessingStats({
      totalFiles,
      completedFiles,
      totalProcessingTime,
      averageQuality: 0, // Will be calculated from insights
      totalTokens: 0 // Will be calculated from processed content
    });

    setTotalInsights(totalInsightsCount);
  };

  const getFileIcon = (type: FileUploadItem['type']) => {
    switch (type) {
      case 'pdf':
      case 'docx':
        return <FileText className="w-6 h-6 text-red-500" />;
      case 'mp3':
      case 'wav':
        return <FileAudio className="w-6 h-6 text-green-500" />;
      case 'mp4':
        return <FileVideo className="w-6 h-6 text-blue-500" />;
      case 'youtube':
        return <Youtube className="w-6 h-6 text-red-600" />;
      case 'xlsx':
        return <FileSpreadsheet className="w-6 h-6 text-green-600" />;
      case 'txt':
        return <FileText className="w-6 h-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status: FileUploadItem['status']) => {
    switch (status) {
      case 'pending': return 'text-gray-500';
      case 'uploading': return 'text-blue-500';
      case 'processing': return 'text-purple-500';
      case 'completed': return 'text-green-500';
      case 'error': return 'text-red-500';
    }
  };

  const getStatusIcon = (status: FileUploadItem['status']) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'uploading': return <Upload className="w-4 h-4" />;
      case 'processing': return <Brain className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const canStartProcessing = uploadedFiles.length > 0 && 
    uploadedFiles.every(file => file.status === 'completed' || file.status === 'error') &&
    !isProcessing;

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold flex items-center justify-center space-x-2">
          <Sparkles className="w-8 h-8 text-purple-500" />
          <span>Revolutionary Multimodal File Processor</span>
        </h2>
        <p className="text-gray-600">
          Upload up to {maxFiles} files (PDF, DOCX, MP3, WAV, MP4, XLSX, TXT) + YouTube links
        </p>
        <div className="flex justify-center space-x-4 text-sm">
          <Badge variant="outline">Gemini 2.5 Pro Processing</Badge>
          <Badge variant="outline">1M Token Context</Badge>
          <Badge variant="outline">Real-time Analysis</Badge>
        </div>
      </div>

      {/* Upload Interface */}
      <Tabs defaultValue="files" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="files">File Upload</TabsTrigger>
          <TabsTrigger value="youtube">YouTube Links</TabsTrigger>
          <TabsTrigger value="processing">Processing Status</TabsTrigger>
        </TabsList>

        <TabsContent value="files" className="space-y-4">
          {/* Drag & Drop Zone */}
          <Card>
            <CardContent className="p-6">
              <div
                {...getRootProps()}
                className={`
                  border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                  ${isDragActive 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-400'
                  }
                  ${uploadedFiles.length >= maxFiles ? 'opacity-50 cursor-not-allowed' : ''}
                `}
              >
                <input {...getInputProps()} ref={fileInputRef} />
                <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                {isDragActive ? (
                  <p className="text-lg text-blue-600">Drop the files here...</p>
                ) : (
                  <div className="space-y-2">
                    <p className="text-lg">Drag & drop files here, or click to select</p>
                    <p className="text-sm text-gray-500">
                      Supports: PDF, DOCX, MP3, WAV, MP4, XLSX, TXT (Max {maxFileSize}MB each)
                    </p>
                    <p className="text-xs text-gray-400">
                      {uploadedFiles.length}/{maxFiles} files uploaded
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="youtube" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Youtube className="w-6 h-6 text-red-600" />
                <span>YouTube Video Processing</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="Paste YouTube URL here..."
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  className="flex-1"
                />
                <Button 
                  onClick={addYouTubeUrl}
                  disabled={!youtubeUrl.trim() || uploadedFiles.length >= maxFiles}
                >
                  Add Video
                </Button>
              </div>
              <div className="text-sm text-gray-500">
                YouTube videos will be downloaded and processed for audio transcription and visual analysis
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="processing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Brain className="w-6 h-6 text-purple-500" />
                  <span>Processing Status</span>
                </div>
                <Button 
                  onClick={startProcessing}
                  disabled={!canStartProcessing}
                  className="flex items-center space-x-2"
                >
                  <Zap className="w-4 h-4" />
                  <span>Start Processing</span>
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isProcessing && (
                <div className="mb-6 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Overall Progress</span>
                    <span>{Math.round(overallProgress)}%</span>
                  </div>
                  <Progress value={overallProgress} className="h-2" />
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-600">Files</div>
                      <div className="font-semibold">
                        {processingStats.completedFiles}/{processingStats.totalFiles}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-600">Insights</div>
                      <div className="font-semibold">{totalInsights}</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Time</div>
                      <div className="font-semibold">
                        {Math.round(processingStats.totalProcessingTime)}s
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-600">Quality</div>
                      <div className="font-semibold">
                        {processingStats.averageQuality.toFixed(1)}/10.0
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Uploaded Files ({uploadedFiles.length})</span>
              <Badge variant="outline">
                {uploadedFiles.filter(f => f.status === 'completed').length} ready for processing
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {uploadedFiles.map((file) => (
                <div key={file.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getFileIcon(file.type)}
                      <div>
                        <div className="font-semibold text-sm">{file.name}</div>
                        <div className="text-xs text-gray-500">
                          {file.size > 0 ? formatFileSize(file.size) : 'External URL'} • 
                          <span className={`ml-1 ${getStatusColor(file.status)}`}>
                            {file.status}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <div className={getStatusColor(file.status)}>
                        {getStatusIcon(file.status)}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(file.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Upload Progress */}
                  {file.status === 'uploading' && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>Uploading...</span>
                        <span>{file.uploadProgress}%</span>
                      </div>
                      <Progress value={file.uploadProgress} className="h-1" />
                    </div>
                  )}

                  {/* Processing Progress */}
                  {file.status === 'processing' && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>Processing with AI...</span>
                        <span>{file.processingProgress}%</span>
                      </div>
                      <Progress value={file.processingProgress} className="h-1" />
                    </div>
                  )}

                  {/* Insights Preview */}
                  {file.insights.length > 0 && (
                    <div className="mt-3 p-3 bg-purple-50 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <Sparkles className="w-4 h-4 text-purple-500" />
                        <span className="text-sm font-semibold">AI Insights ({file.insights.length})</span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        {file.insights.slice(0, 4).map((insight, idx) => (
                          <div key={idx} className="bg-white p-2 rounded border">
                            <div className="font-semibold capitalize mb-1">
                              {insight.type.replace(/_/g, ' ')}
                            </div>
                            <div className="line-clamp-2">{insight.content}</div>
                            <div className="text-gray-500 mt-1">
                              Confidence: {Math.round(insight.confidence * 100)}%
                            </div>
                          </div>
                        ))}
                      </div>
                      {file.insights.length > 4 && (
                        <div className="text-xs text-center mt-2 text-purple-600">
                          +{file.insights.length - 4} more insights
                        </div>
                      )}
                    </div>
                  )}

                  {/* Processing Stats */}
                  {file.status === 'completed' && file.processingTime > 0 && (
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Processing time: {file.processingTime}s</span>
                      <span>Quality: {file.quality.toFixed(1)}/10.0</span>
                      <span>Tokens: {file.tokensGenerated.toLocaleString()}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
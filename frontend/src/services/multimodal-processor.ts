/**
 * Advanced Multimodal Content Processor for HandyWriterz
 * Handles audio, video, documents, and structured data processing
 * Integrates with Gemini 2.5 Pro for context-aware analysis
 */

import { ProcessedContent, FileProcessingEvent, MultimediaInsight } from '@/types/multimodal';

export interface ProcessingProgress {
  fileId: string;
  fileName: string;
  progress: number;
  stage: 'uploading' | 'transcribing' | 'analyzing' | 'chunking' | 'embedding' | 'completed' | 'error';
  insights: MultimediaInsight[];
  processingTime: number;
  estimatedCompletion: number;
}

export interface MultimodalProcessingRequest {
  fileId: string;
  fileType: 'audio' | 'video' | 'pdf' | 'docx' | 'excel' | 'text';
  fileName: string;
  url: string;
  processingOptions: {
    useGeminiVision: boolean;
    extractCharts: boolean;
    identifySpeakers: boolean;
    preserveCitations: boolean;
    generateInsights: boolean;
  };
}

export class MultimodalProcessor {
  private baseUrl: string;
  private wsConnection: WebSocket | null = null;

  constructor(baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Initialize WebSocket connection for real-time processing updates
   */
  initializeRealtimeConnection(traceId: string, onUpdate: (event: FileProcessingEvent) => void): void {
    const wsUrl = `${this.baseUrl.replace('http', 'ws')}/ws/files/${traceId}`;
    this.wsConnection = new WebSocket(wsUrl);

    this.wsConnection.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data as FileProcessingEvent);
    };

    this.wsConnection.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.wsConnection.onclose = () => {
      console.log('WebSocket connection closed');
    };
  }

  /**
   * Process multiple files with parallel execution and progress tracking
   */
  async processFiles(
    files: MultimodalProcessingRequest[],
    traceId: string,
    onProgress?: (progress: ProcessingProgress[]) => void
  ): Promise<ProcessedContent[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/files/process-multimodal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Trace-ID': traceId,
        },
        body: JSON.stringify({
          files,
          processingOptions: {
            maxContextWindow: 1000000, // 1M tokens for Gemini 2.5 Pro
            preserveSemanticStructure: true,
            enableRealtimeUpdates: true,
            qualityThreshold: 0.85,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Processing failed: ${response.statusText}`);
      }

      const result = await response.json();
      return result.processedContent as ProcessedContent[];
    } catch (error) {
      console.error('Multimodal processing error:', error);
      throw error;
    }
  }

  /**
   * Process audio files with speaker identification and insight extraction
   */
  async processAudio(fileId: string, options: {
    identifySpeakers?: boolean;
    extractKeyQuotes?: boolean;
    academicAnalysis?: boolean;
  } = {}): Promise<ProcessedContent> {
    const response = await fetch(`${this.baseUrl}/api/files/process-audio/${fileId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcriptionEngine: 'whisper-large-v3',
        speakerIdentification: options.identifySpeakers ?? true,
        academicAnalysis: options.academicAnalysis ?? true,
        keyQuoteExtraction: options.extractKeyQuotes ?? true,
        geminiAnalysis: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Audio processing failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Process video files with Gemini Vision and audio transcription
   */
  async processVideo(fileId: string, options: {
    extractFrames?: boolean;
    analyzeSlides?: boolean;
    extractCharts?: boolean;
  } = {}): Promise<ProcessedContent> {
    const response = await fetch(`${this.baseUrl}/api/files/process-video/${fileId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        geminiVisionEnabled: true,
        frameExtractionInterval: 30, // Every 30 seconds
        slideDetection: options.analyzeSlides ?? true,
        chartExtraction: options.extractCharts ?? true,
        audioTranscription: true,
        academicContentAnalysis: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Video processing failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Process YouTube videos with download and analysis
   */
  async processYouTube(url: string, options: {
    maxDuration?: number;
    qualityPreference?: 'audio' | 'video' | 'both';
  } = {}): Promise<ProcessedContent> {
    const response = await fetch(`${this.baseUrl}/api/files/process-youtube`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        maxDuration: options.maxDuration ?? 3600, // 1 hour max
        qualityPreference: options.qualityPreference ?? 'both',
        downloadQuality: 'best[height<=720]',
        processAudio: true,
        processVideo: true,
        geminiAnalysis: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`YouTube processing failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Process documents with advanced citation-aware chunking
   */
  async processDocument(fileId: string, options: {
    preserveCitations?: boolean;
    semanticChunking?: boolean;
    extractImages?: boolean;
  } = {}): Promise<ProcessedContent> {
    const response = await fetch(`${this.baseUrl}/api/files/process-document/${fileId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        useAgenticDoc: true,
        preserveCitations: options.preserveCitations ?? true,
        semanticChunking: options.semanticChunking ?? true,
        extractImages: options.extractImages ?? true,
        geminiAnalysis: true,
        academicProcessing: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Document processing failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Process Excel/CSV files with data analysis and visualization
   */
  async processStructuredData(fileId: string, options: {
    generateCharts?: boolean;
    statisticalAnalysis?: boolean;
    dataInsights?: boolean;
  } = {}): Promise<ProcessedContent> {
    const response = await fetch(`${this.baseUrl}/api/files/process-data/${fileId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pandasAnalysis: true,
        generateVisualizations: options.generateCharts ?? true,
        statisticalInsights: options.statisticalAnalysis ?? true,
        dataPatternRecognition: options.dataInsights ?? true,
        geminiDataAnalysis: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Data processing failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get processing status for multiple files
   */
  async getProcessingStatus(fileIds: string[]): Promise<ProcessingProgress[]> {
    const response = await fetch(`${this.baseUrl}/api/files/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fileIds }),
    });

    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Assemble intelligent context for Gemini 2.5 Pro
   */
  async assembleContext(
    processedFiles: ProcessedContent[],
    userPrompt: string,
    options: {
      maxTokens?: number;
      prioritizeRecent?: boolean;
      focusAreas?: string[];
    } = {}
  ): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/context/assemble`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        processedFiles,
        userPrompt,
        maxTokens: options.maxTokens ?? 900000, // Leave room for response
        prioritizeRecent: options.prioritizeRecent ?? false,
        focusAreas: options.focusAreas ?? [],
        semanticRanking: true,
        contextOptimization: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Context assembly failed: ${response.statusText}`);
    }

    const result = await response.json();
    return result.assembledContext;
  }

  /**
   * Cleanup resources and close connections
   */
  cleanup(): void {
    if (this.wsConnection) {
      this.wsConnection.close();
      this.wsConnection = null;
    }
  }
}

// Singleton instance for global use
export const multimodalProcessor = new MultimodalProcessor();
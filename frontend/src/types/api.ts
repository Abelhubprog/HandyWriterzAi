// API Client Types
export interface ApiClientConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  retryDelay: number;
  headers: Record<string, string>;
}

export interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
  retries?: number;
  cache?: RequestCache;
  next?: NextFetchRequestConfig;
}

export interface ApiError {
  code: string;
  message: string;
  status: number;
  details?: Record<string, unknown>;
  timestamp: string;
  requestId?: string;
}

export interface ApiSuccessResponse<T = unknown> {
  success: true;
  data: T;
  message?: string;
  timestamp: string;
  requestId?: string;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiError;
  timestamp: string;
  requestId?: string;
}

export type ApiResponse<T = unknown> = ApiSuccessResponse<T> | ApiErrorResponse;

// Specific API Endpoints
export interface ChatRequest {
  prompt: string;
  mode: string;
  fileIds: string[];
  model: string;
  temperature?: number;
  maxTokens?: number;
  streamingEnabled?: boolean;
}

export interface ChatResponse {
  conversationId: string;
  message: string;
  sources: Source[];
  metadata: {
    model: string;
    tokenCount: number;
    cost: number;
    processingTime: number;
  };
}

export interface FileUploadRequest {
  file: File;
  metadata?: Record<string, unknown>;
}

export interface FileUploadResponse {
  fileId: string;
  url: string;
  metadata: {
    name: string;
    size: number;
    type: string;
    extractedText?: string;
  };
}

export interface UserProfileResponse {
  user: User;
  subscription: Subscription;
  usage: {
    tokensUsed: number;
    tokensLimit: number;
    documentsGenerated: number;
    documentsLimit: number;
  };
}

export interface ModelConfigResponse {
  models: Array<{
    id: string;
    name: string;
    provider: string;
    maxTokens: number;
    costPerToken: number;
    capabilities: string[];
    availability: 'available' | 'limited' | 'unavailable';
  }>;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface DocumentDownloadResponse {
  downloadUrl: string;
  expiresAt: string;
  format: string;
  size: number;
}
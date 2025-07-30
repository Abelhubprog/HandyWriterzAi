// Core API Types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
  };
}

// User and Authentication Types
export interface User {
  id: string;
  email: string;
  username: string;
  avatar?: string;
  walletAddress?: string;
  createdAt: string;
  updatedAt: string;
  subscription?: Subscription;
  preferences: UserPreferences;
}

export interface Subscription {
  id: string;
  plan: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'inactive' | 'cancelled' | 'past_due';
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  usage: {
    tokensUsed: number;
    tokensLimit: number;
    documentsGenerated: number;
    documentsLimit: number;
  };
}

export interface UserPreferences {
  model: string;
  temperature: number;
  maxTokens: number;
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: {
    email: boolean;
    browser: boolean;
    marketing: boolean;
  };
}

// Chat and Conversation Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    model?: string;
    tokenCount?: number;
    cost?: number;
    processingTime?: number;
  };
}

// LangGraph-compatible Message type
export interface Message {
  id?: string;
  content: string;
  type: "human" | "ai" | "system";
  timestamp?: string;
  additional_kwargs?: Record<string, any>;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  status: 'active' | 'completed' | 'failed' | 'cancelled';
  createdAt: string;
  updatedAt: string;
  metadata: {
    model: string;
    mode: DocumentMode;
    totalTokens: number;
    totalCost: number;
    processingTime: number;
  };
}

export type DocumentMode = 
  | 'general'
  | 'essay'
  | 'report'
  | 'dissertation'
  | 'case_study'
  | 'case_scenario'
  | 'critical_review'
  | 'database_search'
  | 'reflection'
  | 'document_analysis'
  | 'presentation'
  | 'poster'
  | 'exam_prep';

// File Upload Types
export interface FileUpload {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  metadata?: {
    pages?: number;
    wordCount?: number;
    extractedText?: string;
    embedding?: number[];
  };
  createdAt: string;
}

export interface FileUploadProgress {
  fileId: string;
  progress: number;
  status: FileUpload['status'];
  error?: string;
}

// Research and Source Types
export interface Source {
  id: string;
  title: string;
  url: string;
  type: 'academic' | 'web' | 'book' | 'journal' | 'news' | 'other';
  authors?: string[];
  publicationDate?: string;
  summary: string;
  relevanceScore: number;
  credibilityScore: number;
  metadata?: {
    doi?: string;
    isbn?: string;
    journal?: string;
    volume?: string;
    issue?: string;
    pages?: string;
  };
}

export interface ResearchQuery {
  query: string;
  filters?: {
    dateRange?: {
      start?: string;
      end?: string;
    };
    sourceTypes?: Source['type'][];
    minCredibilityScore?: number;
    languages?: string[];
  };
  limit?: number;
}

// Document Generation Types
export interface DocumentGeneration {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  stages: GenerationStage[];
  result?: GeneratedDocument;
  error?: string;
  createdAt: string;
  updatedAt: string;
}

export interface GenerationStage {
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  startTime?: string;
  endTime?: string;
  details?: string;
}

export interface GeneratedDocument {
  id: string;
  title: string;
  content: string;
  format: 'markdown' | 'html' | 'docx' | 'pdf';
  wordCount: number;
  metadata: {
    mode: DocumentMode;
    sources: Source[];
    qualityScore: number;
    plagiarismScore: number;
    readabilityScore: number;
    citations: Citation[];
  };
  downloadUrls: {
    docx?: string;
    pdf?: string;
    html?: string;
    markdown?: string;
  };
}

export interface Citation {
  id: string;
  sourceId: string;
  text: string;
  pageNumber?: number;
  style: 'APA' | 'MLA' | 'Chicago' | 'Harvard' | 'IEEE';
  inText: string;
  bibliography: string;
}

// Agent Activity Types
export interface AgentActivity {
  id: string;
  agentName: string;
  action: string;
  status: 'started' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  startTime: string;
  endTime?: string;
  details?: string;
  metadata?: Record<string, unknown>;
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
  stack?: string;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// WebSocket Types
export interface WebSocketMessage<T = unknown> {
  type: string;
  data: T;
  timestamp: string;
  id?: string;
}

export interface StreamingResponse {
  type: 'content' | 'agent_activity' | 'cost_update' | 'error' | 'complete';
  data: unknown;
  conversationId: string;
  timestamp: string;
}

// Form Types
export interface ChatFormData {
  prompt: string;
  mode: DocumentMode;
  fileIds: string[];
  model: string;
  temperature: number;
  maxTokens: number;
}

export interface SettingsFormData {
  model: string;
  temperature: number;
  maxTokens: number;
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: {
    email: boolean;
    browser: boolean;
    marketing: boolean;
  };
}

// Utility Types
export type Status = 'idle' | 'loading' | 'success' | 'error';

export type AsyncState<T> = {
  data: T | null;
  status: Status;
  error: string | null;
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredKeys<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Component Props Types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingProps extends BaseComponentProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'spinner' | 'dots' | 'pulse';
  text?: string;
}

export interface ErrorProps extends BaseComponentProps {
  error: Error | string;
  onRetry?: () => void;
  showDetails?: boolean;
}

// Advanced Type Helpers
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Prettify<T> = {
  [K in keyof T]: T[K];
} & {};

export type UnionToIntersection<U> = (U extends any ? (k: U) => void : never) extends (k: infer I) => void ? I : never;

export type IsEqual<X, Y> = (<T>() => T extends X ? 1 : 2) extends <T>() => T extends Y ? 1 : 2 ? true : false;

export type IsAny<T> = 0 extends 1 & T ? true : false;

export type IsNever<T> = [T] extends [never] ? true : false;

export type IsUnion<T> = IsNever<T> extends true ? false : T extends any ? IsEqual<T, any> extends true ? false : true : false;

// Event Types
export interface CustomEvent<T = unknown> {
  type: string;
  data: T;
  timestamp: string;
  source?: string;
}

export type EventHandler<T = unknown> = (event: CustomEvent<T>) => void;

// Types are exported individually above
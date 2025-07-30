/**
 * Advanced API client with comprehensive error handling, retry logic, and monitoring
 */

import { EventEmitter } from 'events';

// Types
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  rateLimit: {
    requests: number;
    windowMs: number;
  };
  circuitBreaker: {
    threshold: number;
    timeout: number;
    monitoringPeriod: number;
  };
}

export interface ApiError extends Error {
  code: string;
  status?: number;
  details?: any;
  timestamp: number;
  requestId?: string;
}

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  headers: Record<string, string>;
  requestId: string;
  timestamp: number;
  processingTime: number;
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retryAttempts?: number;
  cache?: boolean;
  signal?: AbortSignal;
}

export interface RateLimitState {
  requests: number;
  windowStart: number;
  blocked: boolean;
}

export interface CircuitBreakerState {
  state: 'closed' | 'open' | 'half-open';
  failures: number;
  lastFailureTime: number;
  nextRetryTime: number;
}

export interface ApiMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  errorRate: number;
  rateLimitHits: number;
  circuitBreakerTrips: number;
}

export class AdvancedApiClient extends EventEmitter {
  private config: ApiConfig;
  private rateLimit: RateLimitState;
  private circuitBreaker: CircuitBreakerState;
  private metrics: ApiMetrics;
  private cache: Map<string, { data: any; timestamp: number; ttl: number }>;
  private requestQueue: Map<string, Promise<any>>;

  constructor(config: Partial<ApiConfig> = {}) {
    super();
    
    this.config = {
      baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 30000,
      retryAttempts: 3,
      retryDelay: 1000,
      rateLimit: {
        requests: 100,
        windowMs: 60000
      },
      circuitBreaker: {
        threshold: 5,
        timeout: 30000,
        monitoringPeriod: 60000
      },
      ...config
    };

    this.rateLimit = {
      requests: 0,
      windowStart: Date.now(),
      blocked: false
    };

    this.circuitBreaker = {
      state: 'closed',
      failures: 0,
      lastFailureTime: 0,
      nextRetryTime: 0
    };

    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      errorRate: 0,
      rateLimitHits: 0,
      circuitBreakerTrips: 0
    };

    this.cache = new Map();
    this.requestQueue = new Map();

    // Setup periodic cleanup
    setInterval(() => this.cleanup(), 60000);
  }

  /**
   * Make HTTP request with advanced error handling
   */
  async request<T = any>(
    endpoint: string, 
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const requestId = this.generateRequestId();
    const startTime = Date.now();
    
    try {
      // Check circuit breaker
      if (this.circuitBreaker.state === 'open') {
        if (Date.now() < this.circuitBreaker.nextRetryTime) {
          throw this.createError(
            'CIRCUIT_BREAKER_OPEN',
            'Circuit breaker is open',
            503
          );
        }
        this.circuitBreaker.state = 'half-open';
      }

      // Check rate limit
      if (this.isRateLimited()) {
        this.metrics.rateLimitHits++;
        throw this.createError(
          'RATE_LIMIT_EXCEEDED',
          'Rate limit exceeded',
          429
        );
      }

      // Check cache
      const cacheKey = this.getCacheKey(endpoint, options);
      if (options.cache !== false && this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey)!;
        if (Date.now() - cached.timestamp < cached.ttl) {
          return {
            data: cached.data,
            status: 200,
            headers: {},
            requestId,
            timestamp: Date.now(),
            processingTime: Date.now() - startTime
          };
        }
      }

      // Check for duplicate requests
      if (this.requestQueue.has(cacheKey)) {
        return await this.requestQueue.get(cacheKey);
      }

      // Make request
      const requestPromise = this.executeRequest<T>(endpoint, options, requestId, startTime);
      this.requestQueue.set(cacheKey, requestPromise);

      try {
        const response = await requestPromise;
        
        // Update metrics
        this.updateMetrics(true, Date.now() - startTime);
        
        // Reset circuit breaker on success
        if (this.circuitBreaker.state === 'half-open') {
          this.circuitBreaker.state = 'closed';
          this.circuitBreaker.failures = 0;
        }

        // Cache response if cacheable
        if (options.cache !== false && options.method !== 'POST') {
          this.cache.set(cacheKey, {
            data: response.data,
            timestamp: Date.now(),
            ttl: 300000 // 5 minutes
          });
        }

        return response;
      } finally {
        this.requestQueue.delete(cacheKey);
      }
    } catch (error) {
      this.updateMetrics(false, Date.now() - startTime);
      this.handleError(error as ApiError);
      throw error;
    }
  }

  /**
   * Execute HTTP request with retry logic
   */
  private async executeRequest<T>(
    endpoint: string,
    options: RequestOptions,
    requestId: string,
    startTime: number
  ): Promise<ApiResponse<T>> {
    const { method = 'GET', headers = {}, body, timeout, retryAttempts, signal } = options;
    const url = `${this.config.baseUrl}${endpoint}`;
    
    const requestHeaders = {
      'Content-Type': 'application/json',
      'X-Request-ID': requestId,
      'Authorization': `Bearer ${this.getAuthToken()}`,
      ...headers
    };

    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      body: body ? JSON.stringify(body) : undefined,
      signal
    };

    const maxRetries = retryAttempts ?? this.config.retryAttempts;
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // Create timeout controller
        const timeoutController = new AbortController();
        const timeoutId = setTimeout(() => {
          timeoutController.abort();
        }, timeout ?? this.config.timeout);

        // Combine timeout and external abort signals
        const combinedSignal = this.combineAbortSignals([
          timeoutController.signal,
          signal
        ].filter(Boolean) as AbortSignal[]);

        const response = await fetch(url, {
          ...requestOptions,
          signal: combinedSignal
        });

        clearTimeout(timeoutId);

        // Handle HTTP errors
        if (!response.ok) {
          const errorBody = await response.text();
          let errorData: any;
          
          try {
            errorData = JSON.parse(errorBody);
          } catch {
            errorData = { message: errorBody };
          }

          throw this.createError(
            `HTTP_${response.status}`,
            errorData.message || response.statusText,
            response.status,
            errorData
          );
        }

        // Parse response
        const responseData = await response.json();
        
        return {
          data: responseData,
          status: response.status,
          headers: Object.fromEntries(response.headers.entries()),
          requestId,
          timestamp: Date.now(),
          processingTime: Date.now() - startTime
        };

      } catch (error) {
        lastError = error as Error;
        
        // Don't retry on certain errors
        if (
          error instanceof Error &&
          (error.name === 'AbortError' || 
           (error as any).status === 401 || 
           (error as any).status === 403 ||
           (error as any).status === 404)
        ) {
          break;
        }

        // Wait before retry
        if (attempt < maxRetries) {
          const delay = this.config.retryDelay * Math.pow(2, attempt);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError || new Error('Request failed after all retries');
  }

  /**
   * Specialized chat request
   */
  async chat(request: any): Promise<ApiResponse> {
    return this.request('/api/chat', {
      method: 'POST',
      body: request,
      cache: false
    });
  }

  /**
   * Upload files with progress tracking
   */
  async uploadFiles(
    files: File[],
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<{ file_ids: string[] }>> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          onProgress?.(progress);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve({
            data: JSON.parse(xhr.responseText),
            status: xhr.status,
            headers: {},
            requestId: this.generateRequestId(),
            timestamp: Date.now(),
            processingTime: 0
          });
        } else {
          reject(this.createError(
            `UPLOAD_ERROR_${xhr.status}`,
            'File upload failed',
            xhr.status
          ));
        }
      };

      xhr.onerror = () => {
        reject(this.createError(
          'UPLOAD_NETWORK_ERROR',
          'Network error during upload',
          0
        ));
      };

      xhr.open('POST', `${this.config.baseUrl}/api/files/upload`);
      xhr.setRequestHeader('Authorization', `Bearer ${this.getAuthToken()}`);
      xhr.send(formData);
    });
  }

  /**
   * Stream response handler
   */
  async streamResponse(
    endpoint: string,
    options: RequestOptions = {},
    onChunk?: (chunk: any) => void
  ): Promise<void> {
    const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
      method: options.method || 'GET',
      headers: {
        'Authorization': `Bearer ${this.getAuthToken()}`,
        ...options.headers
      },
      body: options.body ? JSON.stringify(options.body) : undefined
    });

    if (!response.ok) {
      throw this.createError(
        `STREAM_ERROR_${response.status}`,
        'Stream request failed',
        response.status
      );
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No readable stream');
    }

    const decoder = new TextDecoder();
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onChunk?.(data);
            } catch (error) {
              console.error('Error parsing SSE data:', error);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Health check
   */
  async health(): Promise<ApiResponse> {
    return this.request('/api/health', {
      timeout: 5000,
      retryAttempts: 1
    });
  }

  /**
   * Get API metrics
   */
  getMetrics(): ApiMetrics {
    return { ...this.metrics };
  }

  /**
   * Reset metrics
   */
  resetMetrics(): void {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      errorRate: 0,
      rateLimitHits: 0,
      circuitBreakerTrips: 0
    };
  }

  /**
   * Utility methods
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getAuthToken(): string {
    return localStorage.getItem('access_token') || '';
  }

  private getCacheKey(endpoint: string, options: RequestOptions): string {
    return `${options.method || 'GET'}:${endpoint}:${JSON.stringify(options.body || {})}`;
  }

  private isRateLimited(): boolean {
    const now = Date.now();
    
    // Reset window if needed
    if (now - this.rateLimit.windowStart > this.config.rateLimit.windowMs) {
      this.rateLimit.requests = 0;
      this.rateLimit.windowStart = now;
      this.rateLimit.blocked = false;
    }

    // Check if rate limited
    if (this.rateLimit.requests >= this.config.rateLimit.requests) {
      this.rateLimit.blocked = true;
      return true;
    }

    this.rateLimit.requests++;
    return false;
  }

  private updateMetrics(success: boolean, responseTime: number): void {
    this.metrics.totalRequests++;
    
    if (success) {
      this.metrics.successfulRequests++;
    } else {
      this.metrics.failedRequests++;
    }

    // Update average response time
    const totalResponseTime = this.metrics.averageResponseTime * (this.metrics.totalRequests - 1);
    this.metrics.averageResponseTime = (totalResponseTime + responseTime) / this.metrics.totalRequests;

    // Update error rate
    this.metrics.errorRate = this.metrics.failedRequests / this.metrics.totalRequests;
  }

  private handleError(error: ApiError): void {
    // Update circuit breaker
    if (this.circuitBreaker.state === 'closed' || this.circuitBreaker.state === 'half-open') {
      this.circuitBreaker.failures++;
      this.circuitBreaker.lastFailureTime = Date.now();

      if (this.circuitBreaker.failures >= this.config.circuitBreaker.threshold) {
        this.circuitBreaker.state = 'open';
        this.circuitBreaker.nextRetryTime = Date.now() + this.config.circuitBreaker.timeout;
        this.metrics.circuitBreakerTrips++;
        this.emit('circuitBreakerOpen', { error, failures: this.circuitBreaker.failures });
      }
    }

    // Emit error event
    this.emit('error', error);
  }

  private createError(code: string, message: string, status?: number, details?: any): ApiError {
    const error = new Error(message) as ApiError;
    error.code = code;
    error.status = status;
    error.details = details;
    error.timestamp = Date.now();
    return error;
  }

  private combineAbortSignals(signals: AbortSignal[]): AbortSignal {
    const controller = new AbortController();
    
    signals.forEach(signal => {
      if (signal.aborted) {
        controller.abort();
      } else {
        signal.addEventListener('abort', () => controller.abort());
      }
    });

    return controller.signal;
  }

  private cleanup(): void {
    // Clear expired cache entries
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key);
      }
    }

    // Reset circuit breaker if enough time has passed
    if (
      this.circuitBreaker.state === 'open' &&
      now - this.circuitBreaker.lastFailureTime > this.config.circuitBreaker.monitoringPeriod
    ) {
      this.circuitBreaker.failures = 0;
      this.circuitBreaker.state = 'closed';
    }
  }
}

// Export singleton instance
export const apiClient = new AdvancedApiClient();

// Export types for external use
export type {
  ApiConfig,
  ApiError,
  ApiResponse,
  RequestOptions,
  ApiMetrics
};
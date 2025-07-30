import { ApiResponse, ApiError, ApiRequestOptions } from '@/types/api';

export class ApiClient {
  private baseUrl: string;
  private defaultTimeout: number;
  private defaultRetries: number;
  private defaultRetryDelay: number;
  private defaultHeaders: Record<string, string>;
  private requestInterceptors: Array<(options: ApiRequestOptions) => ApiRequestOptions> = [];
  private responseInterceptors: Array<(response: Response) => Response | Promise<Response>> = [];
  private errorInterceptors: Array<(error: ApiError) => ApiError> = [];
  private abortControllers: Map<string, AbortController> = new Map();

  constructor(config: {
    baseUrl?: string;
    timeout?: number;
    retries?: number;
    retryDelay?: number;
    headers?: Record<string, string>;
  } = {}) {
    this.baseUrl = config.baseUrl || '/api';
    this.defaultTimeout = config.timeout || 30000;
    this.defaultRetries = config.retries || 3;
    this.defaultRetryDelay = config.retryDelay || 1000;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...config.headers,
    };
  }

  // Interceptor methods
  addRequestInterceptor(interceptor: (options: ApiRequestOptions) => ApiRequestOptions) {
    this.requestInterceptors.push(interceptor);
    return () => {
      const index = this.requestInterceptors.indexOf(interceptor);
      if (index > -1) this.requestInterceptors.splice(index, 1);
    };
  }

  addResponseInterceptor(interceptor: (response: Response) => Response | Promise<Response>) {
    this.responseInterceptors.push(interceptor);
    return () => {
      const index = this.responseInterceptors.indexOf(interceptor);
      if (index > -1) this.responseInterceptors.splice(index, 1);
    };
  }

  addErrorInterceptor(interceptor: (error: ApiError) => ApiError) {
    this.errorInterceptors.push(interceptor);
    return () => {
      const index = this.errorInterceptors.indexOf(interceptor);
      if (index > -1) this.errorInterceptors.splice(index, 1);
    };
  }

  // Request cancellation
  cancelRequest(requestId: string) {
    const controller = this.abortControllers.get(requestId);
    if (controller) {
      controller.abort();
      this.abortControllers.delete(requestId);
    }
  }

  cancelAllRequests() {
    for (const controller of this.abortControllers.values()) {
      controller.abort();
    }
    this.abortControllers.clear();
  }

  // Core request method
  async request<T = unknown>(
    endpoint: string,
    options: ApiRequestOptions = {},
    requestId?: string
  ): Promise<ApiResponse<T>> {
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = this.defaultTimeout,
      retries = this.defaultRetries,
      cache,
      next,
    } = options;

    let processedOptions: ApiRequestOptions = {
      method,
      headers: { ...this.defaultHeaders, ...headers },
      body,
      timeout,
      retries,
      cache,
      next,
    };

    // Apply request interceptors
    for (const interceptor of this.requestInterceptors) {
      processedOptions = interceptor(processedOptions);
    }

    // Create abort controller
    const controller = new AbortController();
    if (requestId) {
      this.abortControllers.set(requestId, controller);
    }

    const executeRequest = async (attempt: number = 0): Promise<ApiResponse<T>> => {
      try {
        const timeoutId = setTimeout(() => {
          controller.abort();
        }, timeout);

        const fetchOptions: RequestInit = {
          method: processedOptions.method,
          headers: processedOptions.headers as HeadersInit,
          body: this.serializeBody(processedOptions.body),
          signal: controller.signal,
          cache: processedOptions.cache,
          next: processedOptions.next,
        };

        let response = await fetch(`${this.baseUrl}${endpoint}`, fetchOptions);
        clearTimeout(timeoutId);

        // Apply response interceptors
        for (const interceptor of this.responseInterceptors) {
          response = await interceptor(response);
        }

        if (!response.ok) {
          const errorData = await this.parseErrorResponse(response);
          throw new ApiError(
            errorData.code || 'HTTP_ERROR',
            errorData.message || `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData.details,
            new Date().toISOString(),
            response.headers.get('x-request-id') || undefined
          );
        }

        const data = await this.parseResponse<T>(response);
        return {
          success: true,
          data,
          timestamp: new Date().toISOString(),
          requestId: response.headers.get('x-request-id') || undefined,
        };
      } catch (error) {
        if (requestId) {
          this.abortControllers.delete(requestId);
        }

        if (error instanceof ApiError) {
          // Apply error interceptors
          let processedError = error;
          for (const interceptor of this.errorInterceptors) {
            processedError = interceptor(processedError);
          }

          // Retry logic
          if (attempt < retries && this.shouldRetry(error)) {
            await this.delay(this.defaultRetryDelay * Math.pow(2, attempt));
            return executeRequest(attempt + 1);
          }

          return {
            success: false,
            error: processedError,
            timestamp: new Date().toISOString(),
          };
        }

        // Handle network errors, aborted requests, etc.
        const apiError = new ApiError(
          'NETWORK_ERROR',
          error instanceof Error ? error.message : 'Network error occurred',
          0,
          { originalError: error },
          new Date().toISOString()
        );

        if (attempt < retries && !controller.signal.aborted) {
          await this.delay(this.defaultRetryDelay * Math.pow(2, attempt));
          return executeRequest(attempt + 1);
        }

        return {
          success: false,
          error: apiError,
          timestamp: new Date().toISOString(),
        };
      }
    };

    return executeRequest();
  }

  // HTTP method helpers
  async get<T = unknown>(
    endpoint: string,
    options: Omit<ApiRequestOptions, 'method'> = {},
    requestId?: string
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' }, requestId);
  }

  async post<T = unknown>(
    endpoint: string,
    body?: unknown,
    options: Omit<ApiRequestOptions, 'method' | 'body'> = {},
    requestId?: string
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body }, requestId);
  }

  async put<T = unknown>(
    endpoint: string,
    body?: unknown,
    options: Omit<ApiRequestOptions, 'method' | 'body'> = {},
    requestId?: string
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body }, requestId);
  }

  async patch<T = unknown>(
    endpoint: string,
    body?: unknown,
    options: Omit<ApiRequestOptions, 'method' | 'body'> = {},
    requestId?: string
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body }, requestId);
  }

  async delete<T = unknown>(
    endpoint: string,
    options: Omit<ApiRequestOptions, 'method'> = {},
    requestId?: string
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' }, requestId);
  }

  // Streaming request for SSE
  async stream<T = unknown>(
    endpoint: string,
    options: ApiRequestOptions = {},
    onMessage?: (data: T) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<void> {
    const controller = new AbortController();
    const requestId = `stream-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.abortControllers.set(requestId, controller);

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: options.method || 'GET',
        headers: {
          ...this.defaultHeaders,
          ...options.headers,
          Accept: 'text/event-stream',
        },
        body: this.serializeBody(options.body),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onMessage?.(data);
            } catch (error) {
              onError?.(error instanceof Error ? error : new Error('Failed to parse SSE data'));
            }
          }
        }
      }

      onComplete?.();
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error('Stream error'));
    } finally {
      this.abortControllers.delete(requestId);
    }
  }

  // File upload with progress
  async upload<T = unknown>(
    endpoint: string,
    file: File | File[],
    options: {
      onProgress?: (progress: number) => void;
      metadata?: Record<string, string>;
      headers?: Record<string, string>;
    } = {}
  ): Promise<ApiResponse<T>> {
    const formData = new FormData();
    const files = Array.isArray(file) ? file : [file];

    files.forEach((f, index) => {
      formData.append(`file${index}`, f);
    });

    if (options.metadata) {
      Object.entries(options.metadata).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      body: formData,
      headers: {
        ...options.headers,
        // Don't set Content-Type for FormData, let browser set it with boundary
      },
    });
  }

  // Utility methods
  private serializeBody(body: unknown): string | FormData | null {
    if (body === null || body === undefined) return null;
    if (body instanceof FormData) return body;
    if (typeof body === 'string') return body;
    return JSON.stringify(body);
  }

  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      return response.json();
    }
    return response.text() as unknown as T;
  }

  private async parseErrorResponse(response: Response): Promise<{
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
  }> {
    try {
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return await response.json();
      }
      const text = await response.text();
      return { message: text };
    } catch {
      return { message: 'Failed to parse error response' };
    }
  }

  private shouldRetry(error: ApiError): boolean {
    // Don't retry client errors (4xx) except for 429 (rate limit)
    if (error.status >= 400 && error.status < 500 && error.status !== 429) {
      return false;
    }
    return true;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Custom ApiError class
class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
    public details?: Record<string, unknown>,
    public timestamp?: string,
    public requestId?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Create default instance
export const apiClient = new ApiClient();

// Add default interceptors
apiClient.addRequestInterceptor((options) => {
  // Add authentication token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    options.headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return options;
});

apiClient.addResponseInterceptor((response) => {
  // Handle authentication errors
  if (response.status === 401) {
    // Clear token and redirect to login
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  }
  return response;
});

apiClient.addErrorInterceptor((error) => {
  // Log errors to external service
  console.error('API Error:', error);
  
  // You can add error reporting here
  // Sentry.captureException(error);
  
  return error;
});

export { ApiError };
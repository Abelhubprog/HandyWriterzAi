import { useCallback, useEffect, useRef, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { ApiResponse } from '@/types/api';
import { UseApiState, UseApiOptions } from '@/types/hooks';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  staleTime: number;
}

// Global cache for API responses
const apiCache = new Map<string, CacheEntry<unknown>>();

export function useAdvancedApi<T>(
  endpoint: string,
  options: UseApiOptions<T> = {}
): UseApiState<T> {
  const {
    immediate = true,
    onSuccess,
    onError,
    retries = 3,
    retryDelay = 1000,
    staleTime = 5 * 60 * 1000, // 5 minutes
    cacheTime = 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus = true,
    refetchOnMount = true,
  } = options;

  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);
  const requestIdRef = useRef<string | null>(null);

  // Generate cache key
  const getCacheKey = useCallback(() => {
    return `${endpoint}`;
  }, [endpoint]);

  // Check if data is stale
  const isStale = useCallback((entry: CacheEntry<T>) => {
    return Date.now() - entry.timestamp > entry.staleTime;
  }, []);

  // Execute API request
  const execute = useCallback(
    async (force = false): Promise<T | null> => {
      const cacheKey = getCacheKey();
      
      // Check cache first
      if (!force) {
        const cached = apiCache.get(cacheKey) as CacheEntry<T> | undefined;
        if (cached && !isStale(cached)) {
          setState(prev => ({ ...prev, data: cached.data, loading: false, error: null }));
          return cached.data;
        }
      }

      // Cancel previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();
      requestIdRef.current = `${endpoint}-${Date.now()}`;

      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const response = await apiClient.get<T>(
          endpoint,
          { 
            retries,
            timeout: 30000,
          },
          requestIdRef.current
        );

        if (!response.success) {
          throw new Error(response.error.message);
        }

        const data = response.data;

        // Cache the response
        apiCache.set(cacheKey, {
          data,
          timestamp: Date.now(),
          staleTime,
        });

        setState({ data, loading: false, error: null });
        onSuccess?.(data);
        retryCountRef.current = 0;

        return data;
      } catch (error) {
        const apiError = error instanceof Error ? error : new Error('Unknown error');
        
        // Retry logic
        if (retryCountRef.current < retries && !abortControllerRef.current?.signal.aborted) {
          retryCountRef.current++;
          await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, retryCountRef.current - 1)));
          return execute(force);
        }

        setState(prev => ({ ...prev, loading: false, error: apiError }));
        onError?.(apiError);
        return null;
      }
    },
    [endpoint, retries, retryDelay, staleTime, getCacheKey, isStale, onSuccess, onError]
  );

  // Refetch function
  const refetch = useCallback(() => {
    return execute(true);
  }, [execute]);

  // Mutate function for optimistic updates
  const mutate = useCallback(
    (data: T | ((prev: T | null) => T)) => {
      setState(prev => ({
        ...prev,
        data: typeof data === 'function' ? (data as (prev: T | null) => T)(prev.data) : data,
      }));

      // Update cache
      const cacheKey = getCacheKey();
      const newData = typeof data === 'function' ? (data as (prev: T | null) => T)(state.data) : data;
      apiCache.set(cacheKey, {
        data: newData,
        timestamp: Date.now(),
        staleTime,
      });
    },
    [getCacheKey, staleTime, state.data]
  );

  // Effect for initial fetch
  useEffect(() => {
    if (immediate && refetchOnMount) {
      execute();
    }
  }, [immediate, refetchOnMount, execute]);

  // Effect for window focus refetch
  useEffect(() => {
    if (!refetchOnWindowFocus) return;

    const handleFocus = () => {
      const cacheKey = getCacheKey();
      const cached = apiCache.get(cacheKey) as CacheEntry<T> | undefined;
      if (cached && isStale(cached)) {
        execute();
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refetchOnWindowFocus, getCacheKey, isStale, execute]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (requestIdRef.current) {
        apiClient.cancelRequest(requestIdRef.current);
      }
    };
  }, []);

  return {
    ...state,
    refetch,
    mutate,
  };
}

// Hook for mutations
export function useApiMutation<TData, TVariables = unknown>(
  endpoint: string,
  options: {
    onSuccess?: (data: TData) => void;
    onError?: (error: Error) => void;
    onSettled?: (data: TData | null, error: Error | null) => void;
  } = {}
) {
  const { onSuccess, onError, onSettled } = options;
  
  const [state, setState] = useState<{
    data: TData | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const mutate = useCallback(
    async (variables: TVariables, method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST') => {
      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const response = await apiClient.request<TData>(endpoint, {
          method,
          body: variables,
        });

        if (!response.success) {
          throw new Error(response.error.message);
        }

        const data = response.data;
        setState({ data, loading: false, error: null });
        onSuccess?.(data);
        onSettled?.(data, null);
        return data;
      } catch (error) {
        const apiError = error instanceof Error ? error : new Error('Unknown error');
        setState(prev => ({ ...prev, loading: false, error: apiError }));
        onError?.(apiError);
        onSettled?.(null, apiError);
        throw apiError;
      }
    },
    [endpoint, onSuccess, onError, onSettled]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    mutate,
    reset,
  };
}

// Hook for streaming data
export function useApiStream<T>(
  endpoint: string,
  options: {
    onMessage?: (data: T) => void;
    onError?: (error: Error) => void;
    onComplete?: () => void;
    autoConnect?: boolean;
  } = {}
) {
  const { onMessage, onError, onComplete, autoConnect = false } = options;
  
  const [state, setState] = useState<{
    connected: boolean;
    connecting: boolean;
    error: Error | null;
    messages: T[];
  }>({
    connected: false,
    connecting: false,
    error: null,
    messages: [],
  });

  const connectionRef = useRef<boolean>(false);

  const connect = useCallback(async () => {
    if (connectionRef.current) return;

    setState(prev => ({ ...prev, connecting: true, error: null }));
    connectionRef.current = true;

    try {
      await apiClient.stream<T>(
        endpoint,
        {},
        (data) => {
          setState(prev => ({ ...prev, messages: [...prev.messages, data] }));
          onMessage?.(data);
        },
        (error) => {
          setState(prev => ({ ...prev, error, connected: false, connecting: false }));
          connectionRef.current = false;
          onError?.(error);
        },
        () => {
          setState(prev => ({ ...prev, connected: false, connecting: false }));
          connectionRef.current = false;
          onComplete?.();
        }
      );

      setState(prev => ({ ...prev, connected: true, connecting: false }));
    } catch (error) {
      const apiError = error instanceof Error ? error : new Error('Connection failed');
      setState(prev => ({ ...prev, error: apiError, connecting: false }));
      connectionRef.current = false;
      onError?.(apiError);
    }
  }, [endpoint, onMessage, onError, onComplete]);

  const disconnect = useCallback(() => {
    connectionRef.current = false;
    setState(prev => ({ ...prev, connected: false, connecting: false }));
  }, []);

  const clearMessages = useCallback(() => {
    setState(prev => ({ ...prev, messages: [] }));
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    clearMessages,
  };
}

// Hook for paginated data
export function useApiPagination<T>(
  endpoint: string,
  options: {
    limit?: number;
    onSuccess?: (data: T[]) => void;
    onError?: (error: Error) => void;
  } = {}
) {
  const { limit = 10, onSuccess, onError } = options;
  
  const [state, setState] = useState<{
    data: T[];
    loading: boolean;
    error: Error | null;
    hasMore: boolean;
    page: number;
  }>({
    data: [],
    loading: false,
    error: null,
    hasMore: true,
    page: 1,
  });

  const loadMore = useCallback(async () => {
    if (state.loading || !state.hasMore) return;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiClient.get<{
        items: T[];
        hasMore: boolean;
        total: number;
      }>(`${endpoint}?page=${state.page}&limit=${limit}`);

      if (!response.success) {
        throw new Error(response.error.message);
      }

      const { items, hasMore } = response.data;

      setState(prev => ({
        ...prev,
        data: [...prev.data, ...items],
        loading: false,
        hasMore,
        page: prev.page + 1,
      }));

      onSuccess?.(items);
    } catch (error) {
      const apiError = error instanceof Error ? error : new Error('Unknown error');
      setState(prev => ({ ...prev, loading: false, error: apiError }));
      onError?.(apiError);
    }
  }, [endpoint, limit, state.loading, state.hasMore, state.page, onSuccess, onError]);

  const reset = useCallback(() => {
    setState({
      data: [],
      loading: false,
      error: null,
      hasMore: true,
      page: 1,
    });
  }, []);

  return {
    ...state,
    loadMore,
    reset,
  };
}

// Clear cache utility
export function clearApiCache(pattern?: string) {
  if (pattern) {
    const regex = new RegExp(pattern);
    for (const [key] of apiCache.entries()) {
      if (regex.test(key)) {
        apiCache.delete(key);
      }
    }
  } else {
    apiCache.clear();
  }
}

// Preload data utility
export function preloadApiData<T>(endpoint: string, staleTime = 5 * 60 * 1000) {
  const cacheKey = endpoint;
  
  return apiClient.get<T>(endpoint).then(response => {
    if (response.success) {
      apiCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now(),
        staleTime,
      });
    }
  });
}
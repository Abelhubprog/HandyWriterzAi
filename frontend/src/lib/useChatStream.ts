'use client';

import { useCallback, useRef, useState } from 'react';

interface StreamOptions {
  onToken?: (token: string) => void;
  onComplete?: (fullText: string) => void;
  onError?: (error: Error) => void;
}

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const accumulatedTextRef = useRef<string>('');

  const startStream = useCallback(async (
    url: string,
    payload: any,
    options: StreamOptions = {}
  ) => {
    const { onToken, onComplete, onError } = options;

    // Abort any existing stream
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Reset state
    accumulatedTextRef.current = '';
    setIsStreaming(true);
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });

        // Handle SSE format
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);

            if (data === '[DONE]') {
              continue;
            }

            try {
              const parsed = JSON.parse(data);
              const token = parsed.token || parsed.content || parsed.text || '';

              if (token) {
                accumulatedTextRef.current += token;
                onToken?.(token);
              }
            } catch (e) {
              // If not JSON, treat as plain text
              accumulatedTextRef.current += data;
              onToken?.(data);
            }
          }
        }
      }

      onComplete?.(accumulatedTextRef.current);
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        onError?.(error);
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, []);

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
    }
  }, []);

  return {
    isStreaming,
    startStream,
    stopStream,
  };
}

import { useState, useEffect, useRef } from 'react';
import { create } from 'zustand';

export interface TimelineEvent {
  type: string;
  name?: string;
  tokens?: number;
  text?: string;
  cost?: number;
  [key: string]: any;
}

interface StreamState {
  events: TimelineEvent[];
  streamingText: string;
  reasoningText: string;
  totalCost: number;
  plagiarismScore: number;
  qualityScore: number;
  derivatives: { kind: string; url: string }[];
  addEvent: (event: TimelineEvent) => void;
  appendStreamingText: (text: string) => void;
  appendReasoningText: (text: string) => void;
  setMetrics: (metrics: { cost?: number; plagiarismScore?: number; qualityScore?: number }) => void;
  addDerivative: (derivative: { kind: string; url: string }) => void;
  reset: () => void;
}

const useStreamStore = create<StreamState>((set) => ({
  events: [],
  streamingText: '',
  reasoningText: '',
  totalCost: 0,
  plagiarismScore: 0,
  qualityScore: 0,
  derivatives: [],
  addEvent: (event) => set((state) => ({ events: [...state.events, event] })),
  appendStreamingText: (text) => set((state) => ({ streamingText: state.streamingText + text })),
  appendReasoningText: (text) => set((state) => ({ reasoningText: state.reasoningText + text })),
  setMetrics: (metrics) => set((state) => ({ ...state, ...metrics })),
  addDerivative: (derivative) => set((state) => ({ derivatives: [...state.derivatives, derivative] })),
  reset: () => set({
    events: [],
    streamingText: '',
    reasoningText: '',
    totalCost: 0,
    plagiarismScore: 0,
    qualityScore: 0,
    derivatives: []
  })
}));

interface UseStreamOptions {
  onMessage?: (event: TimelineEvent) => void;
  onClose?: () => void;
}

export function useStream(traceId: string | null, options?: UseStreamOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const optionsRef = useRef(options);
  const store = useStreamStore();

  // Update options ref
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  useEffect(() => {
    // Clean up previous connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    // Reset store for new conversation
    store.reset();

    if (traceId) {
      const sseUrl = `/api/chat/stream/${traceId}`;
      const eventSource = new EventSource(sseUrl);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
        console.log(`SSE connection established for trace: ${traceId}`);
      };

      eventSource.onerror = (error) => {
        console.error('SSE error:', error);
        setIsConnected(false);
        eventSource.close();
        if (optionsRef.current?.onClose) optionsRef.current.onClose();
      };

      const messageHandler = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          
          if (optionsRef.current?.onMessage) {
            optionsRef.current.onMessage(data);
          }

          switch (data.type) {
            case 'content':
              if (data.text) store.appendStreamingText(data.text);
              break;
            case 'thinking':
              if (data.text) store.appendReasoningText(data.text);
              break;
            case 'metrics':
              store.setMetrics({
                cost: data.cost,
                plagiarismScore: data.plagiarism_score,
                qualityScore: data.quality_score,
              });
              break;
            case 'derivative_ready':
              if (data.kind && data.url) {
                store.addDerivative({ kind: data.kind, url: data.url });
              }
              break;
            case 'done':
              eventSource.close();
              setIsConnected(false);
              if (optionsRef.current?.onClose) optionsRef.current.onClose();
              break;
            default:
              store.addEvent(data);
          }
        } catch (e) {
          console.error('Failed to parse SSE message:', e);
        }
      };

      eventSource.addEventListener('message', messageHandler);
      
      return () => {
        eventSource.removeEventListener('message', messageHandler);
        eventSource.close();
        setIsConnected(false);
      };
    }
  }, [traceId]);

  return {
    isConnected,
    ...useStreamStore(),
  };
}
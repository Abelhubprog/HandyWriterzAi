import { useState, useEffect, useRef } from 'react';
import { create } from 'zustand';

export interface TimelineEvent {
  type: string;
  name?: string;
  node?: string;
  progress?: number;
  delta?: string;
  text?: string;
  cost?: number;
  ts?: string;
  [key: string]: any;
}

interface SourceItem {
  id: string;
  title: string;
  url?: string;
  author?: string;
  year?: number;
  confidence?: number;
  kind?: string;
  snippet?: string;
}

interface StreamState {
  events: TimelineEvent[];
  streamingText: string;
  reasoningText: string;
  totalCost: number;
  plagiarismScore: number;
  qualityScore: number;
  derivatives: { kind: string; url: string }[];
  sources: Record<string, SourceItem>;
  addEvent: (event: TimelineEvent) => void;
  appendStreamingText: (text: string) => void;
  appendReasoningText: (text: string) => void;
  setMetrics: (metrics: { cost?: number; plagiarismScore?: number; qualityScore?: number }) => void;
  addDerivative: (derivative: { kind: string; url: string }) => void;
  setSourcesSnapshot: (sources: SourceItem[]) => void;
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
  sources: {},
  addEvent: (event) => set((state) => {
    const next = [...state.events, event];
    return { events: next.slice(-300) };
  }),
  appendStreamingText: (text) => set((state) => ({ streamingText: state.streamingText + text })),
  appendReasoningText: (text) => set((state) => ({ reasoningText: state.reasoningText + text })),
  setMetrics: (metrics) => set((state) => ({ ...state, ...metrics })),
  addDerivative: (derivative) => set((state) => ({ derivatives: [...state.derivatives, derivative] })),
  setSourcesSnapshot: (sources) =>
    set(() => ({
      sources: (sources || []).reduce((acc, s) => {
        if (s.id) acc[s.id] = s;
        return acc;
      }, {} as Record<string, SourceItem>),
    })),
  reset: () => set({
    events: [],
    streamingText: '',
    reasoningText: '',
    totalCost: 0,
    plagiarismScore: 0,
    qualityScore: 0,
    derivatives: [],
    sources: {}
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

  // Token coalescing buffer for smooth rendering
  const bufferRef = useRef<string>('');
  const rafIdRef = useRef<number | null>(null);

  const flushBuffer = () => {
    if (bufferRef.current.length > 0) {
      store.appendStreamingText(bufferRef.current);
      bufferRef.current = '';
    }
    rafIdRef.current = null;
  };

  const scheduleFlush = () => {
    if (rafIdRef.current == null) {
      rafIdRef.current = typeof window !== 'undefined' ? window.requestAnimationFrame(flushBuffer) : null;
    }
  };

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
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const sseUrl = `${backendUrl}/api/stream/${traceId}`;
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
            case 'planning_started':
              store.addEvent({ type: 'planning_started', ts: data.ts });
              break;
            case 'search_started':
            case 'search_progress':
              store.addEvent({
                type: data.type,
                node: 'search',
                progress: data.progress ?? undefined,
                ts: data.ts
              });
              break;
            case 'sources_update':
              if (Array.isArray(data.sources)) {
                store.setSourcesSnapshot(data.sources);
              }
              store.addEvent({ type: 'sources_update', ts: data.ts, count: Array.isArray(data.sources) ? data.sources.length : 0 });
              break;
            case 'verify_started':
              store.addEvent({ type: 'verify_started', node: 'verify', ts: data.ts });
              break;
            case 'writer_started':
              store.addEvent({ type: 'writer_started', node: 'writer', ts: data.ts });
              break;
            case 'token':
              if (data.delta) {
                bufferRef.current += data.delta;
                scheduleFlush();
              }
              break;
            case 'content':
              if (data.text) {
                bufferRef.current += data.text;
                scheduleFlush();
              }
              break;
            case 'evaluator_started':
              store.addEvent({ type: 'evaluator_started', node: 'evaluator', ts: data.ts });
              break;
            case 'evaluator_feedback':
              store.addEvent({ type: 'evaluator_feedback', node: 'evaluator', text: data.message, ts: data.ts });
              break;
            case 'formatter_started':
              store.addEvent({ type: 'formatter_started', node: 'formatter', ts: data.ts });
              break;
            case 'cost_update':
              store.setMetrics({ cost: data.estimated_cost_usd });
              store.addEvent({ type: 'cost_update', cost: data.estimated_cost_usd, ts: data.ts });
              break;
            case 'workflow_finished':
            case 'done':
              flushBuffer();
              store.addEvent({ type: data.type, ts: data.ts });
              eventSource.close();
              setIsConnected(false);
              if (optionsRef.current?.onClose) optionsRef.current.onClose();
              break;
            case 'error':
              store.addEvent({ type: 'error', text: data.message, ts: data.ts });
              break;
            // Back-compat legacy events
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
            default:
              store.addEvent(data as TimelineEvent);
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

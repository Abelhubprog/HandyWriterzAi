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
  lastHeartbeatTs: number | null;
  lastError: string | null;
  addEvent: (event: TimelineEvent) => void;
  appendStreamingText: (text: string) => void;
  appendReasoningText: (text: string) => void;
  setMetrics: (metrics: { cost?: number; plagiarismScore?: number; qualityScore?: number }) => void;
  addDerivative: (derivative: { kind: string; url: string }) => void;
  setSourcesSnapshot: (sources: SourceItem[]) => void;
  setHeartbeat: (ts: number) => void;
  setError: (message: string | null) => void;
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
  lastHeartbeatTs: null,
  lastError: null,
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
  setHeartbeat: (ts) => set(() => ({ lastHeartbeatTs: ts })),
  setError: (message) => set(() => ({ lastError: message })),
  reset: () => set({
    events: [],
    streamingText: '',
    reasoningText: '',
    totalCost: 0,
    plagiarismScore: 0,
    qualityScore: 0,
    derivatives: [],
    sources: {},
    lastHeartbeatTs: null,
    lastError: null,
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
      // Connect to unified SSE stream for this conversation
      const sseUrl = `/api/stream/${traceId}`;
      // Prefetch replay snapshot to seed timeline before new events arrive
      (async () => {
        try {
          const res = await fetch(`${sseUrl}/replay`)
          if (res.ok) {
            const data = await res.json()
            const evts: any[] = Array.isArray(data?.events) ? data.events : []
            for (const evt of evts) {
              if (evt && typeof evt === 'object') {
                // Normalize alternate keys for safety
                if (evt.content && !evt.text) evt.text = evt.content
                if (evt.token && !evt.delta) evt.delta = evt.token
                store.addEvent(evt as any)
              }
            }
          }
        } catch (e) {
          // silent fail to avoid blocking stream
        }
      })();
      const eventSource = new EventSource(sseUrl);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
        console.log(`SSE connection established for trace: ${traceId}`);
        store.setHeartbeat(Date.now());
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

          // Normalize alternate keys for safety
          if (data.content && !data.text) {
            data.text = data.content;
          }
          if (data.token && !data.delta) {
            data.delta = data.token;
          }

          switch (data.type) {
            case 'agent:start':
            case 'agent:tool':
            case 'agent:result': {
              // message may be a JSON string with {agent,...}
              let details: any = {}
              try {
                if (typeof data.message === 'string') details = JSON.parse(data.message)
              } catch {}
              store.addEvent({ type: data.type, ...details, ts: data.ts })
              break;
            }
            case 'connected':
              store.setHeartbeat(Date.now());
              break;
            case 'heartbeat':
              store.setHeartbeat(Date.now());
              break;

            // Accept generic progress:* events as timeline entries
            default:
              if (typeof data.type === 'string' && data.type.startsWith('progress:')) {
                store.addEvent({ type: data.type, ...data, ts: data.ts });
                break;
              }
              // fallthrough to specific handlers
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
            case 'node_start':
              store.addEvent({ type: 'node_start', node: data.node, ts: data.ts });
              break;
            case 'node_end':
              store.addEvent({ type: 'node_end', node: data.node, ts: data.ts });
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
            case 'progress': {
              // Accept numeric progress; if <=1 treat as ratio, if <=100 treat as percent
              const p = typeof data.progress === 'number' ? data.progress : undefined;
              const pct = p != null ? (p <= 1 ? Math.round(p * 100) : (p <= 100 ? Math.round(p) : undefined)) : undefined;
              store.addEvent({ type: 'progress', node: data.node, progress: pct, progressRaw: p, ts: data.ts });
              break;
            }
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
              store.addEvent({ type: 'error', text: data.message || data.error, ts: data.ts });
              store.setError(data.message || data.error || 'Streaming error');
              eventSource.close();
              setIsConnected(false);
              if (optionsRef.current?.onClose) optionsRef.current.onClose();
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
            case 'file_processing':
              store.addEvent({ type: 'file_processing', status: data.status, file_id: data.file_id, ts: data.ts });
              break;
            case 'files:status':
              store.addEvent({ type: 'files:status', status: data.status, extra: data.extra, ts: data.ts });
              break;

            // Unknown → keep timeline
            // default handled above
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

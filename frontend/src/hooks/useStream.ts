import { useState, useEffect, useRef } from 'react';
import { create } from 'zustand';

interface TimelineEvent {
  type: string;
  name?: string;
  tokens?: number;
  [key: string]: any;
}

interface StreamState {
  timeline: TimelineEvent[];
  addEvent: (event: TimelineEvent) => void;
}

const useTimelineStore = create<StreamState>((set) => ({
  timeline: [],
  addEvent: (event) => set((state) => ({ timeline: [...state.timeline, event] })),
}));

export function useStream(traceId: string | null) {
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const { addEvent } = useTimelineStore();

  useEffect(() => {
    if (traceId) {
      const socket = new WebSocket(`/ws/${traceId}`);
      ws.current = socket;

      socket.onopen = () => setIsConnected(true);
      socket.onclose = () => setIsConnected(false);
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        addEvent(data);
      };

      return () => {
        socket.close();
      };
    }
  }, [traceId, addEvent]);

  return { isConnected, timeline: useTimelineStore((state) => state.timeline) };
}

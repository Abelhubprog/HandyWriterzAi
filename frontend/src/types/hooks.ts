import { MutableRefObject } from 'react';

// Hook Return Types
export interface UseAsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  execute: (...args: unknown[]) => Promise<T>;
  reset: () => void;
}

export interface UseAsyncOptions {
  immediate?: boolean;
  onSuccess?: (data: unknown) => void;
  onError?: (error: Error) => void;
  retries?: number;
  retryDelay?: number;
}

export interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  mutate: (data: T | ((prev: T | null) => T)) => void;
}

export interface UseApiOptions<T> {
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  retries?: number;
  retryDelay?: number;
  staleTime?: number;
  cacheTime?: number;
  refetchOnWindowFocus?: boolean;
  refetchOnMount?: boolean;
}

export interface UseLocalStorageState<T> {
  value: T;
  setValue: (value: T | ((prev: T) => T)) => void;
  removeValue: () => void;
}

export interface UseLocalStorageOptions<T> {
  serializer?: {
    read: (value: string) => T;
    write: (value: T) => string;
  };
  onError?: (error: Error) => void;
}

export interface UseSessionStorageState<T> {
  value: T;
  setValue: (value: T | ((prev: T) => T)) => void;
  removeValue: () => void;
}

export interface UseDebounceOptions {
  leading?: boolean;
  trailing?: boolean;
  maxWait?: number;
}

export interface UseThrottleOptions {
  leading?: boolean;
  trailing?: boolean;
}

export interface UseIntersectionObserverOptions {
  threshold?: number | number[];
  root?: Element | null;
  rootMargin?: string;
  triggerOnce?: boolean;
}

export interface UseIntersectionObserverState {
  isIntersecting: boolean;
  entry: IntersectionObserverEntry | null;
  ref: MutableRefObject<Element | null>;
}

export interface UseMediaQueryState {
  matches: boolean;
  media: string;
}

export interface UseElementSizeState {
  width: number;
  height: number;
  ref: MutableRefObject<Element | null>;
}

export interface UseScrollState {
  x: number;
  y: number;
  isScrolling: boolean;
  direction: {
    x: 'left' | 'right' | null;
    y: 'up' | 'down' | null;
  };
}

export interface UseClipboardState {
  value: string;
  copy: (text: string) => Promise<void>;
  copied: boolean;
  error: Error | null;
}

export interface UseClipboardOptions {
  timeout?: number;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export interface UseGeolocationState {
  position: GeolocationPosition | null;
  error: GeolocationPositionError | null;
  loading: boolean;
  getCurrentPosition: () => Promise<GeolocationPosition>;
}

export interface UseGeolocationOptions {
  enableHighAccuracy?: boolean;
  timeout?: number;
  maximumAge?: number;
}

export interface UseNetworkState {
  online: boolean;
  effectiveType: string;
  saveData: boolean;
  downlink: number;
  rtt: number;
}

export interface UseBatteryState {
  charging: boolean;
  chargingTime: number;
  dischargingTime: number;
  level: number;
  supported: boolean;
}

export interface UseKeyboardState {
  pressed: Set<string>;
  isPressed: (key: string) => boolean;
  combinations: Map<string, boolean>;
  isCombinationPressed: (combination: string) => boolean;
}

export interface UseKeyboardOptions {
  preventDefault?: boolean;
  stopPropagation?: boolean;
  target?: Element | Window;
}

export interface UseHoverState {
  isHovered: boolean;
  ref: MutableRefObject<Element | null>;
}

export interface UseFocusState {
  isFocused: boolean;
  ref: MutableRefObject<Element | null>;
}

export interface UseClickAwayState {
  ref: MutableRefObject<Element | null>;
}

export interface UseFormState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isSubmitting: boolean;
  isDirty: boolean;
  setValue: (field: keyof T, value: T[keyof T]) => void;
  setError: (field: keyof T, error: string) => void;
  setTouched: (field: keyof T, touched: boolean) => void;
  handleSubmit: (onSubmit: (values: T) => void | Promise<void>) => (event: React.FormEvent) => void;
  reset: () => void;
}

export interface UseFormOptions<T> {
  initialValues: T;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
  onSubmit?: (values: T) => void | Promise<void>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
}

export interface UseSearchState<T> {
  query: string;
  results: T[];
  loading: boolean;
  error: Error | null;
  setQuery: (query: string) => void;
  search: (query: string) => Promise<T[]>;
  reset: () => void;
}

export interface UseSearchOptions<T> {
  searchFn: (query: string) => Promise<T[]>;
  debounceMs?: number;
  minQueryLength?: number;
  maxResults?: number;
  cacheResults?: boolean;
}

export interface UsePaginationState {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  setPage: (page: number) => void;
  setLimit: (limit: number) => void;
  nextPage: () => void;
  previousPage: () => void;
  firstPage: () => void;
  lastPage: () => void;
}

export interface UsePaginationOptions {
  initialPage?: number;
  initialLimit?: number;
  total: number;
  onPageChange?: (page: number) => void;
  onLimitChange?: (limit: number) => void;
}

export interface UseInfiniteScrollState<T> {
  items: T[];
  hasMore: boolean;
  loading: boolean;
  error: Error | null;
  loadMore: () => Promise<void>;
  reset: () => void;
}

export interface UseInfiniteScrollOptions<T> {
  fetchFn: (page: number, limit: number) => Promise<{ items: T[]; hasMore: boolean }>;
  limit?: number;
  threshold?: number;
  onError?: (error: Error) => void;
}

export interface UseWebSocketState {
  readyState: number;
  lastMessage: MessageEvent | null;
  connectionStatus: 'Connecting' | 'Open' | 'Closing' | 'Closed' | 'Uninstantiated';
  send: (message: string | ArrayBuffer | Blob) => void;
  connect: () => void;
  disconnect: () => void;
}

export interface UseWebSocketOptions {
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onMessage?: (event: MessageEvent) => void;
  onError?: (event: Event) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
  reconnectAttempts?: number;
}

export interface UseFileUploadState {
  files: File[];
  uploading: boolean;
  progress: number;
  error: Error | null;
  uploadedFiles: FileUpload[];
  addFiles: (files: File[]) => void;
  removeFile: (index: number) => void;
  upload: () => Promise<void>;
  reset: () => void;
}

export interface UseFileUploadOptions {
  uploadFn: (files: File[], onProgress?: (progress: number) => void) => Promise<FileUpload[]>;
  maxSize?: number;
  maxFiles?: number;
  accept?: string;
  onSuccess?: (files: FileUpload[]) => void;
  onError?: (error: Error) => void;
}

export interface UseAudioRecordingState {
  recording: boolean;
  paused: boolean;
  duration: number;
  audioBlob: Blob | null;
  audioUrl: string | null;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  pauseRecording: () => void;
  resumeRecording: () => void;
  reset: () => void;
}

export interface UseAudioRecordingOptions {
  onStart?: () => void;
  onStop?: (blob: Blob) => void;
  onError?: (error: Error) => void;
  maxDuration?: number;
  mimeType?: string;
}

export interface UseScreenCaptureState {
  capturing: boolean;
  stream: MediaStream | null;
  error: Error | null;
  startCapture: () => Promise<void>;
  stopCapture: () => void;
}

export interface UseScreenCaptureOptions {
  onStart?: (stream: MediaStream) => void;
  onStop?: () => void;
  onError?: (error: Error) => void;
  video?: boolean;
  audio?: boolean;
}

export interface UseNotificationState {
  permission: NotificationPermission;
  notify: (title: string, options?: NotificationOptions) => Promise<void>;
  requestPermission: () => Promise<NotificationPermission>;
}

export interface UseNotificationOptions {
  onShow?: (notification: Notification) => void;
  onClick?: (notification: Notification) => void;
  onClose?: (notification: Notification) => void;
  onError?: (error: Error) => void;
}
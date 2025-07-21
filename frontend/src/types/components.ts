import { ReactNode } from 'react';
import { VariantProps } from 'class-variance-authority';

// Base Component Props
export interface BaseProps {
  className?: string;
  children?: ReactNode;
  'data-testid'?: string;
}

// Button Component Types
export interface ButtonProps extends BaseProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  asChild?: boolean;
}

// Input Component Types
export interface InputProps extends BaseProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'search' | 'tel' | 'url';
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  description?: string;
}

// Select Component Types
export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
  description?: string;
}

export interface SelectProps extends BaseProps {
  options: SelectOption[];
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  description?: string;
  multiple?: boolean;
}

// Textarea Component Types
export interface TextareaProps extends BaseProps {
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  description?: string;
  rows?: number;
  autoResize?: boolean;
  maxLength?: number;
}

// Modal Component Types
export interface ModalProps extends BaseProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  title?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  closable?: boolean;
  overlay?: boolean;
  trigger?: ReactNode;
}

// Loading Component Types
export interface LoadingProps extends BaseProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'spinner' | 'dots' | 'pulse' | 'skeleton';
  text?: string;
  fullscreen?: boolean;
  overlay?: boolean;
}

// Error Component Types
export interface ErrorProps extends BaseProps {
  error: Error | string;
  title?: string;
  description?: string;
  onRetry?: () => void;
  showDetails?: boolean;
  variant?: 'default' | 'destructive' | 'warning';
}

// Toast Component Types
export interface ToastProps {
  id: string;
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success' | 'warning' | 'info';
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  onClose?: () => void;
}

// Tooltip Component Types
export interface TooltipProps extends BaseProps {
  content: ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
  delay?: number;
  disabled?: boolean;
  trigger?: ReactNode;
}

// Card Component Types
export interface CardProps extends BaseProps {
  variant?: 'default' | 'elevated' | 'outline' | 'ghost';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  header?: ReactNode;
  footer?: ReactNode;
  loading?: boolean;
  error?: string;
}

// Badge Component Types
export interface BadgeProps extends BaseProps {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning' | 'info';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  count?: number;
}

// Avatar Component Types
export interface AvatarProps extends BaseProps {
  src?: string;
  alt?: string;
  fallback?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'circular' | 'rounded' | 'square';
  status?: 'online' | 'offline' | 'away' | 'busy';
}

// Navigation Component Types
export interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  icon?: ReactNode;
  badge?: string | number;
  disabled?: boolean;
  children?: NavigationItem[];
}

export interface NavigationProps extends BaseProps {
  items: NavigationItem[];
  activeId?: string;
  onNavigate?: (item: NavigationItem) => void;
  collapsible?: boolean;
  collapsed?: boolean;
  onCollapseChange?: (collapsed: boolean) => void;
}

// Table Component Types
export interface TableColumn<T = unknown> {
  id: string;
  label: string;
  sortable?: boolean;
  width?: string | number;
  minWidth?: string | number;
  maxWidth?: string | number;
  align?: 'left' | 'center' | 'right';
  render?: (value: unknown, row: T, index: number) => ReactNode;
  accessor?: keyof T | ((row: T) => unknown);
}

export interface TableProps<T = unknown> extends BaseProps {
  columns: TableColumn<T>[];
  data: T[];
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  onSort?: (column: string, order: 'asc' | 'desc') => void;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    onPageChange: (page: number) => void;
    onLimitChange: (limit: number) => void;
  };
  selection?: {
    selectedRows: string[];
    onSelectionChange: (selectedRows: string[]) => void;
    getRowId: (row: T) => string;
  };
}

// Form Component Types
export interface FormFieldProps extends BaseProps {
  name: string;
  label?: string;
  description?: string;
  required?: boolean;
  error?: string;
  disabled?: boolean;
}

export interface FormProps extends BaseProps {
  onSubmit?: (data: Record<string, unknown>) => void | Promise<void>;
  onReset?: () => void;
  loading?: boolean;
  disabled?: boolean;
  schema?: any; // Zod schema
  defaultValues?: Record<string, unknown>;
}

// Chat Component Types
export interface ChatMessageProps extends BaseProps {
  message: ChatMessage;
  isOwn?: boolean;
  showAvatar?: boolean;
  showTimestamp?: boolean;
  onEdit?: (messageId: string, content: string) => void;
  onDelete?: (messageId: string) => void;
  onReply?: (messageId: string) => void;
}

export interface ChatInputProps extends BaseProps {
  value?: string;
  onChange?: (value: string) => void;
  onSubmit?: (message: string) => void;
  onFileUpload?: (files: File[]) => void;
  loading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
  allowFileUpload?: boolean;
  allowVoiceInput?: boolean;
  autoFocus?: boolean;
}

// File Upload Component Types
export interface FileUploadProps extends BaseProps {
  accept?: string;
  multiple?: boolean;
  maxSize?: number;
  maxFiles?: number;
  onUpload?: (files: File[]) => void;
  onProgress?: (progress: number) => void;
  onError?: (error: string) => void;
  onComplete?: (files: FileUpload[]) => void;
  disabled?: boolean;
  dragAndDrop?: boolean;
  preview?: boolean;
}

// Search Component Types
export interface SearchProps extends BaseProps {
  value?: string;
  onChange?: (value: string) => void;
  onSearch?: (query: string) => void;
  placeholder?: string;
  suggestions?: string[];
  loading?: boolean;
  disabled?: boolean;
  debounceMs?: number;
  showClearButton?: boolean;
}

// Data Visualization Component Types
export interface ChartProps extends BaseProps {
  data: unknown[];
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'radar' | 'scatter';
  options?: Record<string, unknown>;
  loading?: boolean;
  error?: string;
  height?: number;
  width?: number;
}

// Advanced Component Types
export interface VirtualizedListProps<T = unknown> extends BaseProps {
  items: T[];
  itemHeight: number;
  renderItem: (item: T, index: number) => ReactNode;
  overscan?: number;
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  onEndReached?: () => void;
  onRefresh?: () => void;
}

export interface InfiniteScrollProps extends BaseProps {
  hasMore: boolean;
  loading: boolean;
  onLoadMore: () => void;
  loader?: ReactNode;
  endMessage?: ReactNode;
  threshold?: number;
}

// Layout Component Types
export interface LayoutProps extends BaseProps {
  sidebar?: ReactNode;
  header?: ReactNode;
  footer?: ReactNode;
  sidebarCollapsed?: boolean;
  onSidebarToggle?: () => void;
}

export interface GridProps extends BaseProps {
  columns?: number | Record<string, number>;
  gap?: number | string;
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
}

export interface StackProps extends BaseProps {
  direction?: 'horizontal' | 'vertical';
  spacing?: number | string;
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  wrap?: boolean;
}
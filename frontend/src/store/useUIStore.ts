import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success';
  duration?: number;
}

export interface Modal {
  id: string;
  type: 'export' | 'settings' | 'file-preview' | 'reasoning' | 'share';
  data?: any;
}

interface UIState {
  // Navigation
  sidebarCollapsed: boolean;
  currentPage: string;
  
  // Modals
  activeModals: Modal[];
  
  // Toasts
  toasts: Toast[];
  
  // Loading states
  globalLoading: boolean;
  loadingStates: Record<string, boolean>;
  
  // Export states
  showExportModal: boolean;
  exportProgress?: {
    format: string;
    progress: number;
    status: string;
  };
  
  // File upload states
  isDraggingFiles: boolean;
  uploadProgress: Record<string, number>;
  
  // Actions
  setSidebarCollapsed: (collapsed: boolean) => void;
  setCurrentPage: (page: string) => void;
  
  // Modal management
  openModal: (modal: Omit<Modal, 'id'>) => string;
  closeModal: (id: string) => void;
  closeAllModals: () => void;
  
  // Toast management  
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  
  // Loading management
  setGlobalLoading: (loading: boolean) => void;
  setLoading: (key: string, loading: boolean) => void;
  isLoading: (key: string) => boolean;
  
  // Export management
  setShowExportModal: (show: boolean) => void;
  setExportProgress: (progress: UIState['exportProgress']) => void;
  
  // File upload management
  setIsDraggingFiles: (dragging: boolean) => void;
  setUploadProgress: (fileId: string, progress: number) => void;
  removeUploadProgress: (fileId: string) => void;
}

export const useUIStore = create<UIState>()(
  subscribeWithSelector(
    persist(
      immer((set, get) => ({
        sidebarCollapsed: false,
        currentPage: 'chat',
        activeModals: [],
        toasts: [],
        globalLoading: false,
        loadingStates: {},
        showExportModal: false,
        isDraggingFiles: false,
        uploadProgress: {},
        
        setSidebarCollapsed: (collapsed) => {
          set((state) => {
            state.sidebarCollapsed = collapsed;
          });
        },
        
        setCurrentPage: (page) => {
          set((state) => {
            state.currentPage = page;
          });
        },
        
        openModal: (modalData) => {
          const id = `modal-${Date.now()}-${Math.random()}`;
          const modal: Modal = { ...modalData, id };
          
          set((state) => {
            state.activeModals.push(modal);
          });
          
          return id;
        },
        
        closeModal: (id) => {
          set((state) => {
            state.activeModals = state.activeModals.filter(m => m.id !== id);
          });
        },
        
        closeAllModals: () => {
          set((state) => {
            state.activeModals = [];
          });
        },
        
        addToast: (toastData) => {
          const id = `toast-${Date.now()}-${Math.random()}`;
          const toast: Toast = { 
            ...toastData, 
            id,
            duration: toastData.duration ?? 5000 
          };
          
          set((state) => {
            state.toasts.push(toast);
          });
          
          // Auto-remove toast after duration
          if (toast.duration > 0) {
            setTimeout(() => {
              get().removeToast(id);
            }, toast.duration);
          }
          
          return id;
        },
        
        removeToast: (id) => {
          set((state) => {
            state.toasts = state.toasts.filter(t => t.id !== id);
          });
        },
        
        clearToasts: () => {
          set((state) => {
            state.toasts = [];
          });
        },
        
        setGlobalLoading: (loading) => {
          set((state) => {
            state.globalLoading = loading;
          });
        },
        
        setLoading: (key, loading) => {
          set((state) => {
            if (loading) {
              state.loadingStates[key] = true;
            } else {
              delete state.loadingStates[key];
            }
          });
        },
        
        isLoading: (key) => {
          return get().loadingStates[key] || false;
        },
        
        setShowExportModal: (show) => {
          set((state) => {
            state.showExportModal = show;
          });
        },
        
        setExportProgress: (progress) => {
          set((state) => {
            state.exportProgress = progress;
          });
        },
        
        setIsDraggingFiles: (dragging) => {
          set((state) => {
            state.isDraggingFiles = dragging;
          });
        },
        
        setUploadProgress: (fileId, progress) => {
          set((state) => {
            state.uploadProgress[fileId] = progress;
          });
        },
        
        removeUploadProgress: (fileId) => {
          set((state) => {
            delete state.uploadProgress[fileId];
          });
        },
      })),
      {
        name: 'handywriterz-ui-store',
        version: 1,
        partialize: (state) => ({
          sidebarCollapsed: state.sidebarCollapsed,
          currentPage: state.currentPage,
          // Don't persist ephemeral UI states
        }),
      }
    )
  )
);

// Convenience hooks
export const useModals = () => useUIStore((state) => ({
  activeModals: state.activeModals,
  openModal: state.openModal,
  closeModal: state.closeModal,
  closeAllModals: state.closeAllModals,
}));

export const useToasts = () => useUIStore((state) => ({
  toasts: state.toasts,
  addToast: state.addToast,
  removeToast: state.removeToast,
  clearToasts: state.clearToasts,
}));

export const useLoading = () => useUIStore((state) => ({
  globalLoading: state.globalLoading,
  setGlobalLoading: state.setGlobalLoading,
  setLoading: state.setLoading,
  isLoading: state.isLoading,
}));

export const useFileUpload = () => useUIStore((state) => ({
  isDraggingFiles: state.isDraggingFiles,
  uploadProgress: state.uploadProgress,
  setIsDraggingFiles: state.setIsDraggingFiles,
  setUploadProgress: state.setUploadProgress,
  removeUploadProgress: state.removeUploadProgress,
}));
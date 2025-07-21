import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

type Theme = 'light' | 'dark' | 'system';
type Language = 'en' | 'es' | 'fr' | 'de' | 'zh' | 'ja';

interface UserPrefsState {
  // Model preferences
  model: string;
  temperature: number;
  maxTokens: number;
  
  // UI preferences
  theme: Theme;
  language: Language;
  showCosts: boolean;
  autoSave: boolean;
  
  // Chat preferences
  streamingEnabled: boolean;
  codeHighlighting: boolean;
  autoScrollToBottom: boolean;
  
  // File upload preferences
  maxFileSize: number;
  allowedFileTypes: string[];
  
  // Advanced preferences
  enableExperimentalFeatures: boolean;
  debugMode: boolean;
  
  // Actions
  setModel: (model: string) => void;
  setTemperature: (temperature: number) => void;
  setMaxTokens: (maxTokens: number) => void;
  setTheme: (theme: Theme) => void;
  setLanguage: (language: Language) => void;
  setShowCosts: (showCosts: boolean) => void;
  setAutoSave: (autoSave: boolean) => void;
  setStreamingEnabled: (streamingEnabled: boolean) => void;
  setCodeHighlighting: (codeHighlighting: boolean) => void;
  setAutoScrollToBottom: (autoScrollToBottom: boolean) => void;
  setMaxFileSize: (maxFileSize: number) => void;
  setAllowedFileTypes: (allowedFileTypes: string[]) => void;
  setEnableExperimentalFeatures: (enableExperimentalFeatures: boolean) => void;
  setDebugMode: (debugMode: boolean) => void;
  resetToDefaults: () => void;
}

const defaultState = {
  model: 'gemini-2.5-pro',
  temperature: 0.7,
  maxTokens: 4096,
  theme: 'system' as Theme,
  language: 'en' as Language,
  showCosts: true,
  autoSave: true,
  streamingEnabled: true,
  codeHighlighting: true,
  autoScrollToBottom: true,
  maxFileSize: 100 * 1024 * 1024, // 100MB
  allowedFileTypes: [
    'text/plain',
    'text/markdown',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
  ],
  enableExperimentalFeatures: false,
  debugMode: false,
};

export const usePrefsStore = create<UserPrefsState>()(
  subscribeWithSelector(
    persist(
      immer((set, get) => ({
        ...defaultState,
        
        setModel: (model) => set((state) => { state.model = model; }),
        setTemperature: (temperature) => set((state) => { state.temperature = Math.max(0, Math.min(2, temperature)); }),
        setMaxTokens: (maxTokens) => set((state) => { state.maxTokens = Math.max(1, Math.min(8192, maxTokens)); }),
        setTheme: (theme) => set((state) => { state.theme = theme; }),
        setLanguage: (language) => set((state) => { state.language = language; }),
        setShowCosts: (showCosts) => set((state) => { state.showCosts = showCosts; }),
        setAutoSave: (autoSave) => set((state) => { state.autoSave = autoSave; }),
        setStreamingEnabled: (streamingEnabled) => set((state) => { state.streamingEnabled = streamingEnabled; }),
        setCodeHighlighting: (codeHighlighting) => set((state) => { state.codeHighlighting = codeHighlighting; }),
        setAutoScrollToBottom: (autoScrollToBottom) => set((state) => { state.autoScrollToBottom = autoScrollToBottom; }),
        setMaxFileSize: (maxFileSize) => set((state) => { state.maxFileSize = Math.max(1024 * 1024, maxFileSize); }),
        setAllowedFileTypes: (allowedFileTypes) => set((state) => { state.allowedFileTypes = allowedFileTypes; }),
        setEnableExperimentalFeatures: (enableExperimentalFeatures) => set((state) => { state.enableExperimentalFeatures = enableExperimentalFeatures; }),
        setDebugMode: (debugMode) => set((state) => { state.debugMode = debugMode; }),
        
        resetToDefaults: () => set((state) => {
          Object.assign(state, defaultState);
        }),
      })),
      {
        name: 'handywriterz-user-preferences',
        version: 2,
        migrate: (persistedState: any, version: number) => {
          if (version < 2) {
            return {
              ...defaultState,
              model: persistedState?.model || defaultState.model,
            };
          }
          return persistedState;
        },
      }
    )
  )
);

// Convenience hooks for specific preferences
export const useModelPrefs = () => usePrefsStore((state) => ({
  model: state.model,
  temperature: state.temperature,
  maxTokens: state.maxTokens,
  setModel: state.setModel,
  setTemperature: state.setTemperature,
  setMaxTokens: state.setMaxTokens,
}));

export const useUIPrefs = () => usePrefsStore((state) => ({
  theme: state.theme,
  language: state.language,
  showCosts: state.showCosts,
  autoSave: state.autoSave,
  setTheme: state.setTheme,
  setLanguage: state.setLanguage,
  setShowCosts: state.setShowCosts,
  setAutoSave: state.setAutoSave,
}));

export const useChatPrefs = () => usePrefsStore((state) => ({
  streamingEnabled: state.streamingEnabled,
  codeHighlighting: state.codeHighlighting,
  autoScrollToBottom: state.autoScrollToBottom,
  setStreamingEnabled: state.setStreamingEnabled,
  setCodeHighlighting: state.setCodeHighlighting,
  setAutoScrollToBottom: state.setAutoScrollToBottom,
}));

export const useFileUploadPrefs = () => usePrefsStore((state) => ({
  maxFileSize: state.maxFileSize,
  allowedFileTypes: state.allowedFileTypes,
  setMaxFileSize: state.setMaxFileSize,
  setAllowedFileTypes: state.setAllowedFileTypes,
}));
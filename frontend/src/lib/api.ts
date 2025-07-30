/**
 * API utility functions for connecting to the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  prompt: string;
  mode: "general" | "essay" | "report" | "dissertation" | "case_study" | "case_scenario" | 
        "critical_review" | "database_search" | "reflection" | "document_analysis" | 
        "presentation" | "poster" | "exam_prep";
  file_ids?: string[];
  user_params?: Record<string, any>;
}

export interface SourceItem {
  title: string;
  url: string;
  snippet: string;
}

export interface ChatResponse {
  trace_id: string;
  response: string;
  sources: SourceItem[];
  quality_score: number;
  workflow: string;
  cost_usd: number;
}

export const chatApi = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: request.prompt,
        mode: request.mode,
        file_ids: request.file_ids || [],
        user_params: request.user_params || {}
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    return await response.json();
  },

  async getConversations(userId: string): Promise<{ conversations: any[] }> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/conversations`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  createSSEConnection(conversationId: string): EventSource {
    return new EventSource(`${API_BASE_URL}/api/stream/${conversationId}`);
  }
};
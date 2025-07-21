/**
 * API utility functions for connecting to the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  writeupType: string;
  model: string;
  files?: File[];
  userId?: string;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  sources: any[];
  conversation_id?: string;
  system_used: string;
  complexity_score: number;
  routing_reason: string;
  processing_time: number;
  citation_count: number;
  agent_metrics: any;
}

export const chatApi = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const formData = new FormData();
    formData.append('message', request.message);
    
    const userParams = {
      writeup_type: request.writeupType,
      model: request.model,
      user_id: request.userId || 'anonymous'
    };
    formData.append('user_params', JSON.stringify(userParams));
    
    if (request.files) {
      request.files.forEach((file) => {
        formData.append('files', file);
      });
    }

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
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
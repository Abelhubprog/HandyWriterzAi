/**
 * Real API client for workbench operations
 * Integrates with the FastAPI backend using proper authentication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Types matching backend models
export interface WorkbenchDocument {
  id: string;
  title: string;
  category: 'dissertation' | 'thesis' | 'essay' | 'research_paper' | 'report';
  wordCount: number;
  uploadedAt: string;
  uploadedBy: string;
  status: 'available' | 'claimed' | 'checking' | 'completed' | 'flagged';
  priority: 'urgent' | 'high' | 'normal' | 'low';
  claimedBy?: string;
  claimedAt?: string;
  plagiarismScore?: number;
  aiScore?: number;
  loopCount: number;
  maxLoops: number;
  isZeroMarked: boolean;
  assignmentId?: string;
  requirements?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface WorkbenchAssignment {
  id: string;
  title: string;
  status: string;
  created_at: string;
  assigned_checker_id?: string;
  input_doc_uri?: string;
  requirements?: Record<string, any>;
  ai_metadata?: Record<string, any>;
}

export interface WorkbenchSubmission {
  id: string;
  assignment_id: string;
  similarity_report: {
    score: number;
    urls: string[];
    metadata?: Record<string, any>;
  };
  ai_report: {
    score: number;
    urls: string[];
    metadata?: Record<string, any>;
  };
  modified_document: {
    urls: string[];
    mime_type?: string;
    metadata?: Record<string, any>;
  };
  notes?: string;
  status: string;
  created_at: string;
}

export interface WorkbenchArtifact {
  id: string;
  artifact_type: string;
  object_key: string;
  storage_provider: string;
  size_bytes?: number;
  mime_type?: string;
  checksum_sha256?: string;
  created_at: string;
}

class WorkbenchAPI {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('workbench_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  // Assignment management
  async claimNextAssignment(): Promise<WorkbenchAssignment | null> {
    const response = await fetch(`${API_BASE_URL}/api/workbench/assignments/next`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    const data = await this.handleResponse<any>(response);
    return data.id ? data : null;
  }

  async getAssignmentArtifacts(assignmentId: string): Promise<WorkbenchArtifact[]> {
    const response = await fetch(`${API_BASE_URL}/api/workbench/assignments/${assignmentId}/artifacts`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    const data = await this.handleResponse<{ artifacts: WorkbenchArtifact[] }>(response);
    return data.artifacts;
  }

  async submitAssignmentResults(
    assignmentId: string,
    submissionData: {
      submission_id: string;
      similarity_report: {
        score: number;
        urls: string[];
        metadata?: Record<string, any>;
      };
      ai_report: {
        score: number;
        urls: string[];
        metadata?: Record<string, any>;
      };
      modified_document: {
        urls: string[];
        mime_type?: string;
        metadata?: Record<string, any>;
      };
      notes?: string;
    }
  ): Promise<WorkbenchSubmission> {
    const response = await fetch(`${API_BASE_URL}/api/workbench/assignments/${assignmentId}/submissions`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(submissionData)
    });

    return this.handleResponse<WorkbenchSubmission>(response);
  }

  async verifyAssignment(assignmentId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/workbench/assignments/${assignmentId}/verify`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<any>(response);
  }

  // Document operations
  async getDocuments(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    category?: string;
    search?: string;
  }): Promise<WorkbenchDocument[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.status) searchParams.set('status', params.status);
    if (params?.category) searchParams.set('category', params.category);
    if (params?.search) searchParams.set('search', params.search);

    const response = await fetch(`${API_BASE_URL}/api/workbench/documents?${searchParams}`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<WorkbenchDocument[]>(response);
  }

  async claimDocument(documentId: string): Promise<WorkbenchDocument> {
    const response = await fetch(`${API_BASE_URL}/api/workbench/documents/${documentId}/claim`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<WorkbenchDocument>(response);
  }

  async downloadDocument(documentId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/workbench/documents/${documentId}/download`, {
      method: 'GET',
      headers: {
        ...(localStorage.getItem('workbench_token') && { 
          'Authorization': `Bearer ${localStorage.getItem('workbench_token')}` 
        })
      }
    });

    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }

    return response.blob();
  }

  async uploadReports(
    documentId: string,
    files: {
      plagiarismReport: File;
      aiReport: File;
    },
    notes?: string
  ): Promise<any> {
    const formData = new FormData();
    formData.append('plagiarism_report', files.plagiarismReport);
    formData.append('ai_report', files.aiReport);
    if (notes) formData.append('notes', notes);

    const response = await fetch(`${API_BASE_URL}/api/workbench/documents/${documentId}/upload-reports`, {
      method: 'POST',
      headers: {
        ...(localStorage.getItem('workbench_token') && { 
          'Authorization': `Bearer ${localStorage.getItem('workbench_token')}` 
        })
      },
      body: formData
    });

    return this.handleResponse<any>(response);
  }

  async markDocumentZero(documentId: string): Promise<WorkbenchDocument> {
    const response = await fetch(`${API_BASE_URL}/api/workbench/documents/${documentId}/mark-zero`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<WorkbenchDocument>(response);
  }

  // Admin operations
  async createWorkbenchUser(userData: {
    email: string;
    username: string;
    role: 'checker' | 'admin';
    full_name?: string;
    permissions?: string[];
  }): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/workbench/users`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(userData)
    });

    return this.handleResponse<any>(response);
  }

  async getWorkbenchUsers(params?: { skip?: number; limit?: number }): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());

    const response = await fetch(`${API_BASE_URL}/api/admin/workbench/users?${searchParams}`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<any[]>(response);
  }

  async updateWorkbenchUser(userId: string, updates: {
    role?: 'checker' | 'admin';
    permissions?: string[];
    is_active?: boolean;
    full_name?: string;
  }): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/workbench/users/${userId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updates)
    });

    return this.handleResponse<any>(response);
  }

  async deleteWorkbenchUser(userId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/admin/workbench/users/${userId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
  }

  // Statistics and reporting
  async getWorkbenchStats(): Promise<{
    totalDocuments: number;
    availableDocuments: number;
    inProgressDocuments: number;
    completedDocuments: number;
    flaggedDocuments: number;
    averageProcessingTime: number;
    userStats: any[];
  }> {
    const response = await fetch(`${API_BASE_URL}/api/workbench/stats`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<any>(response);
  }

  // File operations
  async uploadFile(file: File, type: 'plagiarism_report' | 'ai_report' | 'document'): Promise<{
    file_id: string;
    url: string;
    filename: string;
    size: number;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const response = await fetch(`${API_BASE_URL}/api/workbench/files/upload`, {
      method: 'POST',
      headers: {
        ...(localStorage.getItem('workbench_token') && { 
          'Authorization': `Bearer ${localStorage.getItem('workbench_token')}` 
        })
      },
      body: formData
    });

    return this.handleResponse<any>(response);
  }
}

// Export singleton instance
export const workbenchAPI = new WorkbenchAPI();
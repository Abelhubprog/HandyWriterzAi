import { nanoid } from 'nanoid';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// --- Types mirroring backend schemas ---

export type ReportPayload = {
  score: number;
  urls: string[];
  checksum_sha256?: string;
  metadata?: Record<string, any>;
};

export type ModifiedDocPayload = {
  urls: string[];
  mime_type?: string;
  checksum_sha256?: string;
  metadata?: Record<string, any>;
};

export type CreateAssignmentRequest = {
  title: string;
  requirements?: Record<string, any>;
  delivery_channel: "workbench" | "telegram";
  telegram_message_ref?: Record<string, any>;
  source_conversation_id?: string;
  ai_metadata?: Record<string, any>;
};

export type CreateAssignmentResponse = {
  id: string;
  title: string;
  status: string;
  created_at: string; // ISO string
};

export type ClaimNextResponse = {
  id?: string;
  title?: string;
  status?: string;
  created_at?: string; // ISO string
  assigned_checker_id?: number;
  input_doc_uri?: string;
  requirements?: Record<string, any>;
  message: string;
};

export type SubmitResultsRequest = {
  submission_id: string;
  similarity_report: ReportPayload;
  ai_report: ReportPayload;
  modified_document: ModifiedDocPayload;
  notes?: string;
};

export type SubmitResultsResponse = {
  id: string;
  status: string;
  message: string;
  similarity_score?: number;
  ai_score?: number;
};

export type ArtifactRef = {
  id: string;
  artifact_type: string;
  object_key: string;
  storage_provider: string;
  size_bytes?: number;
  mime_type?: string;
  checksum_sha256?: string;
  created_at: string; // ISO string
};

export type ListArtifactsResponse = {
  assignment_id: string;
  artifacts: ArtifactRef[];
};

export type VerifyAssignmentResponse = {
  id: string;
  status: string;
  message: string;
  latest_submission_id?: string;
  similarity_score?: number;
  ai_score?: number;
};

// --- API Client Functions ---

async function callApi<T>(endpoint: string, method: string, body?: any): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    // Add authorization header if you have a token management system
    // 'Authorization': `Bearer ${yourAuthToken}`
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'API request failed');
  }

  return response.json();
}

export async function createAssignment(
  request: CreateAssignmentRequest
): Promise<CreateAssignmentResponse> {
  return callApi<CreateAssignmentResponse>('/api/workbench/assignments', 'POST', request);
}

export async function claimNext(): Promise<ClaimNextResponse> {
  return callApi<ClaimNextResponse>('/api/workbench/assignments/next', 'GET');
}

export async function listArtifacts(assignmentId: string): Promise<ListArtifactsResponse> {
  return callApi<ListArtifactsResponse>(`/api/workbench/assignments/${assignmentId}/artifacts`, 'GET');
}

export async function submitResults(
  assignmentId: string,
  request: SubmitResultsRequest
): Promise<SubmitResultsResponse> {
  return callApi<SubmitResultsResponse>(`/api/workbench/assignments/${assignmentId}/submissions`, 'POST', request);
}

export async function verifyAssignment(assignmentId: string): Promise<VerifyAssignmentResponse> {
  return callApi<VerifyAssignmentResponse>(`/api/workbench/assignments/${assignmentId}/verify`, 'POST');
}

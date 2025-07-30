import { env } from 'process';

const AGENTIC_DOC_SERVICE_URL = env.AGENTIC_DOC_SERVICE_URL || 'http://localhost:8000';

interface ProcessDocumentRequest {
    bucket: string;
    key: string;
    task_id?: string;
}

interface ProcessDocumentResponse {
    accepted: boolean;
    task_id: string;
}

class AgenticDocClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    async processDocument(request: ProcessDocumentRequest): Promise<ProcessDocumentResponse> {
        const response = await fetch(`${this.baseUrl}/process-document`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to process document: ${response.statusText}`);
        }

        return response.json();
    }
}

export const agenticDocClient = new AgenticDocClient(AGENTIC_DOC_SERVICE_URL);

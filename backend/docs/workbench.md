# Human-in-the-Loop (HITL) Turnitin Workbench Protocol

This document defines the backend API and data contracts for the Human-in-the-Loop (HITL) Turnitin Workbench, a system designed to integrate human review into the automated plagiarism and AI detection workflow. It covers assignment creation, checker claiming, submission of reports, and final verification, with an expanded scope to include iterative human-AI collaboration and advanced document processing.

## 1. Overview

The Workbench provides a structured queue for documents requiring human review (e.g., for Turnitin checks, AI detection verification, or manual edits). AI agents can hand over documents to this queue, and human checkers/admins can claim, process, and submit results back into the system. The expanded vision includes a robust platform with distinct authentication for Workbench users, AI-driven document ingestion, iterative human-AI rewrite loops based on visual highlights, and seamless integration with the main application's chat UI and document library.

## 2. Core Concepts

- **Assignment:** A unit of work representing a document (or a set of chunks) that needs human review. Created by an AI agent or an admin.
- **Submission:** A checker's response to an assignment, including plagiarism/AI reports and a modified document.
- **Artifact:** A reference to a file (e.g., original document, PDF report, modified DOCX) stored in object storage.
- **Section Status (Optional):** Granular status tracking for individual sections/chunks within a larger document.
- **Workbench User:** A distinct user role (admin, checker) with specific permissions within the Workbench, managed separately from general application users.
- **Iterative Rewrite Loop:** A multi-step process where human checkers highlight sections for AI agents to rewrite, followed by re-submission and re-verification.
- **Visual Highlight Detection:** A "vision-like" system to detect and interpret highlighted sections in submitted documents.

## 3. Data Models (Backend ORM Reference)

These models are defined in `backend/src/db/models.py` and managed via Alembic migrations.

### 3.1. `WorkbenchAssignment`

Represents a document handed over for human review.

- `id` (UUID PK)
- `tenant_id` (UUID, indexed): Tenant owning the assignment.
- `user_id` (UUID, FK to `users.id`, indexed): Original user who initiated the write-up (main app user).
- `source_conversation_id` (UUID, indexed): Links back to the original AI conversation.
- `title` (TEXT): Title of the document/assignment.
- `status` (ENUM: `WorkbenchAssignmentStatus`, indexed): Current state of the assignment (`QUEUED`, `ASSIGNED`, `CHECKING`, `NEEDS_EDIT`, `AWAITING_UPLOAD`, `AWAITING_VERIFICATION`, `VERIFIED`, `REJECTED`, `CLOSED`, `ITERATION_PENDING_AI_REWRITE`, `ITERATION_PENDING_HUMAN_REVIEW`).
- `assigned_checker_id` (INT, FK to `checkers.id`, nullable, indexed): ID of the human checker currently assigned.
- `delivery_channel` (ENUM: `WorkbenchDeliveryChannel`): How the assignment was delivered (`TELEGRAM`, `WORKBENCH`).
- `ai_metadata` (JSONB, nullable): Metadata from the AI agent (e.g., initial scores, agent decisions, original document URI, current iteration count).
- `requirements` (JSONB, nullable): Specific requirements for verification (e.g., `min_similarity_score`, `max_similarity_score`, `expected_ai_score`).
- `telegram_message_ref` (JSONB, nullable): Reference to Telegram message if applicable (e.g., `chat_id`, `message_id`).
- `created_at` (TIMESTAMP, default `utcnow()`)
- `updated_at` (TIMESTAMP, onupdate `utcnow()`)
- `soft_deleted` (BOOLEAN, default `false`)

**Indices:**
- `ix_workbench_assignments_tenant_created_desc` (`tenant_id`, `created_at` DESC)
- `ix_workbench_assignments_status_created` (`status`, `created_at` ASC)
- `ix_workbench_assignments_source_conversation` (`source_conversation_id`)

### 3.2. `WorkbenchSubmission`

Records a human checker's submission of reports and modified documents.

- `id` (UUID PK)
- `assignment_id` (UUID, FK to `workbench_assignments.id`, indexed)
- `checker_id` (INT, FK to `checkers.id`, indexed)
- `submission_id` (STRING, unique): Client-generated unique ID for idempotency.
- `similarity_report` (JSONB): Contains `score` (float), `urls` (list of strings), `checksum_sha256` (string), `metadata` (dict).
- `ai_report` (JSONB): Contains `score` (float), `urls` (list of strings), `checksum_sha256` (string), `metadata` (dict).
- `modified_document` (JSONB): Contains `urls` (list of strings), `mime_type` (string), `checksum_sha256` (string), `metadata` (dict). This will be a Word document (`.docx`).
- `notes` (TEXT, nullable): Free-form notes from the checker.
- `highlighted_sections` (JSONB, nullable): Data representing highlighted sections detected by the vision system.
- `status` (ENUM: `WorkbenchSubmissionStatus`, indexed): `SUBMITTED`, `UNDER_REVIEW`, `ACCEPTED`, `REJECTED`, `NEEDS_REWRITE`.
- `created_at` (TIMESTAMP, default `utcnow()`)
- `updated_at` (TIMESTAMP, onupdate `utcnow()`)

**Indices:**
- `ix_workbench_submissions_assignment_created_desc` (`assignment_id`, `created_at` DESC)
- `ix_workbench_submissions_checker_created_desc` (`checker_id`, `created_at` DESC)
- `ix_workbench_submissions_status_created` (`status`, `created_at` ASC)
- `uq_workbench_submissions_submission_id` (Unique constraint on `submission_id`)

### 3.3. `WorkbenchArtifact`

References to files stored in object storage (e.g., S3, Supabase Storage). All documents will have unique IDs.

- `id` (UUID PK)
- `assignment_id` (UUID, FK to `workbench_assignments.id`, nullable, indexed)
- `submission_id` (UUID, FK to `workbench_submissions.id`, nullable, indexed)
- `artifact_type` (ENUM: `WorkbenchArtifactType`, indexed): `SIMILARITY_REPORT_PDF`, `AI_REPORT_PDF`, `MODIFIED_DOCX`, `MODIFIED_PDF`, `RAW_CHUNK_PDF`, `ORIGINAL_DOCX_UPLOAD`, `HIGHLIGHTED_IMAGE`, `OTHER`.
- `storage_provider` (STRING): e.g., `s3`, `supabase`.
- `bucket` (STRING, nullable)
- `object_key` (STRING, indexed): Full path/key in object storage.
- `size_bytes` (BIGINT, nullable)
- `mime_type` (STRING, nullable)
- `checksum_sha256` (STRING, nullable, indexed)
- `metadata` (JSONB, nullable): Additional file-specific metadata (e.g., `page_number`, `bounding_box` for highlights).
- `created_at` (TIMESTAMP, default `utcnow()`)

**Indices:**
- `ix_workbench_artifacts_assignment_created_desc` (`assignment_id`, `created_at` DESC)
- `ix_workbench_artifacts_submission_created_desc` (`submission_id`, `created_at` DESC)
- `ix_workbench_artifacts_type_created_desc` (`artifact_type`, `created_at` DESC)
- `ix_workbench_artifacts_object_key` (`object_key`)
- `ix_workbench_artifacts_checksum` (`checksum_sha256`)

### 3.4. `WorkbenchSectionStatus` (Optional)

Tracks status for individual sections/chunks within an assignment.

- `id` (UUID PK)
- `assignment_id` (UUID, FK to `workbench_assignments.id`, indexed)
- `section_id` (STRING): Deterministic key (e.g., chunk index, outline section ID).
- `status` (ENUM: `ChunkStatus`, indexed): `OPEN`, `CHECKING`, `NEEDS_EDIT`, `DONE`, `TELEGRAM_FAILED`, `AI_REWRITING`, `HUMAN_REVIEWING`.
- `evidence` (JSONB, nullable): Notes or links to specific issues/evidence for this section.
- `created_at` (TIMESTAMP, default `utcnow()`)
- `updated_at` (TIMESTAMP, onupdate `utcnow()`)

**Indices:**
- `uq_workbench_section_unique` (Unique constraint on `assignment_id`, `section_id`)
- `ix_workbench_section_status_created_desc` (`status`, `created_at` DESC)

## 4. Workbench User Management & Authentication

The Workbench will have its own distinct user management and authentication system, separate from the main application's user base. This allows for specific roles and permissions tailored to the review process.

- **Roles:**
    - **Admin:** Can add/manage Workbench users (checkers), create assignments, and verify submissions.
    - **Checker:** Can claim assignments, download documents, perform reviews, and submit results.
- **Authentication:** A robust authentication mechanism will be implemented for Workbench users, potentially leveraging a separate identity provider or a dedicated user table.
- **User Provisioning:** Admins will be able to add new checker users to the Workbench.

## 5. AI-Initiated Workflow & Document Ingestion

AI agents will autonomously upload documents to the Workbench for human review.

- **Trigger:** An AI agent (e.g., a writing agent, a quality assurance agent) determines that a document requires human review (e.g., high similarity score, potential AI-generated content, complex edits).
- **Document Format:** Documents uploaded by AI agents will primarily be Word documents (`.docx`).
- **API Endpoint:** A dedicated internal API endpoint (or a specific `CreateAssignmentRequest` with `delivery_channel: "ai_agent"`) will be used by AI agents to create assignments and upload the initial document.
- **Metadata:** AI agents will include relevant metadata (e.g., initial scores, reasons for handover, suggested areas of focus) in the `ai_metadata` field of the `WorkbenchAssignment`.

## 6. Iterative Human-AI Rewrite Loop

This is a core new feature enabling collaborative refinement of documents.

### 6.1. Human Review & Highlighting

- **Download:** Checkers download the Word document (`.docx`) associated with an assignment.
- **Review & Highlight:** Checkers review the document and highlight sections that need revision (e.g., for plagiarism, AI detection, clarity, grammar).
- **Upload:** Checkers upload the highlighted Word document along with the two PDF reports (similarity and AI detection).

### 6.2. Vision-like System for Highlight Detection

Upon submission of a highlighted Word document:

- **Processing:** A backend service will process the uploaded `.docx` file.
- **Highlight Detection:** This service will employ a "vision-like" capability to identify highlighted text sections within the document. This could involve:
    - Parsing the DOCX XML structure to detect text with specific highlighting properties.
    - Converting the DOCX to an image/PDF and using OCR + image processing to detect visual highlights (less preferred due to complexity and potential for error).
- **Extraction:** The highlighted text content will be extracted.
- **Metadata:** For each highlighted section, relevant metadata (e.g., exact text, approximate location/page number, unique identifier) will be stored in the `highlighted_sections` field of the `WorkbenchSubmission` and potentially as `HIGHLIGHTED_IMAGE` artifacts.

### 6.3. AI Agent Rewrite & Re-upload

- **Trigger:** Once highlighted sections are detected, the `WorkbenchAssignment` status will transition to `ITERATION_PENDING_AI_REWRITE`.
- **Agent Orchestration:** The extracted highlighted sections will be passed to a relevant AI agent (e.g., a "Rewrite Agent" or "Editor Agent").
- **Instructions:** The AI agent will receive system instructions and potentially a specific model to use for rewriting the highlighted parts.
- **Rewrite:** The AI agent will rewrite the highlighted sections within the context of the original document.
- **Re-upload:** The AI agent will re-upload the modified Word document (with the rewritten sections) back to the Workbench, creating a new `WorkbenchArtifact` and updating the `WorkbenchAssignment` status to `ITERATION_PENDING_HUMAN_REVIEW`. This new document will retain the same unique ID as the original document, but will be a new version.

### 6.4. Human Re-review & Finalization

- **Notification:** The original human checker will be notified that the document is ready for re-review.
- **Download & Re-check:** The checker downloads the AI-rewritten document, re-checks the AI and plagiarism scores, and uploads new PDF reports.
- **"ZORO" Mark:** If the human checker is satisfied, they will mark the submission as "ZORO" (or a similar finalization flag). This signifies no further rewrite loops are needed.
- **Final Document Handover:** Upon "ZORO" mark, the latest version of the Word document uploaded by the human (or AI, if it was the last step) will be handed over to a "Formatter Agent."

## 7. Final Document Delivery & Archiving

- **Formatter Agent:** The Formatter Agent will receive the final Word document. It will apply predefined system instructions or prompts to format the document (e.g., consistent styling, headers, footers).
- **Chat UI Integration:** The formatted Word document will be made available for download directly within the original user's chat UI. This will also be reflected in the chat history.
- **Document Library:** The final document will be stored in a dedicated document library.
- **Retention Policy:** Documents in the library will be cleared after 7 days to manage storage.

## 8. API Endpoints (Backend `backend/src/api/workbench.py`)

All endpoints are prefixed with `/api/workbench`. New endpoints or expanded functionality will be required for:

- **Workbench User Management:** Endpoints for admin to add/manage checker users.
- **Document Upload (AI Agent):** An endpoint for AI agents to initiate assignments with document uploads.
- **Highlight Processing Trigger:** An internal endpoint or service call to trigger the vision-like system.
- **Iterative Submission:** The existing submission endpoint will need to handle iterative submissions and update assignment status accordingly.
- **Document Download (Signed URLs):** Endpoints to provide signed URLs for secure document downloads from object storage.

### 8.1. `POST /assignments` (Expanded)

Creates a new workbench assignment.

- **Auth:** `admin`, `tutor`, `ai_agent` (internal)
- **Request Body:** `CreateAssignmentRequest` (will include `original_document_uri` for AI uploads)
  ```json
  {
    "title": "PhD Dissertation - Chapter 3 Review",
    "requirements": {
      "min_similarity_score": 0.0,
      "max_similarity_score": 5.0,
      "expected_ai_score": 0.0
    },
    "delivery_channel": "workbench",
    "source_conversation_id": "uuid-of-original-conversation",
    "ai_metadata": { "agent_decision": "high_complexity_review", "original_doc_uri": "s3://bucket/path/doc.docx" }
  }
  ```
- **Response:** `CreateAssignmentResponse`
  ```json
  {
    "id": "uuid-of-new-assignment",
    "title": "PhD Dissertation - Chapter 3 Review",
    "status": "queued",
    "created_at": "2025-08-01T12:00:00Z"
  }
  ```

### 8.2. `GET /assignments/next` (Expanded)

Claims the next available assignment for the authenticated checker.

- **Auth:** `checker`, `admin`
- **Response:** `ClaimNextResponse` (will include `input_doc_uri` for the current document version)
  ```json
  {
    "id": "uuid-of-claimed-assignment",
    "title": "Essay Review - Section 2",
    "status": "assigned",
    "created_at": "2025-08-01T11:00:00Z",
    "assigned_checker_id": 123,
    "input_doc_uri": "https://storage.example.com/original.docx",
    "requirements": { ... },
    "message": "Assignment claimed."
  }
  ```
  Or if no assignments:
  ```json
  { "message": "No assignments available or claimed." }
  ```

### 8.3. `GET /assignments/{assignment_id}/artifacts` (Expanded)

Lists all artifacts associated with a specific assignment.

- **Auth:** `checker`, `admin`
- **Response:** `ListArtifactsResponse`
  ```json
  {
    "assignment_id": "uuid-of-assignment",
    "artifacts": [
      {
        "id": "uuid-of-artifact-1",
        "artifact_type": "original_docx_upload",
        "object_key": "path/to/original_doc.docx",
        "storage_provider": "s3",
        "size_bytes": 12345,
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "checksum_sha256": "abc...",
        "created_at": "2025-08-01T12:05:00Z"
      },
      {
        "id": "uuid-of-artifact-2",
        "artifact_type": "similarity_report_pdf",
        "object_key": "path/to/sim_report.pdf",
        "storage_provider": "s3",
        "created_at": "2025-08-01T12:10:00Z"
      },
      {
        "id": "uuid-of-artifact-3",
        "artifact_type": "highlighted_image",
        "object_key": "path/to/highlight_screenshot.png",
        "storage_provider": "s3",
        "metadata": { "page_number": 1, "bounding_box": [10, 20, 30, 40] },
        "created_at": "2025-08-01T12:15:00Z"
      }
    ]
  }
  ```

### 8.4. `POST /assignments/{assignment_id}/submissions` (Expanded)

Submits checker results (reports and modified document) for an assignment. This endpoint will also trigger the highlight detection and AI rewrite loop.

- **Auth:** `checker`
- **Request Body:** `SubmitResultsRequest` (will include `is_final_submission` flag for "ZORO" mark)
  ```json
  {
    "submission_id": "client-generated-uuid-for-idempotency",
    "similarity_report": {
      "score": 3.5,
      "urls": ["https://storage.example.com/sim_report_v2.pdf"],
      "checksum_sha256": "xyz..."
    },
    "ai_report": {
      "score": 0.0,
      "urls": ["https://storage.example.com/ai_report_v2.pdf"],
      "checksum_sha256": "def..."
    },
    "modified_document": {
      "urls": ["https://storage.example.com/modified_doc_v2.docx"],
      "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "checksum_sha256": "ghi..."
    },
    "notes": "Minor paraphrasing done in section 2. AI score confirmed zero.",
    "is_final_submission": false // Set to true for "ZORO" mark
  }
  ```
- **Response:** `SubmitResultsResponse`
  ```json
  {
    "id": "uuid-of-submission",
    "status": "submitted",
    "message": "Submission received and validated. Highlight detection and AI rewrite triggered.",
    "similarity_score": 3.5,
    "ai_score": 0.0
  }
  ```
  (If validation fails, `status` might be `submitted` but `message` indicates issues, or a 400 HTTP error is returned.)

### 8.5. `POST /assignments/{assignment_id}/verify` (Expanded)

Finalizes the assignment status based on the latest submission's scores and requirements. This will also trigger the final formatting and delivery if `is_final_submission` was true.

- **Auth:** `admin`
- **Response:** `VerifyAssignmentResponse`
  ```json
  {
    "id": "uuid-of-assignment",
    "status": "verified",
    "message": "Assignment uuid-of-assignment set to verified. Final document delivered.",
    "latest_submission_id": "uuid-of-submission",
    "similarity_score": 3.5,
    "ai_score": 0.0
  }
  ```
  (If verification fails, `status` will be `rejected`.)

## 9. Backend Wiring (`backend/src/main.py`)

The `APIRouter` for the Workbench is included in the main FastAPI application.

```python
# backend/src/main.py
# ... (existing imports)
from src.api.workbench import router as workbench_router # New import

app = FastAPI(
    # ... (existing app config)
)

# ... (existing middleware and other router includes)

# Include Workbench routes
app.include_router(workbench_router, prefix="/api/workbench", tags=["workbench"]) # New line

# ... (rest of main.py)
```

## 10. Frontend Integration Points

The frontend will consume these APIs and provide the UI for the complex iterative workflow.

- **API Client:** `frontend/src/services/workbench.ts` will contain `fetch` wrappers for these endpoints.
- **Pages:**
  - `frontend/src/app/admin/workbench/queue/page.tsx` for listing and claiming assignments.
  - `frontend/src/app/checker/workbench/task/page.tsx` for checkers to work on assignments, including download, upload, and highlight visualization.
  - `frontend/src/app/admin/workbench/assignments/[id]/page.tsx` for admin to view details, verify, and potentially manage Workbench users.
- **Components:** Reusable UI components will be created under `frontend/src/components/workbench/`, including:
    - Document viewer with highlighting capabilities.
    - Iteration history display.
    - "ZORO" finalization button.
- **Types:** Shared TypeScript types will mirror the Pydantic schemas in `frontend/src/types/workbench.ts`.
- **Routing:** The Workbench will be accessible at `http://localhost:3000/Workbench`.

## 11. Next Steps

The backend code for the Workbench (schemas, repositories, service, router, and main wiring) has been provided. However, the expanded scope requires significant re-evaluation and potential re-implementation of backend services, especially for document processing and AI orchestration.

**Immediate next actions:**

1.  **Address Pylance Errors:** Resolve the Python dependency issues in the backend environment. This is crucial for any backend development.
2.  **Refine Backend Design:** Based on the updated `workbench.md`, refine the backend data models and service logic to fully support the vision-like system, iterative rewrite loops, and final document delivery. This will likely involve new services for document parsing, image processing (if needed for highlights), and AI agent orchestration for rewrites.
3.  **Implement Workbench User Management:** Design and implement the separate user management system for Workbench admins and checkers.
4.  **Frontend Implementation:** Once the backend is stable and supports the new features, proceed with the comprehensive frontend implementation, including the interactive highlighting and iterative workflow UI.

This expanded scope will require a more detailed plan and potentially new backend services and models.

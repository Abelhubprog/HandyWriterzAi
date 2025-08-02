# Storage, Ordering, Indices, and Retention

## Overview

This document defines comprehensive storage contracts for HandyWriterzAI, including:
- Core conversational AI workflows (chat, research, writing)
- Human-in-the-Loop (HITL) Turnitin workbench
- Multi-agent orchestration state management
- Evidence normalization and citation integrity

Storage is organized across three tiers for performance, reliability, and cost control.

## Storage Tiers

### 1) Hot Path (Ephemeral Streaming)
- **Transport**: Redis Pub/Sub or bounded in-process queues for SSE/WebSocket events
- **Schema**: Unified SSE envelope with correlation_id, node_name, phase, seq (monotonic)
- **Retention**: Channel TTL minutes–hours; overflow coalesces progress/content frames
- **Purpose**: Low-latency fan-out of streaming updates to connected clients

### 2) Operational Database (System of Record)
- **Engine**: PostgreSQL with SQLAlchemy ORM models
- **Entities**: Conversations, Messages, Runs, Usage, SearchArtifacts, ArtifactRefs, HITL Workbench tables
- **Ordering**: Chronological indices with tenant scoping for multi-user isolation
- **Purpose**: Durable state, conversation history, evidence tracking, audit trails

### 3) Object Storage (Cold)
- **Storage**: S3-compatible or Supabase Storage for binary artifacts
- **Structure**: Hierarchical keys with tenant/user/date prefixes
- **Lifecycle**: Hot → Warm → Cold → Archive based on access patterns
- **Purpose**: Large files, exports, uploads, generated documents

HITL Workbench data model (canonical)

A) workbench_assignments
Represents documents handed over from AI agents to HITL queue (via Workbench agent or Telegram agent).
- id (UUID PK)
- tenant_id (UUID, indexed)
- user_id (UUID, indexed) author/user of original write-up
- source_conversation_id (UUID, indexed) correlation back to orchestration
- title (TEXT)
- status (ENUM: queued, assigned, checking, needs_edit, awaiting_upload, awaiting_verification, verified, rejected, closed) indexed
- assigned_checker_id (INT, nullable) FK to checkers.id
- delivery_channel (ENUM: telegram, workbench) for provenance
- ai_metadata (JSONB) e.g. agent decisions, thresholds
- requirements (JSONB) e.g. min similarity pass <= 5%, ai score == 0%
- telegram_message_ref (JSONB) optional: channel, message_id, timestamps
- created_at (TIMESTAMP, default now())
- updated_at (TIMESTAMP)
- soft_deleted (BOOLEAN, default false)

Indices:
- (tenant_id, created_at DESC)
- (status, created_at) for next-available queue patterns
- (source_conversation_id) for audit

B) workbench_submissions
Human uploads result of Turnitin checking (>= 2 reports) and modified document.
- id (UUID PK)
- assignment_id (UUID FK workbench_assignments.id, indexed)
- checker_id (INT FK checkers.id, indexed)
- submission_id (TEXT, unique, idempotency key from client or generated)
- similarity_report (JSONB) structured metadata, URLs, similarity_score (redundant for filtering)
- ai_report (JSONB) structured metadata, URLs, ai_score (redundant for filtering)
- modified_document (JSONB) structured references for updated DOCX/PDF
- notes (TEXT) human notes
- status (ENUM: submitted, under_review, accepted, rejected) indexed
- created_at (TIMESTAMP, default now())
- updated_at (TIMESTAMP)

Indices:
- unique(submission_id)
- (assignment_id, created_at DESC)
- (checker_id, created_at DESC)
- (status, created_at)

C) workbench_artifacts
References for all files stored in object storage, unified for telemetry and integrity checks.
- id (UUID PK)
- assignment_id (UUID, indexed)
- submission_id (UUID, indexed)
- artifact_type (ENUM: similarity_report_pdf, ai_report_pdf, modified_docx, modified_pdf, raw_chunk_pdf, other)
- storage_provider (TEXT) e.g. s3, supabase
- bucket (TEXT)
- object_key (TEXT, indexed)
- size_bytes (BIGINT)
- mime_type (TEXT)
- checksum_sha256 (TEXT, indexed)
- metadata (JSONB) provenance, generator, tool versions, ingestion notes
- created_at (TIMESTAMP, default now())

Indices:
- (assignment_id, created_at DESC)
- (submission_id, created_at DESC)
- (artifact_type, created_at DESC)
- (object_key)
- (checksum_sha256)

D) workbench_section_status (optional)
If chunking is used (aligns with existing lots/chunks), track per-section state within an assignment.
- id (UUID PK)
- assignment_id (UUID, indexed)
- section_id (TEXT) deterministic key (e.g. chunk_index or DOM range)
- status (ENUM: open, checking, needs_edit, done, telegram_failed)
- evidence (JSONB) URLs/keys to reports or comments
- created_at (TIMESTAMP, default now())
- updated_at (TIMESTAMP)

Indices:
- (assignment_id, section_id) unique
- (status, created_at DESC)

Ordering rules
- Assignment lists: ORDER BY created_at DESC (recent first), or by status priority then created_at.
- Submissions: ORDER BY created_at DESC to view latest upload first.
- Artifacts: ORDER BY created_at DESC; prefer artifact_type filters for quick lookups.
- Section status: ORDER BY section_id ASC for stable UI display.

Retention and redaction
- Anonymous users: 30d for assignments/submissions/artifacts; soft-delete after; purge 7d later.
- Free tier: 90d; Paid tier: 365d (configurable).
- Artifacts: lifecycle to IA/Glacier after 90–180d based on tier; always keep checksums and minimal metadata for audit.
- PII: redact or hash identifiers inside JSONB before persistence; never vectorize PII content.
- Soft-delete records first; a scheduled purge process permanently removes after the grace period.

Security and tenancy
- Every row is tenant-scoped; user_id/checker_id constrained where applicable.
- Object storage prefixes include tenant and user. Example:
  - tenant/{tenant_id}/user/{user_id}/date/{YYYY}/{MM}/{DD}/assignments/{assignment_id}/{artifact_type}/{uuid}.ext
- Logs include correlation_id and source_conversation_id when present.

API/agent handover summary
- AI agents produce Assignment with requirements and delivery_channel; Workbench agent uploads the original document and links Telegram references if used.
- Human logs into Workbench UI, downloads the document, checks Turnitin, and re-uploads:
  - At least two reports (similarity and AI detection) + modified document.
- Workbench agent validates uploads (scores meet thresholds), transitions assignment to verified, and returns results to the orchestration.

Query patterns (examples)
- Next work item: WHERE status IN ('queued','assigned') ORDER BY created_at LIMIT 1
- My queue: WHERE status='assigned' AND assigned_checker_id=:id ORDER BY created_at DESC
- Audit trail: JOIN assignments, submissions, artifacts ON assignment_id ORDER BY submissions.created_at DESC
- Verification gate: SELECT submissions WHERE similarity_report->>'score' <= '5' AND ai_report->>'score' = '0'

Testing guidance
- Integrity: create assignment → upload submissions (2+ reports, 1 modified doc) → verify indices and unique constraints enforce idempotency.
- Ordering: ensure listing is stable and index-backed.
- Retention: simulate soft-delete + purge; artifacts with lifecycle moves remain referenced or are safely deleted.
- Security: ensure tenant scoping in all queries; attempt cross-tenant access must fail in tests.

Versioning
- This document is v1. Any schema change must update Alembic migrations and include a storage.md delta note.

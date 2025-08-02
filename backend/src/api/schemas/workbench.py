from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# --- Request/Response Schemas for Workbench API ---

class ReportPayload(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Similarity or AI detection score (0-100)")
    urls: List[AnyHttpUrl] = Field(..., description="URLs to the report files (PDFs)")
    checksum_sha256: Optional[str] = Field(None, description="SHA256 checksum of the report file")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional report metadata")

class ModifiedDocPayload(BaseModel):
    urls: List[AnyHttpUrl] = Field(..., description="URLs to the modified document files (DOCX/PDF)")
    mime_type: Optional[str] = Field(None, description="MIME type of the modified document")
    checksum_sha256: Optional[str] = Field(None, description="SHA256 checksum of the modified document file")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional document metadata")

class CreateAssignmentRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Title of the assignment")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Specific requirements for the check (e.g., min_similarity_score, max_ai_score)")
    delivery_channel: str = Field("workbench", description="Channel for delivery (e.g., 'workbench', 'telegram')")
    telegram_message_ref: Optional[Dict[str, Any]] = Field(None, description="Reference to Telegram message if applicable")
    source_conversation_id: Optional[str] = Field(None, description="Original conversation ID if assignment is from an agent workflow")

class CreateAssignmentResponse(BaseModel):
    id: str = Field(..., description="UUID of the created workbench assignment")
    title: str
    status: str
    created_at: datetime

class ClaimNextResponse(BaseModel):
    id: Optional[str] = Field(None, description="UUID of the claimed workbench assignment")
    title: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]
    assigned_checker_id: Optional[int]
    input_doc_uri: Optional[str] = Field(None, description="URI to the original input document")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Requirements for the assignment")
    message: str = Field("No assignments available or claimed.", description="Status message")

class SubmitResultsRequest(BaseModel):
    submission_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this submission (for idempotency)")
    similarity_report: ReportPayload
    ai_report: ReportPayload
    modified_document: ModifiedDocPayload
    notes: Optional[str] = Field(None, description="Notes from the checker")

class SubmitResultsResponse(BaseModel):
    id: str = Field(..., description="UUID of the workbench submission")
    status: str = Field(..., description="Status of the submission (e.g., 'submitted', 'accepted', 'rejected')")
    message: str = Field(..., description="Detailed message about the submission result")
    similarity_score: Optional[float] = None
    ai_score: Optional[float] = None

class ArtifactRef(BaseModel):
    id: str
    artifact_type: str
    object_key: str
    storage_provider: str
    size_bytes: Optional[int]
    mime_type: Optional[str]
    checksum_sha256: Optional[str]
    created_at: datetime

class ListArtifactsResponse(BaseModel):
    assignment_id: str
    artifacts: List[ArtifactRef]

class VerifyAssignmentResponse(BaseModel):
    id: str = Field(..., description="UUID of the workbench assignment")
    status: str = Field(..., description="Final status of the assignment (e.g., 'verified', 'rejected')")
    message: str = Field(..., description="Detailed message about the verification result")
    latest_submission_id: Optional[str] = Field(None, description="ID of the submission used for verification")
    similarity_score: Optional[float] = None
    ai_score: Optional[float] = None
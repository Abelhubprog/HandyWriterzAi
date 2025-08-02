import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..db.database import get_db
from ..db.repositories.workbench_assignment_repo import WorkbenchAssignmentRepository
from ..db.repositories.workbench_submission_repo import WorkbenchSubmissionRepository
from ..db.repositories.workbench_artifact_repo import WorkbenchArtifactRepository
from ..db.repositories.workbench_section_status_repo import WorkbenchSectionStatusRepository
from ..services.workbench_service import WorkbenchService
from ..services.security_service import get_current_user, require_authorization
from ..api.schemas.workbench import (
    CreateAssignmentRequest, CreateAssignmentResponse, ClaimNextResponse,
    SubmitResultsRequest, SubmitResultsResponse, ListArtifactsResponse,
    VerifyAssignmentResponse, ArtifactRef
)
from ..db.models import WorkbenchAssignmentStatus, WorkbenchDeliveryChannel, WorkbenchArtifactType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workbench", tags=["Workbench"])

# Dependency to get WorkbenchService
def get_workbench_service(db: Session = Depends(get_db)) -> WorkbenchService:
    assignment_repo = WorkbenchAssignmentRepository(db)
    submission_repo = WorkbenchSubmissionRepository(db)
    artifact_repo = WorkbenchArtifactRepository(db)
    section_status_repo = WorkbenchSectionStatusRepository(db)
    return WorkbenchService(assignment_repo, submission_repo, artifact_repo, section_status_repo)

@router.post("/assignments", response_model=CreateAssignmentResponse, status_code=status.HTTP_201_CREATED)
@require_authorization(["admin", "tutor"]) # Only admins or agents can create assignments
async def create_assignment(
    request: CreateAssignmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    workbench_service: WorkbenchService = Depends(get_workbench_service),
    db: Session = Depends(get_db)
):
    """
    Creates a new workbench assignment for human review.
    Typically called by an AI agent or an admin.
    """
    tenant_id = uuid.UUID(current_user["tenant_id"]) if "tenant_id" in current_user else uuid.uuid4() # Placeholder for actual tenant_id
    user_id = uuid.UUID(current_user["id"]) if "id" in current_user else uuid.uuid4() # Placeholder for actual user_id

    try:
        assignment = workbench_service.create_assignment(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            source_conversation_id=uuid.UUID(request.source_conversation_id) if request.source_conversation_id else None,
            title=request.title,
            requirements=request.requirements,
            delivery_channel=WorkbenchDeliveryChannel(request.delivery_channel),
            telegram_message_ref=request.telegram_message_ref,
            ai_metadata=request.ai_metadata,
        )
        return CreateAssignmentResponse(
            id=str(assignment.id),
            title=assignment.title,
            status=assignment.status.value,
            created_at=assignment.created_at
        )
    except Exception as e:
        logger.error(f"Failed to create workbench assignment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/assignments/next", response_model=ClaimNextResponse)
@require_authorization(["checker", "admin"]) # Checkers or admins can claim next
async def claim_next_assignment(
    current_user: Dict[str, Any] = Depends(get_current_user),
    workbench_service: WorkbenchService = Depends(get_workbench_service),
    db: Session = Depends(get_db)
):
    """
    Claims the next available workbench assignment for the current checker.
    """
    tenant_id = uuid.UUID(current_user["tenant_id"]) if "tenant_id" in current_user else uuid.uuid4()
    checker_id = current_user["checker_id"] # Assuming checker_id is part of JWT payload for checkers

    try:
        assignment = workbench_service.claim_next_assignment(db, tenant_id, checker_id)
        if assignment:
            return ClaimNextResponse(
                id=str(assignment.id),
                title=assignment.title,
                status=assignment.status.value,
                created_at=assignment.created_at,
                assigned_checker_id=assignment.assigned_checker_id,
                input_doc_uri=assignment.input_doc_uri,
                requirements=assignment.requirements,
                message=f"Assignment {assignment.id} claimed."
            )
        else:
            return ClaimNextResponse(message="No assignments available or claimed.")
    except Exception as e:
        logger.error(f"Failed to claim next assignment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/assignments/{assignment_id}/artifacts", response_model=ListArtifactsResponse)
@require_authorization(["checker", "admin"]) # Checkers or admins can view artifacts
async def list_assignment_artifacts(
    assignment_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    workbench_service: WorkbenchService = Depends(get_workbench_service),
    db: Session = Depends(get_db)
):
    """
    Lists all artifacts (e.g., original document, reports) associated with an assignment.
    """
    tenant_id = uuid.UUID(current_user["tenant_id"]) if "tenant_id" in current_user else uuid.uuid4()

    # Ensure assignment exists and is accessible by tenant
    assignment = workbench_service.assignment_repo.get_by_id(tenant_id, assignment_id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found or not accessible.")

    try:
        artifacts = workbench_service.list_artifacts_for_assignment(db, assignment_id)
        return ListArtifactsResponse(
            assignment_id=str(assignment_id),
            artifacts=[
                ArtifactRef(
                    id=str(a.id),
                    artifact_type=a.artifact_type.value,
                    object_key=a.object_key,
                    storage_provider=a.storage_provider,
                    size_bytes=a.size_bytes,
                    mime_type=a.mime_type,
                    checksum_sha256=a.checksum_sha256,
                    created_at=a.created_at
                ) for a in artifacts
            ]
        )
    except Exception as e:
        logger.error(f"Failed to list artifacts for assignment {assignment_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/assignments/{assignment_id}/submissions", response_model=SubmitResultsResponse)
@require_authorization(["checker"]) # Only checkers can submit results
async def submit_assignment_results(
    assignment_id: uuid.UUID,
    request: SubmitResultsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    workbench_service: WorkbenchService = Depends(get_workbench_service),
    db: Session = Depends(get_db)
):
    """
    Submits checker results for an assignment, including similarity/AI reports and modified document.
    """
    tenant_id = uuid.UUID(current_user["tenant_id"]) if "tenant_id" in current_user else uuid.uuid4()
    checker_id = current_user["checker_id"]

    try:
        submission = workbench_service.submit_results(
            db=db,
            tenant_id=tenant_id,
            assignment_id=assignment_id,
            checker_id=checker_id,
            submission_id=request.submission_id,
            similarity_report_payload=request.similarity_report,
            ai_report_payload=request.ai_report,
            modified_document_payload=request.modified_document,
            notes=request.notes,
        )

        # Check if the submission passed the initial validation (scores, presence of docs)
        similarity_score = submission.similarity_report.get("score")
        ai_score = submission.ai_report.get("score")

        message = "Submission received and validated."
        if not (assignment.requirements.get("min_similarity_score", 0.0) <= similarity_score <= assignment.requirements.get("max_similarity_score", 5.0)):
            message = f"Submission received, but similarity score {similarity_score}% is outside acceptable range."
        elif ai_score != assignment.requirements.get("expected_ai_score", 0.0):
            message = f"Submission received, but AI score {ai_score}% is not the expected {assignment.requirements.get('expected_ai_score', 0.0)}%."

        return SubmitResultsResponse(
            id=str(submission.id),
            status=submission.status.value,
            message=message,
            similarity_score=similarity_score,
            ai_score=ai_score
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit results for assignment {assignment_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/assignments/{assignment_id}/verify", response_model=VerifyAssignmentResponse)
@require_authorization(["admin"]) # Only admins can verify
async def verify_assignment(
    assignment_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    workbench_service: WorkbenchService = Depends(get_workbench_service),
    db: Session = Depends(get_db)
):
    """
    Verifies an assignment based on the latest submission and sets its final status (VERIFIED/REJECTED).
    """
    tenant_id = uuid.UUID(current_user["tenant_id"]) if "tenant_id" in current_user else uuid.uuid4()

    try:
        assignment = workbench_service.verify_assignment(db, tenant_id, assignment_id)
        latest_submission = workbench_service.submission_repo.get_latest_by_assignment(assignment_id)

        return VerifyAssignmentResponse(
            id=str(assignment.id),
            status=assignment.status.value,
            message=f"Assignment {assignment.id} set to {assignment.status.value}.",
            latest_submission_id=str(latest_submission.id) if latest_submission else None,
            similarity_score=latest_submission.similarity_report.get("score") if latest_submission else None,
            ai_score=latest_submission.ai_report.get("score") if latest_submission else None
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to verify assignment {assignment_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

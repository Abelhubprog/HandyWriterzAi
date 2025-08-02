import uuid
import logging
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..db.repositories.workbench_assignment_repo import WorkbenchAssignmentRepository
from ..db.repositories.workbench_submission_repo import WorkbenchSubmissionRepository
from ..db.repositories.workbench_artifact_repo import WorkbenchArtifactRepository
from ..db.repositories.workbench_section_status_repo import WorkbenchSectionStatusRepository
from ..db.models import (
    WorkbenchAssignment, WorkbenchAssignmentStatus, WorkbenchDeliveryChannel,
    WorkbenchSubmission, WorkbenchSubmissionStatus, WorkbenchArtifact, WorkbenchArtifactType,
    WorkbenchSectionStatus, ChunkStatus, User, Checker
)
from ..api.schemas.workbench import ReportPayload, ModifiedDocPayload

logger = logging.getLogger(__name__)

class WorkbenchService:
    def __init__(
        self,
        assignment_repo: WorkbenchAssignmentRepository,
        submission_repo: WorkbenchSubmissionRepository,
        artifact_repo: WorkbenchArtifactRepository,
        section_status_repo: WorkbenchSectionStatusRepository,
    ):
        self.assignment_repo = assignment_repo
        self.submission_repo = submission_repo
        self.artifact_repo = artifact_repo
        self.section_status_repo = section_status_repo

    def create_assignment(
        self,
        db: Session,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        requirements: Optional[Dict[str, Any]] = None,
        delivery_channel: WorkbenchDeliveryChannel = WorkbenchDeliveryChannel.WORKBENCH,
        telegram_message_ref: Optional[Dict[str, Any]] = None,
        source_conversation_id: Optional[uuid.UUID] = None,
        ai_metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkbenchAssignment:
        """Creates a new workbench assignment for human review."""
        assignment = self.assignment_repo.create(
            tenant_id=tenant_id,
            user_id=user_id,
            source_conversation_id=source_conversation_id,
            title=title,
            requirements=requirements,
            delivery_channel=delivery_channel,
            telegram_message_ref=telegram_message_ref,
            ai_metadata=ai_metadata,
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        logger.info(f"Workbench assignment created: {assignment.id} for tenant {tenant_id}")
        return assignment

    def claim_next_assignment(self, db: Session, tenant_id: uuid.UUID, checker_id: int) -> Optional[WorkbenchAssignment]:
        """Claims the next available assignment for a checker."""
        assignment = self.assignment_repo.claim_next(tenant_id, checker_id)
        if assignment:
            logger.info(f"Checker {checker_id} claimed assignment {assignment.id} for tenant {tenant_id}")
        else:
            logger.info(f"No assignments available for checker {checker_id} in tenant {tenant_id}")
        return assignment

    def submit_results(
        self,
        db: Session,
        tenant_id: uuid.UUID,
        assignment_id: uuid.UUID,
        checker_id: int,
        submission_id: str,
        similarity_report_payload: ReportPayload,
        ai_report_payload: ReportPayload,
        modified_document_payload: ModifiedDocPayload,
        notes: Optional[str] = None,
    ) -> WorkbenchSubmission:
        """Submits checker results for an assignment, including reports and modified document."""
        assignment = self.assignment_repo.get_by_id(tenant_id, assignment_id)
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found or not accessible by tenant {tenant_id}")

        # Basic validation of reports and modified document presence
        if not similarity_report_payload.urls or not ai_report_payload.urls or not modified_document_payload.urls:
            raise ValueError("All reports (similarity, AI) and modified document must have URLs.")

        # Enforce thresholds (configurable via requirements in assignment)
        min_similarity_score = assignment.requirements.get("min_similarity_score", 0.0)
        max_similarity_score = assignment.requirements.get("max_similarity_score", 5.0) # Default to 5%
        expected_ai_score = assignment.requirements.get("expected_ai_score", 0.0) # Default to 0%

        if not (min_similarity_score <= similarity_report_payload.score <= max_similarity_score):
            raise ValueError(f"Similarity score {similarity_report_payload.score}% is outside acceptable range ({min_similarity_score}-{max_similarity_score}%).")
        if ai_report_payload.score != expected_ai_score:
            raise ValueError(f"AI detection score {ai_report_payload.score}% is not the expected {expected_ai_score}%.")

        # Create/update submission
        submission = self.submission_repo.upsert_by_submission_id(
            assignment_id=assignment_id,
            checker_id=checker_id,
            submission_id=submission_id,
            similarity_report=similarity_report_payload.dict(),
            ai_report=ai_report_payload.dict(),
            modified_document=modified_document_payload.dict(),
            notes=notes,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Update assignment status
        self.assignment_repo.update_status(tenant_id, assignment_id, WorkbenchAssignmentStatus.AWAITING_VERIFICATION)
        logger.info(f"Submission {submission.id} for assignment {assignment_id} by checker {checker_id} processed. Status: {submission.status}")
        return submission

    def verify_assignment(self, db: Session, tenant_id: uuid.UUID, assignment_id: uuid.UUID) -> WorkbenchAssignment:
        """Verifies an assignment based on the latest submission and sets final status."""
        assignment = self.assignment_repo.get_by_id(tenant_id, assignment_id)
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found or not accessible by tenant {tenant_id}")

        if assignment.status != WorkbenchAssignmentStatus.AWAITING_VERIFICATION:
            raise ValueError(f"Assignment {assignment_id} is not in AWAITING_VERIFICATION status. Current: {assignment.status.value}")

        latest_submission = self.submission_repo.get_latest_by_assignment(assignment_id)
        if not latest_submission:
            raise ValueError(f"No submissions found for assignment {assignment_id}. Cannot verify.")

        # Re-run validation rules on the latest submission
        similarity_score = latest_submission.similarity_report.get("score", 100.0)
        ai_score = latest_submission.ai_report.get("score", 100.0)

        min_similarity_score = assignment.requirements.get("min_similarity_score", 0.0)
        max_similarity_score = assignment.requirements.get("max_similarity_score", 5.0)
        expected_ai_score = assignment.requirements.get("expected_ai_score", 0.0)

        is_similarity_ok = (min_similarity_score <= similarity_score <= max_similarity_score)
        is_ai_ok = (ai_score == expected_ai_score)

        if is_similarity_ok and is_ai_ok:
            assignment.status = WorkbenchAssignmentStatus.VERIFIED
            logger.info(f"Assignment {assignment_id} VERIFIED. Scores: Sim={similarity_score}%, AI={ai_score}%")
        else:
            assignment.status = WorkbenchAssignmentStatus.REJECTED
            logger.warning(f"Assignment {assignment_id} REJECTED. Scores: Sim={similarity_score}%, AI={ai_score}%. Expected Sim<={max_similarity_score}%, AI=={expected_ai_score}%.")

        assignment.updated_at = datetime.utcnow()
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def list_artifacts_for_assignment(self, db: Session, assignment_id: uuid.UUID) -> List[WorkbenchArtifact]:
        """Lists all artifacts associated with an assignment."""
        return self.artifact_repo.list_by_assignment(assignment_id)

    def list_submissions_for_assignment(self, db: Session, assignment_id: uuid.UUID) -> List[WorkbenchSubmission]:
        """Lists all submissions for a given assignment."""
        return self.submission_repo.list_by_assignment(assignment_id)

    def get_assignment_details(self, db: Session, tenant_id: uuid.UUID, assignment_id: uuid.UUID) -> Optional[WorkbenchAssignment]:
        """Gets full assignment details including related submissions and artifacts."""
        assignment = self.assignment_repo.get_by_id(tenant_id, assignment_id)
        if assignment:
            assignment.submissions = self.submission_repo.list_by_assignment(assignment_id)
            assignment.artifacts = self.artifact_repo.list_by_assignment(assignment_id)
        return assignment
